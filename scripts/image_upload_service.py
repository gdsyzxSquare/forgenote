"""
本地文件服务
职责：
1. 图片上传：允许网页将图片写入本地 assets 目录
2. 文件保存：保存 Markdown 编辑内容
3. 站点导出：生成纯净的只读 Docsify 站点
运行：python scripts/image_upload_service.py
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import re
import time
import shutil
import zipfile
from pathlib import Path

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 配置
BASE_DIR = Path(__file__).parent.parent  # 项目根目录
OUTPUT_DIR = BASE_DIR / 'output' / 'SC2006'
DOCSIFY_SITE = OUTPUT_DIR / 'docsify_site'
ASSETS_DIR = DOCSIFY_SITE / 'assets'
CONTENT_DIR = DOCSIFY_SITE

@app.route('/upload-image', methods=['POST'])
def upload_image():
    """
    接收图片上传请求
    
    请求参数：
    - file: 图片文件
    - document: 文档名称（如 1_-_Introduction.pdf-xxx）
    
    返回：
    - success: bool
    - path: 相对路径（如 assets/xxx/images/image_123.png）
    - message: 消息
    """
    try:
        # 验证请求
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'Empty filename'}), 400
        
        # 获取文档名称
        document_name = request.form.get('document', 'default')
        
        # 生成文件名（时间戳 + 原扩展名）
        ext = os.path.splitext(file.filename)[1] or '.png'
        timestamp = int(time.time() * 1000)
        new_filename = f'image_{timestamp}{ext}'
        
        # 构建目标目录：assets/[document]/images/
        target_dir = ASSETS_DIR / document_name / 'images'
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # 保存文件
        target_path = target_dir / new_filename
        file.save(str(target_path))
        
        # 生成相对路径（相对于 docsify_site/）
        relative_path = f'assets/{document_name}/images/{new_filename}'
        
        return jsonify({
            'success': True,
            'path': relative_path,
            'message': f'Image saved: {new_filename}'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Upload failed: {str(e)}'
        }), 500

@app.route('/save-markdown', methods=['POST'])
def save_markdown():
    """
    保存 Markdown 文件
    
    请求参数：
    - filename: 文件名（如 1_-_Introduction.md）
    - content: Markdown 内容
    
    返回：
    - success: bool
    - message: 消息
    """
    try:
        data = request.json
        if not data or 'filename' not in data or 'content' not in data:
            return jsonify({'success': False, 'message': 'Missing filename or content'}), 400
        
        filename = data['filename']
        content = data['content']
        
        # 安全检查：防止路径遍历攻击
        if '..' in filename or '/' in filename or '\\' in filename:
            return jsonify({'success': False, 'message': 'Invalid filename'}), 400
        
        if not filename.endswith('.md'):
            return jsonify({'success': False, 'message': 'Only .md files allowed'}), 400
        
        # 保存到 docsify_site 目录
        target_path = CONTENT_DIR / filename
        
        # 备份原文件（只保留最近 3 个备份）
        if target_path.exists():
            # 创建新备份
            backup_path = target_path.with_suffix(f'.md.bak.{int(time.time())}')
            shutil.copy2(target_path, backup_path)
            
            # 清理旧备份：只保留最新的 3 个
            backup_pattern = target_path.stem + '.md.bak.*'
            backup_files = sorted(
                target_path.parent.glob(backup_pattern),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )
            # 删除超过 3 个的旧备份
            for old_backup in backup_files[3:]:
                old_backup.unlink()
                print(f'Cleaned old backup: {old_backup.name}')
        
        # 保存新内容
        target_path.write_text(content, encoding='utf-8')
        
        # 更新 sidebar
        try:
            update_sidebar(filename, content)
        except Exception as e:
            print(f'Warning: Failed to update sidebar: {e}')
        
        return jsonify({
            'success': True,
            'message': f'File saved: {filename}'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Save failed: {str(e)}'
        }), 500

def extract_headings(content: str) -> list:
    """
    提取 Markdown 中的一级和二级标题
    
    Args:
        content: Markdown 内容
        
    Returns:
        [(level, title, anchor), ...] 
        level: 1 或 2
        title: 标题文本
        anchor: 锚点 ID
    """
    headings = []
    lines = content.split('\n')
    
    for line in lines:
        line = line.strip()
        
        # 匹配 # 标题 或 ## 标题
        if line.startswith('# ') and not line.startswith('## '):
            # 一级标题
            title = line[2:].strip()
            # 生成锚点：转小写，空格转连字符，移除特殊字符
            anchor = re.sub(r'[^\w\s-]', '', title.lower())
            anchor = re.sub(r'[-\s]+', '-', anchor).strip('-')
            headings.append((1, title, anchor))
            
        elif line.startswith('## '):
            # 二级标题
            title = line[3:].strip()
            anchor = re.sub(r'[^\w\s-]', '', title.lower())
            anchor = re.sub(r'[-\s]+', '-', anchor).strip('-')
            headings.append((2, title, anchor))
    
    return headings

def update_sidebar(filename: str, content: str):
    """
    更新 _sidebar.md 中对应文档的目录结构
    
    Args:
        filename: 文件名（如 1_Introduction.md）
        content: Markdown 内容
    """
    sidebar_path = DOCSIFY_SITE / '_sidebar.md'
    
    if not sidebar_path.exists():
        print('Warning: _sidebar.md not found')
        return
    
    # 提取标题
    headings = extract_headings(content)
    
    if not headings:
        print(f'No headings found in {filename}')
        return
    
    # 读取当前 sidebar
    sidebar_content = sidebar_path.read_text(encoding='utf-8')
    lines = sidebar_content.split('\n')
    
    # 找到对应文档的起始行
    doc_pattern = f'\\* \\[.*\\]\\({re.escape(filename)}'
    doc_start = -1
    
    for i, line in enumerate(lines):
        if re.search(doc_pattern, line):
            doc_start = i
            break
    
    if doc_start == -1:
        print(f'Document {filename} not found in sidebar')
        return
    
    # 找到下一个文档的起始行（或文件末尾）
    # 注意：要找到下一个顶层的 "* [" 而不是缩进的 "  * ["
    doc_end = len(lines)
    for i in range(doc_start + 1, len(lines)):
        line = lines[i]
        # 只匹配顶层项（没有前导空格）
        if line.startswith('* [') and not line.startswith('  '):
            doc_end = i
            break
    
    # 生成新的目录项
    new_lines = []
    
    # 第一个一级标题作为文档标题
    first_heading = headings[0]
    new_lines.append(f'* [{first_heading[1]}]({filename})')
    
    # 后续标题作为子项
    for level, title, anchor in headings[1:]:
        # 所有后续标题都作为缩进子项
        new_lines.append(f'  * [{title}]({filename}#{anchor})')
    
    # 替换 sidebar 中对应部分
    # 在文档之间添加空行（如果不是最后一个文档）
    if doc_end < len(lines):
        updated_lines = lines[:doc_start] + new_lines + [''] + lines[doc_end:]
    else:
        updated_lines = lines[:doc_start] + new_lines
    
    # 写回 sidebar
    sidebar_path.write_text('\n'.join(updated_lines), encoding='utf-8')
    print(f'✓ Updated sidebar for {filename}')

@app.route('/export-site', methods=['POST'])
def export_site():
    """
    导出纯净的只读 Docsify 站点
    
    工作流程：
    1. 扫描所有 .md 文件，提取使用的图片引用
    2. 复制必要文件到临时目录
    3. 只复制被引用的图片
    4. 移除编辑功能相关代码
    5. 打包成 ZIP
    
    返回：ZIP 文件下载
    """
    try:
        # 创建临时导出目录
        export_dir = OUTPUT_DIR / f'export_{int(time.time())}'
        export_dir.mkdir(parents=True, exist_ok=True)
        
        # 收集所有使用的图片路径
        used_images = set()
        
        # 扫描所有 .md 文件（包括子目录）
        all_md_files = list(DOCSIFY_SITE.rglob('*.md'))
        
        # 正则匹配各种可能的图片引用格式
        # 注意：经过生成器处理后，所有路径应该都是 assets/... 格式
        # 但为了兼容性，仍然匹配多种格式
        patterns = [
            re.compile(r'!\[.*?\]\(((?:\.\./)*assets/[^)]+)\)'),  # Markdown: ![](../assets/... 或 assets/...)
            re.compile(r'!\[.*?\]\((/assets/[^)]+)\)'),            # Markdown: ![](/assets/...)
            re.compile(r'src="((?:\.\./)*assets/[^"]+)"'),         # HTML: src="../assets/..." 或 src="assets/..."
            re.compile(r'src="(/assets/[^"]+)"'),                  # HTML: src="/assets/..."
            re.compile(r"src='((?:\.\./)*assets/[^']+)'"),         # HTML: src='../assets/...' 或 src='assets/...'
            re.compile(r"src='(/assets/[^']+)'"),                  # HTML: src='/assets/...'
            re.compile(r'url\(((?:\.\./)*assets/[^)]+)\)'),        # CSS: url(../assets/... 或 assets/...)
        ]
        
        # 扫描所有 markdown 文件
        for md_file in all_md_files:
            try:
                content = md_file.read_text(encoding='utf-8')
                for pattern in patterns:
                    for match in pattern.finditer(content):
                        img_path = match.group(1)
                        # 清理路径中的引号
                        img_path = img_path.strip('\'"')
                        # 规范化路径：移除 ../ 和 / 前缀，统一为 assets/...
                        img_path = re.sub(r'^(?:\.\./)+', '', img_path)  # 移除 ../
                        img_path = re.sub(r'^\./', '', img_path)          # 移除 ./
                        img_path = re.sub(r'^/', '', img_path)            # 移除 /
                        used_images.add(img_path)
            except Exception as e:
                print(f'Warning: Failed to read {md_file}: {e}')
        
        # 同样扫描 index.html
        index_html = DOCSIFY_SITE / 'index.html'
        if index_html.exists():
            try:
                content = index_html.read_text(encoding='utf-8')
                for pattern in patterns:
                    for match in pattern.finditer(content):
                        img_path = match.group(1).strip('\'"')
                        # 规范化路径
                        img_path = re.sub(r'^(?:\.\./)+', '', img_path)
                        img_path = re.sub(r'^\./', '', img_path)
                        img_path = re.sub(r'^/', '', img_path)
                        used_images.add(img_path)
            except Exception as e:
                print(f'Warning: Failed to read index.html: {e}')
        
        print(f'Found {len(used_images)} used images in {len(all_md_files)} files')
        
        # 复制必要文件
        files_to_copy = [
            'index.html',
            '_sidebar.md',
            '_navbar.md',
            'README.md'
        ]
        
        for filename in files_to_copy:
            src = DOCSIFY_SITE / filename
            if src.exists():
                dst = export_dir / filename
                if filename == 'index.html':
                    # 移除编辑器相关代码
                    content = src.read_text(encoding='utf-8')
                    # 移除编辑器 JS 引用
                    content = re.sub(r'<script src="docsify-editor\.js"></script>', '', content)
                    # 移除编辑按钮容器
                    content = re.sub(r'<div id="docsify-edit-button"></div>', '', content)
                    # 移除导出按钮容器
                    content = re.sub(r'<div id="docsify-export-button"></div>', '', content)
                    dst.write_text(content, encoding='utf-8')
                else:
                    shutil.copy2(src, dst)
        
        # 复制所有 .md 文件（使用 all_md_files 而不是 md_files）
        for md_file in all_md_files:
            if md_file.name not in ['_sidebar.md', '_navbar.md', 'README.md']:
                relative_path = md_file.relative_to(DOCSIFY_SITE)
                dst_file = export_dir / relative_path
                dst_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(md_file, dst_file)
        
        # 只复制被使用的图片
        for img_path in used_images:
            src_img = DOCSIFY_SITE / img_path
            if src_img.exists():
                dst_img = export_dir / img_path
                dst_img.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_img, dst_img)
        
        # 打包成 ZIP
        zip_path = OUTPUT_DIR / f'docsify_site_export_{int(time.time())}.zip'
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file in export_dir.rglob('*'):
                if file.is_file():
                    arcname = file.relative_to(export_dir)
                    zipf.write(file, arcname)
        
        # 清理临时目录
        shutil.rmtree(export_dir)
        
        # 返回 ZIP 文件
        return send_file(
            zip_path,
            as_attachment=True,
            download_name=f'docsify_site_{int(time.time())}.zip',
            mimetype='application/zip'
        )
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Export failed: {str(e)}'
        }), 500

@app.route('/health', methods=['GET'])
def health():
    """健康检查"""
    return jsonify({'status': 'running', 'service': 'file-service'})

if __name__ == '__main__':
    print('=' * 60)
    print('ForgeNote File Service')
    print('=' * 60)
    print(f'Content Directory: {CONTENT_DIR}')
    print(f'Assets Directory: {ASSETS_DIR}')
    print('Listening on: http://localhost:8001')
    print('Endpoints:')
    print('  POST /upload-image     - Upload image')
    print('  POST /save-markdown    - Save markdown file (auto-update sidebar)')
    print('  POST /export-site      - Export clean site (ZIP)')
    print('  POST /cleanup-backups  - Clean all backup files')
    print('  GET  /health           - Health check')
    print('=' * 60)
    print('Press Ctrl+C to stop')
    print()
    
    app.run(host='localhost', port=8001, debug=False)
