from .cvlangnames import LANGNAMES
import base64
import json
import urllib.request
from .cvhelpers import get_image_content_from_image


class PBAPIError(Exception):
    pass


def piccyBot(image: any, lang: str = "en"):
    langname = LANGNAMES.get(lang, "English")
    if len(lang) > 3:
        langname = lang.lower().capitalize()
    image_content = get_image_content_from_image(image)

    url = "https://sparklingapps.com/piccybotapi/index.php/chat"

    # Подготавливаем данные для запроса
    chat_data = {
        "model": "openai41",
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
                        "text": f"What's in this image?, Explain this only in {langname} language.",
                        "type": "text",
                    },
                ],
            }
        ],
        "sub": False,
        "token": 40,
        "exp": True,
    }

    json_data = json.dumps(chat_data).encode("utf-8")

    # Настраиваем запрос
    request = urllib.request.Request(url, data=json_data, method="POST")
    request.add_header("Content-Type", "application/json")
    request.add_header(
        "User-Agent", "PiccyBot/2.17.6 CFNetwork/1498.700.2 Darwin/23.6.0"
    )

    # Отправляем запрос и получаем ответ
    with urllib.request.urlopen(request, timeout=59) as response:
        response_data = response.read()

    data = json.loads(response_data)

    # Обработка ответа
    txt = data.get("Text", "")
    if txt == "":
        raise PBAPIError(response_data)
    txt = txt.replace("*", "")

    return txt
