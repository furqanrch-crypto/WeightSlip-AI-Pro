from typing import Any

from paddleocr import PaddleOCR


ocr = PaddleOCR(
    use_angle_cls=True,
    lang="en",
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
        # PaddleOCR 2.x commonly returns [box, (text, confidence)].
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

    # PaddleOCR 3.x result objects may expose a json attribute/property.
    json_value = getattr(value, "json", None)
    if json_value is not None:
        try:
            payload = json_value() if callable(json_value) else json_value
            _collect_text_and_scores(payload, texts, scores)
        except Exception:
            pass


def run_ocr(image) -> dict:
    """Run PaddleOCR and return a normalized result."""
    raw_result = ocr.ocr(image)

    texts: list[str] = []
    scores: list[float] = []
    _collect_text_and_scores(raw_result, texts, scores)

    # Preserve reading order while removing exact repeated strings.
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
