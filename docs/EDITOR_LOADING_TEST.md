# 编辑器加载逻辑 - 简化版测试指南

## ✅ 已完成的修改

### 核心改进

1. **移除所有降级方案** - 专注于直接加载 .md 文件
2. **优化文件名获取逻辑** - 三层检测机制
3. **清晰的错误提示** - 加载失败时明确显示

---

## 🔍 新的加载逻辑

### 三层文件名检测

```javascript
// 优先级从高到低：

1. Docsify.vm.route.file (最准确)
   └─> 从 Docsify 内部获取当前实际加载的文件

2. $docsify.homepage (适用于首页)
   └─> 当 URL hash 为空时，使用配置的首页文件

3. window.location.hash (兜底)
   └─> 从 URL 解析文件名
```

### 执行流程

```
点击 Edit 按钮
    ↓
尝试方法 1: window.Docsify.vm.route.file
    ├─ 成功 → 使用此文件名
    └─ 失败 ↓
尝试方法 2: window.$docsify.homepage (仅首页)
    ├─ 成功 → 使用此文件名
    └─ 失败 ↓
尝试方法 3: 解析 window.location.hash
    └─ 使用解析结果
    ↓
使用 fetch() 加载文件
    ├─ 成功 → 显示内容 ✅
    └─ 失败 → 显示错误 ❌
```

---

## 🧪 测试步骤

### 测试 1：演示页面（homepage 配置）

```bash
# 1. 启动服务器（项目根目录）
cd E:\others\working\hkustgz\ai\forgenote
python -m http.server 8000

# 2. 访问
http://localhost:8000/docs/editor-demo.html
```

**预期行为：**
1. 页面加载后显示 README_demo.md 的内容
2. 打开浏览器控制台（F12）
3. 点击 Edit 按钮
4. 查看控制台输出：
   ```
   从 Docsify.vm.route 获取文件名: README_demo.md
   最终文件名: README_demo.md
   ```
5. 编辑器左侧应该显示完整的 Markdown 内容 ✅

---

### 测试 2：实际项目站点

```bash
# 1. 运行 pipeline 生成站点
python scripts/run_pipeline.py

# 2. 启动站点
cd output/SC2006/docsify_site
python -m http.server 3000

# 3. 访问
http://localhost:3000
```

**测试不同页面：**
- 首页 `#/`
- 章节页面 `#/1_-_Introduction.md`
- 子页面 `#/2_-_Requirements_Elicitation_1.md`

**预期行为：**
- 所有页面都能正确加载对应的 .md 文件
- 控制台显示正确的文件名
- 编辑器显示完整内容

---

## 🐛 调试信息

### 打开控制台查看日志

每次点击 Edit 时，控制台会输出：

```javascript
// 成功示例
从 Docsify.vm.route 获取文件名: README_demo.md
最终文件名: README_demo.md
✅ Loaded: README_demo.md

// 失败示例
从 Docsify.vm.route 获取文件名: chapter1.md
最终文件名: chapter1.md
Failed to load markdown content: Error: File not found: chapter1.md
❌ Failed to load: chapter1.md
```

### 检查点

1. **文件名是否正确？**
   - 查看 "最终文件名" 输出
   - 确认与实际文件匹配

2. **fetch 请求是否成功？**
   - F12 → Network 标签
   - 查找 .md 文件请求
   - 状态码应该是 200

3. **文件路径是否正确？**
   - 检查 fetch 的完整 URL
   - 确认与文件实际位置匹配

---

## ⚠️ 可能的问题

### 问题 1：Docsify.vm 未定义

**现象：**
```
从 hash 解析文件名: README.md
最终文件名: README.md
```

**原因：** Docsify 未完全初始化

**解决：**
- 确保页面完全加载后再点击 Edit
- 或添加延迟加载逻辑

### 问题 2：仍然加载错误的文件

**现象：**
```
从 Docsify.vm.route 获取文件名: README.md
但实际应该是: README_demo.md
```

**原因：** Docsify 的路由信息不准确

**解决：**
- 检查 Docsify 配置
- 确认 homepage 设置正确

### 问题 3：CORS 错误

**现象：**
```
Failed to load markdown content: TypeError: Failed to fetch
```

**原因：** 必须通过 HTTP 服务器访问

**解决：**
```bash
# ❌ 错误方式
file:///E:/forgenote/docs/editor-demo.html

# ✅ 正确方式
http://localhost:8000/docs/editor-demo.html
```

---

## 📊 测试清单

- [ ] 演示页面能加载 README_demo.md
- [ ] 控制台显示正确的文件名
- [ ] 编辑器显示完整的 Markdown 内容
- [ ] 没有 404 错误（除了 favicon.ico）
- [ ] 成功提示显示 "✅ Loaded: xxx.md"
- [ ] 实时预览正常工作
- [ ] 可以编辑和导出内容

---

## 🎯 预期结果

### 成功加载时：

```
界面显示：
┌─────────────────────────────────────────┐
│ 📝 Editing: README_demo.md   [按钮区]   │
├──────────────────┬──────────────────────┤
│  # Docsify ...   │  渲染后的预览        │
│  Welcome to ...  │                      │
│  ## Features     │  (实时更新)          │
│  - Edit          │                      │
│  ...             │                      │
└──────────────────┴──────────────────────┘

提示框：
✅ Loaded: README_demo.md
```

### 失败时：

```
界面显示：
┌─────────────────────────────────────────┐
│ 📝 Editing: xxx.md (load failed) [按钮] │
├──────────────────┬──────────────────────┤
│  # Load Failed   │  渲染后的预览        │
│  Cannot load:... │                      │
│  Error: ...      │                      │
└──────────────────┴──────────────────────┘

提示框：
❌ Failed to load: xxx.md
```

---

## 💡 验证成功的标志

1. ✅ 控制台没有报错
2. ✅ 编辑器显示的是完整的 Markdown（不是空白）
3. ✅ 文件名正确（没有 "reconstructed" 或 "load failed"）
4. ✅ 右侧预览能正确渲染
5. ✅ 可以编辑并实时预览
6. ✅ 复制/下载功能正常

---

**现在可以重新测试了！** 🚀

记得：
1. 从项目根目录启动服务器
2. 访问 http://localhost:8000/docs/editor-demo.html
3. 打开 F12 控制台查看日志
4. 点击 Edit 按钮
