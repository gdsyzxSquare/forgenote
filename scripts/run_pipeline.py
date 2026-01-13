"""
ForgeNote简化版主流程

流程：
1. 导入文档 -> 合并markdown内容
2. 结构提取 -> LLM直接生成sidebar
3. 内容填充 -> 根据sidebar生成章节文件
4. 生成Docsify站点
"""
import sys
from pathlib import Path
import yaml
from dotenv import load_dotenv

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.modules.document_importer import DocumentImporter
from src.modules.structure_extractor_new import StructureExtractor
from src.modules.content_reorganizer_new import ContentReorganizer
from src.modules.docsify_generator_new import DocsifyGenerator
from src.utils.llm_client import OpenAIClient


def main():
    """主流程"""
    # 加载环境变量
    load_dotenv()
    
    # 读取配置
    config_path = Path("config/cfg.yaml")
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    print(f"\n{'='*60}")
    print(f"ForgeNote - {config['course']['name']}")
    print(f"{'='*60}\n")
    
    # 创建工作目录（使用配置文件中的输出路径）
    output_base = Path(config['paths'].get('output', 'output'))
    work_dir = output_base / config['course']['code'].split('/')[0]
    work_dir.mkdir(parents=True, exist_ok=True)
    
    content_dir = work_dir / "content"
    site_dir = work_dir / "docsify_site"
    
    # 初始化LLM客户端
    llm_client = None
    if config['processing'].get('use_llm', False):
        print("🤖 初始化LLM客户端...")
        llm_client = OpenAIClient(model=config['processing']['llm_model'])
        print(f"   模型: {config['processing']['llm_model']}\n")
    
    # ========== 步骤1: 导入文档 ==========
    print("📥 步骤1: 导入文档")
    print("-" * 60)
    
    importer = DocumentImporter(
        course_name=config['course']['name'],
        output_dir=work_dir
    )
    result = importer.import_from_mineru(
        mineru_output_dir=Path(config['paths']['mineru_output'])
    )
    file_mappings = result['file_mappings']
    imported_dir = importer.raw_md_dir  # 导入的文件在这里
    
    print(f"\n✓ 导入完成: {len(file_mappings)} 个文件\n")
    
    # ========== 步骤2: 提取结构 ==========
    print("🏗️  步骤2: 提取结构")
    print("-" * 60)
    
    extractor = StructureExtractor(llm_client=llm_client)
    
    # 读取所有导入的文件
    raw_contents = {}
    for dest_filename in file_mappings.keys():
        filepath = imported_dir / dest_filename
        if filepath.exists():
            raw_contents[dest_filename] = filepath.read_text(encoding='utf-8')
    
    # 提取结构
    # 合并所有内容
    all_content = "\n\n".join([
        f"# {filename}\n\n{content}"
        for filename, content in raw_contents.items()
    ])
    
    # 调用LLM生成sidebar
    if llm_client:
        structure = extractor._extract_with_llm(
            content=all_content,
            course_name=config['course']['name']
        )
    else:
        structure = extractor._extract_with_rules(
            content=all_content,
            course_name=config['course']['name']
        )
    
    print(f"\n✓ 结构提取完成:")
    print(f"   章节数: {len(structure.chapters)}")
    total_sections = sum(len(ch.sections) for ch in structure.chapters)
    print(f"   小节数: {total_sections}\n")
    
    # 保存sidebar预览
    sidebar_preview = work_dir / "sidebar_preview.md"
    sidebar_preview.write_text(structure.sidebar_md, encoding='utf-8')
    print(f"✓ Sidebar预览已保存: {sidebar_preview}\n")
    
    # ========== 步骤3: 重组内容 ==========
    print("📝 步骤3: 重组内容")
    print("-" * 60)
    
    reorganizer = ContentReorganizer(llm_client=llm_client)
    
    # 根据结构填充内容
    chapter_contents = reorganizer.reorganize_by_structure(
        structure=structure,
        raw_contents=raw_contents,
        course_name=config['course']['name']
    )
    
    print(f"\n✓ 内容重组完成: {len(chapter_contents)} 个章节文件\n")
    
    # ========== 步骤3.5: 美化内容 ==========
    print("✨ 步骤3.5: 美化内容")
    print("-" * 60)
    
    if config['processing'].get('use_llm', False):
        chapter_contents = reorganizer.beautify_content(chapter_contents)
        print(f"\n✓ 内容美化完成\n")
    else:
        print("  跳过美化（LLM未启用）\n")
    
    # 保存章节文件
    reorganizer.save_to_files(chapter_contents, content_dir)
    
    # ========== 步骤4: 生成Docsify站点 ==========
    print("🌐 步骤4: 生成Docsify站点")
    print("-" * 60)
    
    generator = DocsifyGenerator()
    generator.generate_site(
        course_name=config['course']['name'],
        sidebar_md=structure.sidebar_md,
        content_dir=content_dir,
        output_dir=site_dir,
        assets_dir=importer.assets_dir  # 传递assets目录
    )
    
    print(f"\n{'='*60}")
    print("✅ 处理完成!")
    print(f"{'='*60}\n")
    print(f"📂 Docsify站点目录: {site_dir.absolute()}")
    print(f"📄 Sidebar预览: {sidebar_preview.absolute()}")
    print(f"\n💡 预览网站:")
    print(f"   cd {site_dir.absolute()}")
    print(f"   python -m http.server 3000")
    print(f"   然后打开: http://localhost:3000\n")


if __name__ == "__main__":
    main()
