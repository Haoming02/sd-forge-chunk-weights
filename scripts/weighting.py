from functools import wraps
from typing import Callable

import gradio as gr
from modules import scripts
from modules.infotext_utils import PasteField
from modules.processing import StableDiffusionProcessing, StableDiffusionProcessingTxt2Img
from modules.script_callbacks import on_app_started, on_script_unloaded
from modules.sd_hijack_clip import FrozenCLIPEmbedderWithCustomWordsBase
from modules.ui_components import InputAccordion

from scripts.cw_logger import logger

IS_NEGATIVE_PROMPT: bool = False
WEIGHTS: list[float] = []
INDEX: int = 0

original_process_texts: Callable = None
original_process_tokens: Callable = None


class ChunkWeight(scripts.Script):
    _error_logged: bool

    def title(self):
        return "Chunk Weight"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def ui(self, is_img2img):
        with InputAccordion(False, label=self.title()) as enable:
            weights = gr.Textbox(
                label="Weighting",
                placeholder="1.0, 2.0, 0.5",
                value="",
                lines=1,
                max_lines=1,
            )

            weights.do_not_save_to_config = True

        self.infotext_fields = [PasteField(weights, "Chunk Weights")]
        return [enable, weights]

    def setup(self, p: "StableDiffusionProcessing", enable: bool, weights: str):
        WEIGHTS.clear()

        if not enable:
            return

        for v in weights.split(","):
            try:
                WEIGHTS.append(float(v))
            except ValueError:
                logger.error(f'Failed to parse "{v.strip()}" as number...')
                continue

        p.extra_generation_params["Chunk Weights"] = ", ".join(str(v) for v in WEIGHTS)

        if (weights := len(WEIGHTS)) != (chunks := len(p.prompt.split("BREAK"))):
            logger.warning(f'Mismatch number of Weights ({weights}) and BREAK-Chunks ({chunks})\n(Explicitly separating the chunks using the "BREAK" keyword is recommended)\n')

        p.cached_c = [None, None]
        p.cached_uc = [None, None]
        p.cached_hr_c = [None, None]
        p.cached_hr_uc = [None, None]

        ChunkWeight._error_logged = False

    def postprocess(self, *args):
        enable: bool = args[2]
        if not enable:
            return

        StableDiffusionProcessing.cached_c = [None, None]
        StableDiffusionProcessing.cached_uc = [None, None]
        StableDiffusionProcessingTxt2Img.cached_hr_c = [None, None]
        StableDiffusionProcessingTxt2Img.cached_hr_uc = [None, None]
        logger.debug("Cond Cache Reset")


def patch(*args, **kwargs):
    global original_process_texts
    original_process_texts = FrozenCLIPEmbedderWithCustomWordsBase.process_texts

    global original_process_tokens
    original_process_tokens = FrozenCLIPEmbedderWithCustomWordsBase.process_tokens

    @wraps(original_process_texts)
    def patched_process_texts(self: "FrozenCLIPEmbedderWithCustomWordsBase", texts: list[str]):
        global IS_NEGATIVE_PROMPT

        if hasattr(texts, "is_negative_prompt"):
            IS_NEGATIVE_PROMPT = texts.is_negative_prompt
        else:
            IS_NEGATIVE_PROMPT = None

        global INDEX
        INDEX = 0

        return original_process_texts(self, texts)

    @wraps(original_process_tokens)
    def patched_process_tokens(self: "FrozenCLIPEmbedderWithCustomWordsBase", remade_batch_tokens: list, batch_multipliers: list):
        global INDEX

        if not WEIGHTS:
            return original_process_tokens(self, remade_batch_tokens, batch_multipliers)

        if INDEX >= 0 and IS_NEGATIVE_PROMPT is False:
            batches: int = len(batch_multipliers)
            context: int = len(batch_multipliers[0])  # 77

            if len(WEIGHTS) == INDEX:
                INDEX = -1
                if not ChunkWeight._error_logged:
                    logger.error("Insufficient number of Weights!\n(Default to 1.0 for the rest of the chunks)\n")
                    ChunkWeight._error_logged = True

            else:
                logger.debug(f"Applied {WEIGHTS[INDEX]}x to Chunk {INDEX}")
                for b in range(batches):
                    for i in range(context):
                        batch_multipliers[b][i] *= WEIGHTS[INDEX]

                INDEX += 1

        return original_process_tokens(self, remade_batch_tokens, batch_multipliers)

    FrozenCLIPEmbedderWithCustomWordsBase.process_texts = patched_process_texts
    FrozenCLIPEmbedderWithCustomWordsBase.process_tokens = patched_process_tokens


def unpatch(*args, **kwargs):
    FrozenCLIPEmbedderWithCustomWordsBase.process_texts = original_process_texts
    FrozenCLIPEmbedderWithCustomWordsBase.process_tokens = original_process_tokens


on_app_started(patch)
on_script_unloaded(unpatch)
