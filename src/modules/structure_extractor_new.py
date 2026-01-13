"""
课程结构抽取模块 - 简化版

直接让LLM生成Docsify sidebar，然后解析为结构
"""
import json
import re
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass

from ..prompts.templates import STRUCTURE_EXTRACTION_PROMPT


@dataclass
class Section:
    """小节数据类"""
    title: str


@dataclass
class Chapter:
    """章节数据类"""
    title: str
    filename: str  # 文件名（不含.md）
    sections: List[Section]
    order: int = 0


@dataclass
class CourseStructure:
    """课程结构数据类"""
    course_name: str
    chapters: List[Chapter]
    sidebar_md: str = ""  # 保存生成的sidebar markdown
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "course": self.course_name,
            "chapters": [
                {
                    "title": ch.title,
                    "filename": ch.filename,
                    "order": ch.order,
                    "sections": [s.title for s in ch.sections]
                }
                for ch in self.chapters
            ]
        }
    
    def to_json(self, output_file: Path):
        """保存为JSON文件"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)


class StructureExtractor:
    """课程结构抽取器"""
    
    def __init__(self, llm_client=None):
        """
        初始化结构抽取器
        
        Args:
            llm_client: LLM客户端
        """
        self.llm_client = llm_client
    
    def extract_from_markdown(self, md_file: Path) -> CourseStructure:
        """
        从Markdown文件中提取课程结构
        
        Args:
            md_file: Markdown文件路径
            
        Returns:
            课程结构对象
        """
        content = md_file.read_text(encoding='utf-8')
        
        if self.llm_client:
            return self._extract_with_llm(content, md_file.stem)
        else:
            return self._extract_with_rules(content, md_file.stem)
    
    def _extract_with_llm(self, content: str, course_name: str) -> CourseStructure:
        """
        使用LLM提取结构（直接生成sidebar）
        
        Args:
            content: Markdown内容
            course_name: 课程名称
            
        Returns:
            课程结构对象
        """
        prompt = f"""{STRUCTURE_EXTRACTION_PROMPT}

```markdown
{content[:60000]}
```

