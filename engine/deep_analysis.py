# engine/deep_analysis.py
# PyForge Deep Analysis Engine v2 (model-family agnostic)
# Created By: David Kistner (Unconditional Love) at GlyphicMind Solutions LLC.



#system imports
from typing import List, Optional, Dict, Any, Callable



# ==================================
# DEEP ANALYSIS ENGINE CLASS (v2)
# ==================================
class DeepAnalysisEngine:
    """
    Deep Analysis Engine v2

    Pipeline:
    - Chunk → Summarize (fast model or same model)
    - Meta-summarize (fast model or same model)
    - Final rewrite (smart model or same model)

    Enhancements in v2:
    - Internal event log (self.events)
    - Safe LLM calls with error handling
    - Empty-output protection
    - Optional debug flag
    - Graceful fallback to original code on failure

    Dependencies:
    - prompt_builder with:
        - build_prompt(topic, model_key)
    - llm_engine with:
        - generate(prompt, model_key)
    """

    # --------------
    # Initialize
    # --------------
    def __init__(
        self,
        prompt_builder,
        llm_engine,
        model_fast: str,
        model_smart: str,
        chunk_size: int = 4000,
        debug: bool = False,
    ):
        """
            -Initializes the prompt_builder, llm_engine, and declares chunk size
            -debug: if True, prints events to stdout as they occur
        """
        self.prompt_builder = prompt_builder
        self.llm = llm_engine
        self.model_fast = model_fast
        self.model_smart = model_smart
        self.chunk_size = chunk_size
        self.debug = debug

        # internal event log for inspection
        self.events: List[Dict[str, Any]] = []

    # -------------------------
    # Logging helper
    # -------------------------
    def _log(self, stage: str, message: str, extra: Optional[Dict[str, Any]] = None):
        entry = {
            "stage": stage,
            "message": message,
        }
        if extra:
            entry.update(extra)
        self.events.append(entry)
        if self.debug:
            print(f"[DeepAnalysis:{stage}] {message}")

    def get_log(self) -> List[Dict[str, Any]]:
        """
            -Returns the internal event log for this DeepAnalysisEngine instance
        """
        return list(self.events)

    # -------------------------
    # Safe LLM call
    # -------------------------
    def _safe_generate(self, prompt: str, model_key: str, stage: str) -> str:
        """
            -Wraps llm.generate with error handling and logging
        """
        try:
            raw = self.llm.generate(prompt, model_key=model_key)
            if not raw or not str(raw).strip():
                self._log(stage, "LLM returned empty output.", {"model_key": model_key})
                return ""
            return str(raw).strip()
        except FileNotFoundError as e:
            self._log(stage, "Model file not found.", {"model_key": model_key, "error": str(e)})
            return ""
        except Exception as e:
            self._log(stage, "LLM generate failed.", {"model_key": model_key, "error": str(e)})
            return ""

    # -------------------------
    # Chunk Code
    # -------------------------
    def chunk_code(self, code: str) -> List[str]:
        """
            -Chunks sections of a file up so the LLM can summarize the code
        """
        chunks = []
        while code:
            chunks.append(code[: self.chunk_size])
            code = code[self.chunk_size :]
        self._log("chunk_code", "Code chunked.", {"chunk_count": len(chunks)})
        return chunks

    # -------------------------
    # Summarize a single chunk
    # -------------------------
    def summarize_chunk(self, chunk: str, index: int, total: int) -> str:
        """
            -Summarizes a chunk/section of code
        """
        topic = f"Summarize this Python code for later reconstruction:\n\n{chunk}"
        prompt = self.prompt_builder.build_prompt(topic, self.model_fast)
        self._log("summarize_chunk", "Summarizing chunk.", {"index": index + 1, "total": total})
        raw = self._safe_generate(prompt, model_key=self.model_fast, stage="summarize_chunk")

        if not raw:
            # fallback: minimal synthetic summary
            fallback = f"[Summary unavailable for chunk {index + 1}/{total}]"
            self._log("summarize_chunk", "Using fallback summary.", {"index": index + 1})
            return fallback

        return raw

    # -------------------------
    # Merge summaries
    # -------------------------
    def merge_summaries(self, summaries: List[str]) -> str:
        """
            -Merges code summaries into a project summary
        """
        joined = "\n\n--- SUMMARY BREAK ---\n\n".join(summaries)
        topic = (
            "Merge these code summaries into a single, coherent project summary. "
            "Focus on architecture, responsibilities, and relationships:\n\n"
            f"{joined}"
        )
        prompt = self.prompt_builder.build_prompt(topic, self.model_fast)
        self._log("merge_summaries", "Merging summaries.", {"summary_count": len(summaries)})
        raw = self._safe_generate(prompt, model_key=self.model_fast, stage="merge_summaries")

        if not raw:
            # fallback: join summaries directly
            self._log("merge_summaries", "Using joined summaries as meta-summary fallback.")
            return joined

        return raw

    # -------------------------
    # Analyze From Summary
    # -------------------------
    def analyze_from_summary(self, meta_summary: str) -> str:
        """
            -Analyzes everything from summary built and reconstructs/refactors code
        """
        topic = (
            "Using ONLY this project summary, reconstruct or refactor the Python code. "
            "Preserve logic, improve structure, and ensure correctness:\n\n"
            f"{meta_summary}"
        )
        prompt = self.prompt_builder.build_prompt(topic, self.model_smart)
        self._log("analyze_from_summary", "Reconstructing code from meta-summary.")
        raw = self._safe_generate(prompt, model_key=self.model_smart, stage="analyze_from_summary")

        if not raw:
            self._log("analyze_from_summary", "Reconstruction failed or empty.")
            return ""

        return raw

    # -----------------
    # Run 
    # -----------------
    def run(self, code: str) -> str:
        """
            -Runs the full pipeline
            -Returns reconstructed/refactored code
            -If anything fails, returns the original code
        """
        self.events.clear()
        self._log("run_start", "Deep Analysis v2 run started.")

        if not code or not code.strip():
            self._log("run_abort", "Empty code input; returning original.")
            return code

        # 1. Chunk
        chunks = self.chunk_code(code)
        if not chunks:
            self._log("run_abort", "No chunks produced; returning original.")
            return code

        # 2. Summaries
        summaries: List[str] = []
        total = len(chunks)
        for idx, chunk in enumerate(chunks):
            summary = self.summarize_chunk(chunk, index=idx, total=total)
            summaries.append(summary)

        # 3. Meta-summary
        meta = self.merge_summaries(summaries)
        if not meta or not meta.strip():
            self._log("run_fallback", "Meta-summary empty; returning original code.")
            return code

        # 4. Reconstruction
        corrected = self.analyze_from_summary(meta)
        if not corrected or not corrected.strip():
            self._log("run_fallback", "Corrected code empty; returning original code.")
            return code

        self._log("run_complete", "Deep Analysis v2 completed successfully.")
        return corrected

