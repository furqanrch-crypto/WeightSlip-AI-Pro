import os
from typing import Any

# PaddleOCR/PaddlePaddle 3.x can crash or become very slow on some CPU
# environments when oneDNN/MKLDNN and the document pre-processing modules
# are enabled. Disable those features for a lightweight weighbridge OCR path.
os.environ.setdefault("PADDLE_PDX_ENABLE_MKLDNN_BYDEFAULT", "0")
os.environ.setdefault("FLAGS_use_mkldnn", "0")

from paddleocr import PaddleOCR


ocr = PaddleOCR(
    lang="en",
    enable_mkldnn=False,
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
    text_detection_model_name="PP-OCRv5_mobile_det",
    text_recognition_model_name="PP-OCRv5_mobile_rec",
)


def _collect_text_and_scores(value: Any, texts: list[str], scores: list[float]) -> None:
    if value is None:
        return

    if isinstance(value, dict):
        rec_texts = value.get("rec_texts")
        rec_scores = value.get("rec_scores")

        if isinstance(rec_texts, list):
            texts.extend(str(item) for item in rec_texts if item)

        if isinstance(rec_scores, list):
            for score in rec_scores:
                try:
                    scores.append(float(score))
                except (TypeError, ValueError):
                    pass

        for child in value.values():
            _collect_text_and_scores(child, texts, scores)
        return

    if isinstance(value, (list, tuple)):
        if (
            len(value) == 2
            and isinstance(value[1], (list, tuple))
            and len(value[1]) >= 2
            and isinstance(value[1][0], str)
        ):
            texts.append(value[1][0])
            try:
                scores.append(float(value[1][1]))
            except (TypeError, ValueError):
                pass

        for child in value:
            _collect_text_and_scores(child, texts, scores)
        return

    json_value = getattr(value, "json", None)
    if json_value is not None:
        try:
            payload = json_value() if callable(json_value) else json_value
            _collect_text_and_scores(payload, texts, scores)
        except Exception:
            pass


def run_ocr(image) -> dict:
    """Run PaddleOCR and return a normalized result."""
    raw_result = ocr.predict(image)

    texts: list[str] = []
    scores: list[float] = []
    _collect_text_and_scores(raw_result, texts, scores)

    unique_texts = list(dict.fromkeys(text.strip() for text in texts if text.strip()))

    confidence = None
    if scores:
        confidence = round(sum(scores) / len(scores), 4)

    return {
        "text": "\n".join(unique_texts),
        "lines": unique_texts,
        "confidence": confidence,
        "raw": raw_result,
    }
