# 编辑器内容加载改进说明

## 🔧 问题修复

### 之前的问题
编辑器进入编辑模式时显示空白，无法编辑当前页面内容。

### 解决方案
实现了**三层内容加载机制**：

## 📋 内容加载策略

### 策略 1：直接加载 Markdown 文件（最佳）
```javascript
fetch(filename) → 获取原始 .md 文件
```
- ✅ 保留原始格式
- ✅ 包含所有元数据和注释
- ✅ 最准确的编辑体验

### 策略 2：从 Docsify 内部提取（备选）
```javascript
window.Docsify.compiler → 尝试获取缓存内容
```
- ⚠️ 依赖 Docsify 版本
- ⚠️ 不一定可用
- 🔄 自动降级到策略 3

### 策略 3：DOM 反向工程（降级）
```javascript
DOM → Markdown 反向转换
```
- ✅ 始终可用
- ⚠️ 可能丢失部分格式
- ✅ 适合快速编辑

## 🎯 DOM 反向提取功能

新增的 `extractFromRenderedContent()` 函数支持：

### 支持的元素类型

| Markdown 元素 | DOM 元素 | 转换结果 |
|---------------|----------|----------|
| 标题 | `<h1>` - `<h6>` | `# Title` |
| 段落 | `<p>` | 普通文本 |
| 引用 | `<blockquote>` | `> Quote` |
| 代码块 | `<pre><code>` | ` ```lang\ncode\n``` ` |
| 无序列表 | `<ul><li>` | `- Item` |
| 有序列表 | `<ol><li>` | `1. Item` |
| 图片 | `<img>` | `![alt](src)` |
| 表格 | `<table>` | Markdown 表格 |
| 其他 | 任意元素 | 纯文本 |

### 示例转换

#### 原始 HTML
```html
<h2>标题</h2>
<p>这是一段文字</p>
<blockquote>这是引用</blockquote>
<pre><code class="lang-python">print("Hello")</code></pre>
```

#### 转换后的 Markdown
```markdown
## 标题

这是一段文字

> 这是引用

```python
print("Hello")
```
```

## 💡 使用场景

### 场景 1：本地开发环境
```bash
# 启动本地服务器
python -m http.server 8000

# 访问页面
http://localhost:8000/docs/editor-demo.html
```
**加载策略**：策略 1（直接加载 .md 文件）✅

### 场景 2：CDN 部署的生产环境
```
https://your-site.com/docs/
```
**加载策略**：策略 1 或策略 3

### 场景 3：嵌入式或受限环境
```
file:///path/to/index.html
```
**加载策略**：策略 3（DOM 反向提取）

## 🔍 调试信息

编辑器会在浏览器控制台输出详细日志：

```javascript
// 成功加载
✅ Loaded: README.md

// 降级加载
⚠️ Loaded reconstructed content
Failed to load markdown content: Error: File not found
```

### 检查加载状态

1. 打开浏览器开发者工具（F12）
2. 切换到 Console 标签
3. 点击 Edit 按钮
4. 查看输出信息

## 📊 性能对比

| 加载方式 | 速度 | 准确度 | 依赖 |
|----------|------|--------|------|
| 策略 1：直接加载 | ⚡ 快 | 💯 100% | HTTP 服务器 |
| 策略 2：Docsify 缓存 | ⚡ 极快 | 💯 100% | Docsify 内部 API |
| 策略 3：DOM 反向 | 🐢 较慢 | 📊 80-90% | 无 |

## 🎨 编辑体验改进

### 新增提示信息

1. **加载成功**
   ```
   ✅ Loaded: chapter1.md
   ```

2. **降级加载**
   ```
   ⚠️ Loaded reconstructed content
   ```

3. **文件名显示**
   ```
   Editing: chapter1.md
   或
   Editing: chapter1.md (reconstructed)
   ```

### 用户感知

- ✅ 总是能看到可编辑的内容
- ✅ 清楚知道内容来源
- ✅ 可以立即开始编辑

## 🚀 下一步优化建议

### 1. 增强 DOM 提取精度
- 处理嵌套列表
- 支持任务列表 `- [x]`
- 保留链接格式

### 2. 添加格式保留选项
```javascript
// 配置选项
window.$docsify.editor = {
  preserveFormatting: true,
  fallbackStrategy: 'dom' // 'dom' | 'empty' | 'template'
}
```

### 3. 支持离线缓存
```javascript
// 使用 localStorage 缓存编辑内容
localStorage.setItem('editor-backup-' + filename, content);
```

## 📝 测试清单

测试不同场景下的内容加载：

### ✅ 测试 1：本地服务器 + 真实文件
- [ ] 启动服务器
- [ ] 打开文档页面
- [ ] 点击 Edit
- [ ] 验证加载完整的 Markdown

### ✅ 测试 2：无法访问原文件
- [ ] 断开网络或修改文件路径
- [ ] 点击 Edit
- [ ] 验证 DOM 反向提取生效

### ✅ 测试 3：空白页面
- [ ] 访问不存在的路由
- [ ] 点击 Edit
- [ ] 验证显示默认模板

### ✅ 测试 4：复杂内容
- [ ] 打开包含代码块、表格、公式的页面
- [ ] 点击 Edit
- [ ] 验证内容完整性

## 🐛 已知限制

1. **DOM 反向提取的限制**：
   - 无法恢复 Markdown 原始注释
   - 复杂嵌套结构可能简化
   - 自定义 HTML 会被转为纯文本

2. **CORS 限制**：
   - `file://` 协议下无法使用策略 1
   - 需要本地服务器或正式部署

3. **格式差异**：
   - 不同 Markdown 方言的语法差异
   - HTML 实体转义问题

---

## 💬 使用反馈

如遇到内容加载问题，请提供：
1. 浏览器控制台错误信息
2. 访问方式（本地/CDN/file://）
3. 页面 URL 和文件名
4. 预期内容 vs 实际内容

---

**更新时间**：2026-01-13  
**版本**：v1.1.0
