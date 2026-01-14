# Docsify 编辑器功能使用指南

## 📖 功能概述

Docsify 编辑器插件为 ForgeNote 生成的文档站点添加了**浏览器内编辑功能**，允许用户直接在网页上修改 Markdown 文档并导出。

### ✨ 核心特性

- ✅ **无缝切换**：一键在阅读模式和编辑模式间切换
- ✅ **实时预览**：编辑时同步显示渲染效果
- ✅ **双向导出**：支持复制到剪贴板或下载 .md 文件
- ✅ **纯前端**：无需后端，无需登录
- ✅ **非破坏性**：不自动保存，不覆盖原文件
- ✅ **响应式**：支持桌面端和移动端

---

## 🚀 快速开始

### 1. 自动集成（推荐）

运行 ForgeNote pipeline 后，编辑器会自动集成到生成的 Docsify 站点中：

```bash
python scripts/run_pipeline.py
```

生成的站点已包含编辑器功能，无需额外配置。

### 2. 手动集成

如果需要在现有的 Docsify 站点中添加编辑器：

1. 复制文件到站点目录：
   ```
   docsify-editor.css
   docsify-editor.js
   ```

2. 在 `index.html` 的 `</body>` 前添加：
   ```html
   <!-- Docsify Editor Plugin -->
   <link rel="stylesheet" href="docsify-editor.css">
   <script src="docsify-editor.js"></script>
   ```

---

## 💡 使用方法

### 进入编辑模式

**方式 1：点击按钮**
- 页面右上角有 `✏️ Edit` 按钮
- 点击即可进入编辑模式

**方式 2：快捷键**
- 按 `Ctrl+E` (Windows/Linux) 或 `Cmd+E` (Mac)

### 编辑界面布局

```
┌─────────────────────────────────────────┐
│  📝 Editing: chapter1.md    [操作按钮]  │
├──────────────────┬──────────────────────┤
│  📝 Markdown编辑  │  👁️ 实时预览         │
│                  │                      │
│  在这里编辑      │  实时显示渲染效果    │
│  Markdown内容    │                      │
│                  │                      │
└──────────────────┴──────────────────────┘
```

### 导出内容

**方法 1：复制到剪贴板**
- 点击 `📋 Copy Markdown` 按钮
- 内容自动复制到剪贴板
- 粘贴到任意编辑器

**方法 2：下载文件**
- 点击 `💾 Download .md` 按钮
- 自动下载 `文件名_edited.md`
- 文件名带 `_edited` 后缀，避免覆盖

**方法 3：快捷键保存**
- 按 `Ctrl+S` (Windows/Linux) 或 `Cmd+S` (Mac)
- 触发下载

### 退出编辑模式

**方式 1：点击按钮**
- 点击 `❌ Exit` 按钮
- 如有未保存修改，会弹出确认

**方式 2：快捷键**
- 按 `ESC` 键

---

## ⌨️ 快捷键列表

| 快捷键 | 功能 |
|--------|------|
| `Ctrl/Cmd + E` | 进入/退出编辑模式 |
| `Ctrl/Cmd + S` | 下载当前文档 |
| `ESC` | 退出编辑模式 |

---

## 🔧 高级特性

### 实时预览支持

编辑器自动识别并渲染：
- ✅ Markdown 基础语法（标题、列表、引用等）
- ✅ 代码块（带语法高亮）
- ✅ 数学公式（KaTeX）
- ✅ 图片（相对路径和绝对路径）
- ✅ 表格
- ✅ HTML 标签

### 图片路径处理

编辑器会保持原有图片路径：
```markdown
# 相对路径（推荐）
![图片](../assets/Software_Engineering/images/diagram.png)

# 绝对路径
![图片](/assets/Software_Engineering/images/diagram.png)
```

### 数学公式编辑

支持 LaTeX 语法：
```markdown
行内公式：$E = mc^2$

块级公式：
$$
\int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}
$$
```

---

## 🎯 典型使用场景

### 场景 1：快速修正错误

```
1. 浏览文档时发现错别字
2. 点击 Edit 进入编辑模式
3. 修正错误
4. 复制修改后的内容
5. 提交给维护者或创建 PR
```

### 场景 2：添加批注

```
1. 进入编辑模式
2. 在需要批注的地方添加：
   > **批注**: 此处需要补充实例
3. 下载文件
4. 发送给同事审阅
```

### 场景 3：导出为其他格式

```
1. 在编辑器中调整格式
2. 复制 Markdown 内容
3. 粘贴到 Notion / 语雀 / Typora
4. 利用这些工具导出为 PDF/Word
```

