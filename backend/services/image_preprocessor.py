import cv2


def preprocess_image(image_path: str):
    """Load and enhance a weight-slip image for OCR.

    PaddleOCR expects a 3-channel image array. We enhance luminance for
    readability while preserving a BGR output shape (H, W, 3).
    """
    image = cv2.imread(str(image_path), cv2.IMREAD_COLOR)

    if image is None:
        raise ValueError(f"Unable to read image: {image_path}")

    # Improve local contrast without converting the final OCR input to 2D.
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l_channel, a_channel, b_channel = cv2.split(lab)

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced_l = clahe.apply(l_channel)

    enhanced_lab = cv2.merge((enhanced_l, a_channel, b_channel))
    enhanced = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)

    # Light denoising while preserving printed characters and barcode edges.
    enhanced = cv2.GaussianBlur(enhanced, (3, 3), 0)

    return enhanced