Now generate ONLY the sidebar markdown, no explanation:
"""
        
        # 调用LLM，使用deepseek-reasoner支持的更高token限制
        response = self.llm_client.generate(prompt, temperature=0.3, max_tokens=32000)
        
        print(f"\n{'='*60}")
        print(f"LLM生成的Sidebar (前500字符):")
        print(f"{'='*60}")
        print(response[:500] if len(response) > 500 else response)
        print(f"{'='*60}\n")
        
        # 清理response（移除代码块标记）
        sidebar_md = response.strip()
        if sidebar_md.startswith('```'):
            # 移除```markdown 或 ```
            sidebar_md = re.sub(r'^```\w*\n', '', sidebar_md)
            sidebar_md = re.sub(r'\n```$', '', sidebar_md)
        
        # 解析sidebar生成CourseStructure
        structure = self._parse_sidebar_to_structure(sidebar_md, course_name)
        
        return structure
    
    def _parse_sidebar_to_structure(self, sidebar_md: str, course_name: str) -> CourseStructure:
        """
        将sidebar markdown解析为CourseStructure对象
        
        Args:
            sidebar_md: Sidebar markdown文本
            course_name: 课程名称
            
        Returns:
            CourseStructure对象
        """
        chapters = []
        lines = sidebar_md.strip().split('\n')
        
        current_chapter = None
        current_filename = None
        current_sections = []
        order = 0
        
        for line in lines:
            line = line.rstrip()
            if not line or line.startswith('<!--'):
                continue
            
            # 检测顶级章节: * [Title](File.md)
            if re.match(r'^\* \[', line):
                # 保存前一个章节
                if current_chapter and current_filename:
                    chapters.append(Chapter(
                        title=current_chapter,
                        filename=current_filename,
                        sections=[Section(title=s) for s in current_sections],
                        order=order
                    ))
                    order += 1
                
                # 提取新章节
                match = re.match(r'^\* \[(.*?)\]\((.*?)\)', line)
                if match:
                    current_chapter = match.group(1)
                    current_filename = match.group(2).replace('.md', '')
                    current_sections = []
            
            # 检测小节: 2个空格开头 * [Title](File.md#anchor)
            elif re.match(r'^  \* \[', line):
                match = re.match(r'^  \* \[(.*?)\]\(.*?#.*?\)', line)
                if match and current_chapter:
                    section_title = match.group(1)
                    current_sections.append(section_title)
        
        # 保存最后一个章节
        if current_chapter and current_filename:
            chapters.append(Chapter(
                title=current_chapter,
                filename=current_filename,
                sections=[Section(title=s) for s in current_sections],
                order=order
            ))
        
        # 创建结构并保存sidebar
        structure = CourseStructure(
            course_name=course_name,
            chapters=chapters,
            sidebar_md=sidebar_md
        )
        
        return structure
    
    def _extract_with_rules(self, content: str, course_name: str) -> CourseStructure:
        """
        使用规则方法提取结构（备用）
        
        Args:
            content: Markdown内容
            course_name: 课程名称
            
        Returns:
            课程结构对象
        """
        chapters = []
        lines = content.split('\n')
        
        current_chapter = None
        current_sections = []
        order = 0
        
        for line in lines:
            # 检测章节标题（# 或 ##）
            if line.startswith('# '):
                if current_chapter:
                    chapters.append(Chapter(
                        title=current_chapter,
                        filename=self._sanitize_filename(current_chapter),
                        sections=[Section(title=s) for s in current_sections],
                        order=order
                    ))
                    order += 1
                
                current_chapter = line.lstrip('#').strip()
                current_sections = []
            
            elif line.startswith('## ') and current_chapter:
                section_title = line.lstrip('#').strip()
                current_sections.append(section_title)
        
        # 保存最后一个章节
        if current_chapter:
            chapters.append(Chapter(
                title=current_chapter,
                filename=self._sanitize_filename(current_chapter),
                sections=[Section(title=s) for s in current_sections],
                order=order
            ))
        
        return CourseStructure(
            course_name=course_name,
            chapters=chapters
        )
    
    def _sanitize_filename(self, title: str) -> str:
        """清理文件名"""
        import re
        # 移除特殊字符
        filename = re.sub(r'[^\w\s-]', '_', title)
        filename = re.sub(r'\s+', '_', filename)
        filename = re.sub(r'_+', '_', filename)
        return filename.strip('_')
    
    def merge_structures(self, structures: List[CourseStructure]) -> CourseStructure:
        """
        合并多个课程结构
        
        Args:
            structures: 结构列表
            
        Returns:
            合并后的结构
        """
        if not structures:
            return CourseStructure(course_name="Unknown", chapters=[])
        
        # 使用第一个的课程名
        course_name = structures[0].course_name
        
        # 合并所有chapters
        all_chapters = []
        for struct in structures:
            all_chapters.extend(struct.chapters)
        
        # 重新编号
        for i, ch in enumerate(all_chapters):
            ch.order = i + 1
        
        # 合并sidebar
        merged_sidebar = f"* [{course_name}](README.md)\n\n"
        for ch in all_chapters:
            merged_sidebar += f"* [{ch.title}]({ch.filename}.md)\n"
            for section in ch.sections:
                anchor = self._generate_anchor(section.title)
                merged_sidebar += f"  * [{section.title}]({ch.filename}.md#{anchor})\n"
            merged_sidebar += "\n"
        
        return CourseStructure(
            course_name=course_name,
            chapters=all_chapters,
            sidebar_md=merged_sidebar
        )
    
    def _generate_anchor(self, text: str) -> str:
        """生成锚点"""
        import re
        anchor = text.lower()
        anchor = re.sub(r'[^\w\s-]', '', anchor)
        anchor = re.sub(r'\s+', '-', anchor)
        anchor = re.sub(r'-+', '-', anchor)
        return anchor.strip('-')
