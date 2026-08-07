import cv2
import numpy as np


def preprocess_image(image_path):
    image = cv2.imread(image_path)

    if image is None:
        raise ValueError("Unable to read image.")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    gray = cv2.GaussianBlur(gray, (3, 3), 0)

    gray = cv2.equalizeHist(gray)

    return gray