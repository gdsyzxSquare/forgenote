# ForgeNote 调试服务使用指南

## 快速启动

### Windows 用户（推荐）

双击项目根目录的 `start_debug.bat` 文件

### 所有平台

在项目根目录运行：

```bash
python scripts/start_debug_server.py
```

---

## 功能说明

一键启动以下所有服务：

1. **Docsify 文档服务** (http://localhost:3000)
   - 浏览和阅读文档
   - 编辑 Markdown 内容
   - 实时预览

2. **图片上传服务** (http://localhost:8001)
   - 直接上传图片到 assets 目录
   - 自动生成 markdown 链接
   - 无需手动文件管理

---

## 启动流程

```
╔═══════════════════════════════════════════════════════════╗
║  ForgeNote Debug Server                                   ║
╚═══════════════════════════════════════════════════════════╝

[1/4] Checking dependencies...
  ✓ Node.js: v20.x.x
  ✓ docsify-cli: 4.x.x
  ✓ Flask: 3.x.x
  ✓ flask-cors: 4.x.x

[2/4] Starting Docsify service...
  Directory: E:\...\output\SC2006\docsify_site
  URL: http://localhost:3000
  ✓ Docsify service started

[3/4] Starting image upload service...
  URL: http://localhost:8001
  ✓ Image upload service started

[4/4] All services running!
══════════════════════════════════════════════════════════════

  📚 Docsify Documentation:  http://localhost:3000
  🖼️  Image Upload Service:   http://localhost:8001

══════════════════════════════════════════════════════════════

Usage:
  1. Open http://localhost:3000 in browser
  2. Click "✏️ Edit" button to enter edit mode
  3. Click "🖼️ Upload Image" to add images

Press Ctrl+C to stop all services
══════════════════════════════════════════════════════════════
```

---

## 使用流程

### 1. 启动服务

运行启动脚本，等待所有服务就绪

### 2. 打开浏览器

访问 http://localhost:3000

### 3. 编辑文档

- 点击右下角 **"✏️ Edit"** 按钮
- 进入编辑模式，看到分栏编辑器

### 4. 上传图片

- 点击工具栏 **"🖼️ Upload Image"** 按钮
- 选择图片文件
- 图片自动上传并插入到编辑器光标位置

### 5. 保存更改

- 使用 **"📋 Copy Markdown"** 复制内容
- 或使用 **"💾 Download .md"** 下载文件
- 手动保存到源文件

---

## 停止服务

在运行窗口按 `Ctrl+C`，所有服务会自动停止

```
══════════════════════════════════════════════════════════════
Stopping all services...
══════════════════════════════════════════════════════════════
  Stopping Docsify...
  ✓ Docsify stopped
  Stopping Image Upload...
  ✓ Image Upload stopped

All services stopped. Goodbye!
══════════════════════════════════════════════════════════════
```

---

## 依赖检查

脚本会自动检查以下依赖：

### 必需依赖

- **Node.js** - 运行 Docsify
- **docsify-cli** - 文档服务
  ```bash
  npm install -g docsify-cli
  ```

- **Flask** - 图片上传服务
  ```bash
  pip install flask flask-cors
  ```

### 缺失依赖

如果检测到缺失，脚本会：
1. 提示安装命令
2. 自动退出（避免错误启动）

---

## 端口占用

如果端口被占用：

### Docsify (3000)

编辑 `scripts/start_debug_server.py`：

```python
# 第79行
['docsify', 'serve', '.', '--port', '3000'],  # 修改端口号
```

### 图片上传 (8001)

编辑 `scripts/image_upload_service.py`：

```python
# 最后一行
app.run(host='localhost', port=8001, debug=False)  # 修改端口号
```

同时修改前端配置 `src/static/docsify-editor-upload.js`：

```javascript
// 第6行
const IMAGE_UPLOAD_SERVICE_URL = 'http://localhost:8001';  // 修改端口号
```

---

## 故障排除

### 服务启动失败

1. 检查端口是否被占用
   ```bash
   # Windows
   netstat -ano | findstr "3000"
   netstat -ano | findstr "8001"
   
   # Linux/Mac
   lsof -i :3000
   lsof -i :8001
   ```

2. 检查依赖是否安装
   ```bash
   node --version
   docsify --version
   python -c "import flask; print(flask.__version__)"
   ```

3. 检查项目目录是否存在
   - `output/SC2006/docsify_site/`

### 图片上传失败

1. 确认图片上传服务正在运行
   - 访问 http://localhost:8001/health
   - 应返回：`{"status": "running", "service": "image-upload"}`

2. 检查浏览器控制台错误
   - F12 打开开发者工具
   - 查看 Console 和 Network 标签

3. 检查 assets 目录权限
   - 确保有写入权限

---

## 开发说明

### 修改服务配置

所有配置在 `scripts/start_debug_server.py` 中：

```python
# 第10行 - Docsify 目录
DOCSIFY_DIR = BASE_DIR / 'output' / 'SC2006' / 'docsify_site'

# 第79行 - Docsify 端口
['docsify', 'serve', '.', '--port', '3000']

# 第98行 - 图片上传服务路径
service_script = BASE_DIR / 'scripts' / 'image_upload_service.py'
```

### 添加新服务

在 `start_debug_server.py` 中添加：

```python
def start_your_service():
    """启动你的服务"""
    process = subprocess.Popen(
        ['your-command', 'args'],
        cwd=str(your_dir),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    processes.append(('YourService', process))
    return process

# 在 main() 函数中调用
your_process = start_your_service()
```

---

## 目录结构

```
forgenote/
├── start_debug.bat          ← Windows 快捷启动
├── scripts/
│   ├── start_debug_server.py   ← 主启动脚本
│   └── image_upload_service.py ← 图片上传服务
├── output/
│   └── SC2006/
│       └── docsify_site/    ← Docsify 文档目录
└── docs/
    └── DEBUG_SERVER_GUIDE.md ← 本文档
```

---

## 许可证

与主项目相同
