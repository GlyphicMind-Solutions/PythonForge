# engine/llm_engine.py
# PyForge LLM Engine (llama_cpp, multi-model via manifest.yaml)
# Created By: David Kistner (Unconditional Love) at GlyphicMind Solutions LLC.



#system imports
import os, yaml, sys
from llama_cpp import Llama
from pathlib import Path
from typing import Dict, Optional
from contextlib import contextmanager, redirect_stdout, redirect_stderr


# ---------------------
# Suppress model noise
# ---------------------
@contextmanager
def suppress_llama_io():
    """Silence llama.cpp stdout/stderr spam during model load."""
    with open(os.devnull, "w") as devnull:
        old_stdout, old_stderr = sys.stdout, sys.stderr
        try:
            with redirect_stdout(devnull), redirect_stderr(devnull):
                yield
        finally:
            sys.stdout, sys.stderr = old_stdout, old_stderr



# ============================
# LLM ENGINE CLASS
# ============================
class LLMEngine:
    """
    LLMEngine
    - Loads local .gguf models via llama_cpp
    - Uses models/manifest.yaml for configuration
    - Supports multiple models, selected by key
    """
    # ------------
    # Initialize
    # ------------
    def __init__(self, manifest_path: Path):
        self.manifest_path = Path(manifest_path)
        self.models_config: Dict[str, dict] = {}
        self.models: Dict[str, Llama] = {}
        self.default_key: Optional[str] = None

        self._load_manifest()

    # -------------------
    # Load Manifest
    # -------------------
    def _load_manifest(self):
        if not self.manifest_path.exists():
            raise FileNotFoundError(f"manifest.yaml not found at {self.manifest_path}")

        with open(self.manifest_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        self.models_config = data.get("models", {})
        if not self.models_config:
            raise ValueError("No models defined in manifest.yaml")

        # First model in manifest is default
        self.default_key = next(iter(self.models_config.keys()))

    # ----------------------
    # Get available models
    # ----------------------
    def get_available_models(self):
        """
        Returns a list of dicts: [{key, path, n_ctx, template}, ...]
        """
        out = []
        for key, cfg in self.models_config.items():
            out.append(
                {
                    "key": key,
                    "path": cfg.get("path"),
                    "n_ctx": cfg.get("n_ctx", 32768),
                    "template": cfg.get("template", "llama"),
                }
            )
        return out

    # -------------------
    # Load model
    # -------------------
    def load_model(self, key: Optional[str] = None) -> Llama:
        """
        Load (or return cached) model by key.
        If key is None, use default.
        """
        if key is None:
            key = self.default_key

        if key in self.models:
            return self.models[key]

        cfg = self.models_config.get(key)
        if not cfg:
            raise KeyError(f"Model key '{key}' not found in manifest.yaml")

        path = cfg.get("path")
        if not path:
            raise ValueError(f"Model '{key}' missing 'path' in manifest.yaml")

        model_path = Path(path)
        if not model_path.exists():
            raise FileNotFoundError(f"Model file not found: {model_path}")

        n_ctx = int(cfg.get("n_ctx", 32768))

        # Silence llama.cpp noise during model load
        with suppress_llama_io():
            llm = Llama(
                model_path=str(model_path),
                n_ctx=n_ctx,
                n_threads=os.cpu_count() or 4,
            )

        self.models[key] = llm
        return llm

    # -------------------
    # Generate
    # -------------------
    def generate(self, prompt: str, model_key: Optional[str] = None, max_tokens: int = 2048) -> str:
        """
        Generate text from the selected model.
        """
        llm = self.load_model(model_key)

        out = llm(
            prompt,
            max_tokens=max_tokens,
            stop=["FIN~"],
            echo=False,
        )

        # llama_cpp returns a dict with 'choices'
        text = out["choices"][0]["text"]
        return text

