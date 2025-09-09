from logHandler import log
from urllib.parse import unquote
import os.path
import sys
sys.path.insert(0, os.path.dirname(__file__))
import urllib3
import urllib.request
from urllib.parse import urlencode
from threading import Timer
import os.path
import winsound
from cvconf import getConfig
from advanced_http_pool import AdvancedHttpPool
del sys.path[0]

BME_WAV = os.path.join(
    os.path.dirname(__file__),
    "bmai.wav"
)

_beep_thr = None
def beep_start(fthr=False):
    global _beep_thr
    if _beep_thr is None and fthr: return
    winsound.PlaySound(BME_WAV, True)
    _beep_thr= Timer(11, beep_start, (True,))
    _beep_thr.start()
    return True

def beep_stop():
    global _beep_thr
    winsound.PlaySound(None, True)
    try:
        if _beep_thr: _beep_thr.cancel()
    except RuntimeError as e:
        log.exception("cancel beep")
    _beep_thr=None
    return True


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
        "Content-Type": "application/x-www-form-urlencoded",
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

def smartsplit(t, s, e):
    """
    smartsplit(text, start_position, end_position)
    Splits a string into parts according to the number of characters.
    If there is a space between the start and end positions, split before a space, the word will not end in the middle.
    If there are no spaces in the specified range, divide as is, by the finite number of characters.
    """
    t = t.replace("\r\n", "\n").replace("\r", "\n")
    if e >= len(t):
        return [t]
    l = []
    tmp = ""
    i = 0
    for sim in t:
        i = i + 1
        tmp = tmp + sim
        if i < s:
            continue
        if i == e:
            l.append(tmp)
            tmp = ""
            i = 0
            continue
        if (i > s and i < e) and (
            sim == chr(160) or sim == chr(9) or sim == chr(10) or sim == chr(32)
        ):
            l.append(tmp)
            tmp = ""
            i = 0
            continue
    if len(tmp) > 0:
        l.append(tmp)
    return l
