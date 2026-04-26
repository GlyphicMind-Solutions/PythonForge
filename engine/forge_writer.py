# engine/forge_writer.py
# PyForge File Writer
# Created By: David Kistner (Unconditional Love) at GlyphicMind Solutions LLC.



#system imports
import json
from pathlib import Path
from datetime import datetime



# ===========================================
# FORGE WRITER CLASS
# ===========================================
class ForgeWriter:
    """
    ForgeWriter
    - Writes Python files into storage/pending
    - Can also save arbitrary files into storage/saved
    - Logs actions into storage/logs/forge.log
    """
    # --------------
    # Initialize
    # --------------
    def __init__(self, storage_root: Path):
        """
            -initialization of storage, logs
        """
        self.storage_root = Path(storage_root)
        self.pending_dir = self.storage_root / "pending"
        self.saved_dir = self.storage_root / "saved"
        self.logs_dir = self.storage_root / "logs"
        self.log_path = self.logs_dir / "forge.log"

        self.pending_dir.mkdir(parents=True, exist_ok=True)
        self.saved_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

    # -------------------------
    # Inject Brand Tag
    # -------------------------
    def _inject_brand_tag(self, code: str) -> str:
        """
            -Injects GlyphicMind Solutions Brand into file
        """
        lines = code.splitlines()
        if len(lines) >= 3:
            lines.insert(2, "#--- Created with GlyphicMind Solutions: PythonForge ---#")
        else:
            while len(lines) < 2:
                lines.append("")
            lines.append("#--- Created with GlyphicMind Solutions: PythonForge ---#")
        return "\n".join(lines)

    # -------------------------
    # Forge script
    # -------------------------
    def forge_script(self, filename: str, code: str, purpose: str = "") -> bool:
        """
            -Forges script and sends it to the pending path
        """
        if not filename.endswith(".py"):
            filename += ".py"

        path = self.pending_dir / filename

        # Inject brand tag BEFORE writing
        code = self._inject_brand_tag(code)

        try:
            compile(code, filename, "exec")
        except SyntaxError as e:
            print(f"⚠️ Syntax error in generated code: {e}")
            return False

        path.write_text(code, encoding="utf-8")
        self._log_event("forge_pending", {"filename": filename, "purpose": purpose, "path": str(path)})
        print(f"🛠️ Script forged (pending): {path}")
        return True

    # -------------------------
    # Save script directly
    # -------------------------
    def save_script(self, filename: str, code: str) -> bool:
        """
            -Saves the script/file
        """
        if not filename.endswith(".py"):
            filename += ".py"

        path = self.saved_dir / filename

        # Inject brand tag BEFORE writing
        code = self._inject_brand_tag(code)

        try:
            compile(code, filename, "exec")
        except SyntaxError as e:
            print(f"⚠️ Syntax error in code: {e}")
            return False

        path.write_text(code, encoding="utf-8")
        self._log_event("save_script", {"filename": filename, "path": str(path)})
        print(f"💾 Script saved: {path}")
        return True

    # -------------------------
    # Log event
    # -------------------------
    def _log_event(self, event_type: str, details: dict):
        """
            -Logs the Event
        """
        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event_type": event_type,
            "details": details,
        }

        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            print(f"⚠️ Failed to write forge log: {e}")

