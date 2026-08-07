import cv2


def _read_image(image_path: str):
    image = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f"Unable to read image: {image_path}")
    return image


def preprocess_image(image_path: str):
    """Primary balanced preprocessing for normal weight slips."""
    image = _read_image(image_path)

    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l_channel, a_channel, b_channel = cv2.split(lab)

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced_l = clahe.apply(l_channel)

    enhanced_lab = cv2.merge((enhanced_l, a_channel, b_channel))
    enhanced = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
    enhanced = cv2.GaussianBlur(enhanced, (3, 3), 0)

    return enhanced


def fallback_preprocess_images(image_path: str):
    """Return one lightweight fallback OCR variant.

    Older builds created multiple large/upscaled images. On Codespaces that could
    make one difficult slip spend several minutes in OCR retry and block every
    queued slip behind it. Keep retries bounded: one same-resolution sharpened,
    high-contrast variant only.
    """
    image = _read_image(image_path)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    contrasted = clahe.apply(gray)
    contrast_bgr = cv2.cvtColor(contrasted, cv2.COLOR_GRAY2BGR)

    blurred = cv2.GaussianBlur(contrast_bgr, (0, 0), 1.0)
    sharpened = cv2.addWeighted(contrast_bgr, 1.6, blurred, -0.6, 0)

    return [sharpened]
