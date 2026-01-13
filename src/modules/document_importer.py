"""
文档导入与预处理模块

功能：
1. 调用MinerU转换PPT/PDF为Markdown
2. 整理输出文件到标准目录结构
3. 提取和组织图片资源
"""
import os
import shutil
from pathlib import Path
from typing import List, Dict
import json


class DocumentImporter:
    """文档导入处理器"""
    
    def __init__(self, course_name: str, output_dir: Path):
        """
        初始化文档导入器
        
        Args:
            course_name: 课程名称
            output_dir: 输出目录根路径（如 output/SC2006/）
        """
        self.course_name = course_name
        self.course_name_sanitized = self._sanitize_filename(course_name)
        self.output_dir = output_dir
        self.raw_md_dir = output_dir / "raw_md" / course_name
        # 直接将assets保存到docsify_site下，避免冗余复制
        self.assets_dir = output_dir / "docsify_site" / "assets"
        
        # 创建必要的目录
        self.raw_md_dir.mkdir(parents=True, exist_ok=True)
        self.assets_dir.mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        """
        规范化文件名，移除或替换特殊字符
        
        Args:
            filename: 原始文件名
            
        Returns:
            规范化后的文件名
        """
        import re
        # 替换空格为下划线
        sanitized = filename.replace(' ', '_')
        # 移除其他特殊字符（保留字母、数字、下划线、连字符、点）
        sanitized = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', sanitized)
        # 移除连续的下划线
        sanitized = re.sub(r'_+', '_', sanitized)
        # 移除首尾下划线
        sanitized = sanitized.strip('_')
        return sanitized
    
    def import_from_mineru(self, mineru_output_dir: Path) -> Dict[str, any]:
        """
        从MinerU输出目录导入文件
        
        MinerU输出结构：
        mineru_output_dir/
        ├── file1/
        │   ├── file1.md
        │   └── images/
        │       ├── img1.png
        │       └── img2.png
        ├── file2/
        │   ├── file2.md
        │   └── images/
        │       └── img1.png
        
        Args:
            mineru_output_dir: MinerU的输出目录
            
        Returns:
            包含导入信息的字典
        """
        result = {
            "course_name": self.course_name,
            "markdown_files": [],
            "image_files": [],
            "file_mappings": {},  # 记录文件和图片的映射关系
            "status": "success"
        }
        
        try:
            # 遍历MinerU输出目录中的每个文件夹
            for item in mineru_output_dir.iterdir():
                if not item.is_dir():
                    continue
                
                file_name = item.name
                file_name_sanitized = self._sanitize_filename(file_name)
                
                # 查找该文件夹下的.md文件
                md_files = list(item.glob("*.md"))
                if not md_files:
                    print(f"警告: 文件夹 {file_name} 中未找到.md文件")
                    continue
                
                # 复制Markdown文件（通常每个文件夹只有一个）
                dest_filename = None
                for idx, md_file in enumerate(md_files):
                    # 使用文件夹名作为文件名前缀，避免重复
                    # 例如：lecture1/full.md -> lecture1.md
                    if md_file.name == "full.md":
                        dest_filename = f"{file_name}.md"
                    else:
                        dest_filename = f"{file_name}_{md_file.stem}.md"
                    
                    dest_file = self.raw_md_dir / dest_filename
                    shutil.copy2(md_file, dest_file)
                    result["markdown_files"].append(str(dest_file))
                    
                    # 初始化该文件的图片映射
                    result["file_mappings"][dest_filename] = {
                        "source_folder": str(item),
                        "original_filename": md_file.name,
                        "images": []
                    }
                
                # 如果没有找到md文件，跳过图片处理
                if not dest_filename:
                    continue
                
                # 复制该文件夹下的images子文件夹
                images_dir = item / "images"
                if images_dir.exists() and images_dir.is_dir():
                    # 为每个源文件创建独立的图片目录（使用规范化的文件名）
                    dest_images_dir = self.assets_dir / file_name_sanitized / "images"
                    dest_images_dir.mkdir(parents=True, exist_ok=True)
                    
                    # 复制所有图片
                    image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.bmp', '.webp']
                    for img_file in images_dir.iterdir():
                        if img_file.is_file() and img_file.suffix.lower() in image_extensions:
                            dest_img = dest_images_dir / img_file.name
                            shutil.copy2(img_file, dest_img)
                            result["image_files"].append(str(dest_img))
                            
                            # 记录图片映射（使用规范化的路径）
                            result["file_mappings"][dest_filename]["images"].append({
                                "original": str(img_file),
                                "destination": str(dest_img),
                                "relative_path": f"../assets/{file_name_sanitized}/images/{img_file.name}"
                            })
            
            # 更新Markdown中的图片路径
            self._update_image_paths(result["file_mappings"])
            
        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            import traceback
            result["traceback"] = traceback.format_exc()
        
        return result
    
    def _update_image_paths(self, file_mappings: Dict):
        """
        更新Markdown文件中的图片路径为相对路径
        
        Args:
            file_mappings: 文件和图片的映射关系
        """
        import re
        
        for md_filename, mapping in file_mappings.items():
            md_file = self.raw_md_dir / md_filename
            if not md_file.exists():
                continue
            
            content = md_file.read_text(encoding='utf-8')
            
            # 替换图片路径
            # MinerU通常使用相对路径: images/xxx.png 或 ./images/xxx.png
            for img_info in mapping["images"]:
                img_name = Path(img_info["original"]).name
                new_relative_path = img_info["relative_path"]
                
                # 匹配多种可能的图片引用格式
                patterns = [
                    rf'!\[([^\]]*)\]\(images/{re.escape(img_name)}\)',
                    rf'!\[([^\]]*)\]\(\.\/images/{re.escape(img_name)}\)',
                    rf'!\[([^\]]*)\]\(\.\.\/images/{re.escape(img_name)}\)',
                    rf'!\[([^\]]*)\]\({re.escape(img_name)}\)',
                ]
                
                for pattern in patterns:
                    content = re.sub(
                        pattern,
                        rf'![\1]({new_relative_path})',
                        content
                    )
            
            # 写回文件
            md_file.write_text(content, encoding='utf-8')
            print(f"✓ 已更新图片路径: {md_filename}")
    
    def list_imported_files(self) -> Dict[str, List[str]]:
        """
        列出已导入的文件
        
        Returns:
            包含Markdown和图片文件列表的字典
        """
        return {
            "markdown_files": [str(f) for f in self.raw_md_dir.glob("*.md")],
            "image_files": [str(f) for f in self.assets_dir.rglob("*") if f.is_file()]
        }
    
    def save_metadata(self, metadata: Dict):
        """
        保存导入元数据
        
        Args:
            metadata: 元数据字典
        """
        metadata_file = self.raw_md_dir / "metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)


def process_single_file(input_file: Path, course_name: str, output_dir: Path) -> Dict:
    """
    处理单个PPT/PDF文件
    
    Args:
        input_file: 输入文件路径
        course_name: 课程名称
        output_dir: 输出目录
        
    Returns:
        处理结果字典
    """
    # 这里应该调用MinerU的API或命令行工具
    # 由于MinerU的具体接口可能需要配置，这里提供框架
    
    print(f"处理文件: {input_file}")
    print(f"课程名称: {course_name}")
    print(f"输出目录: {output_dir}")
    
    # TODO: 实际调用MinerU
    # mineru_command = f"mineru convert {input_file} -o {temp_output}"
    # os.system(mineru_command)
    
    return {
        "status": "success",
        "message": "请配置MinerU后使用"
    }
