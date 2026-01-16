# ForgeNote - Automated Course Documentation System

<div align="center">

**Transform scattered PPT/PDF course materials → Structured Docsify online documentation**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)

</div>

---

## 📖 Overview

ForgeNote is an intelligent course documentation processing system that converts unstructured lecture slides into well-organized, searchable online documentation.

### Key Features

- 🔄 **Automated Conversion**: Transform PPT/PDF slides into structured Markdown documents
- 📚 **Intelligent Structure Extraction**: LLM-powered recognition of course chapters and topics
- ✨ **Content Reorganization**: Restructure "page-driven" slides into "knowledge-driven" documentation
- 🎨 **Format Beautification**: Automatically standardize Markdown format for Docsify rendering
- ✏️ **Browser-based Editing**: Built-in editor for online Markdown modification and export
- 🌐 **Online Documentation Site**: One-click generation of deployable Docsify static sites

### System Architecture

```
[PPT/PDF Slides]
     ↓
[MinerU Conversion]
     ↓
[Raw Markdown + Images]
     ↓
[Course Structure Extraction (LLM)]
     ↓
[Content Reorganization (LLM)]
     ↓
[Markdown Beautification]
     ↓
[Docsify Documentation Site]
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js (for Docsify)
- OpenAI-compatible API key (DeepSeek recommended)

### Installation

1. **Clone repository**
   ```bash
   git clone <repository-url>
   cd forgenote
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   npm install -g docsify-cli
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env and add your API key
   ```

4. **Configure project**
   ```bash
   cp config/cfg.example.yaml config/cfg.yaml
   # Edit cfg.yaml with your course information
   ```

### Usage

1. **Run processing pipeline**
   ```bash
   python scripts/run_pipeline.py
   ```
   This generates the Docsify site in `output/<COURSE_CODE>/docsify_site/`

2. **Start debug server**
   ```bash
   python scripts/start_debug_server.py 
   ```

   Then access at: http://localhost:3000

---

## 📁 Project Structure

```
forgenote/
├── config/              # Configuration files
├── scripts/             # Executable scripts
│   ├── run_pipeline.py         # Main processing pipeline
│   └── start_debug_server.py   # Development server launcher
├── src/
│   ├── modules/         # Core processing modules
│   ├── prompts/         # LLM prompt templates
│   └── utils/           # Utility functions
├── output/              # Generated documentation
└── docs/                # Project documentation
```

---

## 🔧 Configuration

Edit `config/cfg.yaml`:

```yaml
course:
  name: "Your Course Name"
  code: "COURSE001"

processing:
  use_llm: true
  llm_model: "deepseek-reasoner"

paths:
  mineru_output: "your_mineru_output"  # MinerU output directory
  output: "output"
```

---


## 🙏 Acknowledgments

- [MinerU](https://github.com/opendatalab/MinerU) - PDF/PPT to Markdown conversion
- [Docsify](https://docsify.js.org/) - Documentation site generator


