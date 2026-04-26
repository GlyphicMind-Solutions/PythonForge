# pyforge.py
# PyForge Standalone Entrypoint
# Created By: David Kistner (Unconditional Love) at GlyphicMind Solutions LLC.



#system imports
import sys
from pathlib import Path
from PyQt5.QtWidgets import QApplication

#folder imports
from engine.llm_engine import LLMEngine
from gui.pyforge_window import PyForgeWindow



# -----------------
# Main
# -----------------
def main():
    """
        -Loads models, storage, and initializes the LLM engine
    """
    root = Path(__file__).resolve().parent
    models_manifest = root / "models" / "manifest.yaml"
    storage_root = root / "storage"

    llm_engine = LLMEngine(models_manifest)

    app = QApplication(sys.argv)
    window = PyForgeWindow(llm_engine=llm_engine, storage_root=storage_root)
    window.show()
    sys.exit(app.exec_())

# ---------------------------
# if name = main for window
# ---------------------------
if __name__ == "__main__":
    main()

