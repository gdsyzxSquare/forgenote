"""
Markdown美化与规范化模块

功能：
1. 统一标题层级
2. 规范化引用块（定义、定理、例子）
3. 修正图片路径
4. 格式化代码块和公式
"""
import re
from pathlib import Path
from typing import Dict, List
from ..prompts.templates import MARKDOWN_BEAUTIFY_PROMPT


class MarkdownBeautifier:
    """Markdown美化器"""
    
    def __init__(self, llm_client=None):
        """
        初始化Markdown美化器
        
        Args:
            llm_client: LLM客户端（可选）
        """
        self.llm_client = llm_client
    
    def beautify_file(self, input_file: Path, output_file: Path, course_name: str):
        """
        美化单个Markdown文件
        
        Args:
            input_file: 输入文件路径
            output_file: 输出文件路径
            course_name: 课程名称（用于图片路径）
        """
        content = input_file.read_text(encoding='utf-8')
        
        if self.llm_client:
            beautified = self._beautify_with_llm(content)
        else:
            beautified = self._beautify_with_rules(content, course_name)
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(beautified, encoding='utf-8')
    
    def _beautify_with_llm(self, content: str) -> str:
        """
        使用LLM美化内容
        
        Args:
            content: 原始内容
            
        Returns:
            美化后的内容
        """
        prompt = MARKDOWN_BEAUTIFY_PROMPT.format(content=content[:8000])
        response = self.llm_client.generate(prompt)
        return response
    
    def _beautify_with_rules(self, content: str, course_name: str) -> str:
        """
        使用规则方法美化内容
        
        Args:
            content: 原始内容
            course_name: 课程名称
            
        Returns:
            美化后的内容
        """
        # 1. 规范化标题层级
        content = self._normalize_headings(content)
        
        # 2. 标记定义、定理、例子
        content = self._mark_special_blocks(content)
        
        # 3. 修正图片路径
        content = self._fix_image_paths(content, course_name)
        
        # 4. 格式化代码块
        content = self._format_code_blocks(content)
        
        # 5. 清理多余空行
        content = self._clean_empty_lines(content)
        
        return content
    
    def _normalize_headings(self, content: str) -> str:
        """
        规范化标题层级
        
        Args:
            content: 原始内容
            
        Returns:
            规范化后的内容
        """
        lines = content.split('\n')
        normalized = []
        
        for line in lines:
            # 确保标题后有空格
            if line.startswith('#'):
                # 统计#的数量
                level = 0
                for char in line:
                    if char == '#':
                        level += 1
                    else:
                        break
                
                # 提取标题文本
                title = line[level:].strip()
                
                # 重新格式化
                normalized.append(f"{'#' * level} {title}")
            else:
                normalized.append(line)
        
        return '\n'.join(normalized)
    
    def _mark_special_blocks(self, content: str) -> str:
        """
        标记特殊内容块（定义、定理、例子）
        
        Args:
            content: 原始内容
            
        Returns:
            标记后的内容
        """
        # 使用正则匹配常见模式
        patterns = {
            r'(?i)^定义[：:]\s*(.+)': r'> **Definition**: \1',
            r'(?i)^Definition[：:]\s*(.+)': r'> **Definition**: \1',
            r'(?i)^定理[：:]\s*(.+)': r'> **Theorem**: \1',
            r'(?i)^Theorem[：:]\s*(.+)': r'> **Theorem**: \1',
            r'(?i)^例子[：:]\s*(.+)': r'> **Example**: \1',
            r'(?i)^Example[：:]\s*(.+)': r'> **Example**: \1',
            r'(?i)^注意[：:]\s*(.+)': r'> **Note**: \1',
            r'(?i)^Note[：:]\s*(.+)': r'> **Note**: \1',
        }
        
        for pattern, replacement in patterns.items():
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
        
        return content
    
    def _fix_image_paths(self, content: str, course_name: str) -> str:
        """
        修正图片路径为相对路径
        
        Args:
            content: 原始内容
            course_name: 课程名称
            
        Returns:
            修正后的内容
        """
        # 匹配Markdown图片语法
        # ![alt](path)
        
        def replace_path(match):
            alt_text = match.group(1)
            old_path = match.group(2)
            
            # 提取文件名
            filename = Path(old_path).name
            
            # 构建新路径（相对于文档根目录）
            new_path = f"../assets/{course_name}/images/{filename}"
            
            return f"![{alt_text}]({new_path})"
        
        content = re.sub(
            r'!\[(.*?)\]\((.*?)\)',
            replace_path,
            content
        )
        
        return content
    
    def _format_code_blocks(self, content: str) -> str:
        """
        格式化代码块
        
        Args:
            content: 原始内容
            
        Returns:
            格式化后的内容
        """
        # 确保代码块有语言标识
        # 这里是简单实现，可以根据需要扩展
        
        lines = content.split('\n')
        result = []
        in_code_block = False
        
        for line in lines:
            if line.strip().startswith('```'):
                if not in_code_block:
                    # 代码块开始
                    if line.strip() == '```':
                        # 没有指定语言，尝试推断或使用默认
                        result.append('```python')  # 默认使用python
                    else:
                        result.append(line)
                    in_code_block = True
                else:
                    # 代码块结束
                    result.append(line)
                    in_code_block = False
            else:
                result.append(line)
        
        return '\n'.join(result)
    
    def _clean_empty_lines(self, content: str) -> str:
        """
        清理多余的空行
        
        Args:
            content: 原始内容
            
        Returns:
            清理后的内容
        """
        # 将连续的3个以上空行替换为2个空行
        content = re.sub(r'\n{4,}', '\n\n\n', content)
        
        # 移除文件开头的空行
        content = content.lstrip('\n')
        
        # 确保文件结尾只有一个换行
        content = content.rstrip('\n') + '\n'
        
        return content
    
    def beautify_directory(self, input_dir: Path, output_dir: Path, course_name: str):
        """
        美化目录中的所有Markdown文件
        
        Args:
            input_dir: 输入目录
            output_dir: 输出目录
            course_name: 课程名称
        """
        for md_file in input_dir.glob("*.md"):
            output_file = output_dir / md_file.name
            self.beautify_file(md_file, output_file, course_name)
            print(f"已美化: {md_file.name}")
