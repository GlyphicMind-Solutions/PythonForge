# prompt/prompt_builder.py
# PyForge Prompt Builder (model-family aware)
# Created By: David Kistner (Unconditional Love) at GlyphicMind Solutions LLC.



#system imports
import re
from typing import Tuple



# ==========================
# PROMPT BUILDER CLASS
# ==========================
class PromptBuilder:
    """
    PromptBuilder
    - Builds model-family-aware prompts for PyForge
    - Families: gpt, mistral, qwen, deepseek, phi, llama (default)
    """

    # ---------------
    # Build Prompt
    # ---------------
    def build_prompt(self, topic: str, model_key: str) -> str:
        """
            -Builds the Prompt based on family model
        """
        family = self._infer_family(model_key)

        if family == "gpt":
            return self._build_gpt_prompt(topic)
        if family == "mistral":
            return self._build_mistral_prompt(topic)
        if family == "qwen":
            return self._build_qwen_prompt(topic)
        if family == "deepseek":
            return self._build_deepseek_prompt(topic)
        if family == "phi":
            return self._build_phi_prompt(topic)

        # default → llama-style
        return self._build_llama_prompt(topic)

    # ---------------
    # Infer Family
    # ---------------
    def _infer_family(self, model_key: str) -> str:
        """
            -Detects a Model Family
        """
        k = model_key.lower()

        if "gpt" in k:
            return "gpt"
        if "mistral" in k:
            return "mistral"
        if "qwen" in k:
            return "qwen"
        if "deepseek" in k:
            return "deepseek"
        if "phi" in k:
            return "phi"
        if "llama" in k or "hermes" in k:
            return "llama"

        return "llama"

# ==================================== #
# Template Section                     #
# ==================================== #
    # ---------------
    # GPT template
    # ---------------
    def _build_gpt_prompt(self, topic: str) -> str:
        """
            -Template for GPT Models
        """
        return (
            "<|start|>system<|message|>\n"
            "\"-You are an Agent using PyForge. Generate Python code only. No markdown. End with FIN~\"\n"
            "\"-Rules-\"\n"
            "\"1. Provide your reasoning ONLY inside the assistant analysis channel:\\n\"\n"
            "\"   <|start|>assistant<|channel|>analysis<|message|>\\n\"\n"
            "\"   Thinking:\\n\"\n"
            "\"   ...\\n\"\n"
            "\"   <|end|>\\n\"\n\n"
            "\"2. Provide your final answer ONLY inside the assistant final channel:\\n\"\n"
            "\"   <|start|>assistant<|channel|>final<|message|>\\n\"\n"
            "\"   Answer:\\n\"\n"
            "\"   ...\\n\"\n"
            "\"   <|end|>\\n\"\n"
            "<|end|>\n\n"
            "<|start|>user<|message|>\n"
            f"{topic}\n"
            "<|end|>\n\n"
            "<|start|>assistant<|channel|>analysis<|message|>\n"
            "Thinking:\n"
            "...\n"
            "<|start|>assistant<|channel|>final<|message|>\n"
            "Answer:\n"
        )

    # ---------------
    # Mistral template
    # ---------------
    def _build_mistral_prompt(self, topic: str) -> str:
        """
            -Template for Mistral Models
        """
        return (
            "<|im_start|>system\n"
            "[INST]\n\n"
            "You are an Agent using PyForge. Generate Python code only. No markdown. End with FIN~.\n"
            "[/INST]\n"
            "<|im_end|>\n\n"
            "<|im_start|>user\n"
            f"{topic}\n"
            "<|im_end|>\n\n"
            "<|im_start|>assistant\n"
        )

    # ---------------
    # Qwen template
    # ---------------
    def _build_qwen_prompt(self, topic: str) -> str:
        """
            -Template for Qwen Models
        """
        return (
            "<|im_start|>system\n"
            "Generate Python code only. No markdown. End with FIN~.\n"
            "<|im_end|>\n\n"
            "<|im_start|>user\n"
            f"{topic}\n"
            "<|im_end|>\n\n"
            "<|im_start|>assistant\n"
        )

    # ---------------
    # DeepSeek template
    # ---------------
    def _build_deepseek_prompt(self, topic: str) -> str:
        """
            -Template for DeepSeek Models
        """
        return (
            "<|begin_of_text|><|system|>\n"
            "Generate Python code only. No markdown. End with FIN~.\n"
            "<|end|>\n\n"
            "<|user|>\n"
            f"{topic}\n"
            "<|end|>\n\n"
            "<|assistant|>\n"
        )

    # ---------------
    # Phi template
    # ---------------
    def _build_phi_prompt(self, topic: str) -> str:
        """
            -Template for Phi Models
        """
        return (
            "### System\n"
            "Generate Python code only. No markdown. End with FIN~.\n\n"
            "### User\n"
            f"{topic}\n\n"
            "### Assistant\n"
        )

    # ---------------
    # Llama / default template
    # ---------------
    def _build_llama_prompt(self, topic: str) -> str:
        """
            -Template for Llama Models
        """
        return (
            "<|im_start|>system\n"
            "You are PyForge. Generate Python code only. No markdown. End with FIN~.\n"
            "<|im_end|>\n\n"
            "<|im_start|>user\n"
            f"{topic}\n"
            "<|im_end|>\n\n"
            "<|im_start|>assistant\n"
        )

# ==================================== #
# Helpers Section                      #
# ==================================== #
    # ------------------------
    # GPT output splitter
    # ------------------------
    @staticmethod
    def split_gpt_oss_output(text: str) -> Tuple[str, str]:
        """
            -Removes GPT's "thinking" and outputs only the "Answer:"
        """

        t = text.replace("\r", "")
        match = re.search(r"\bAnswer:\b", t, re.IGNORECASE)

        if not match:
            return "", t.strip()

        idx = match.start()
        thoughts = t[:idx].replace("Thinking:", "").strip()
        content = t[idx:].replace("Answer:", "").strip()
        return thoughts, content

