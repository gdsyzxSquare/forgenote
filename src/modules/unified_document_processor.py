"""
统一文档处理器 - 一次性生成完整章节

替代旧的三步骤流程（结构提取 → 内容重组 → 美化）
每个章节仅需一次LLM调用即可生成完整Markdown文档
"""
import re
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass


# 统一处理Prompt
UNIFIED_PROCESSING_PROMPT = """
You are a professional documentation expert. Generate a complete, well-formatted chapter from raw course material.

## CRITICAL CONSTRAINTS

1. **One File = One Chapter**: Generate EXACTLY ONE chapter for this input file
2. **Complete Output**: Output a full Markdown document with structure AND content (no placeholders)
3. **Preserve Language**: Keep ALL content in the original language (English/Chinese/etc.)
4. **No Translation**: DO NOT translate any content

## INPUT INFORMATION

**Original PDF Filename:** {filename}
**Extracted Content Title:** {title}

## TITLE GENERATION RULES

1. If the PDF filename contains semantic information:
   - Examples: "Chapter05Polymorphism" → "Chapter 5: Polymorphism"
   - Examples: "UML-ClassDiagram" → "UML Class Diagram"
   - Examples: "Introduction" → "Introduction"
2. If filename is meaningless (random UUID, "document1.pdf"), use the extracted title
3. DO NOT invent chapter numbers that don't exist in the filename

## STRUCTURE REQUIREMENTS

1. **Top-level heading** (# Chapter Title): ONE chapter title only
2. **Second-level headings** (## Section Title): Logical sections extracted from content
3. **Third-level headings** (### Subsection): Optional for detailed topics

## CONTENT REQUIREMENTS

1. **Extract and Reorganize**: Convert page-oriented slides to topic-oriented documentation
2. **Format Properly**:
   - Code blocks with language tags: ```java, ```python
   - Lists with proper indentation
   - Images: ![alt](path) - keep original paths
   - Tables: properly formatted
3. **Quality Standards**:
   - Clear explanations with context
   - Keep all examples, diagrams, formulas
   - Maintain academic rigor
4. **No Placeholders**: All sections must have complete content (no "Content to be added")

## OUTPUT FORMAT

```markdown
# Chapter Title

## Section 1: Title

[Complete formatted content with explanations, examples, code blocks...]

## Section 2: Title

[Complete formatted content...]

### Subsection 2.1

[Detailed content if needed...]

## Section 3: Title

[Complete formatted content...]
```

## RAW CONTENT

```markdown
{content}
```

---

**Now generate the complete chapter with full content and proper formatting:**
"""


@dataclass
class ChapterOutput:
    """章节输出"""
    title: str              # 章节标题
    filename: str           # 文件名（用于保存）
    content: str            # 完整Markdown内容
    sections: List[str]     # 提取的section标题列表（用于sidebar）


