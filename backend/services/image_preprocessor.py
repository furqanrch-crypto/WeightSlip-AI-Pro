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
    """Return extra OCR variants for slips whose first OCR pass misses weights.

    These are intentionally used only as fallbacks because they cost extra OCR time.
    """
    image = _read_image(image_path)
    variants = []

    # Variant 1: original image. Sometimes preprocessing softens small printed digits.
    variants.append(image)

    # Variant 2: upscale and sharpen. Helpful for WhatsApp-compressed / distant photos.
    height, width = image.shape[:2]
    scale = 2.0 if width < 1800 else 1.5
    upscaled = cv2.resize(
        image,
        None,
        fx=scale,
        fy=scale,
        interpolation=cv2.INTER_CUBIC,
    )

    gaussian = cv2.GaussianBlur(upscaled, (0, 0), 1.2)
    sharpened = cv2.addWeighted(upscaled, 1.7, gaussian, -0.7, 0)
    variants.append(sharpened)

    # Variant 3: stronger local contrast, still kept as a 3-channel BGR image.
    gray = cv2.cvtColor(upscaled, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)
    contrast_bgr = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    variants.append(contrast_bgr)

    return variants
