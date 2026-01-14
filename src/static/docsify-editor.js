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

  // 更新预览
  function updatePreview() {
    const textarea = document.getElementById('docsify-markdown-editor');
    const preview = document.getElementById('docsify-preview-content');
    
    const markdown = textarea.value;
    editorState.currentContent = markdown;
    
    // 使用 marked.js 渲染（docsify 已经加载了）
    if (window.marked) {
      const html = window.marked.parse(markdown);
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
