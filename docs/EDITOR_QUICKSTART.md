# Docsify 编辑器 - 快速测试指南

## 🚀 快速测试编辑器功能

### 方式一：使用演示页面（最快）

1. **打开演示页面**
   ```bash
   cd docs
   python -m http.server 8000
   ```

2. **访问浏览器**
   ```
   http://localhost:8000/editor-demo.html
   ```

3. **开始测试**
   - 点击右上角 `✏️ Edit` 按钮
   - 或按 `Ctrl+E` 快捷键
   - 开始编辑和测试

---

### 方式二：在实际项目中测试

1. **运行 pipeline 生成站点**
   ```bash
   python scripts/run_pipeline.py
   ```

2. **启动本地服务器**
   ```bash
   cd output/SC2006/docsify_site
   python -m http.server 3000
   ```

3. **访问浏览器**
   ```
   http://localhost:3000
   ```

4. **测试编辑功能**
   - 浏览任意文档页面
   - 点击右上角 `Edit` 按钮
   - 开始编辑

---

## 📋 功能清单

测试时请验证以下功能：

### ✅ 基础功能
- [ ] 编辑按钮正常显示
- [ ] 点击按钮进入编辑模式
- [ ] 快捷键 `Ctrl+E` 工作正常
- [ ] 编辑器界面正常显示

### ✅ 编辑功能
- [ ] 左侧编辑区可以输入文本
- [ ] 右侧实时预览正常显示
- [ ] Markdown 语法正确渲染
- [ ] 代码块高亮正常
- [ ] 数学公式渲染正常
- [ ] 图片正常显示

### ✅ 导出功能
- [ ] 复制到剪贴板按钮工作
- [ ] 下载文件按钮工作
- [ ] 快捷键 `Ctrl+S` 触发下载
- [ ] 文件名包含 `_edited` 后缀

### ✅ 退出功能
- [ ] Exit 按钮工作正常
- [ ] 快捷键 `ESC` 退出编辑
- [ ] 有未保存修改时弹出确认
- [ ] 退出后恢复原页面

---

## 🐛 常见问题

### 问题 1：编辑按钮不显示

**检查步骤：**
1. 打开浏览器开发者工具（F12）
2. 查看 Console 是否有错误
3. 确认以下文件加载成功：
   - `docsify-editor.css`
   - `docsify-editor.js`

**解决方法：**
- 确认文件路径正确
- 检查文件是否存在于 `docsify_site` 目录

### 问题 2：预览不显示

**可能原因：**
- Marked.js 未加载

**解决方法：**
- 确认 `index.html` 中已引入 Marked.js：
  ```html
  <script src="//cdn.jsdelivr.net/npm/marked@4"></script>
  ```

### 问题 3：数学公式不渲染

**可能原因：**
- KaTeX 库未加载

**解决方法：**
- 确认已引入 KaTeX：
  ```html
  <link rel="stylesheet" href="//cdn.jsdelivr.net/npm/katex@latest/dist/katex.min.css"/>
  <script src="//cdn.jsdelivr.net/npm/katex@latest/dist/katex.min.js"></script>
  ```

---

## 📊 性能测试

### 大文件编辑测试

1. 创建一个包含 5000+ 行的 Markdown 文件
2. 进入编辑模式
3. 观察响应速度
4. 实时预览是否流畅

### 多图片文档测试

1. 打开包含大量图片的文档
2. 进入编辑模式
3. 检查图片是否正常显示
4. 编辑后图片路径是否保持

### 复杂公式测试

使用包含复杂 LaTeX 公式的文档：
```markdown
$$
\begin{pmatrix}
a & b \\
c & d
\end{pmatrix}
\cdot
\begin{pmatrix}
x \\
y
\end{pmatrix}
=
\begin{pmatrix}
ax + by \\
cx + dy
\end{pmatrix}
$$
```

---

## 🎯 下一步

测试完成后，可以：

1. **查看详细文档**
   - [编辑器使用指南](EDITOR_GUIDE.md)
   - [配置说明](CONFIG_GUIDE.md)

2. **自定义样式**
   - 修改 `docsify-editor.css`
   - 调整颜色、字体、布局

3. **集成到生产环境**
   - 部署生成的 docsify_site 目录
   - 配置 CDN 或静态托管服务

---

## 💬 反馈

如发现 bug 或有改进建议，请提交 Issue！
