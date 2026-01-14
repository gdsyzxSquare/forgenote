/**
 * Docsify 编辑器插件
 * 
 * 功能：在 docsify 页面中提供轻量级的 Markdown 编辑和导出能力
 * 
 * 使用方式：
 * 在 docsify index.html 中引入：
 * <link rel="stylesheet" href="docsify-editor.css">
 * <script src="docsify-editor.js"></script>
 */

(function() {
  'use strict';

  // 编辑器状态
  let editorState = {
    isEditMode: false,
    currentContent: '',
    currentFile: '',
    originalContent: ''
  };

  // 源码映射表（Markdown 行号 <-> HTML 元素）
  let sourceMap = [];

  // 初始化编辑器
  function initEditor() {
    // 创建编辑按钮
    createEditButton();
    
    // 创建编辑器容器
    createEditorContainer();
    
    // 监听 docsify 路由变化
    if (window.$docsify) {
      const originalRouter = window.$docsify.router;
      window.$docsify.plugins = window.$docsify.plugins || [];
      
      window.$docsify.plugins.push(function(hook) {
        // 页面加载完成后更新编辑器内容
        hook.doneEach(function() {
          if (editorState.isEditMode) {
            loadCurrentPageContent();
          }
        });
      });
    }
  }

  // 创建编辑按钮
  function createEditButton() {
    const btn = document.createElement('button');
    btn.className = 'docsify-edit-btn';
    btn.textContent = '✏️ Edit';
    btn.onclick = toggleEditMode;
    document.body.appendChild(btn);
  }

  // 创建编辑器容器
  function createEditorContainer() {
    const container = document.createElement('div');
    container.className = 'docsify-editor-container';
    container.innerHTML = `
      <div class="docsify-editor-toolbar">
        <div class="docsify-editor-title">
          Editing: <span id="editor-filename">Current Page</span>
        </div>
        <div class="docsify-editor-actions">
          <button onclick="docsifyEditor.copyToClipboard()">
            📋 Copy Markdown
          </button>
          <button onclick="docsifyEditor.downloadMarkdown()">
            💾 Download .md
          </button>
          <button class="danger" onclick="docsifyEditor.exitEditMode()">
            ❌ Exit
          </button>
        </div>
      </div>
      <div class="docsify-editor-body">
        <div class="docsify-editor-pane">
          <div class="docsify-editor-pane-header">📝 Markdown Editor</div>
          <textarea 
            class="docsify-editor-textarea" 
            id="docsify-markdown-editor"
            placeholder="Start editing your markdown here..."
            spellcheck="false"
          ></textarea>
        </div>
        <div class="docsify-editor-preview">
          <div class="docsify-editor-pane-header">👁️ Live Preview</div>
          <div class="docsify-editor-preview-content">
            <div class="markdown-section" id="docsify-preview-content">
              <p>Preview will appear here...</p>
            </div>
          </div>
        </div>
      </div>
      <div class="docsify-editor-toast" id="editor-toast"></div>
    `;
    document.body.appendChild(container);

    // 绑定编辑器输入事件（实时预览）
    const textarea = document.getElementById('docsify-markdown-editor');
    textarea.addEventListener('input', debounce(updatePreview, 300));
  }

  // 切换编辑模式
  function toggleEditMode() {
    if (editorState.isEditMode) {
      exitEditMode();
    } else {
      enterEditMode();
    }
  }

  // 进入编辑模式
  function enterEditMode() {
    editorState.isEditMode = true;
    
    // 隐藏 docsify 内容
    const app = document.getElementById('app');
    if (app) app.style.display = 'none';
    
    // 显示编辑器
    const container = document.querySelector('.docsify-editor-container');
    container.classList.add('active');
    
    // 更新按钮状态
    const btn = document.querySelector('.docsify-edit-btn');
    btn.textContent = '👁️ Preview';
    btn.classList.add('edit-mode');
    
    // 设置编辑器和预览区的点击联动（首次进入编辑模式时）
    setupEditorClickLink();
    setupPreviewClickLink();
    
    // 加载当前页面内容
    loadCurrentPageContent();
    
    showToast('Entered Edit Mode', 'success');
  }

  // 退出编辑模式
  function exitEditMode() {
    // 确认是否有未保存的修改
    const textarea = document.getElementById('docsify-markdown-editor');
    if (textarea.value !== editorState.originalContent) {
      if (!confirm('You have unsaved changes. Are you sure you want to exit?')) {
        return;
      }
    }
    
    editorState.isEditMode = false;
    
    // 显示 docsify 内容
    const app = document.getElementById('app');
    if (app) app.style.display = 'block';
    
    // 隐藏编辑器
    const container = document.querySelector('.docsify-editor-container');
    container.classList.remove('active');
    
    // 更新按钮状态
    const btn = document.querySelector('.docsify-edit-btn');
    btn.textContent = '✏️ Edit';
    btn.classList.remove('edit-mode');
    
    showToast('Exited Edit Mode', 'success');
  }

  // 加载当前页面内容
  function loadCurrentPageContent() {
    // 获取真实的 Markdown 文件路径
    let filename = null;
    let routePath = null;
    
    // 方法1：从 Docsify 的 vm 对象获取当前路由路径
    if (window.Docsify && window.Docsify.vm && window.Docsify.vm.route) {
      routePath = window.Docsify.vm.route.path;
      console.log('从 Docsify.vm.route.path 获取路径:', routePath);
      console.log('完整 route 对象:', window.Docsify.vm.route);
      
      // 处理路径，提取文件名
      if (routePath) {
        // 移除开头的 '/'
        filename = routePath.replace(/^\//, '');
        
        // 如果是空或只有 '/'，使用首页
        if (!filename || filename === '/') {
          filename = window.$docsify?.homepage || 'README.md';
        } else {
          // 确保有 .md 扩展名（Docsify 通常会在路由中去掉 .md）
          if (!filename.endsWith('.md')) {
            filename = filename + '.md';
          }
        }
      }
    }
    
    // 方法2：从 hash 直接解析
    if (!filename) {
      let hash = window.location.hash.replace('#/', '');
      console.log('从 hash 获取:', hash);
      
      // 先移除查询参数
      if (hash.includes('?')) {
        hash = hash.split('?')[0];
        console.log('移除查询参数后:', hash);
      }
      
      if (!hash || hash === '/' || hash === '') {
        // 首页
        filename = window.$docsify?.homepage || 'README.md';
      } else {
        // 其他页面 - 先处理完查询参数再添加 .md
        filename = hash.endsWith('.md') ? hash : hash + '.md';
      }
    }
    
    console.log('最终文件名:', filename);
    
    // 尝试获取原始 Markdown 内容
    fetchMarkdownContent(filename)
      .then(content => {
        editorState.currentFile = filename;
        editorState.currentContent = content;
        editorState.originalContent = content;
        
        const textarea = document.getElementById('docsify-markdown-editor');
        textarea.value = content;
        
        const filenameSpan = document.getElementById('editor-filename');
        filenameSpan.textContent = filename;
        
        updatePreview();
        showToast('✅ Loaded: ' + filename, 'success');
      })
      .catch(error => {
        console.error('Failed to load markdown content:', error);
        showToast('❌ Failed to load: ' + filename, 'error');
        
        // 显示错误提示
        const textarea = document.getElementById('docsify-markdown-editor');
        textarea.value = '# Load Failed\n\nCannot load: ' + filename + '\n\nError: ' + error.message;
        
        const filenameSpan = document.getElementById('editor-filename');
        filenameSpan.textContent = filename + ' (load failed)';
      });
  }

  // 获取 Markdown 原始内容
  function fetchMarkdownContent(filename) {
    console.log('Fetching file:', filename);
    console.log('Full URL will be:', window.location.origin + window.location.pathname.replace('index.html', '') + filename);
    
    return fetch(filename)
      .then(response => {
        console.log('Response status:', response.status);
        console.log('Response URL:', response.url);
        console.log('Content-Type:', response.headers.get('content-type'));
        
        if (!response.ok) {
          throw new Error('File not found: ' + filename);
        }
        return response.text();
      })
      .then(content => {
        console.log('Content length:', content.length);
        console.log('Content preview:', content.substring(0, 200));
        
        // 检查是否意外获取了 HTML 内容（而不是 Markdown）
        if (content.trim().startsWith('<!DOCTYPE') || content.trim().startsWith('<html')) {
          console.error('❌ 获取到的是 HTML 而不是 Markdown!');
          throw new Error('Server returned HTML instead of Markdown. The file might not exist or server is misconfigured.');
        }
        
        return content;
      });
  }

  // ==================== 源码映射功能 ====================

  /**
   * 解析 Markdown 源码，生成行号到预览块的映射表
   * @param {string} markdown - Markdown 源码
   * @returns {Array} 映射表数组
   */
  function parseSourceMap(markdown) {
    if (!window.marked || !window.marked.lexer) {
      console.warn('marked.lexer not available');
      return [];
    }

    const tokens = window.marked.lexer(markdown);
    const map = [];
    let currentLine = 1;
    let blockIndex = 0;

    // 只映射会被渲染成独立块的 token 类型（不包括 space）
    const blockTypes = ['paragraph', 'heading', 'list', 'code', 'blockquote', 'table', 'hr'];

    console.log('=== Parsing tokens ===');
    tokens.forEach((token, index) => {
      // 计算当前 token 占用的行数
      const lineCount = (token.raw || '').split('\n').length;
      
      console.log(`Token ${index}: type=${token.type}, lines=${currentLine}-${currentLine + lineCount - 1}, isBlock=${blockTypes.includes(token.type)}`);
      
      // 只为块级元素创建映射
      if (blockTypes.includes(token.type)) {
        map.push({
          blockId: `md-block-${blockIndex}`,
          tokenIndex: index,
          lineStart: currentLine,
          lineEnd: currentLine + lineCount - 1,
          type: token.type,
          text: (token.text || token.raw || '').substring(0, 50)
        });
        console.log(`  → Created mapping for block ${blockIndex}`);
        blockIndex++;
      }
      
      currentLine += lineCount;
    });

    console.log(`=== Source map generated: ${map.length} blocks from ${tokens.length} tokens ===`);
    return map;
  }

  /**
   * 从 textarea 获取当前光标所在行号
   * @param {HTMLTextAreaElement} textarea
   * @returns {number} 行号（从1开始）
   */
  function getLineNumberFromTextarea(textarea) {
    const text = textarea.value;
    const cursorPos = textarea.selectionStart;
    const textBeforeCursor = text.substring(0, cursorPos);
    return textBeforeCursor.split('\n').length;
  }

  /**
   * 高亮编辑区指定行范围
   * @param {number} lineStart - 起始行号
   * @param {number} lineEnd - 结束行号
   */
  function highlightEditorLines(lineStart, lineEnd) {
    const textarea = document.getElementById('docsify-markdown-editor');
    if (!textarea) return;

    // 计算行的字符位置
    const lines = textarea.value.split('\n');
    let startPos = 0;
    for (let i = 0; i < lineStart - 1; i++) {
      startPos += lines[i].length + 1; // +1 for newline
    }

    let endPos = startPos;
    for (let i = lineStart - 1; i <= lineEnd - 1 && i < lines.length; i++) {
      endPos += lines[i].length + 1;
    }

    // 选中文本
    textarea.focus();
    textarea.setSelectionRange(startPos, endPos - 1);
    
    // 滚动到可见区域
    const lineHeight = 20; // 假设行高
    textarea.scrollTop = (lineStart - 1) * lineHeight - textarea.clientHeight / 3;

    // 添加高亮样式（临时）
    textarea.classList.add('editor-highlight-active');
    setTimeout(() => {
      textarea.classList.remove('editor-highlight-active');
    }, 2000);

    console.log(`Highlighted editor lines ${lineStart}-${lineEnd}`);
  }

  /**
   * 高亮预览区指定 offset 对应的块
   * @param {number} offset - 源码字符偏移量
   */
  function highlightPreviewBlock(offset) {
    const preview = document.getElementById('docsify-preview-content');
    if (!preview) return;

    // 移除之前的高亮
    const previousHighlight = preview.querySelector('.preview-highlight-active');
    if (previousHighlight) {
      previousHighlight.classList.remove('preview-highlight-active');
    }

    // 查找包含该 offset 的元素
    const elements = preview.querySelectorAll('[data-source-start]');
    let targetElement = null;
    
    for (const el of elements) {
      const start = parseInt(el.getAttribute('data-source-start'));
      const end = parseInt(el.getAttribute('data-source-end'));
      
      if (offset >= start && offset <= end) {
        targetElement = el;
        break;
      }
    }

    if (targetElement) {
      targetElement.classList.add('preview-highlight-active');
      
      // 滚动到可见区域
      targetElement.scrollIntoView({ behavior: 'smooth', block: 'center' });

      // 2秒后移除高亮
      setTimeout(() => {
        targetElement.classList.remove('preview-highlight-active');
      }, 2000);

      const start = targetElement.getAttribute('data-source-start');
      const end = targetElement.getAttribute('data-source-end');
      console.log(`✓ Highlighted preview: offset [${start}-${end}] (clicked offset ${offset})`);
    } else {
      console.warn(`✗ No preview element found for offset ${offset}`);
    }
  }

  /**
   * 高亮编辑区指定的字符区间
   * @param {number} startOffset - 起始偏移量
   * @param {number} endOffset - 结束偏移量
   */
  function highlightEditorRange(startOffset, endOffset) {
    const textarea = document.getElementById('docsify-markdown-editor');
    if (!textarea) return;

    // 选中文本
    textarea.focus();
    textarea.setSelectionRange(startOffset, endOffset);
    
    // 滚动到可见区域（估算）
    const avgLineLength = 50;
    const lineNumber = Math.floor(startOffset / avgLineLength);
    const lineHeight = 20;
    textarea.scrollTop = lineNumber * lineHeight - textarea.clientHeight / 3;

    // 添加高亮样式（临时）
    textarea.classList.add('editor-highlight-active');
    setTimeout(() => {
      textarea.classList.remove('editor-highlight-active');
    }, 2000);

    console.log(`✓ Highlighted editor: offset [${startOffset}-${endOffset}]`);
  }

  /**
   * 设置编辑区点击联动
   */
  function setupEditorClickLink() {
    const textarea = document.getElementById('docsify-markdown-editor');
    if (!textarea) return;

    textarea.addEventListener('click', function(e) {
      const offset = textarea.selectionStart;
      console.log('→ Editor clicked at offset:', offset);
      highlightPreviewBlock(offset);
    });
  }

  /**
   * 设置预览区点击联动
   */
  function setupPreviewClickLink() {
    const preview = document.getElementById('docsify-preview-content');
    if (!preview) return;

    preview.addEventListener('click', function(e) {
      // 查找最近的带 data-source-start 的元素
      const element = e.target.closest('[data-source-start]');
      if (!element) return;

      const start = parseInt(element.getAttribute('data-source-start'));
      const end = parseInt(element.getAttribute('data-source-end'));
      
      if (start !== null && end !== null) {
        console.log(`← Preview clicked: offset [${start}-${end}]`);
        highlightEditorRange(start, end);
      }
    });
  }

  // ==================== 源码映射功能结束 ====================

  // 更新预览
  function updatePreview() {
    const textarea = document.getElementById('docsify-markdown-editor');
    const preview = document.getElementById('docsify-preview-content');
    
    const markdown = textarea.value;
    editorState.currentContent = markdown;
    
    // 使用 marked.js 渲染（docsify 已经加载了）
    if (window.marked) {
      // ========== Source Span 追踪机制 ==========
      const sourceText = markdown;
      let cursorOffset = 0; // 全局源码消费指针（单调递增）
      
      // 辅助函数：在源码中查找 raw 内容并返回 { startOffset, endOffset }
      function findSourceSpan(raw) {
        if (!raw) return { start: 0, end: 0 };
        
        // 从 cursorOffset 开始查找 raw
        const index = sourceText.indexOf(raw, cursorOffset);
        
        if (index === -1) {
          console.warn(`⚠ Cannot find raw in source from offset ${cursorOffset}:`, raw.substring(0, 50));
          return { start: cursorOffset, end: cursorOffset };
        }
        
        const startOffset = index;
        const endOffset = index + raw.length;
        
        // 更新游标到当前块结束位置
        cursorOffset = endOffset;
        
        console.log(`✓ Span [${startOffset}-${endOffset}]: "${raw.substring(0, 30).replace(/\n/g, '↵')}..."`);
        return { start: startOffset, end: endOffset };
      }
      
      // 自定义 renderer，在每个 block 上标注 source span
      const renderer = new window.marked.Renderer();
      const originalParagraph = renderer.paragraph;
      const originalHeading = renderer.heading;
      const originalList = renderer.list;
      const originalCode = renderer.code;
      const originalBlockquote = renderer.blockquote;
      const originalTable = renderer.table;
      const originalHr = renderer.hr;

      // ========== 包裹函数：给渲染结果添加 source span 标注 ==========
      function wrapWithSourceSpan(html, raw) {
        const span = findSourceSpan(raw);
        return `<div class="md-block md-mappable" data-source-start="${span.start}" data-source-end="${span.end}">${html}</div>`;
      }
      
      // 段落（通过文本内容在源码中查找）
      renderer.paragraph = function(text) {
        // 移除 HTML 标签获取纯文本
        const plainText = text.replace(/<[^>]*>/g, '');
        const raw = plainText; // 近似
        const html = `<p>${text}</p>`;
        return wrapWithSourceSpan(html, raw);
      };

      // 标题
      renderer.heading = function(text, level, raw) {
        // marked 的 heading 提供 raw 参数
        const actualRaw = raw || `${'#'.repeat(level)} ${text}`;
        const html = `<h${level}>${text}</h${level}>`;
        return wrapWithSourceSpan(html, actualRaw);
      };

      // 列表（通过内容查找）
      renderer.list = function(body, ordered, start) {
        const type = ordered ? 'ol' : 'ul';
        const startAttr = (ordered && start !== 1) ? ` start="${start}"` : '';
        const html = `<${type}${startAttr}>${body}</${type}>`;
        // 简化：暂时不标注精确 span（列表嵌套复杂）
        return `<div class="md-block md-mappable" data-source-start="0" data-source-end="0">${html}</div>`;
      };

      // 代码块
      renderer.code = function(code, language, isEscaped) {
        const lang = language ? ` class="language-${language}"` : '';
        const html = `<pre><code${lang}>${escapeHtml(code)}</code></pre>`;
        // 构造预期的 raw（包含 ``` 标记）
        const raw = language ? `\`\`\`${language}\n${code}\n\`\`\`` : `\`\`\`\n${code}\n\`\`\``;
        return wrapWithSourceSpan(html, raw);
      };

      // 引用块
      renderer.blockquote = function(quote) {
        const html = `<blockquote>${quote}</blockquote>`;
        // 简化：不标注精确 span
        return `<div class="md-block md-mappable" data-source-start="0" data-source-end="0">${html}</div>`;
      };

      // 表格
      renderer.table = function(header, body) {
        const html = `<table><thead>${header}</thead><tbody>${body}</tbody></table>`;
        // 简化：不标注精确 span
        return `<div class="md-block md-mappable" data-source-start="0" data-source-end="0">${html}</div>`;
      };

      // 水平线
      renderer.hr = function() {
        const html = `<hr>`;
        const raw = '---';
        return wrapWithSourceSpan(html, raw);
      };

      // 图片（不包裹，因为通常在段落内）
      renderer.image = function(href, title, text) {
        const titleAttr = title ? ` title="${title}"` : '';
        return `<img src="${href}" alt="${text}"${titleAttr}>`;
      };

      const html = window.marked.parse(markdown, { renderer });
      preview.innerHTML = html;
      
      // 渲染数学公式（如果有 KaTeX）
      if (window.katex && window.renderMathInElement) {
        try {
          renderMathInElement(preview, {
            delimiters: [
              {left: '$$', right: '$$', display: true},
              {left: '$', right: '$', display: false}
            ]
          });
        } catch (e) {
          console.warn('KaTeX rendering failed:', e);
        }
      }
    } else {
      // 降级：纯文本显示
      preview.innerHTML = `<pre>${escapeHtml(markdown)}</pre>`;
    }
  }

  // 复制到剪贴板
  function copyToClipboard() {
    const textarea = document.getElementById('docsify-markdown-editor');
    const content = textarea.value;
    
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(content)
        .then(() => {
          showToast('✅ Copied to clipboard!', 'success');
        })
        .catch(err => {
          console.error('Failed to copy:', err);
          fallbackCopy(textarea);
        });
    } else {
      fallbackCopy(textarea);
    }
  }

  // 降级复制方法
  function fallbackCopy(textarea) {
    textarea.select();
    try {
      document.execCommand('copy');
      showToast('✅ Copied to clipboard!', 'success');
    } catch (err) {
      showToast('❌ Copy failed. Please manually select and copy.', 'error');
    }
  }

  // 下载 Markdown 文件
  function downloadMarkdown() {
    const textarea = document.getElementById('docsify-markdown-editor');
    const content = textarea.value;
    const filename = editorState.currentFile || 'document.md';
    
    // 创建 Blob
    const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    
    // 创建下载链接
    const a = document.createElement('a');
    a.href = url;
    a.download = filename.replace('.md', '_edited.md');
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    
    // 释放 URL
    URL.revokeObjectURL(url);
    
    showToast('✅ Downloaded: ' + a.download, 'success');
  }

  // 显示提示消息
  function showToast(message, type = 'success') {
    const toast = document.getElementById('editor-toast');
    toast.textContent = message;
    toast.className = 'docsify-editor-toast show ' + type;
    
    setTimeout(() => {
      toast.classList.remove('show');
    }, 3000);
  }

  // 防抖函数
  function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }

  // HTML 转义
  function escapeHtml(unsafe) {
    return unsafe
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  // 暴露全局接口
  window.docsifyEditor = {
    enterEditMode,
    exitEditMode,
    toggleEditMode,
    copyToClipboard,
    downloadMarkdown,
    showToast
  };

  // DOM 加载完成后初始化
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initEditor);
  } else {
    initEditor();
  }

  // 键盘快捷键支持
  document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + E: 切换编辑模式
    if ((e.ctrlKey || e.metaKey) && e.key === 'e') {
      e.preventDefault();
      toggleEditMode();
    }
    
    // Ctrl/Cmd + S: 下载文件（在编辑模式下）
    if (editorState.isEditMode && (e.ctrlKey || e.metaKey) && e.key === 's') {
      e.preventDefault();
      downloadMarkdown();
    }
    
    // ESC: 退出编辑模式
    if (editorState.isEditMode && e.key === 'Escape') {
      exitEditMode();
    }
  });

})();
