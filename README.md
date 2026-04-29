# PyForge — Standalone Python Code Generator & Editor

PyForge is a lightweight, standalone Python application for generating, editing, and refining Python code using local `.gguf` LLM models.  
It includes a full GUI, multi-model support, deep analysis, and a clean file‑forging workflow.

---

## ✨ Features

- **Local LLM support** via `llama-cpp-python`
- **Multi-model registry** using `models/manifest.yaml`
- **Model-family-aware prompts** (GPT, Mistral, Qwen, DeepSeek, Phi, Llama)
- **Python code generator** (topic → code)
- **Refinement loop** (add corrections → re-run)
- **Deep Analysis Engine**  
  - Chunk → Summarize → Meta → Rewrite
- **GUI editor** with:
  - Raw LLM output
  - Extracted code
  - Save / Open
  - Forge to `/storage/pending`

---

## 📁 Project Structure
```
PythonForge/
│
├── pyforge.py
├── requirements.txt
├── README.md
│
├── config/
│   └── settings.json
│
├── engine/
│   ├── llm_engine.py
│   ├── deep_analysis.py
│   ├── forge_writer.py
│
├── gui/
│   └── pyforge_window.py
│
├── llm/
│   └── (optional controllers)
│
├── prompt/
│   └── prompt_builder.py
│
├── models/
│   ├── manifest.yaml
│   └── *.gguf
│
└── storage/
├── pending/
├── saved/
└── logs/
```

---

## 🚀 Getting Started
1. Install dependencies
```bash
pip install -r requirements.txt

```
2. Add your .gguf models
- Place them in the folder:
```
./PythonForge/models/
```
3. Edit models/manifest.yaml
- Example:
```
models:
  gpt_default:
    path: ./models/gpt-oss-20b.gguf
    n_ctx: 32768
    template: gpt
```
4. Run PyForge
```
python pyforge.py
```

---

### 🧠 Deep Analysis
PyForge includes a multi-stage analysis pipeline:

Chunk the code

Summarize each chunk

Merge summaries

Rewrite the code using the summary

This helps restructure large or messy codebases.


### 📦 Storage
-Generated files go to folder:
```
./PythonForge/storage/pending/
```

-Saved files go to folder:
```
./PythonForge/storage/saved/
```

-Logs go to folder:
```
./PythonForge/storage/logs/
```

📝 License
read license

Created By: David Kistner (Unconditional Love) at GlyphicMind Solutions LLC
