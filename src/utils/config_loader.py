"""
配置文件加载模块

支持从YAML文件加载课程配置
"""
import yaml
from pathlib import Path
from typing import Dict, Optional


class CourseConfig:
    """课程配置类"""
    
    def __init__(self, config_dict: Dict):
        """
        初始化配置
        
        Args:
            config_dict: 配置字典
        """
        self.raw_config = config_dict
        
        # 课程基本信息
        self.course_name = config_dict.get('course', {}).get('name', 'Unknown Course')
        self.course_code = config_dict.get('course', {}).get('code', '')
        self.semester = config_dict.get('course', {}).get('semester', '')
        
        # 处理配置
        processing = config_dict.get('processing', {})
        self.use_llm = processing.get('use_llm', False)
        self.llm_provider = processing.get('llm_provider', 'openai')
        self.llm_model = processing.get('llm_model', 'gpt-4')
        self.apply_patches = processing.get('apply_patches', False)
        
        # Docsify配置
        docsify = config_dict.get('docsify', {})
        self.docsify_name = docsify.get('name', self.course_name)
        self.docsify_repo = docsify.get('repo', '')
        self.docsify_theme = docsify.get('theme', 'vue')
        self.docsify_plugins = docsify.get('plugins', {})
        
        # 路径配置
        paths = config_dict.get('paths', {})
        self.mineru_output = paths.get('mineru_output', 'data/mineru_output')
        self.raw_md = paths.get('raw_md', 'data/raw_md')
        self.output = paths.get('output', 'data/output')
        self.assets = paths.get('assets', 'data/assets')
    
    def get_docsify_config(self) -> Dict:
        """
        获取Docsify配置字典
        
        Returns:
            Docsify配置
        """
        plugins = self.docsify_plugins
        config = {
            "name": self.docsify_name,
            "repo": self.docsify_repo,
            "loadSidebar": True,
            "subMaxLevel": 3,
            "auto2top": True,
        }
        
        # 添加搜索插件配置
        if plugins.get('search', True):
            config["search"] = {
                "placeholder": "搜索...",
                "noData": "没有结果",
                "depth": 3
            }
        
        return config
    
    def __repr__(self):
        return (f"CourseConfig(name='{self.course_name}', "
                f"use_llm={self.use_llm}, "
                f"llm_model='{self.llm_model}')")


def load_config(config_file: Path) -> CourseConfig:
    """
    从YAML文件加载配置
    
    Args:
        config_file: 配置文件路径
        
    Returns:
        CourseConfig对象
    """
    if not config_file.exists():
        raise FileNotFoundError(f"配置文件不存在: {config_file}")
    
    with open(config_file, 'r', encoding='utf-8') as f:
        config_dict = yaml.safe_load(f)
    
    return CourseConfig(config_dict)


def create_default_config(output_file: Path, course_name: str = "示例课程"):
    """
    创建默认配置文件
    
    Args:
        output_file: 输出文件路径
        course_name: 课程名称
    """
    default_config = {
        "course": {
            "name": course_name,
            "code": "COURSE101",
            "semester": "2026春季"
        },
        "processing": {
            "use_llm": False,
            "llm_provider": "openai",
            "llm_model": "gpt-4",
            "apply_patches": False
        },
        "docsify": {
            "name": f"{course_name}课程文档",
            "repo": "",
            "theme": "vue",
            "plugins": {
                "search": True,
                "zoom_image": True,
                "copy_code": True,
                "pagination": True,
                "katex": True
            }
        },
        "paths": {
            "mineru_output": "data/mineru_output",
            "raw_md": "data/raw_md",
            "output": "data/output",
            "assets": "data/assets"
        }
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        yaml.dump(default_config, f, allow_unicode=True, default_flow_style=False)
    
    print(f"✓ 已创建配置文件: {output_file}")
