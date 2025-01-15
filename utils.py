import mss
import numpy as np
from PIL import Image

def capture_screenshot(geometry):
    try:
        with mss.mss() as sct:
            monitor = {
                "top": geometry.top(),
                "left": geometry.left(),
                "width": geometry.width(),
                "height": geometry.height()
            }
            sct_img = sct.grab(monitor)
            return Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
    except Exception as e:
        print(f"Screenshot capture failed: {str(e)}")
        return Image.new('RGB', (geometry.width(), geometry.height()), color = 'red')