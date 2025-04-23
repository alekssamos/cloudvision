from uuid import uuid4
import re
import json
import base64
import urllib.request
from .cvhelpers import get_image_content_from_image

class ChromeOCRError(Exception): pass
def chromeOCREngine(image: any, lang: str = "en"):
    image_content = get_image_content_from_image(image)
    image_id = str(uuid4()).replace("-", "")
    BASE_URL = "https://ckintersect-pa.googleapis.com/v1/intersect/"
    request_data = {
        "imageRequests": [
            {
                "engineParameters": [
                    {"ocrParameters": {}},
                    {"descriptionParameters": {"preferredLanguages": [lang]}},
                ],
                "imageBytes": base64.b64encode(image_content).decode(),
                "imageId": image_id,
            }
        ]
    }
    json_data = json.dumps(request_data).encode("utf-8")
    request = urllib.request.Request(BASE_URL + "pixels", data=json_data, method="POST")
    request.add_header("X-Goog-Api-Key", "AIzaSyBOti4mM-6x9WDnZIjIeyEU21OpBXqWBgw")
    request.add_header(
        "User-Agent",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36",
    )
    request.add_header("Content-Type", "application/json")
    request.add_header("Sec-Fetch-Site", "none")
    request.add_header("Sec-Fetch-Mode", "no-cors")
    request.add_header(
        "Accept-Language", "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,it;q=0.6"
    )
    content = urllib.request.urlopen(request, timeout=9).read()
    resp = json.loads(content)
    try:
        if "ocrRegions" not in resp["results"][0]["engineResults"][0]["ocrEngine"]:
            return ""
        lines = resp["results"][0]["engineResults"][0]["ocrEngine"]["ocrRegions"]
    except (KeyError, IndexError):
        raise ChromeOCRError(content)

    text = ""
    for line in lines:
        for word in line["words"]:
            text = text + word["detectedText"] + " "
        text = text + "\n"

    text = re.sub(r' ([?><-_:!@№#$%^&*])', r'\1', text)
    text = re.sub(r' ([./!?,])', r'\1', text)
    return text
