"""
配置模块
"""
import os
from pathlib import Path

# 项目根目录
ROOT_DIR = Path(__file__).parent.parent.parent

# 数据目录
DATA_DIR = ROOT_DIR / "data"
RAW_MD_DIR = DATA_DIR / "raw_md"
OUTPUT_DIR = DATA_DIR / "output"
ASSETS_DIR = DATA_DIR / "assets"

# 配置目录
CONFIG_DIR = ROOT_DIR / "config"

# 确保目录存在
for directory in [DATA_DIR, RAW_MD_DIR, OUTPUT_DIR, ASSETS_DIR, CONFIG_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# LLM 配置
LLM_CONFIG = {
    "model": "gpt-4",
    "temperature": 0.3,
    "max_tokens": 4000,
}

# MinerU 配置
MINERU_CONFIG = {
    "output_format": "markdown",
    "extract_images": True,
    "image_dir": "images",
}

# Docsify 配置
DOCSIFY_CONFIG = {
    "name": "课程文档",
    "repo": "",
    "loadSidebar": True,
    "subMaxLevel": 3,
    "auto2top": True,
}
