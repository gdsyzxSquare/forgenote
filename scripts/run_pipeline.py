"""
ForgeNote Main Pipeline

Pipeline:
1. Import documents -> Merge markdown content
2. Structure extraction -> LLM generates sidebar
3. Content reorganization -> Generate chapter files based on sidebar
4. Generate Docsify site
"""
import sys
from pathlib import Path
import yaml
from dotenv import load_dotenv

# 添加src到路径
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

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
        print("🤖 Initializing LLM client...")
        llm_client = OpenAIClient(model=config['processing']['llm_model'])
        print(f"   Model: {config['processing']['llm_model']}\n")
    
    # ========== Step 1: Import Documents ==========
    print("📥 Step 1: Importing documents")
    print("-" * 60)
    
    importer = DocumentImporter(
        course_name=config['course']['name'],
        output_dir=work_dir
    )
    result = importer.import_from_mineru(
        mineru_output_dir=Path(config['paths']['mineru_output'])
    )
    file_mappings = result['file_mappings']
    imported_dir = importer.raw_md_dir
    
    print(f"✓ Imported {len(file_mappings)} files\n")
    
    # ========== Step 2: Extract Structure ==========
    print("🏗️  Step 2: Extracting structure")
    print("-" * 60)
    
    extractor = StructureExtractor(llm_client=llm_client)
    
    # 读取所有导入的文件
    raw_contents = {}
    for dest_filename in file_mappings.keys():
        filepath = imported_dir / dest_filename
        if filepath.exists():
            raw_contents[dest_filename] = filepath.read_text(encoding='utf-8')
    
    # 提取结构 - 合并所有内容
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
    
    print(f"✓ Structure extracted: {len(structure.chapters)} chapters, {sum(len(ch.sections) for ch in structure.chapters)} sections\n")
    
    # 保存sidebar预览
    sidebar_preview = work_dir / "sidebar_preview.md"
    sidebar_preview.write_text(structure.sidebar_md, encoding='utf-8')
    
    # ========== Step 3: Reorganize Content ==========
    print("📝 Step 3: Reorganizing content")
    print("-" * 60)
    
    reorganizer = ContentReorganizer(llm_client=llm_client)
    
    # 根据结构填充内容
    chapter_contents = reorganizer.reorganize_by_structure(
        structure=structure,
        raw_contents=raw_contents,
        course_name=config['course']['name']
    )
    
    print(f"✓ Content reorganized: {len(chapter_contents)} chapters\n")
    
    # ========== Step 3.5: Beautify Content ==========
    if config['processing'].get('use_llm', False):
        print("✨ Step 3.5: Beautifying content")
        print("-" * 60)
        chapter_contents = reorganizer.beautify_content(chapter_contents)
        print(f"✓ Content beautified\n")
    
    # 保存章节文件
    reorganizer.save_to_files(chapter_contents, content_dir)
    
    # ========== Step 4: Generate Docsify Site ==========
    print("🌐 Step 4: Generating Docsify site")
    print("-" * 60)
    
    generator = DocsifyGenerator()
    generator.generate_site(
        course_name=config['course']['name'],
        sidebar_md=structure.sidebar_md,
        content_dir=content_dir,
        output_dir=site_dir,
        assets_dir=importer.assets_dir
    )
    
    print(f"\n{'='*60}")
    print("✅ Pipeline completed successfully!")
    print(f"{'='*60}\n")
    print(f"📂 Documentation: {site_dir.absolute()}")
    print(f"\n💡 Next steps:")
    print(f"   Start debug server with:")
    print(f"   python scripts/start_debug_server.py {site_dir}")
    print(f"   Or simply: python scripts/start_debug_server.py")
    print(f"   (You'll be prompted to enter the path)")
    print(f"\n   Then open: http://localhost:3000\n")


if __name__ == "__main__":
    main()
