# gui/pyforge_window.py
# PyForge GUI Window (Tabbed IDE Layout)
# Created By: David Kistner (Unconditional Love) at GlyphicMind Solutions LLC.


# system imports
import re
from datetime import datetime
from pathlib import Path
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QLabel,
    QMessageBox,
    QSplitter,
    QComboBox,
    QFileDialog,
    QTabWidget,
)

# folder imports
from engine.deep_analysis import DeepAnalysisEngine
from engine.forge_writer import ForgeWriter
from prompt.prompt_builder import PromptBuilder


# =======================================
# PYFORGE WINDOW CLASS
# =======================================
class PyForgeWindow(QMainWindow):
    """
    PyForge GUI (Tabbed IDE Layout)

    Tabs:
    - Topic / Corrections (large topic + corrections editors)
    - Raw LLM Output (read-only)
    - Extracted Code (append-only LLM/Deep Analysis output)
    - Master Code (primary editable workspace; open/save target)
    - Deep Analysis Log (read-only event log)

    Global controls:
    - Generate
    - Re-run with Corrections
    - Deep Analysis
    - Save File
    - Open File
    - Forge → Pending
    - Clear (full reset)
    """

    # --------------
    # Initialize
    # --------------
    def __init__(self, llm_engine, storage_root: Path, parent=None):
        """
            -Initializes LLM Engine, Prompt Builder, Forge Writer
            -Sets GUI window
        """
        super().__init__(parent)
        # llm_engine / prompt_builder / forge_writer
        self.llm = llm_engine
        self.prompt_builder = PromptBuilder()
        self.forge_writer = ForgeWriter(storage_root)
        # window name and size
        self.setWindowTitle("PyForge — Python Script Forge")
        self.resize(1100, 800)

        self._last_topic = ""
        self._last_model_key = ""
        self.recent_block = ""
        self.memory_block = ""

        # build central QWidget
        central = QWidget()
        self.setCentralWidget(central)
        self.layout = QVBoxLayout(central)

        # build_ui / populate_models
        self._build_ui()
        self._populate_models()

    # -------------------------
    # UI
    # -------------------------
    def _build_ui(self):
        """
            -User Interface Layer with Model Selector, Tabs, and global controls
        """
        layout = self.layout

        # --- Model selector --- #
        model_row = QHBoxLayout()
        model_label = QLabel("Model:")
        self.model_select = QComboBox()
        model_row.addWidget(model_label)
        model_row.addWidget(self.model_select)
        layout.addLayout(model_row)

        # --- Tabs --- #
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs, stretch=4)

        # ---------------------------
        # Tab 1: Topic / Corrections
        # ---------------------------
        topic_widget = QWidget()
        topic_layout = QVBoxLayout(topic_widget)

        topic_label = QLabel("Forge Topic (can contain full code or instructions):")
        self.topic_edit = QTextEdit()
        self.topic_edit.setPlaceholderText(
            "Describe what you want to forge, refactor, or enhance.\n"
            "You can paste full code here as the 'topic' for the model."
        )

        corrections_label = QLabel("Corrections / Guidance for Next Run:")
        self.corrections_edit = QTextEdit()
        self.corrections_edit.setPlaceholderText(
            "Write corrections, refinements, or additional requirements here.\n"
            "These will be fed back into PyForge on the next run."
        )

        topic_layout.addWidget(topic_label)
        topic_layout.addWidget(self.topic_edit, stretch=3)
        topic_layout.addWidget(corrections_label)
        topic_layout.addWidget(self.corrections_edit, stretch=2)

        self.tabs.addTab(topic_widget, "Topic / Corrections")

        # -----------------------
        # Tab 2: Raw LLM Output
        # -----------------------
        self.llm_output_edit = QTextEdit()
        self.llm_output_edit.setReadOnly(True)
        self.llm_output_edit.setPlaceholderText("Raw LLM output will appear here.")
        self.tabs.addTab(self.llm_output_edit, "Raw LLM Output")

        # ------------------------
        # Tab 3: Extracted Code
        # ------------------------
        self.extracted_code_edit = QTextEdit()
        self.extracted_code_edit.setPlaceholderText(
            "Extracted code from LLM output and Deep Analysis will appear here.\n"
            "Use this as a staging area, then move curated code into 'Master Code'."
        )
        self.tabs.addTab(self.extracted_code_edit, "Extracted Code")

        # ---------------------
        # Tab 4: Master Code
        # ---------------------
        self.master_code_edit = QTextEdit()
        self.master_code_edit.setPlaceholderText(
            "This is your primary working area.\n"
            "- Opened files load here.\n"
            "- Save writes from here.\n"
            "- You can organize, comment, and refine code here."
        )
        self.tabs.addTab(self.master_code_edit, "Master Code")

        # --------------------------
        # Tab 5: Deep Analysis Log
        # --------------------------
        self.deep_log_edit = QTextEdit()
        self.deep_log_edit.setReadOnly(True)
        self.deep_log_edit.setPlaceholderText(
            "Deep Analysis v2 event log will appear here.\n"
            "Chunking, summarization, meta-summary, reconstruction, fallbacks, and errors."
        )
        self.tabs.addTab(self.deep_log_edit, "Deep Analysis Log")

        # --- Global Buttons --- #
        button_row = QHBoxLayout()
        # pending
        self.approve_button = QPushButton("Forge → Pending")
        self.approve_button.clicked.connect(self._on_approve_clicked)
        # re-run
        self.rerun_button = QPushButton("Re-run with Corrections")
        self.rerun_button.clicked.connect(self._on_rerun_clicked)
        # clear
        self.clear_button = QPushButton("Clear (New Session)")
        self.clear_button.clicked.connect(self._on_clear_clicked)
        # save file
        self.save_button = QPushButton("Save File")
        self.save_button.clicked.connect(self._on_save_clicked)
        # open file
        self.open_button = QPushButton("Open File")
        self.open_button.clicked.connect(self._on_open_clicked)
        # deep analysis
        self.deepanalyze_button = QPushButton("Deep Analysis")
        self.deepanalyze_button.clicked.connect(self._on_deep_analysis_clicked)
        # generate
        self.generate_button = QPushButton("Generate")
        self.generate_button.clicked.connect(self._on_generate_clicked)

        # button layout
        button_row.addWidget(self.generate_button)
        button_row.addWidget(self.rerun_button)
        button_row.addWidget(self.deepanalyze_button)
        button_row.addWidget(self.open_button)
        button_row.addWidget(self.save_button)
        button_row.addWidget(self.approve_button)
        button_row.addWidget(self.clear_button)
        layout.addLayout(button_row)

        # Status
        self.status_label = QLabel("Ready.")
        layout.addWidget(self.status_label)

    # -------------------------
    # Populate models
    # -------------------------
    def _populate_models(self):
        """
            -Populates the LLM List
        """
        models = self.llm.get_available_models()
        for m in models:
            key = m.get("key")
            if key:
                self.model_select.addItem(key)
        if self.model_select.count() > 0:
            self.model_select.setCurrentIndex(0)

