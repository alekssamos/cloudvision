from logHandler import log
from urllib.parse import unquote
import urllib3
import urllib.request
from urllib.parse import urlencode
import os.path
from .cvconf import getConfig
from .utils import smartsplit
from .advanced_http_pool import AdvancedHttpPool


def get_prompt():
    briefOrDetailed, promptInput = (
        getConfig()["briefOrDetailed"],
        getConfig()["promptInput"],
    )
    prompts = [
        "Briefly describe what's in this image?",
        "Describe it in as much detail as possible what's in this image?",
        unquote(promptInput),
    ]
    return prompts[briefOrDetailed]


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


def translate_text(text, lang):
    texts = smartsplit(text, 530, 550)
    http = AdvancedHttpPool().Pool
    url = "https://translate.yandex.net/api/v1/tr.json/translate?srv=ios&ucid=9676696D-0B56-4F13-B4D5-4A3DA2A3344D&sid=1A5A10A952AB4A3B82533F44B87EE696&id=1A5A10A952AB4A3B82533F44B87EE696-0-0"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    textsresults = []
    for txt in texts:
        resp = None
        try:
            resp = http.request(
                method="POST",
                url=url,
                headers=headers,
                body=urlencode({"text": txt, "lang": lang}),
            ).json()
            textsresults.append(resp["text"][0])
        except (urllib3.exceptions.HTTPError, KeyError, AttributeError, ValueError):
            log.exception(f"translate error: {resp}")
            textsresults.append(txt)
    return " ".join(textsresults)
