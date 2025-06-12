from functools import wraps
from typing import Callable

import gradio as gr

from modules import scripts
from modules.script_callbacks import on_app_started, on_script_unloaded
from modules.sd_hijack_clip import FrozenCLIPEmbedderWithCustomWordsBase
from modules.ui_components import InputAccordion

IS_NEGATIVE_PROMPT: bool = False
WEIGHTS: list[float] = []
INDEX: int = 0

original_process_texts: Callable = None
original_process_tokens: Callable = None


class ChunkWeight(scripts.Script):
    def title(self):
        return "Chunk Weight"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def ui(self, is_img2img):
        with InputAccordion(False, label=self.title()) as enable:
            weights = gr.Textbox(
                value="",
                placeholder="1.0, 2.0, 0.5",
                lines=1,
                max_lines=1,
                label="Weighting",
            )

        return [enable, weights]

    def setup(self, p, enable: bool, weights: str):
        global WEIGHTS
        WEIGHTS.clear()

        if not enable:
            return

        for v in weights.split(","):
            try:
                WEIGHTS.append(float(v))
            except ValueError:
                continue


def patch(*args, **kwargs):
    global original_process_texts
    original_process_texts = FrozenCLIPEmbedderWithCustomWordsBase.process_texts

    global original_process_tokens
    original_process_tokens = FrozenCLIPEmbedderWithCustomWordsBase.process_tokens

    @wraps(original_process_texts)
    def patched_process_texts(self, texts: list[str]):
        global IS_NEGATIVE_PROMPT
        if hasattr(texts, "is_negative_prompt"):
            IS_NEGATIVE_PROMPT = texts.is_negative_prompt
        else:
            IS_NEGATIVE_PROMPT = None

        global INDEX
        INDEX = 0

        return original_process_texts(self, texts)

    @wraps(original_process_tokens)
    def patched_process_tokens(
        self: "FrozenCLIPEmbedderWithCustomWordsBase",
        remade_batch_tokens: list,
        batch_multipliers: list,
    ):
        global INDEX

        if IS_NEGATIVE_PROMPT is False:
            assert len(batch_multipliers) == 1
            assert len(batch_multipliers[0]) == 77

            if len(WEIGHTS) > INDEX:
                print(INDEX, WEIGHTS[INDEX])
                for i in range(77):
                    batch_multipliers[0][i] *= WEIGHTS[INDEX]

            INDEX += 1

        return original_process_tokens(self, remade_batch_tokens, batch_multipliers)

    FrozenCLIPEmbedderWithCustomWordsBase.process_texts = patched_process_texts
    FrozenCLIPEmbedderWithCustomWordsBase.process_tokens = patched_process_tokens


def unpatch(*args, **kwargs):
    FrozenCLIPEmbedderWithCustomWordsBase.process_texts = original_process_texts
    FrozenCLIPEmbedderWithCustomWordsBase.process_tokens = original_process_tokens


on_app_started(patch)
on_script_unloaded(unpatch)
