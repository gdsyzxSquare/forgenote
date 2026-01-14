# 运行演示说明

## ✅ 正常运行步骤

### 1. 启动服务器

在项目**根目录**运行（而非 docs 目录）：

```bash
# Windows PowerShell
cd E:\others\working\hkustgz\ai\forgenote
python -m http.server 8000
```

### 2. 访问演示页面

打开浏览器访问：
```
http://localhost:8000/docs/editor-demo.html
```

### 3. 开始测试

- 点击右上角 `✏️ Edit` 按钮
- 或按 `Ctrl+E` 快捷键

---

## 🐛 关于 404 错误

### favicon.ico 404（正常）

```
::1 - - [13/Jan/2026 23:27:35] "GET /favicon.ico HTTP/1.1" 404 -
```

**这是正常的！** 浏览器会自动请求网站图标。我已在 HTML 中添加了内联 SVG 图标。

### 其他 404 错误

如果看到其他文件的 404 错误，检查：

1. **确保在项目根目录运行服务器**
   ```bash
   pwd  # 应该显示: E:\others\working\hkustgz\ai\forgenote
   ```

2. **检查文件路径**
   - CSS: `src/static/docsify-editor.css`
   - JS: `src/static/docsify-editor.js`
   - Demo: `docs/README_demo.md`

3. **访问正确的 URL**
   ```
   ✅ http://localhost:8000/docs/editor-demo.html
   ❌ http://localhost:8000/editor-demo.html
   ```

---

## 🔧 故障排查

### 问题：编辑器样式未加载

**症状**：页面显示但没有编辑按钮

**解决**：
1. 打开浏览器开发者工具（F12）
2. 查看 Network 标签
3. 确认以下文件加载成功（状态码 200）：
   - `docsify-editor.css`
   - `docsify-editor.js`

### 问题：Cannot GET /docs/README_demo.md

**原因**：服务器在错误的目录启动

**解决**：
```bash
cd ..  # 回到上级目录
python -m http.server 8000
```

---

## 🚀 快速测试（推荐方式）

最简单的方法是从项目根目录一步到位：

```bash
# 1. 确保在项目根目录
cd E:\others\working\hkustgz\ai\forgenote

# 2. 启动服务器
python -m http.server 8000

# 3. 浏览器访问
# http://localhost:8000/docs/editor-demo.html
```

服务器输出应该是：
```
Serving HTTP on :: port 8000 (http://[::]:8000/) ...
::1 - - [13/Jan/2026 23:30:00] "GET /docs/editor-demo.html HTTP/1.1" 200 -
::1 - - [13/Jan/2026 23:30:01] "GET /src/static/docsify-editor.css HTTP/1.1" 200 -
::1 - - [13/Jan/2026 23:30:01] "GET /src/static/docsify-editor.js HTTP/1.1" 200 -
::1 - - [13/Jan/2026 23:30:01] "GET /docs/README_demo.md HTTP/1.1" 200 -
```

所有状态码应该是 **200**（成功）。

---

## ✨ 使用提示

1. **favicon.ico 404 可以忽略** - 这不影响功能
2. **其他 404 需要检查** - 说明文件路径或启动目录不对
3. **使用 F12 开发者工具** - 可以查看详细的加载情况
4. **Ctrl+Shift+R** - 强制刷新浏览器缓存

---

## 📋 预期行为

### 正确加载时应该看到：

1. ✅ Docsify 演示页面正常显示
2. ✅ 右上角有绿色 `✏️ Edit` 按钮
3. ✅ 左下角有黄色提示框
4. ✅ 点击 Edit 可以进入编辑模式
5. ✅ 编辑界面分为左右两栏
6. ✅ 左侧可以编辑，右侧实时预览

### 如果出现问题：

- ❌ 没有 Edit 按钮 → CSS/JS 未加载
- ❌ 页面空白 → HTML 路径错误
- ❌ 点击 Edit 无反应 → JS 加载失败或有错误

---

需要更多帮助？检查浏览器控制台（F12 → Console 标签）是否有错误信息。
