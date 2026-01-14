/**
 * 图片上传功能模块
 * 使用本地文件桥接服务实现图片上传
 */

const IMAGE_UPLOAD_SERVICE_URL = 'http://localhost:8001';

/**
 * 检查本地服务是否运行
 */
async function checkLocalService() {
  try {
    const response = await fetch(`${IMAGE_UPLOAD_SERVICE_URL}/health`, {
      method: 'GET',
      signal: AbortSignal.timeout(2000) // 2秒超时
    });
    return response.ok;
  } catch (error) {
    return false;
  }
}

/**
 * 上传图片到本地服务
 */
async function uploadImageToLocal(file, documentName) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('document', documentName);
  
  const response = await fetch(`${IMAGE_UPLOAD_SERVICE_URL}/upload-image`, {
    method: 'POST',
    body: formData
  });
  
  if (!response.ok) {
    throw new Error(`Upload failed: ${response.statusText}`);
  }
  
  return await response.json();
}

/**
 * 主上传函数
 */
async function uploadImage() {
  // 检查服务是否运行
  const serviceRunning = await checkLocalService();
  
  if (!serviceRunning) {
    const useService = confirm(
      'Local Image Upload Service Not Running\n\n' +
      'To upload images directly:\n' +
      '1. Open terminal in project folder\n' +
      '2. Run: python scripts/image_upload_service.py\n' +
      '3. Keep terminal running\n\n' +
      'Click OK to use fallback mode (manual download)'
    );
    
    if (useService) {
      uploadImageFallback();
    }
    return;
  }
  
  // 创建文件选择器
  const input = document.createElement('input');
  input.type = 'file';
  input.accept = 'image/*';
  input.multiple = false;
  
  input.onchange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    // 验证文件类型
    if (!file.type.startsWith('image/')) {
      showToast('❌ Please select an image file', 'error');
      return;
    }
    
    // 验证文件大小（最大 10MB）
    if (file.size > 10 * 1024 * 1024) {
      showToast('❌ Image too large (max 10MB)', 'error');
      return;
    }
    
    showToast('⏳ Uploading image...', 'info');
    
    try {
      // 获取当前文档名称
      const currentFile = editorState.currentFile || 'README.md';
      const fileName = currentFile.includes('/') ? currentFile.split('/').pop() : currentFile;
      const documentName = fileName.replace(/\.md$/, '');
      
      // 上传到本地服务
      const result = await uploadImageToLocal(file, documentName);
      
      if (!result.success) {
        throw new Error(result.message || 'Upload failed');
      }
      
      // 生成 markdown 链接
      const markdown = `![${file.name}](${result.path})`;
      
      // 复制到剪贴板
      await navigator.clipboard.writeText(markdown);
      
      // 自动插入到编辑器光标位置
      const textarea = document.getElementById('docsify-markdown-editor');
      if (textarea) {
        const cursorPos = textarea.selectionStart;
        const textBefore = textarea.value.substring(0, cursorPos);
        const textAfter = textarea.value.substring(cursorPos);
        
        // 插入时添加换行以保持格式整洁
        const needsNewlineBefore = textBefore && !textBefore.endsWith('\n');
        const needsNewlineAfter = textAfter && !textAfter.startsWith('\n');
        
        textarea.value = textBefore + 
          (needsNewlineBefore ? '\n' : '') + 
          markdown + 
          (needsNewlineAfter ? '\n' : '') + 
          textAfter;
        
        // 更新光标位置
        const newCursorPos = cursorPos + (needsNewlineBefore ? 1 : 0) + markdown.length;
        textarea.setSelectionRange(newCursorPos, newCursorPos);
        textarea.focus();
        
        // 更新预览
        updatePreview();
      }
      
      showToast(
        `✅ Image uploaded!\n📁 ${result.path}`,
        'success',
        3000
      );
      
      console.log('✓ Image uploaded:', result.path);
      
    } catch (error) {
      showToast('❌ Upload failed: ' + error.message, 'error');
      console.error('Upload error:', error);
    }
  };
  
  // 触发文件选择
  input.click();
}

/**
 * 降级方案：下载图片文件
 */
function uploadImageFallback() {
  const input = document.createElement('input');
  input.type = 'file';
  input.accept = 'image/*';
  input.multiple = false;
  
  input.onchange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    if (!file.type.startsWith('image/')) {
      showToast('❌ Please select an image file', 'error');
      return;
    }
    
    if (file.size > 10 * 1024 * 1024) {
      showToast('❌ Image too large (max 10MB)', 'error');
      return;
    }
    
    const timestamp = Date.now();
    const ext = file.name.split('.').pop();
    const newFilename = `image_${timestamp}.${ext}`;
    
    const currentFile = editorState.currentFile || 'README.md';
    const fileName = currentFile.includes('/') ? currentFile.split('/').pop() : currentFile;
    const baseName = fileName.replace(/\.md$/, '');
    const targetPath = `assets/${baseName}/images/${newFilename}`;
    const markdown = `![${file.name}](${targetPath})`;
    
    // 触发下载
    const blob = new Blob([file], { type: file.type });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = newFilename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    await navigator.clipboard.writeText(markdown);
    
    showToast(
      `✅ Image downloaded!\n📋 Link copied\n📁 Move to: ${targetPath}`,
      'success',
      5000
    );
    
    console.log('✓ Fallback mode: image downloaded');
    console.log('- Target:', targetPath);
  };
  
  input.click();
}
