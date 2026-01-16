"""
ForgeNote Debug Server Launcher
Start all necessary services: Docsify documentation + Image upload service

Usage: python scripts/start_debug_server.py [docsify_site_path]
Stop: Ctrl+C
"""

import subprocess
import sys
import time
import signal
import os
import platform
from pathlib import Path
from threading import Thread

# Project root
BASE_DIR = Path(__file__).parent.parent
DOCSIFY_DIR = None  # Will be set from user input or default

# Windows platform requires .cmd extension
IS_WINDOWS = platform.system() == 'Windows'
NPM_CMD = 'npm.cmd' if IS_WINDOWS else 'npm'
DOCSIFY_CMD = 'docsify.cmd' if IS_WINDOWS else 'docsify'

# Process list
processes = []

def get_docsify_dir():
    """Get Docsify site directory from command line argument or prompt user"""
    # Check command line argument
    if len(sys.argv) > 1:
        user_path = Path(sys.argv[1])
        if not user_path.is_absolute():
            user_path = BASE_DIR / user_path
        
        if user_path.is_dir():
            print(f"📂 Using Docsify site: {user_path}")
            return user_path
        else:
            print(f"❌ Invalid path: {user_path}")
            sys.exit(1)
    
    # Prompt user for input
    print("\n" + "="*60)
    print("Please enter the path to your Docsify site directory:")
    print("Example: output/COURSE001/docsify_site")
    print("         output/MyProject/docsify_site")
    print("="*60)
    
    while True:
        user_input = input("\nPath: ").strip()
        if not user_input:
            print("❌ Path cannot be empty")
            continue
        
        user_path = Path(user_input)
        if not user_path.is_absolute():
            user_path = BASE_DIR / user_path
        
        if user_path.is_dir():
            print(f"✓ Using: {user_path}")
            return user_path
        else:
            print(f"❌ Directory not found: {user_path}")
            retry = input("Try again? (y/n): ").strip().lower()
            if retry != 'y':
                sys.exit(1)

def print_banner():
    """Print startup banner"""
    print('=' * 70)
    print('  ForgeNote Debug Server')
    print('=' * 70)
    print()

def check_dependencies():
    """Check dependencies"""
    print('[1/4] Checking dependencies...')
    
    # Check Node.js
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        print(f'  ✓ Node.js: {result.stdout.strip()}')
    except FileNotFoundError:
        print('  ✗ Node.js not found. Please install Node.js first.')
        print('     Download: https://nodejs.org/')
        sys.exit(1)
    
    # Check npm
    try:
        result = subprocess.run([NPM_CMD, '--version'], capture_output=True, text=True, shell=IS_WINDOWS)
        print(f'  ✓ npm: {result.stdout.strip()}')
    except FileNotFoundError:
        print('  ✗ npm not found. Please install Node.js (includes npm).')
        print('     Download: https://nodejs.org/')
        sys.exit(1)
    
    # Check docsify-cli
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
    
    # Check Flask
    try:
        import flask
        print(f'  ✓ Flask: {flask.__version__}')
    except ImportError:
        print('  ✗ Flask not found. Please run: pip install flask flask-cors')
        sys.exit(1)
    
    # Check flask-cors
    try:
        import flask_cors
        print(f'  ✓ flask-cors: {flask_cors.__version__}')
    except ImportError:
        print('  ✗ flask-cors not found. Please run: pip install flask-cors')
        sys.exit(1)
    
    print()

def start_docsify_service():
    """Start Docsify documentation service"""
    print('[2/4] Starting Docsify service...')
    print(f'  Directory: {DOCSIFY_DIR}')
    print('  URL: http://localhost:3000')
    
    # Check if directory exists
    if not DOCSIFY_DIR.exists():
        print(f'  ✗ Directory not found: {DOCSIFY_DIR}')
        print('  Please run the pipeline first: python scripts/run_pipeline.py')
        sys.exit(1)
    
    # Start docsify serve
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
    """Start file service (image upload, save, export)"""
    print('[3/4] Starting file service...')
    print('  URL: http://localhost:8001')
    
    service_script = BASE_DIR / 'scripts' / 'image_upload_service.py'
    
    if not service_script.exists():
        print(f'  ✗ Service script not found: {service_script}')
        sys.exit(1)
    
    # Start Flask service
    process = subprocess.Popen(
        [sys.executable, str(service_script)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    processes.append(('File Service', process))
    print('  ✓ File service started')
    print()
    
    return process

def monitor_output(name, process):
    """Monitor process output"""
    try:
        for line in process.stdout:
            if line.strip():
                print(f'[{name}] {line.rstrip()}')
    except:
        pass

def print_summary():
    """Print service summary"""
    print('[4/4] All services running!')
    print('=' * 70)
    print()
    print('  📚 Docsify Documentation:  http://localhost:3000')
    print('  � File Service:           http://localhost:8001')
    print()
    print('=' * 70)
    print()
    print('Usage:')
    print('  1. Open http://localhost:3000 in browser')
    print('  2. Click "✏️ Edit" to edit markdown files')
    print('  3. Click "💾 Save" to save changes')
    print('  4. Click "🖼️ Upload Image" to add images')
    print('  5. Click "📦 Export Site" to download clean site')
    print()
    print('Press Ctrl+C to stop all services')
    print('=' * 70)
    print()

def signal_handler(sig, frame):
    """Handle Ctrl+C signal"""
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
    """Main function"""
    global DOCSIFY_DIR
    
    # Get Docsify directory
    DOCSIFY_DIR = get_docsify_dir()
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Print banner
    print_banner()
    
    # Check dependencies
    check_dependencies()
    
    # Start services
    docsify_process = start_docsify_service()
    image_upload_process = start_image_upload_service()
    
    # Wait for services to start
    time.sleep(2)
    
    # Print summary
    print_summary()
    
    # Start output monitoring threads
    Thread(target=monitor_output, args=('Docsify', docsify_process), daemon=True).start()
    Thread(target=monitor_output, args=('FileService', image_upload_process), daemon=True).start()
    
    # Keep running
    try:
        while True:
            # Check if processes are still running
            for name, process in processes:
                if process.poll() is not None:
                    print(f'\n⚠️  {name} service stopped unexpectedly!')
                    print('Exit code:', process.returncode)
                    
                    # Try to get error output
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
