"""
内容重组模块 - 简化版

基于sidebar结构，为每个章节填充内容
"""
from pathlib import Path
from typing import List, Dict
from dataclasses import dataclass

from ..prompts.templates import CONTENT_REORGANIZATION_PROMPT, MARKDOWN_BEAUTIFY_PROMPT


@dataclass
class ChapterContent:
    """章节内容"""
    filename: str
    title: str
    sections: List[Dict[str, str]]  # [{"title": "xxx", "content": "yyy"}]


class ContentReorganizer:
    """内容重组器"""
    
    def __init__(self, llm_client=None):
        """
        初始化重组器
        
        Args:
            llm_client: LLM客户端
        """
        self.llm_client = llm_client
    
    def reorganize_by_structure(
        self,
        structure: 'CourseStructure',
        raw_contents: Dict[str, str],  # {filename: content}
        course_name: str
    ) -> List[ChapterContent]:
        """
        根据结构重组内容
        
        Args:
            structure: 课程结构
            raw_contents: 原始内容 {filename: content}
            course_name: 课程名称
            
        Returns:
            章节内容列表
        """
        chapter_contents = []
        
        # 将raw_contents按文件名排序，便于匹配
        raw_list = list(raw_contents.items())
        
        for idx, chapter in enumerate(structure.chapters):
            print(f"\n处理章节: {chapter.title}")
            
            # 尝试找到对应的原始文件
            # 假设章节按导入顺序对应原始文件
            chapter_raw_content = ""
            if idx < len(raw_list):
                chapter_raw_content = raw_list[idx][1]
                print(f"  使用原始文件: {raw_list[idx][0]}")
            else:
                # 如果没有对应文件，使用所有内容
                chapter_raw_content = "\n\n".join(raw_contents.values())
                print(f"  使用所有原始内容")
            
            if self.llm_client and chapter.sections:
                # 使用LLM填充内容
                content = self._fill_chapter_with_llm(
                    chapter.title,
                    [s.title for s in chapter.sections],
                    chapter_raw_content
                )
            else:
                # 简单填充
                content = self._fill_chapter_simple(
                    chapter.title,
                    [s.title for s in chapter.sections]
                )
            
            chapter_contents.append(ChapterContent(
                filename=chapter.filename,
                title=chapter.title,
                sections=content
            ))
        
        return chapter_contents
    
    def _fill_chapter_with_llm(
        self,
        chapter_title: str,
        section_titles: List[str],
        raw_content: str
    ) -> List[Dict[str, str]]:
        """
        使用LLM填充章节内容
        
        Args:
            chapter_title: 章节标题
            section_titles: 小节标题列表
            raw_content: 原始内容
            
        Returns:
            [{"title": "section", "content": "..."}]
        """
        # 构建sections列表字符串
        sections_str = "\n".join([f"- {s}" for s in section_titles])
        
        prompt = CONTENT_REORGANIZATION_PROMPT.format(
            chapter_title=chapter_title,
            sections=sections_str,
            content=raw_content[:60000]  # deepseek-reasoner支持更长输入
        )
        
        # 调用LLM，使用deepseek-reasoner的32k输出能力
        response = self.llm_client.generate(prompt, temperature=0.3, max_tokens=32000)
        
        # 调试输出：显示LLM返回的前1000字符
        print(f"\n  [调试] LLM返回内容前1000字符:")
        print(f"  {response[:1000]}")
        print(f"  [调试] LLM返回总长度: {len(response)} 字符\n")
        
        # 解析markdown响应
        sections = self._parse_chapter_markdown(response, section_titles)
        
        return sections
    
    def _parse_chapter_markdown(
        self,
        markdown: str,
        expected_sections: List[str]
    ) -> List[Dict[str, str]]:
        """
        解析LLM返回的章节markdown
        
        Args:
            markdown: LLM返回的markdown
            expected_sections: 期望的小节列表
            
        Returns:
            [{"title": "section", "content": "..."}]
        """
        import re
        
        sections = []
        lines = markdown.split('\n')
        
        current_section = None
        current_content = []
        
        for line in lines:
            # 检测## 小节标题
            if line.startswith('## '):
                # 保存前一个section
                if current_section:
                    sections.append({
                        "title": current_section,
                        "content": '\n'.join(current_content).strip()
                    })
                
                # 开始新section
                current_section = line.lstrip('#').strip()
                current_content = []
            elif current_section:
                current_content.append(line)
        
        # 保存最后一个section
        if current_section:
            sections.append({
                "title": current_section,
                "content": '\n'.join(current_content).strip()
            })
        
        # 调试输出：显示解析结果
        print(f"  [调试] 解析到 {len(sections)} 个sections")
        if sections:
            print(f"  [调试] 第一个section标题: '{sections[0]['title']}'")
            print(f"  [调试] 第一个section内容长度: {len(sections[0]['content'])} 字符")
        
        # 确保所有expected_sections都有内容
        section_map = {s["title"]: s["content"] for s in sections}
        result = []
        
        print(f"  [调试] Expected sections: {len(expected_sections)} 个")
        print(f"  [调试] Section map keys: {list(section_map.keys())[:3]}...")
        
        for expected in expected_sections:
            content = section_map.get(expected, "*(Content to be added)*")
            # 模糊匹配
            if content == "*(Content to be added)*":
                matched = False
                for key, value in section_map.items():
                    if expected.lower() in key.lower() or key.lower() in expected.lower():
                        content = value
                        matched = True
                        break
                if not matched:
                    print(f"  [警告] 无法匹配section: '{expected}'")
            
            result.append({
                "title": expected,
                "content": content
            })
        
        return result
    
    def _fill_chapter_simple(
        self,
        chapter_title: str,
        section_titles: List[str]
    ) -> List[Dict[str, str]]:
        """
        简单填充（无LLM）
        
        Args:
            chapter_title: 章节标题
            section_titles: 小节标题列表
            
        Returns:
            [{"title": "section", "content": "..."}]
        """
        return [
            {
                "title": s,
                "content": "*(Content to be added)*"
            }
            for s in section_titles
        ]
    
    def beautify_content(
        self,
        chapter_contents: List[ChapterContent]
    ) -> List[ChapterContent]:
        """
        美化章节内容
        
        Args:
            chapter_contents: 章节内容列表
            
        Returns:
            美化后的章节内容列表
        """
        if not self.llm_client:
            print("  跳过美化（无LLM客户端）")
            return chapter_contents
        
        beautified_contents = []
        
        for chapter in chapter_contents:
            print(f"  美化章节: {chapter.title}")
            
            # 构建完整的章节markdown
            content_parts = [f"# {chapter.title}\n"]
            for section in chapter.sections:
                content_parts.append(f"\n## {section['title']}\n")
                content_parts.append(section['content'])
                content_parts.append("\n")
            
            full_content = '\n'.join(content_parts)
            
            # 调用LLM美化
            try:
                prompt = MARKDOWN_BEAUTIFY_PROMPT.format(content=full_content[:60000])
                beautified = self.llm_client.generate(prompt, temperature=0.2, max_tokens=32000)
                
                # 清理可能的代码块标记
                beautified = beautified.strip()
                if beautified.startswith('```'):
                    beautified = beautified.split('\n', 1)[1]
                if beautified.endswith('```'):
                    beautified = beautified.rsplit('\n', 1)[0]
                
                # 重新解析美化后的内容
                beautified_sections = self._parse_chapter_markdown(
                    beautified,
                    [s['title'] for s in chapter.sections]
                )
                
                beautified_contents.append(ChapterContent(
                    filename=chapter.filename,
                    title=chapter.title,
                    sections=beautified_sections
                ))
            except Exception as e:
                print(f"    美化失败: {e}，使用原始内容")
                beautified_contents.append(chapter)
        
        return beautified_contents
    
    def save_to_files(
        self,
        chapter_contents: List[ChapterContent],
        output_dir: Path
    ):
        """
        将章节内容保存为文件
        
        Args:
            chapter_contents: 章节内容列表
            output_dir: 输出目录
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for chapter in chapter_contents:
            filepath = output_dir / f"{chapter.filename}.md"
            
            # 构建markdown内容
            content_parts = [f"# {chapter.title}\n"]
            
            for section in chapter.sections:
                content_parts.append(f"\n## {section['title']}\n")
                content_parts.append(section['content'])
                content_parts.append("\n")
            
            # 写入文件
            filepath.write_text('\n'.join(content_parts), encoding='utf-8')
            print(f"✓ 生成: {chapter.filename}.md")
