"""
ForgeNote 调试服务启动器
一键启动所有必要服务：Docsify 文档服务 + 图片上传服务

运行: python scripts/start_debug_server.py
停止: Ctrl+C
"""

import subprocess
import sys
import time
import signal
import os
import platform
from pathlib import Path
from threading import Thread

# 项目路径
BASE_DIR = Path(__file__).parent.parent
DOCSIFY_DIR = BASE_DIR / 'output' / 'SC2006' / 'docsify_site'

# Windows 平台需要 .cmd 扩展名
IS_WINDOWS = platform.system() == 'Windows'
NPM_CMD = 'npm.cmd' if IS_WINDOWS else 'npm'
DOCSIFY_CMD = 'docsify.cmd' if IS_WINDOWS else 'docsify'

# 进程列表
processes = []

def print_banner():
    """打印启动横幅"""
    print('=' * 70)
    print('  ForgeNote Debug Server')
    print('=' * 70)
    print()

def check_dependencies():
    """检查依赖"""
    print('[1/4] Checking dependencies...')
    
    # 检查 Node.js
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        print(f'  ✓ Node.js: {result.stdout.strip()}')
    except FileNotFoundError:
        print('  ✗ Node.js not found. Please install Node.js first.')
        print('     Download: https://nodejs.org/')
        sys.exit(1)
    
    # 检查 npm
    try:
        result = subprocess.run([NPM_CMD, '--version'], capture_output=True, text=True, shell=IS_WINDOWS)
        print(f'  ✓ npm: {result.stdout.strip()}')
    except FileNotFoundError:
        print('  ✗ npm not found. Please install Node.js (includes npm).')
        print('     Download: https://nodejs.org/')
        sys.exit(1)
    
    # 检查 docsify-cli
    try:
        result = subprocess.run([DOCSIFY_CMD, '--version'], capture_output=True, text=True, shell=IS_WINDOWS)
        print(f'  ✓ docsify-cli: {result.stdout.strip()}')
    except FileNotFoundError:
        print('  ✗ docsify-cli not found.')
        install = input('    Install now? (y/n): ').lower().strip()
        if install == 'y':
            print('    Installing docsify-cli...')
            try:
                subprocess.run([NPM_CMD, 'install', '-g', 'docsify-cli'], 
                             check=True, 
                             shell=IS_WINDOWS)
                print('  ✓ docsify-cli installed')
            except subprocess.CalledProcessError as e:
                print('  ✗ Failed to install docsify-cli')
                print('     Please run manually: npm install -g docsify-cli')
                sys.exit(1)
        else:
            print('  ✗ docsify-cli is required. Please install manually:')
            print('     npm install -g docsify-cli')
            sys.exit(1)
    
    # 检查 Flask
    try:
        import flask
        print(f'  ✓ Flask: {flask.__version__}')
    except ImportError:
        print('  ✗ Flask not found. Please run: pip install flask flask-cors')
        sys.exit(1)
    
    # 检查 flask-cors
    try:
        import flask_cors
        print(f'  ✓ flask-cors: {flask_cors.__version__}')
    except ImportError:
        print('  ✗ flask-cors not found. Please run: pip install flask-cors')
        sys.exit(1)
    
    print()

def start_docsify_service():
    """启动 Docsify 文档服务"""
    print('[2/4] Starting Docsify service...')
    print(f'  Directory: {DOCSIFY_DIR}')
    print('  URL: http://localhost:3000')
    
    # 检查目录是否存在
    if not DOCSIFY_DIR.exists():
        print(f'  ✗ Directory not found: {DOCSIFY_DIR}')
        print('  Please run the pipeline first: python scripts/run_pipeline.py')
        sys.exit(1)
    
    # 启动 docsify serve
    process = subprocess.Popen(
        [DOCSIFY_CMD, 'serve', '.', '--port', '3000'],
        cwd=str(DOCSIFY_DIR),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        shell=IS_WINDOWS
    )
    
    processes.append(('Docsify', process))
    print('  ✓ Docsify service started')
    print()
    
    return process

def start_image_upload_service():
    """启动图片上传服务"""
    print('[3/4] Starting image upload service...')
    print('  URL: http://localhost:8001')
    
    service_script = BASE_DIR / 'scripts' / 'image_upload_service.py'
    
    if not service_script.exists():
        print(f'  ✗ Service script not found: {service_script}')
        sys.exit(1)
    
    # 启动 Flask 服务
    process = subprocess.Popen(
        [sys.executable, str(service_script)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    processes.append(('Image Upload', process))
    print('  ✓ Image upload service started')
    print()
    
    return process

def monitor_output(name, process):
    """监控进程输出"""
    try:
        for line in process.stdout:
            if line.strip():
                print(f'[{name}] {line.rstrip()}')
    except:
        pass

def print_summary():
    """打印服务摘要"""
    print('[4/4] All services running!')
    print('=' * 70)
    print()
    print('  📚 Docsify Documentation:  http://localhost:3000')
    print('  🖼️  Image Upload Service:   http://localhost:8001')
    print()
    print('=' * 70)
    print()
    print('Usage:')
    print('  1. Open http://localhost:3000 in browser')
    print('  2. Click "✏️ Edit" button to enter edit mode')
    print('  3. Click "🖼️ Upload Image" to add images')
    print()
    print('Press Ctrl+C to stop all services')
    print('=' * 70)
    print()

def signal_handler(sig, frame):
    """处理 Ctrl+C 信号"""
    print('\n')
    print('=' * 70)
    print('Stopping all services...')
    print('=' * 70)
    
    for name, process in processes:
        print(f'  Stopping {name}...')
        try:
            process.terminate()
            process.wait(timeout=5)
            print(f'  ✓ {name} stopped')
        except subprocess.TimeoutExpired:
            process.kill()
            print(f'  ✓ {name} killed (forced)')
        except Exception as e:
            print(f'  ✗ Error stopping {name}: {e}')
    
    print()
    print('All services stopped. Goodbye!')
    print('=' * 70)
    sys.exit(0)

def main():
    """主函数"""
    # 设置信号处理
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 打印横幅
    print_banner()
    
    # 检查依赖
    check_dependencies()
    
    # 启动服务
    docsify_process = start_docsify_service()
    image_upload_process = start_image_upload_service()
    
    # 等待服务启动
    time.sleep(2)
    
    # 打印摘要
    print_summary()
    
    # 启动输出监控线程
    Thread(target=monitor_output, args=('Docsify', docsify_process), daemon=True).start()
    Thread(target=monitor_output, args=('Upload', image_upload_process), daemon=True).start()
    
    # 保持运行
    try:
        while True:
            # 检查进程是否还在运行
            for name, process in processes:
                if process.poll() is not None:
                    print(f'\n⚠️  {name} service stopped unexpectedly!')
                    print('Exit code:', process.returncode)
                    
                    # 尝试获取错误输出
                    stderr = process.stderr.read() if process.stderr else ''
                    if stderr:
                        print('Error output:')
                        print(stderr)
                    
                    signal_handler(None, None)
            
            time.sleep(1)
    
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == '__main__':
    main()