### 场景 4：离线编辑

```
1. 在线打开文档
2. 进入编辑模式
3. 下载 Markdown 文件
4. 离线使用 VS Code 等工具编辑
5. 下次访问时重新上传（手动）
```

---

## 🛡️ 安全性说明

### 数据不会丢失
- ❌ **不会自动保存**：所有修改仅存在于浏览器内存
- ❌ **不会覆盖原文件**：下载文件带 `_edited` 后缀
- ✅ **退出前提醒**：有未保存修改时会弹出确认

### 隐私保护
- ✅ 纯前端运行，不向服务器发送任何数据
- ✅ 不收集用户信息
- ✅ 不使用 Cookie 或 LocalStorage（除非浏览器缓存）

### 权限控制
- 此编辑器**不提供权限控制**
- 任何访问者都可以编辑和导出
- 如需权限控制，请在站点部署层面实现（如 HTTP Basic Auth）

---

## 🐛 故障排查

### 问题 1：编辑按钮不显示

**可能原因**：
- CSS/JS 文件未正确加载

**解决方法**：
1. 打开浏览器开发者工具（F12）
2. 查看 Console 是否有错误
3. 确认 `docsify-editor.css` 和 `docsify-editor.js` 路径正确

### 问题 2：预览不显示或样式错乱

**可能原因**：
- Docsify 或 Marked.js 库未加载

**解决方法**：
- 确保 `index.html` 中已加载 Docsify 和 Marked.js

### 问题 3：数学公式不渲染

**可能原因**：
- KaTeX 库未加载

**解决方法**：
- 确保 `index.html` 中已引入 KaTeX CSS 和 JS

### 问题 4：复制到剪贴板失败

**可能原因**：
- 浏览器不支持 Clipboard API
- HTTPS 要求（某些浏览器）

**解决方法**：
- 使用 `Ctrl+A` 全选后 `Ctrl+C` 手动复制
- 或使用"下载文件"功能

---

## 🔌 API 接口（开发者）

如需在其他脚本中调用编辑器功能：

```javascript
// 进入编辑模式
window.docsifyEditor.enterEditMode();

// 退出编辑模式
window.docsifyEditor.exitEditMode();

// 切换模式
window.docsifyEditor.toggleEditMode();

// 复制到剪贴板
window.docsifyEditor.copyToClipboard();

// 下载文件
window.docsifyEditor.downloadMarkdown();

// 显示提示
window.docsifyEditor.showToast('操作成功', 'success');
```

---

## 🎨 自定义样式

如需自定义编辑器外观，可在站点的自定义 CSS 中覆盖：

```css
/* 修改编辑按钮颜色 */
.docsify-edit-btn {
  background: #ff6b6b;
}

/* 修改编辑器字体 */
.docsify-editor-textarea {
  font-family: 'JetBrains Mono', monospace;
  font-size: 16px;
}

/* 修改预览区背景 */
.docsify-editor-preview-content {
  background: #f9f9f9;
}
```

---

## 📝 工作流建议

### 个人使用
1. 浏览文档 → 发现问题
2. 进入编辑模式 → 修改
3. 下载文件 → 本地保存
4. （可选）创建 Git commit

### 团队协作
1. 成员在线编辑 → 导出 Markdown
2. 通过 GitHub Issue/PR 提交修改
3. 维护者审查后合并
4. 重新运行 pipeline 生成更新

### 课程维护
1. 教师在线标注需要更新的内容
2. 助教导出并修改
3. 更新到源文件
4. 重新生成并部署

---

## 🙋 常见问题

**Q: 修改会自动保存吗？**
A: 不会。必须手动复制或下载。

**Q: 能否多人同时编辑？**
A: 不支持。每个用户的编辑互不影响，需手动合并。

**Q: 编辑后如何更新网站？**
A: 需要将修改后的 Markdown 替换原文件，重新运行 pipeline。

**Q: 移动端能用吗？**
A: 可以，但建议在平板或大屏手机上使用以获得更好体验。

**Q: 能否编辑 _sidebar.md 等特殊文件？**
A: 编辑器仅对内容页面有效，不支持编辑侧边栏等元数据文件。

---

## 💬 反馈与支持

如有问题或建议，欢迎：
- 📧 提交 GitHub Issue
- 💬 在讨论区留言
- 📝 贡献代码改进

---

**设计理念**：编辑器的职责是"降低修改门槛"，而非"管理文档生命周期"。
内容的保存、审批、发布由外部流程控制。
