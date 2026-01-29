from .cvlangnames import LANGNAMES
import base64
import json
import tempfile
import urllib3
import os.path
from .advanced_http_pool import AdvancedHttpPool
from .cvhelpers import get_image_content_from_image


class PBAPIError(Exception):
    pass


lastImageFilePath = os.path.join(tempfile.gettempdir(), "cv_last_image")


def piccyBot(
    image: any,
    lang: str = "en",
    prompt: str = "Describe it in as much detail as possible what's in this image?",
):
    langname = LANGNAMES.get(lang, "English")
    if len(lang) > 3:
        langname = lang.lower().capitalize()
    if image:
        image_content = get_image_content_from_image(image)
    elif os.path.isfile(lastImageFilePath) and os.path.getsize(lastImageFilePath) > 50:
        with open(lastImageFilePath, "rb") as f:
            image_content = f.read()

    url = "https://sparklingapps.com/piccybotapi/index.php/chat"

    chat_data = {
        "model": "openai5chat",
        "user_message": [
            {
                "role": "user",
                "content": [
                    {
                        "image_url": {
                            "url": "data:image/jpeg;base64,"
                            + base64.b64encode(image_content).decode()
                        },
                        "type": "image_url",
                    },
                    {
                        "text": f"{prompt}, Explain this only in {langname} language.",
                        "type": "text",
                    },
                ],
            }
        ],
        "sub": True,
        "token": 40,
        "exp": True,
    }

    http = AdvancedHttpPool().Pool
    http.headers = {
        "Content-Type": "application/json",
        "User-Agent": "PiccyBot/2.42.12 CFNetwork/1498.700.2 Darwin/23.6.0",
    }
    response = http.request("POST", url, json=chat_data)
    data = response.json()

    txt = data.get("Text", "")
    if txt == "":
        raise PBAPIError(response_data)
    txt = txt.replace("*", "")

    with open(lastImageFilePath, "wb") as fp:
        fp.write(image_content)
    return txt
