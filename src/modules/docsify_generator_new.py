"""
Docsify站点生成器 - 简化版

直接使用结构中的sidebar markdown
"""
from pathlib import Path
import shutil
import re
from typing import Dict, List


class DocsifyGenerator:
    """Docsify站点生成器"""
    
    def __init__(self):
        pass
    
    def generate_site(
        self,
        course_name: str,
        sidebar_md: str,
        content_dir: Path,
        output_dir: Path,
        assets_dir: Path = None,
        navbar_items: List[Dict[str, str]] = None
    ):
        """
        生成Docsify站点
        
        Args:
            course_name: 课程名称
            sidebar_md: sidebar markdown文本
            content_dir: 内容目录（章节文件所在位置）
            output_dir: 输出目录
            assets_dir: 资源目录（图片等）
            navbar_items: 导航栏项目
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. 生成index.html
        self._generate_index_html(course_name, output_dir)
        
        # 2. 生成_sidebar.md
        self._generate_sidebar(sidebar_md, output_dir)
        
        # 3. 生成_navbar.md
        self._generate_navbar(navbar_items or [], output_dir)
        
        # 4. 生成README.md
        self._generate_readme(course_name, output_dir)
        
        # 5. 复制内容文件
        self._copy_content_files(content_dir, output_dir)
        
        # 6. 复制资源文件
        if assets_dir and assets_dir.exists():
            self._copy_assets(assets_dir, output_dir)
        
        # 7. 复制编辑器插件文件
        self._copy_editor_plugin(output_dir)
        
        print(f"\n✓ Docsify站点生成完成: {output_dir}")
    
    def _generate_index_html(self, course_name: str, output_dir: Path):
        """生成index.html，包含图片缩放、代码块和LaTeX渲染插件"""
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{course_name}</title>
  <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1" />
  <meta name="description" content="Description">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, minimum-scale=1.0">
  <link rel="stylesheet" href="//cdn.jsdelivr.net/npm/docsify@4/lib/themes/vue.css">
  <!-- KaTeX for LaTeX rendering -->
  <link rel="stylesheet" href="//cdn.jsdelivr.net/npm/katex@latest/dist/katex.min.css"/>
  <!-- 自定义样式：限制图片尺寸 -->
  <style>
    .markdown-section img {{
      max-width: 70%;
      max-height: 500px;
      display: block;
      margin: 20px auto;
      cursor: zoom-in;
    }}
    .markdown-section img.medium-zoom-image--opened {{
      cursor: zoom-out;
    }}
  </style>
</head>
<body>
  <div id="app"></div>
  <script>
    window.$docsify = {{
      name: '{course_name}',
      repo: '',
      loadSidebar: true,
      loadNavbar: true,
      subMaxLevel: 0,
      auto2top: true,
      search: {{
        maxAge: 86400000,
        paths: 'auto',
        placeholder: 'Search',
        noData: 'No Results!',
        depth: 6
      }},
      // 代码块复制按钮配置
      copyCode: {{
        buttonText: 'Copy',
        errorText: 'Error',
        successText: 'Copied!'
      }},
      // 分页配置
      pagination: {{
        previousText: 'Previous',
        nextText: 'Next',
        crossChapter: true,
        crossChapterText: true
      }}
    }}
  </script>
  
  <!-- Docsify core -->
  <script src="//cdn.jsdelivr.net/npm/docsify@4"></script>
  
  <!-- Docsify plugins -->
  <script src="//cdn.jsdelivr.net/npm/docsify/lib/plugins/search.min.js"></script>
  <script src="//cdn.jsdelivr.net/npm/docsify-copy-code@2"></script>
  <script src="//cdn.jsdelivr.net/npm/docsify/lib/plugins/zoom-image.min.js"></script>
  <script src="//cdn.jsdelivr.net/npm/docsify-pagination@2/dist/docsify-pagination.min.js"></script>
  
  <!-- Prism for code highlighting (multiple languages) -->
  <script src="//cdn.jsdelivr.net/npm/prismjs@1/components/prism-bash.min.js"></script>
  <script src="//cdn.jsdelivr.net/npm/prismjs@1/components/prism-python.min.js"></script>
  <script src="//cdn.jsdelivr.net/npm/prismjs@1/components/prism-java.min.js"></script>
  <script src="//cdn.jsdelivr.net/npm/prismjs@1/components/prism-javascript.min.js"></script>
  <script src="//cdn.jsdelivr.net/npm/prismjs@1/components/prism-typescript.min.js"></script>
  <script src="//cdn.jsdelivr.net/npm/prismjs@1/components/prism-json.min.js"></script>
  <script src="//cdn.jsdelivr.net/npm/prismjs@1/components/prism-markdown.min.js"></script>
  <script src="//cdn.jsdelivr.net/npm/prismjs@1/components/prism-c.min.js"></script>
  <script src="//cdn.jsdelivr.net/npm/prismjs@1/components/prism-cpp.min.js"></script>
  
  <!-- KaTeX for LaTeX rendering -->
  <script src="//cdn.jsdelivr.net/npm/katex@latest/dist/katex.min.js"></script>
  <script src="//cdn.jsdelivr.net/npm/marked@4"></script>
  
  <!-- Custom LaTeX renderer -->
  <script>
    // Custom renderer for LaTeX formulas
    window.$docsify.markdown = window.$docsify.markdown || {{}};
    window.$docsify.markdown.renderer = {{
      code: function(code, lang) {{
        if (lang === "latex" || lang === "tex") {{
          return '<span class="tex">' + katex.renderToString(code, {{
            throwOnError: false,
            displayMode: true
          }}) + '</span>';
        }}
        return this.origin.code.apply(this, arguments);
      }}
    }};
    
    // Auto-render inline and display LaTeX after page load
    window.$docsify.plugins = [].concat(window.$docsify.plugins || [], function(hook) {{
      hook.doneEach(function() {{
        // Render display math: $$...$$
        document.querySelectorAll('p').forEach(function(el) {{
          var html = el.innerHTML;
          html = html.replace(/\$\$([^\$]+)\$\$/g, function(match, tex) {{
            try {{
              return katex.renderToString(tex, {{ throwOnError: false, displayMode: true }});
            }} catch (e) {{
              return match;
            }}
          }});
          // Render inline math: $...$
          html = html.replace(/\$([^\$]+)\$/g, function(match, tex) {{
            try {{
              return katex.renderToString(tex, {{ throwOnError: false, displayMode: false }});
            }} catch (e) {{
              return match;
            }}
          }});
          el.innerHTML = html;
        }});
      }});
    }});
  </script>
  
  <!-- Docsify Editor Plugin -->
  <link rel="stylesheet" href="docsify-editor.css">
  <script src="docsify-editor.js"></script>
</body>
</html>
"""
        (output_dir / "index.html").write_text(html_content, encoding='utf-8')
        print("✓ 生成 index.html (包含图片缩放、代码块和LaTeX渲染插件)")
    
    def _generate_sidebar(self, sidebar_md: str, output_dir: Path):
        """生成_sidebar.md"""
        (output_dir / "_sidebar.md").write_text(sidebar_md, encoding='utf-8')
        print("✓ 生成 _sidebar.md")
    
    def _generate_navbar(self, navbar_items: List[Dict[str, str]], output_dir: Path):
        """生成_navbar.md"""
        if not navbar_items:
            navbar_items = [{"name": "Home", "link": "/"}]
        
        navbar_lines = []
        for item in navbar_items:
            navbar_lines.append(f"* [{item['name']}]({item['link']})")
        
        navbar_content = '\n'.join(navbar_lines)
        (output_dir / "_navbar.md").write_text(navbar_content, encoding='utf-8')
        print("✓ 生成 _navbar.md")
    
    def _generate_readme(self, course_name: str, output_dir: Path):
        """生成README.md"""
        readme_content = f"""# {course_name}

Welcome to the {course_name} documentation!

## Navigation

Use the sidebar on the left to navigate through different sections.

## About

This documentation is automatically generated from course materials.
"""
        (output_dir / "README.md").write_text(readme_content, encoding='utf-8')
        print("✓ 生成 README.md")
    
    def _copy_content_files(self, content_dir: Path, output_dir: Path):
        """复制内容文件并规范化图片路径"""
        if not content_dir.exists():
            print(f"警告: 内容目录不存在 {content_dir}")
            return
        
        # 删除旧的章节文件（保留特殊文件）
        for f in output_dir.glob("*.md"):
            if f.name not in ["_sidebar.md", "_navbar.md", "README.md"]:
                f.unlink()
        
        # 复制新的章节文件并规范化图片路径
        copied = 0
        for md_file in content_dir.glob("*.md"):
            # 读取文件内容
            content = md_file.read_text(encoding='utf-8')
            
            # 规范化图片路径：统一转换为 assets/... 格式
            # 处理各种可能的相对路径格式
            content = self._normalize_image_paths(content)
            
            # 写入到输出目录
            (output_dir / md_file.name).write_text(content, encoding='utf-8')
            copied += 1
        
        print(f"✓ 复制内容文件: {copied} 个（已规范化图片路径）")
    
    def _normalize_image_paths(self, content: str) -> str:
        """
        规范化 Markdown 中的图片路径
        
        将以下格式统一转换为 assets/...：
        - ../assets/...
        - ./assets/...
        - ../../assets/...
        - /assets/...
        
        Args:
            content: Markdown 内容
            
        Returns:
            规范化后的内容
        """
        # 匹配 markdown 图片语法和 HTML img 标签
        patterns = [
            # Markdown: ![alt](path)
            (r'!\[([^\]]*)\]\((\.\./)*assets/([^)]+)\)', r'![\1](assets/\3)'),
            (r'!\[([^\]]*)\]\((\./)*assets/([^)]+)\)', r'![\1](assets/\3)'),
            (r'!\[([^\]]*)\]\(/assets/([^)]+)\)', r'![\1](assets/\2)'),
            
            # HTML: <img src="path">
            (r'<img\s+([^>]*)src="(\.\./)*assets/([^"]+)"', r'<img \1src="assets/\3"'),
            (r'<img\s+([^>]*)src="(\./)*assets/([^"]+)"', r'<img \1src="assets/\3"'),
            (r'<img\s+([^>]*)src="/assets/([^"]+)"', r'<img \1src="assets/\2"'),
            
            # HTML: <img src='path'>
            (r"<img\s+([^>]*)src='(\.\./)*assets/([^']+)'", r"<img \1src='assets/\3'"),
            (r"<img\s+([^>]*)src='(\./)*assets/([^']+)'", r"<img \1src='assets/\3'"),
            (r"<img\s+([^>]*)src='/assets/([^']+)'", r"<img \1src='assets/\2'"),
        ]
        
        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content)
        
        return content
    
    def _copy_assets(self, assets_dir: Path, output_dir: Path):
        """
        复制资源文件（图片等）
        
        Args:
            assets_dir: 资源目录
            output_dir: 输出目录（docsify_site目录）
        """
        dest_assets = output_dir / "assets"
        
        # 如果assets_dir已经是dest_assets（即直接导入到docsify_site/assets），则跳过复制
        if assets_dir.resolve() == dest_assets.resolve():
            file_count = sum(1 for _ in dest_assets.rglob("*") if _.is_file())
            print(f"✓ 资源文件已就位: {file_count} 个")
            return
        
        # 否则需要复制（兼容旧逻辑）
        # 删除旧的assets目录
        if dest_assets.exists():
            shutil.rmtree(dest_assets)
        
        # 创建assets目录
        dest_assets.mkdir(parents=True, exist_ok=True)
        
        # 复制assets_dir下的所有内容到dest_assets
        if assets_dir.exists():
            for item in assets_dir.iterdir():
                dest_item = dest_assets / item.name
                if item.is_dir():
                    shutil.copytree(item, dest_item, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, dest_item)
        
        # 统计文件数
        file_count = sum(1 for _ in dest_assets.rglob("*") if _.is_file())
        print(f"✓ 复制资源文件: {file_count} 个")
    
    def _copy_editor_plugin(self, output_dir: Path):
        """
        复制编辑器插件文件到站点目录
        
        Args:
            output_dir: 输出目录（docsify_site）
        """
        # 获取静态文件目录
        static_dir = Path(__file__).parent.parent / "static"
        
        editor_css = static_dir / "docsify-editor.css"
        editor_js = static_dir / "docsify-editor.js"
        
        if editor_css.exists():
            shutil.copy2(editor_css, output_dir / "docsify-editor.css")
            print("✓ 复制编辑器样式文件")
        else:
            print("⚠️  警告: 编辑器CSS文件不存在")
        
        if editor_js.exists():
            shutil.copy2(editor_js, output_dir / "docsify-editor.js")
            print("✓ 复制编辑器脚本")
        else:
            print("⚠️  警告: 编辑器JS文件不存在")
    
    def preview_site(self, output_dir: Path, port: int = 3000):
        """
        预览站点
        
        Args:
            output_dir: 站点目录
            port: 端口号
        """
        import http.server
        import socketserver
        import os
        
        os.chdir(output_dir)
        
        Handler = http.server.SimpleHTTPRequestHandler
        with socketserver.TCPServer(("", port), Handler) as httpd:
            print(f"\n🌐 Docsify预览: http://localhost:{port}")
            print("按 Ctrl+C 停止服务器")
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\n服务器已停止")
