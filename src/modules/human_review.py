"""
人工干预机制模块

功能：
1. 生成需要人工审查的内容清单
2. 保存人工修正的patch
3. 应用patch到最终文档
"""
import json
import yaml
from pathlib import Path
from typing import Dict, List
from dataclasses import dataclass, asdict
from ..prompts.templates import HUMAN_REVIEW_PROMPT


@dataclass
class ReviewItem:
    """审查项"""
    type: str  # image_mismatch, content_error, format_issue等
    location: str  # 位置描述（章节、小节）
    line_number: int  # 行号
    description: str  # 问题描述
    suggestion: str  # 修改建议
    severity: str  # high, medium, low
    status: str = "pending"  # pending, confirmed, fixed, ignored


@dataclass
class ImagePatch:
    """图片修正补丁"""
    file: str  # 文件路径
    line: int  # 行号
    old_image: str  # 原图片路径
    new_image: str  # 新图片路径
    reason: str  # 修正原因


@dataclass
class ContentPatch:
    """内容修正补丁"""
    file: str
    line_start: int
    line_end: int
    old_content: str
    new_content: str
    reason: str


class HumanReviewManager:
    """人工审查管理器"""
    
    def __init__(self, course_name: str, data_dir: Path):
        """
        初始化审查管理器
        
        Args:
            course_name: 课程名称
            data_dir: 数据目录
        """
        self.course_name = course_name
        self.data_dir = data_dir
        self.review_dir = data_dir / "reviews" / course_name
        self.patch_dir = data_dir / "patches" / course_name
        
        self.review_dir.mkdir(parents=True, exist_ok=True)
        self.patch_dir.mkdir(parents=True, exist_ok=True)
        
        self.llm_client = None
    
    def generate_review_list(self, content_dir: Path) -> List[ReviewItem]:
        """
        生成审查清单
        
        Args:
            content_dir: 内容目录
            
        Returns:
            审查项列表
        """
        review_items = []
        
        # 遍历所有Markdown文件
        for md_file in content_dir.glob("*.md"):
            content = md_file.read_text(encoding='utf-8')
            
            if self.llm_client:
                # 使用LLM识别高风险项
                items = self._analyze_with_llm(content, md_file.name)
                review_items.extend(items)
            else:
                # 使用规则方法识别
                items = self._analyze_with_rules(content, md_file.name)
                review_items.extend(items)
        
        # 保存审查清单
        self._save_review_list(review_items)
        
        return review_items
    
    def _analyze_with_llm(self, content: str, filename: str) -> List[ReviewItem]:
        """
        使用LLM分析内容
        
        Args:
            content: 文件内容
            filename: 文件名
            
        Returns:
            审查项列表
        """
        prompt = HUMAN_REVIEW_PROMPT.format(content=content[:8000])
        response = self.llm_client.generate(prompt)
        
        # 解析LLM返回的JSON
        result = json.loads(response)
        
        items = []
        for severity in ['high_risk_items', 'medium_risk_items', 'low_risk_items']:
            severity_level = severity.split('_')[0]
            for item in result.get(severity, []):
                items.append(ReviewItem(
                    type=item['type'],
                    location=f"{filename} - {item['location']}",
                    line_number=item['line_number'],
                    description=item['description'],
                    suggestion=item['suggestion'],
                    severity=severity_level
                ))
        
        return items
    
    def _analyze_with_rules(self, content: str, filename: str) -> List[ReviewItem]:
        """
        使用规则方法分析内容
        
        Args:
            content: 文件内容
            filename: 文件名
            
        Returns:
            审查项列表
        """
        items = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # 检查图片引用
            if '![' in line and '](' in line:
                # 简单检测：图片路径是否存在
                # 实际实现需要检查文件系统
                items.append(ReviewItem(
                    type="image_reference",
                    location=f"{filename} - Line {i}",
                    line_number=i,
                    description="检查图片路径是否正确，图片内容是否匹配",
                    suggestion="人工验证图片",
                    severity="medium"
                ))
            
            # 检查是否有残留的页码标记
            if any(marker in line for marker in ['Page ', '第', '页']):
                items.append(ReviewItem(
                    type="noise_text",
                    location=f"{filename} - Line {i}",
                    line_number=i,
                    description="可能包含页码或其他噪声文本",
                    suggestion="确认是否需要删除",
                    severity="low"
                ))
        
        return items
    
    def _save_review_list(self, items: List[ReviewItem]):
        """
        保存审查清单
        
        Args:
            items: 审查项列表
        """
        # 保存为JSON
        review_file = self.review_dir / "review_list.json"
        with open(review_file, 'w', encoding='utf-8') as f:
            json.dump([asdict(item) for item in items], f, ensure_ascii=False, indent=2)
        
        # 同时保存为YAML（更易读）
        review_yaml = self.review_dir / "review_list.yaml"
        with open(review_yaml, 'w', encoding='utf-8') as f:
            yaml.dump([asdict(item) for item in items], f, allow_unicode=True)
    
    def save_patch(self, patch: ImagePatch or ContentPatch):
        """
        保存人工修正补丁
        
        Args:
            patch: 补丁对象
        """
        # 生成补丁文件名
        patch_file = self.patch_dir / f"patch_{len(list(self.patch_dir.glob('*.yaml'))) + 1}.yaml"
        
        with open(patch_file, 'w', encoding='utf-8') as f:
            yaml.dump(asdict(patch), f, allow_unicode=True)
    
    def apply_patches(self, content_dir: Path):
        """
        应用所有补丁
        
        Args:
            content_dir: 内容目录
        """
        # 读取所有补丁文件
        patches = []
        for patch_file in self.patch_dir.glob("*.yaml"):
            with open(patch_file, 'r', encoding='utf-8') as f:
                patch_data = yaml.safe_load(f)
                patches.append(patch_data)
        
        # 按文件分组
        file_patches = {}
        for patch in patches:
            file_path = patch['file']
            if file_path not in file_patches:
                file_patches[file_path] = []
            file_patches[file_path].append(patch)
        
        # 应用补丁
        for file_path, patches in file_patches.items():
            self._apply_patches_to_file(content_dir / file_path, patches)
    
    def _apply_patches_to_file(self, file_path: Path, patches: List[Dict]):
        """
        应用补丁到单个文件
        
        Args:
            file_path: 文件路径
            patches: 补丁列表
        """
        if not file_path.exists():
            return
        
        content = file_path.read_text(encoding='utf-8')
        lines = content.split('\n')
        
        # 按行号排序（从大到小，避免行号偏移）
        patches_sorted = sorted(patches, key=lambda p: p.get('line', 0), reverse=True)
        
        for patch in patches_sorted:
            if 'old_image' in patch:
                # 图片补丁
                line_num = patch['line'] - 1  # 转为0-based索引
                if line_num < len(lines):
                    lines[line_num] = lines[line_num].replace(
                        patch['old_image'],
                        patch['new_image']
                    )
            elif 'old_content' in patch:
                # 内容补丁
                start = patch['line_start'] - 1
                end = patch['line_end']
                lines[start:end] = [patch['new_content']]
        
        # 写回文件
        file_path.write_text('\n'.join(lines), encoding='utf-8')
    
    def export_review_ui_data(self) -> Dict:
        """
        导出用于UI的审查数据
        
        Returns:
            UI数据字典
        """
        review_file = self.review_dir / "review_list.json"
        if not review_file.exists():
            return {"items": []}
        
        with open(review_file, 'r', encoding='utf-8') as f:
            items = json.load(f)
        
        # 按严重程度分组
        grouped = {
            "high": [item for item in items if item['severity'] == 'high'],
            "medium": [item for item in items if item['severity'] == 'medium'],
            "low": [item for item in items if item['severity'] == 'low']
        }
        
        return {
            "course_name": self.course_name,
            "total_items": len(items),
            "items_by_severity": grouped,
            "all_items": items
        }
