# ForgeNote - 电子课程文档自动化处理系统

<div align="center">

**将零散的 PPT/PDF 课件 → 自动转换为结构清晰的 Docsify 在线文档**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

</div>

---

## 📖 项目简介

ForgeNote 是一个智能化的课程文档处理系统，旨在解决高校教学资料组织混乱、检索困难的问题。

### 核心功能

- 🔄 **自动化转换**：将 PPT/PDF 课件自动转换为结构化 Markdown 文档
- 📚 **智能结构提取**：基于 LLM 识别课程的章节和知识点结构
- ✨ **内容重组**：将"页面驱动"的课件重构为"知识驱动"的文档
- 🎨 **格式美化**：自动规范化 Markdown 格式，适配 Docsify 渲染
- 👀 **人工审查**：提供结构化的人工审查机制，确保内容准确性
- 🌐 **在线文档站**：一键生成可部署的 Docsify 静态文档站点

### 系统架构

```
[PPT/PDF 课件]
     ↓
[MinerU 转换]
     ↓
[原始 Markdown + 图片]
     ↓
[课程结构提取（LLM）]
     ↓
[内容重组与补全（LLM）]
     ↓
[Markdown 美化与规范化]
     ↓
[人工审查与修正（可选）]
     ↓
[Docsify 文档站点]
```

---

## 🚀 快速开始

### 环境要求

- Python 3.8+
- Node.js 14+（用于运行 Docsify）
- MinerU（用于 PPT/PDF 转换）

### MinerU 输出结构说明

ForgeNote 支持 MinerU 的标准输出格式，每个转换的文件对应一个文件夹：

```
mineru_output/
├── lecture1/              # 每个文件一个文件夹
│   ├── lecture1.md        # Markdown文件
│   └── images/            # 图片子文件夹
│       ├── image1.png
│       └── image2.png
├── lecture2/
│   ├── lecture2.md
│   └── images/
│       └── image1.png
```

系统会自动：
- 识别所有文件夹中的 `.md` 文件
- 复制对应的 `images` 子文件夹
- 更新 Markdown 中的图片路径为正确的相对路径

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/your-repo/forgenote.git
cd forgenote
```

2. **安装 Python 依赖**
```bash
pip install -r requirements.txt
```

3. **配置 LLM API**

推荐使用 **DeepSeek**（性价比高，国内可直接访问）：

```bash
# 编辑 .env 文件
OPENAI_API_KEY=sk-your-deepseek-api-key
OPENAI_API_BASE=https://api.deepseek.com
DEFAULT_MODEL=deepseek-chat
```

> 📖 详细配置指南：[DeepSeek API 配置](docs/DEEPSEEK_SETUP.md)  
> 💡 也支持 OpenAI、Azure OpenAI 等其他兼容 API

4. **安装 Docsify CLI（可选，用于本地预览）**
```bash
npm install -g docsify-cli
```

### 基本使用

**方式一：使用配置文件（推荐）**

```bash
# 1. 创建配置文件
cp config/example_course_config.yaml config/my_course.yaml

# 2. 编辑配置文件，设置课程信息和路径

# 3. 运行流水线
python scripts/run_pipeline.py --config config/my_course.yaml
```

**方式二：命令行参数**

```bash
python scripts/run_pipeline.py "线性代数" "path/to/mineru_output"
```

**参数说明**：
- `--config, -c`：配置文件路径（YAML格式）
- `course_name`：课程名称
- `mineru_output`：MinerU 转换后的输出目录
- `--use-llm`：启用 LLM 智能处理（需配置 API）
- `--apply-patches`：应用人工修正补丁
- `--create-config`：创建默认配置文件

**详细配置说明**：
- 📖 [配置文件使用指南](docs/CONFIG_GUIDE.md) - 完整配置项说明
- 🎯 [配置示例文档](docs/CONFIG_EXAMPLES.md) - 快速上手示例
- 📝 [example_course_config.yaml](config/example_course_config.yaml) - 配置模板

**方式三：Python API**

```python
from scripts.run_pipeline import PipelineOrchestrator
from pathlib import Path

# 创建流水线
pipeline = PipelineOrchestrator("线性代数")

# 运行完整流程
pipeline.run_full_pipeline(
    mineru_output_dir=Path("data/mineru_output"),
    apply_patches=False
)
```

### 预览生成的文档

```bash
cd data/output/线性代数
docsify serve .
```

在浏览器中访问 `http://localhost:3000`

---

## 📂 项目结构

