"""
LLM Prompt模板
"""

# 结构提取Prompt - 直接生成Sidebar
STRUCTURE_EXTRACTION_PROMPT = """
You are a course documentation expert. Analyze the course content and generate a **Docsify sidebar in Markdown format**.

## CRITICAL - Preserve Original Language

Keep ALL titles in their original language (English/Chinese/etc.). DO NOT translate any content.

## Output Format

Generate sidebar in this exact format:

```
* [Lecture Title](Filename.md)
  * [Section 1](Filename.md#anchor-1)
  * [Section 2](Filename.md#anchor-2)

* [Next Lecture](Filename2.md)
  * [Section A](Filename2.md#anchor-a)
```

## Rules

1. **File Names**: 
   - Remove special chars: #, spaces, /, ?, etc.
   - Replace spaces with underscores
   - Example: "Lecture #1: Intro" → `Lecture_1_Intro.md`

2. **Anchors**:
   - Lowercase
   - Replace spaces with hyphens
   - Example: "What is SE?" → `#what-is-se`

3. **Structure**:
   - Top level: lectures/chapters
   - Sub level (2 spaces indent): sections/topics
   - Skip page numbers, metadata

## Course Content

"""

# 内容重组Prompt - 基于Sidebar填充
CONTENT_REORGANIZATION_PROMPT = """
You are a content organization expert. Fill in content for a chapter based on the sidebar structure and source material.

## Task

Generate a complete Markdown file for the chapter: **{chapter_title}**

The chapter should contain these sections:
{sections}

## Rules

1. **Preserve Original Language**: Keep ALL content in the source language. DO NOT translate.

2. **Output Format**:
```markdown
# Chapter Title

## Section 1 Title

[Content extracted from source...]

## Section 2 Title

[Content extracted from source...]
```

3. **Content Extraction**:
   - Find relevant content from the source material
   - Reorganize from "page-oriented" to "topic-oriented"
   - Preserve code blocks, images, lists, tables
   - If no content found for a section, write: `*(Content to be added)*`

4. **Quality**:
   - Clear explanations
   - Keep examples and diagrams
   - Maintain academic rigor

## Source Material

```markdown
{content}
```

Now generate the complete chapter with all sections filled:
"""

# Markdown美化Prompt
MARKDOWN_BEAUTIFY_PROMPT = """
You are a markdown formatting expert. Please beautify and standardize the following markdown content.

## Rules

1. **Preserve Original Language**: Keep ALL content in the original language. DO NOT translate.

2. **Fix Formatting Issues**:
   - Add proper spacing around headings, lists, code blocks
   - Fix inconsistent bullet points and numbering
   - Ensure proper blank lines between sections
   - Fix table formatting if needed

3. **Text Cleanup**:
   - Remove excessive whitespace
   - Fix obvious typos (only clear mistakes)
   - Ensure consistent punctuation spacing
   - Separate merged words (e.g., "hellopworld" → "hello world")

4. **Preserve Content**:
   - Keep all images, links, code blocks unchanged
   - Keep all technical terms and formulas unchanged
   - Keep original meaning and structure

5. **Output**: Return only the beautified markdown, no explanations.

## Content to Beautify

```markdown
{content}
```

Now return the beautified markdown:
"""
