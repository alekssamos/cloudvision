import urllib.request
import os.path


def get_image_content_from_image(image: any):
    image_content = b""
    try:
        if isinstance(image, str) and image.startswith("http") and "://" in image:
            request = urllib.request.Request(image, method="GET")
            request.add_header(
                "User-Agent",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0",
            )
            with urllib.request.urlopen(request) as response:
                image_content = response.read()
        elif isinstance(image, bytearray) or isinstance(image, bytes):
            image_content = bytes(image)
        elif isinstance(image, str) and os.path.isfile(image):
            with open(image, "rb") as f:
                image_content = f.read()
        elif hasattr(image, "read"):
            image_content = f.read()
        if image_content == "":
            raise ValueError("Couldn't read the image")
    except Exception:
        return False

    return image_content