# ==================================================================
# Events
# ==================================================================
    # ---------------------
    # On Generate Clicked
    # ---------------------
    def _on_generate_clicked(self):
        topic = self.topic_edit.toPlainText().strip()
        if not topic:
            QMessageBox.warning(self, "PyForge", "Please enter a forge topic (can be code or instructions).")
            return
        self._run_forge(topic, use_feedback=False)

    # ------------------
    # On Rerun Clicked
    # ------------------
    def _on_rerun_clicked(self):
        # Allow rerun even if no previous generate, as long as topic exists
        topic = self.topic_edit.toPlainText().strip()
        if not topic and not self._last_topic:
            QMessageBox.warning(self, "PyForge", "No topic available. Please enter a topic in the Topic tab.")
            return

        if topic:
            self._last_topic = topic

        feedback = self.corrections_edit.toPlainText().strip()
        if feedback:
            self.memory_block += f"\n[Correction at {datetime.utcnow().isoformat()}Z]\n{feedback}\n"
            self.memory_block = self._trim_block(self.memory_block, max_chars=6000)

        self._run_forge(self._last_topic, use_feedback=True)

    # ------------------
    # On Clear Clicked
    # ------------------
    def _on_clear_clicked(self):
        # Full reset: all tabs, all state
        self.topic_edit.clear()
        self.corrections_edit.clear()
        self.llm_output_edit.clear()
        self.extracted_code_edit.clear()
        self.master_code_edit.clear()
        self.deep_log_edit.clear()

        self.status_label.setText("Cleared. New session.")
        self._last_topic = ""
        self._last_model_key = ""
        self.recent_block = ""
        self.memory_block = ""

    # --------------------
    # On Approve Clicked
    # --------------------
    def _on_approve_clicked(self):
        # Forge from Master Code (curated, user-approved code)
        code = self.master_code_edit.toPlainText().strip()
        if not code:
            QMessageBox.warning(self, "PyForge", "No code in 'Master Code' to forge.")
            return

        topic = self._last_topic or self.topic_edit.toPlainText().strip()
        if not topic:
            QMessageBox.warning(self, "PyForge", "No topic associated with this code. Please enter a topic.")
            return

        filename = self._infer_filename(topic)
        ok = self.forge_writer.forge_script(filename, code, purpose=topic)
        if ok:
            self.status_label.setText(f"Script '{filename}' forged to pending.")
        else:
            self.status_label.setText("Forge failed: syntax error.")

    # ------------------
    # On Save Clicked
    # ------------------
    def _on_save_clicked(self):
        # Save from Master Code
        code = self.master_code_edit.toPlainText()
        if not code.strip():
            QMessageBox.warning(self, "PyForge", "No code in 'Master Code' to save.")
            return

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Python File",
            "",
            "Python Files (*.py)",
        )
        if filename:
            Path(filename).write_text(code, encoding="utf-8")
            self.status_label.setText(f"Saved to {filename}")

    # ------------------
    # On Open Clicked
    # ------------------
    def _on_open_clicked(self):
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Open Python File",
            "",
            "Python Files (*.py)",
        )
        if not filename:
            return

        try:
            file_code = Path(filename).read_text(encoding="utf-8")
        except Exception as e:
            QMessageBox.critical(self, "PyForge", f"Failed to open file: {e}")
            return

        # Load into Master Code (primary workspace)
        existing = self.master_code_edit.toPlainText().strip()
        if existing:
            merged = (
                existing
                + "\n\n# --- Imported File Begin: " + Path(filename).name + " ---\n\n"
                + file_code
                + "\n\n# --- Imported File End ---\n"
            )
        else:
            merged = file_code

        self.master_code_edit.setPlainText(merged)
        self.status_label.setText(f"Loaded into Master Code: {filename}")

    # --------------------------
    # On Deep Analysis Clicked
    # --------------------------
    def _on_deep_analysis_clicked(self):
        # Deep Analysis runs on Master Code (curated code)
        code = self.master_code_edit.toPlainText().strip()
        if not code:
            QMessageBox.warning(self, "PyForge", "No code in 'Master Code' to analyze.")
            return

        model_key = self.model_select.currentText().strip()
        engine = DeepAnalysisEngine(
            prompt_builder=self.prompt_builder,
            llm_engine=self.llm,
            model_fast=model_key,
            model_smart=model_key,
        )
        corrected = engine.run(code)

        # Populate Deep Analysis Log
        log_entries = engine.get_log()
        log_text = ""
        for entry in log_entries:
            stage = entry.get("stage", "unknown")
            msg = entry.get("message", "")
            extra = {k: v for k, v in entry.items() if k not in ("stage", "message")}
            log_text += f"[{stage}] {msg}\n"
            if extra:
                log_text += f"    {extra}\n"
        log_text = log_text.strip()
        self.deep_log_edit.setPlainText(log_text)

        if not corrected or not corrected.strip():
            QMessageBox.warning(self, "PyForge", "Deep Analysis produced no corrected code (fallback to original).")
            return

        # Append corrected code into Extracted Code tab
        existing = self.extracted_code_edit.toPlainText().strip()
        if existing:
            merged = (
                existing
                + "\n\n# --- Deep Analysis Correction Pass ---\n\n"
                + corrected
            )
        else:
            merged = (
                "# --- Deep Analysis Correction Pass ---\n\n"
                + corrected
            )

        self.extracted_code_edit.setPlainText(merged)
        self.status_label.setText("Deep Analysis complete. Review in 'Extracted Code' tab.")

    # -------------------------
    # Core forge logic
    # -------------------------
    def _run_forge(self, topic: str, use_feedback: bool):
        self.status_label.setText("Generating...")
        self.llm_output_edit.clear()

        model_key = self.model_select.currentText().strip()
        self._last_topic = topic
        self._last_model_key = model_key

        if use_feedback:
            full_topic = (
                f"{topic}\n\n"
                f"Previous code (Master Code):\n{self.master_code_edit.toPlainText()}\n\n"
                f"Corrections:\n{self.corrections_edit.toPlainText()}\n"
            )
        else:
            full_topic = topic

        prompt = self.prompt_builder.build_prompt(full_topic, model_key)
        raw = self.llm.generate(prompt, model_key=model_key)

        # GPT splitter if needed
        if "gpt" in model_key.lower():
            thoughts, content = self.prompt_builder.split_gpt_oss_output(raw)
            self.llm_output_edit.setPlainText(raw)
            code = self._extract_code(content)
        else:
            self.llm_output_edit.setPlainText(raw)
            code = self._extract_code(raw)

        if not code:
            self.status_label.setText("No valid code found in LLM output.")
            QMessageBox.warning(self, "PyForge", "No valid code found in LLM output.")
            return

        # Append into Extracted Code tab
        existing = self.extracted_code_edit.toPlainText().strip()
        if existing:
            merged = existing + "\n\n# --- Next Forge Pass ---\n\n" + code
        else:
            merged = code

        self.extracted_code_edit.setPlainText(merged)

        self.recent_block += (
            f"\n[Forge run at {datetime.utcnow().isoformat()}Z]\n"
            f"Topic:\n{topic}\n\n"
            f"Extracted Code:\n{code}\n"
        )
        self.recent_block = self._trim_block(self.recent_block, max_chars=4000)
        self.status_label.setText("Generation complete. Review in 'Extracted Code' tab, then curate into 'Master Code'.")

# ================================================================
# Helpers
# ================================================================
    # ------------------
    # Extract Code
    # ------------------
    def _extract_code(self, raw: str):
        if not raw:
            return None
        match = re.search(r"^(def |class )", raw, flags=re.MULTILINE)
        if not match:
            return raw.strip() if raw.strip().startswith("#") else None
        return raw[match.start():].strip()

    # ------------------
    # Infer Filename
    # ------------------
    def _infer_filename(self, topic: str) -> str:
        name = topic.lower()
        name = re.sub(r"[^a-z0-9]+", "_", name)
        name = name.strip("_")
        if not name:
            name = "forged_script"
        return f"{name}.py"

    # ------------------
    # Trim Block
    # ------------------
    def _trim_block(self, text: str, max_chars: int) -> str:
        if len(text) <= max_chars:
            return text
        return text[-max_chars:]

