"""
LLM客户端封装

支持多种LLM后端（OpenAI, Claude, 本地模型等）
"""
from typing import Optional, Dict, List
import os
from pathlib import Path

# 加载.env文件
try:
    from dotenv import load_dotenv
    # 获取项目根目录
    root_dir = Path(__file__).parent.parent.parent
    env_file = root_dir / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        print(f"✓ 已加载环境变量文件: {env_file}")
except ImportError:
    print("⚠ python-dotenv未安装，无法自动加载.env文件")


class LLMClient:
    """LLM客户端基类"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        """
        初始化LLM客户端
        
        Args:
            api_key: API密钥
            model: 模型名称
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
    
    def generate(self, prompt: str, **kwargs) -> str:
        """
        生成文本
        
        Args:
            prompt: 输入提示
            **kwargs: 其他参数
            
        Returns:
            生成的文本
        """
        raise NotImplementedError("子类需要实现此方法")


class OpenAIClient(LLMClient):
    """OpenAI兼容客户端（支持OpenAI、DeepSeek等）"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4", base_url: Optional[str] = None):
        super().__init__(api_key, model)
        
        # 获取base_url配置
        self.base_url = base_url or os.getenv("OPENAI_API_BASE") or os.getenv("LLM_API_BASE")
        
        # 检测提供商
        provider = "OpenAI"
        if self.base_url:
            if "deepseek" in self.base_url.lower():
                provider = "DeepSeek"
            elif "azure" in self.base_url.lower():
                provider = "Azure OpenAI"
            else:
                provider = "OpenAI兼容API"
        
        # 检查API key
        if not self.api_key:
            print(f"❌ 错误: 未找到API密钥")
            print("   请在.env文件中设置: OPENAI_API_KEY=your-key")
            self.client = None
            return
        
        # 显示API key前缀（用于调试）
        key_preview = self.api_key[:10] + "..." if len(self.api_key) > 10 else "***"
        print(f"✓ 已加载API Key: {key_preview}")
        if self.base_url:
            print(f"✓ 使用自定义API地址: {self.base_url}")
        
        # 延迟导入，避免未安装时报错
        try:
            import openai
            # 根据是否有base_url决定初始化方式
            if self.base_url:
                self.client = openai.OpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url
                )
            else:
                self.client = openai.OpenAI(api_key=self.api_key)
            print(f"✓ {provider}客户端初始化成功 (模型: {self.model})")
        except ImportError:
            print("❌ 错误: openai包未安装")
            print("   请运行: pip install openai")
            self.client = None
        except Exception as e:
            print(f"❌ {provider}客户端初始化失败: {e}")
            self.client = None
    
    def generate(self, prompt: str, temperature: float = 0.3, max_tokens: int = 4000) -> str:
        """
        使用OpenAI API生成文本
        
        Args:
            prompt: 输入提示
            temperature: 温度参数
            max_tokens: 最大token数
            
        Returns:
            生成的文本
        """
        if not self.client:
            return "错误: OpenAI客户端未初始化"
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的课程文档处理专家。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"错误: {str(e)}"


class MockLLMClient(LLMClient):
    """模拟LLM客户端（用于测试）"""
    
    def generate(self, prompt: str, **kwargs) -> str:
        """
        返回模拟响应
        
        Args:
            prompt: 输入提示
            **kwargs: 其他参数
            
        Returns:
            模拟的响应
        """
        # 返回简单的JSON格式响应
        return """{
  "course": "示例课程",
  "chapters": [
    {
      "title": "第一章",
      "sections": ["1.1 简介", "1.2 基础概念"]
    }
  ]
}"""


def create_llm_client(provider: str = "openai", **kwargs) -> LLMClient:
    """
    创建LLM客户端工厂函数
    
    Args:
        provider: 提供商名称（openai, mock等）
        **kwargs: 客户端参数
        
    Returns:
        LLM客户端实例
    """
    if provider == "openai":
        return OpenAIClient(**kwargs)
    elif provider == "mock":
        return MockLLMClient(**kwargs)
    else:
        raise ValueError(f"不支持的提供商: {provider}")
