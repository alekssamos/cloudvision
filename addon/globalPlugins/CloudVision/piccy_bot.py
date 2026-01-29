from threading import Lock
from datetime import datetime, timedelta
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


MODELS_PATH = os.path.join(os.path.dirname(__file__), "pb_models.json")
MODELS_URL = "https://sparklingapps.com/piccybotapi/index.php/chat"
_locker = Lock()
lastImageFilePath = os.path.join(tempfile.gettempdir(), "cv_last_image")


def _update_models():
    need_update = False
    if not os.path.isfile(MODELS_PATH):
        need_update = True
    else:
        file_mod_time = datetime.fromtimestamp(os.path.getmtime(MODELS_PATH))
        current_time = datetime.now()
        time_diff = current_time - file_mod_time
        need_update = time_diff > timedelta(hours=6)
    if not need_update:
        return
    http = AdvancedHttpPool().Pool
    http.headers = {
        "Content-Type": "application/json",
        "User-Agent": "PiccyBot/2.42.12 CFNetwork/1498.700.2 Darwin/23.6.0",
    }
    response = http.request("GET", MODELS_URL)
    data = response.json()
    if (
        isinstance(data, dict)
        and "models" in data
        and isinstance(data["models"], list)
        and len(data["models"]) > 0
        and "key" in data["models"][0]
        and "value" in data["models"][0]
    ):
        with open(MODELS_PATH, "w", encoding="UTF-8") as fp:
            json.dump(data, fp)


def update_models()->bool:
    try:
        _update_models()
        return True
    except (KeyError, ValueError, IndexError, TypeError):
        return False
    return False

def get_models() -> list:
    data = {}
    with _locker:
        update_models()
    with open(MODELS_PATH, "r", encoding="UTF-8") as f:
        data = json.load(f)
    if not data:
        return []
    else:
        return data["models"]


def get_model(key_or_value) -> list:
    "returns [key, value, index]"
    models = get_models()
    i = -1
    for model in models:
        i += 1
        if model["key"] == key_or_value or model["value"] == key_or_value:
            return [model["key"], model["value"], i]
    return []


def models_keys() -> list:
    models = get_models()
    return [m["key"] for m in models]


def models_values() -> list:
    models = get_models()
    return [m["value"] for m in models]


def piccyBot(
    image: any,
    lang: str = "en",
    prompt: str = "Describe it in as much detail as possible what's in this image?",
    pbMODEL: str = "openai",
):
    model = get_model(pbMODEL)[1]
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
        "model": model,
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