```
forgenote/
├── src/                      # 核心代码
│   ├── modules/              # 功能模块
│   │   ├── document_importer.py      # 文档导入与预处理
│   │   ├── structure_extractor.py    # 课程结构提取
│   │   ├── content_reorganizer.py    # 内容重组
│   │   ├── markdown_beautifier.py    # Markdown 美化
│   │   ├── docsify_generator.py      # Docsify 站点生成
│   │   └── human_review.py           # 人工审查机制
│   ├── prompts/              # LLM Prompt 模板
│   │   └── templates.py
│   ├── utils/                # 工具函数
│   │   └── llm_client.py     # LLM 客户端封装
│   └── config.py             # 配置管理
├── scripts/                  # 可执行脚本
│   └── run_pipeline.py       # 主流程编排脚本
├── data/                     # 数据目录（自动创建）
│   ├── raw_md/               # MinerU 原始输出
│   ├── output/               # 最终文档输出
│   ├── assets/               # 资源文件（图片等）
│   ├── reviews/              # 人工审查清单
│   └── patches/              # 人工修正补丁
├── config/                   # 配置文件
│   └── example_course_config.yaml
├── requirements.txt          # Python 依赖
├── .env.example              # 环境变量示例
└── README.md                 # 项目文档
```

---

## 🔧 详细功能

### 1. 文档导入与预处理

- 从 MinerU 输出目录导入 Markdown 和图片
- 整理文件到标准目录结构
- 更新 Markdown 中的图片路径

### 2. 课程结构提取

- 使用 LLM 识别章节和小节
- 去除页码、重复标题等噪声
- 生成结构化目录（JSON 格式）

**LLM Prompt 示例**（见 [src/prompts/templates.py](src/prompts/templates.py)）

### 3. 内容重组

- 将页面驱动的内容重构为知识驱动
- 补充逻辑衔接语句
- 保持定义、定理、例子的完整性

### 4. Markdown 美化

- 规范化标题层级
- 标记定义、定理、例子（使用引用块）
- 修正图片路径
- 格式化代码块和公式

### 5. Docsify 站点生成

自动生成：
- `index.html`：Docsify 配置和插件
- `README.md`：课程首页
- `_sidebar.md`：侧边栏导航
- `_navbar.md`：顶部导航栏
- `package.json`：npm 配置

### 6. 人工审查机制

- 自动识别高风险项（图片错位、内容断裂等）
- 生成审查清单（JSON/YAML）
- 支持结构化补丁（patch）
- 补丁可复用、可版本控制

---

## 🎯 使用场景

### 场景 1：课程资料整理

将多个学期的 PPT 课件统一整理为在线文档库

```bash
python scripts/run_pipeline.py "数据结构" "ppt_output_dir"
```

### 场景 2：知识库构建

为课程问答系统（RAG）准备结构化知识源

### 场景 3：多版本课件合并

合并不同教师、不同版本的课件

---

## ⚙️ 配置说明

### LLM 配置

编辑 `.env` 文件：

```bash
OPENAI_API_KEY=sk-xxxxxxxx
DEFAULT_MODEL=gpt-4
TEMPERATURE=0.3
```

### 课程配置

复制并编辑 `config/example_course_config.yaml`：

```yaml
course:
  name: "线性代数"
  code: "MATH101"

processing:
  use_llm: true
  llm_provider: "openai"
  apply_patches: false

docsify:
  name: "线性代数课程文档"
  theme: "vue"
```

---

## 🤝 贡献指南

欢迎贡献代码、报告问题或提出建议！

### 开发环境搭建

```bash
# 克隆项目
git clone https://github.com/your-repo/forgenote.git
cd forgenote

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装开发依赖
pip install -r requirements.txt
```

### 提交规范

- 功能开发：`feat: 添加xxx功能`
- Bug 修复：`fix: 修复xxx问题`
- 文档更新：`docs: 更新xxx文档`
- 代码重构：`refactor: 重构xxx模块`

---

## 📝 待办事项

- [ ] 集成 MinerU API 调用
- [ ] 添加 Web UI 界面
- [ ] 支持更多 LLM 后端（Claude, 本地模型等）
- [ ] 批量处理多门课程
- [ ] 生成课程摘要和练习题
- [ ] 集成向量数据库（RAG 支持）

---

## 📄 许可证

MIT License

---

## 🙏 致谢

- [MinerU](https://github.com/opendatalab/MinerU) - PDF/PPT 转 Markdown
- [Docsify](https://docsify.js.org/) - 文档站点生成
- [OpenAI](https://openai.com/) - LLM API

---

## 📧 联系方式

- 项目维护者：[Your Name]
- 问题反馈：[GitHub Issues](https://github.com/your-repo/forgenote/issues)

---

<div align="center">

**如果这个项目对你有帮助，请给个 ⭐️ Star！**

</div>
