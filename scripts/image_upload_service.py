"""
本地图片上传服务
职责：作为浏览器与文件系统的桥接，允许网页将图片写入本地 assets 目录
运行：python scripts/image_upload_service.py
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import time
from pathlib import Path

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 配置
BASE_DIR = Path(__file__).parent.parent  # 项目根目录
ASSETS_DIR = BASE_DIR / 'output' / 'SC2006' / 'docsify_site' / 'assets'

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

@app.route('/health', methods=['GET'])
def health():
    """健康检查"""
    return jsonify({'status': 'running', 'service': 'image-upload'})

if __name__ == '__main__':
    print('=' * 60)
    print('Image Upload Service')
    print('=' * 60)
    print(f'Assets Directory: {ASSETS_DIR}')
    print('Listening on: http://localhost:8001')
    print('Endpoints:')
    print('  POST /upload-image  - Upload image')
    print('  GET  /health        - Health check')
    print('=' * 60)
    print('Press Ctrl+C to stop')
    print()
    
    app.run(host='localhost', port=8001, debug=False)
