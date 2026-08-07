from paddleocr import PaddleOCR

ocr = PaddleOCR(
    use_angle_cls=True,
    lang="en",
)


def run_ocr(image):
    result = ocr.ocr(image)

    return result