class UnifiedDocumentProcessor:
    """统一文档处理器"""
    
    def __init__(self, llm_client=None):
        """
        初始化处理器
        
        Args:
            llm_client: LLM客户端
        """
        self.llm_client = llm_client
    
    def process_chapters(
        self,
        chapter_list: List[Dict],
        output_dir: Path,
        course_name: str
    ) -> List[ChapterOutput]:
        """
        逐章处理，每章一次LLM调用生成完整文档
        
        Args:
            chapter_list: [{"filename": "xxx.md", "title": "xxx", "content": "xxx"}]
            output_dir: 输出目录
            course_name: 课程名称
            
        Returns:
            章节输出列表
        """
        if not self.llm_client:
            # 无LLM时使用简单模式
            return self._process_chapters_simple(chapter_list, output_dir)
        
        output_dir.mkdir(parents=True, exist_ok=True)
        chapters = []
        total = len(chapter_list)
        used_filenames = set()  # 追踪已使用的文件名，避免冲突
        
        print(f"\n{'='*60}")
        print(f"📝 统一处理流程（共{total}章）")
        print(f"{'='*60}\n")
        
        for i, chapter_info in enumerate(chapter_list, 1):
            print(f"[{i}/{total}] 处理: {chapter_info['title']}")
            print(f"  原始文件: {chapter_info['filename']}")
            
            # 构建prompt
            prompt = UNIFIED_PROCESSING_PROMPT.format(
                filename=chapter_info['filename'],
                title=chapter_info['title'],
                content=chapter_info['content'][:60000]  # deepseek-reasoner 60k输入限制
            )
            
            # 一次LLM调用生成完整章节
            try:
                response = self.llm_client.generate(
                    prompt,
                    temperature=0.3,
                    max_tokens=32000
                )
                
                # 清理markdown代码块标记
                markdown_content = response.strip()
                if markdown_content.startswith('```'):
                    markdown_content = re.sub(r'^```\w*\n', '', markdown_content)
                    markdown_content = re.sub(r'\n```$', '', markdown_content)
                
                # 解析生成的内容
                chapter_output = self._parse_generated_content(
                    markdown_content,
                    chapter_info['filename']
                )
                
                # 文件名去重：如果已存在，添加后缀
                chapter_output.filename = self._ensure_unique_filename(
                    chapter_output.filename,
                    used_filenames
                )
                used_filenames.add(chapter_output.filename)
                
                # 保存文件
                output_file = output_dir / chapter_output.filename
                output_file.write_text(chapter_output.content, encoding='utf-8')
                
                chapters.append(chapter_output)
                
                print(f"  ✓ 章节标题: {chapter_output.title}")
                print(f"  ✓ Sections: {len(chapter_output.sections)} 个")
                print(f"  ✓ 内容长度: {len(chapter_output.content)} 字符")
                print(f"  ✓ 已保存: {chapter_output.filename}\n")
                
            except Exception as e:
                print(f"  ✗ 处理失败: {e}")
                # 降级到简单模式
                fallback = self._create_fallback_chapter(chapter_info)
                chapters.append(fallback)
                output_file = output_dir / fallback.filename
                output_file.write_text(fallback.content, encoding='utf-8')
                print(f"  ⚠ 使用fallback模式\n")
        
        print(f"{'='*60}")
        print(f"✅ 全部完成: {len(chapters)} 个章节")
        print(f"{'='*60}\n")
        
        return chapters
    
    def _parse_generated_content(
        self,
        markdown_content: str,
        original_filename: str
    ) -> ChapterOutput:
        """
        解析LLM生成的Markdown内容
        
        Args:
            markdown_content: LLM生成的完整Markdown
            original_filename: 原始文件名（用于生成输出文件名）
            
        Returns:
            ChapterOutput对象
        """
        # 提取章节标题（第一个 # 标题）
        title_match = re.search(r'^#\s+(.+)$', markdown_content, re.MULTILINE)
        chapter_title = title_match.group(1).strip() if title_match else "Untitled Chapter"
        
        # 提取所有二级标题作为sections
        sections = re.findall(r'^##\s+(.+)$', markdown_content, re.MULTILINE)
        
        # 生成文件名：优先使用原始文件名基础部分，避免冲突
        filename = self._generate_output_filename(chapter_title, original_filename)
        
        return ChapterOutput(
            title=chapter_title,
            filename=filename,
            content=markdown_content,
            sections=sections
        )
    
    def generate_sidebar(self, chapters: List[ChapterOutput]) -> str:
        """
        从已处理的章节生成sidebar
        
        Args:
            chapters: 章节输出列表
            
        Returns:
            Sidebar markdown字符串
        """
        sidebar_lines = []
        
        for chapter in chapters:
            # 章节标题
            sidebar_lines.append(f"* [{chapter.title}]({chapter.filename})")
            
            # Sections（从内容中提取二级标题）
            for section in chapter.sections:
                anchor = self._create_anchor(section)
                sidebar_lines.append(f"  * [{section}]({chapter.filename}#{anchor})")
        
        return '\n'.join(sidebar_lines)
    
    def _generate_output_filename(
        self,
        chapter_title: str,
        original_filename: str
    ) -> str:
        """
        生成输出文件名，优先使用原始文件名避免冲突
        
        Args:
            chapter_title: LLM生成的章节标题
            original_filename: 原始PDF文件名（如 "CECZ2002_Chapter0_Introduction(1).pdf-xxx.md"）
            
        Returns:
            输出文件名（含.md扩展名）
        """
        # 提取原始文件名的语义部分（移除UUID和.pdf扩展名）
        # 例如: "CECZ2002_Chapter0_Introduction(1).pdf-xxx.md" → "CECZ2002_Chapter0_Introduction_1"
        base_name = original_filename.split('.pdf-')[0] if '.pdf-' in original_filename else original_filename
        base_name = base_name.replace('.pdf', '').replace('.md', '')
        
        # 清理特殊字符
        base_name = re.sub(r'[<>:"/\\|?*#()]', '', base_name)
        base_name = re.sub(r'\s+', '_', base_name).strip('_.')
        
        # 如果原始文件名有意义（长度>10且包含字母），优先使用
        if len(base_name) > 10 and re.search(r'[a-zA-Z]', base_name):
            # 限制长度
            if len(base_name) > 80:
                base_name = base_name[:80]
            return base_name + ".md"
        
        # 否则使用章节标题（处理冲突由外层 ensure_unique_filename 处理）
        filename = self._sanitize_filename(chapter_title)
        return filename + ".md"
    
    def _sanitize_filename(self, title: str) -> str:
        """
        清理标题为合法文件名
        
        Args:
            title: 章节标题
            
        Returns:
            合法文件名（不含扩展名）
        """
        # 移除特殊字符
        filename = re.sub(r'[<>:"/\\|?*#]', '', title)
        # 替换空格和多个连续空格
        filename = re.sub(r'\s+', '_', filename)
        # 移除开头结尾的下划线和点
        filename = filename.strip('_.')
        # 限制长度
        if len(filename) > 100:
            filename = filename[:100]
        
        return filename or "Chapter"
    
    def _ensure_unique_filename(
        self,
        filename: str,
        used_filenames: set
    ) -> str:
        """
        确保文件名唯一，如果冲突则添加后缀
        
        Args:
            filename: 候选文件名（含.md扩展名）
            used_filenames: 已使用的文件名集合
            
        Returns:
            唯一的文件名
        """
        if filename not in used_filenames:
            return filename
        
        # 文件名冲突，添加数字后缀
        base = filename.replace('.md', '')
        counter = 2
        while f"{base}_{counter}.md" in used_filenames:
            counter += 1
        
        return f"{base}_{counter}.md"
    
    def _create_anchor(self, section_title: str) -> str:
        """
        创建Docsify anchor
        
        Args:
            section_title: Section标题
            
        Returns:
            anchor字符串
        """
        # Docsify规则：小写，空格替换为连字符，移除特殊字符
        anchor = section_title.lower()
        anchor = re.sub(r'[^\w\s\u4e00-\u9fff-]', '', anchor)  # 保留中文
        anchor = re.sub(r'\s+', '-', anchor)
        anchor = anchor.strip('-')
        return anchor
    
    def _process_chapters_simple(
        self,
        chapter_list: List[Dict],
        output_dir: Path
    ) -> List[ChapterOutput]:
        """
        简单模式：无LLM时的降级处理
        
        Args:
            chapter_list: 章节列表
            output_dir: 输出目录
            
        Returns:
            章节输出列表
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        chapters = []
        
        print("\n⚠ 无LLM客户端，使用简单模式\n")
        
        for chapter_info in chapter_list:
            fallback = self._create_fallback_chapter(chapter_info)
            chapters.append(fallback)
            
            output_file = output_dir / fallback.filename
            output_file.write_text(fallback.content, encoding='utf-8')
            print(f"✓ {fallback.filename}")
        
        return chapters
    
    def _create_fallback_chapter(self, chapter_info: Dict) -> ChapterOutput:
        """
        创建降级章节（无LLM或出错时使用）
        
        Args:
            chapter_info: 章节信息
            
        Returns:
            ChapterOutput对象
        """
        title = chapter_info['title']
        content = f"# {title}\n\n{chapter_info['content']}"
        
        # 提取二级标题
        sections = re.findall(r'^##\s+(.+)$', content, re.MULTILINE)
        
        filename = self._sanitize_filename(title) + ".md"
        
        return ChapterOutput(
            title=title,
            filename=filename,
            content=content,
            sections=sections
        )
