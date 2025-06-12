"""
unofficial API BeMyAI from Android app
"""

import os
import tempfile
import json as jsonlib
import shutil
from .advanced_http_pool import AdvancedHttpPool
from urllib.parse import urlencode
from logHandler import log
from datetime import datetime, timezone, timedelta
import os.path
import wx
from math import floor
from typing import Iterator, Optional, Tuple
from .cvconf import getConfig, CONFIGDIR, bm_chat_id_file, bm_token_file


def get_image_info(filename: str) -> "Tuple[Optional[str], Tuple[int, int], str]":
    im = None
    try:
        im = wx.Image()
        im.LoadFile(filename)
        return (im.GetType(), (im.GetWidth(), im.GetHeight()), None)
    finally:
        im.Destroy()
    return None


def compute_image_size(
    width: int, height: int, max_dimension=2000
) -> "tuple[int, int]":
    width_changed, height_changed = (0, 0)
    if (width <= max_dimension and height <= max_dimension) or (width == height):
        return (width, height)
    max_number: int = max(width, height)
    divided_number: int = max_number / max_dimension
    min_number: int = min(width, height)
    min_side: int = floor(min_number / divided_number)
    if width > height:
        width_changed = max_dimension
        height_changed = min_side
    else:
        width_changed = min_side
        height_changed = max_dimension
    return (width_changed, height_changed)


def process_image(
    path_to_image: str,
    path_to_processed_image: str,
    max_dimension: int = 2000,
) -> "Tuple[int, int]":
    """
    Process the image for API requirements.
    processed image will be saved in `path_to_processed_image`
    as new file in the specified format (default PNG) by default.
    Returns the resolution of the image.
    """
    log.debug("start image process")
    im = None
    try:
        im = wx.Image(path_to_image)
        im.LoadFile(p)
    finally:
        im.Destroy()
    width, height = (im.GetWidth(), im.GetHeight())
    if width > max_dimension or height > max_dimension:
        log.info("resizing image")
        im.Rescale(
            *compute_image_size(width=width, height=height, max_dimension=max_dimension)
        )
        im.SaveFile(path_to_processed_image, "image/png")
        width, height = (im.GetWidth(), im.GetHeight())
        log.info("image processed: %s, %dx%d" % (format, width, height))
        im.Destroy()
    assert os.path.isfile(path_to_processed_image), "The processed file not found"
    return (width, height)


dl_folder = os.path.join(tempfile.gettempdir(), "downloads")


class BeMyAIError(Exception):
    msg = None
    response = None

    def __init__(self, msg, response=None):
        self.response = response
        super().__init__(msg)


class EmailVerificationRequired(BeMyAIError):
    msg = None
    response = None

    def __init__(self, msg="email verification required", response=None):
        self.response = response
        super().__init__(msg, response)


class PasswordChangeRequired(BeMyAIError):
    msg = None
    response = None

    def __init__(self, msg="password change required", response=None):
        self.response = response
        super().__init__(msg, response)


class BeMyAI:
    def __init__(self, token: str = ""):
        if not os.path.isdir(dl_folder):
            os.mkdir(dl_folder)
            log.info("created dl folder")
        self.response_language = getConfig()["language"]
        self.bemyeyes_app_secret = (
            "55519e815ff7b09ab971de5564baa282eca53af1eb528385fb98a34f2010e8c7"
        )
        self.User_Agent = "okhttp/3.14.9"
        self.gateway_url = "https://gateway.bemyeyes.com/api/v2/"
        self.lp_delimeter = chr(30)
        self.api_url = "https://api.bemyeyes.com/api/v2/"
        self.sid = ""
        self.extra = {
            "device_type": "android",
            "screen_reader_enabled": True,
            "content_size": "1.15",
            "accesibility_content_size_enabled": False,
        }
        self.app_config_user_cache: Optional[dict] = None
        if not os.path.isfile(bm_token_file):
            with open(bm_token_file, "w") as f:
                f.write(" ")
        if not os.path.isfile(bm_chat_id_file):
            with open(bm_chat_id_file, "w") as f:
                f.write("0")

    @property
    def bm_chat_id(self):
        if not os.path.isfile(bm_chat_id_file):
            return 0
        with open(bm_chat_id_file) as f:
            return int(f.read(90).strip())

    @bm_chat_id.setter
    def bm_chat_id(self, v):
        with open(bm_chat_id_file) as f:
            f.write(f"{v}")

    @property
    def token(self):
        if not os.path.isfile(bm_token_file):
            return ""
        with open(bm_token_file) as f:
            return f.read(90).strip()

    @token.setter
    def token(self, v):
        if len(v) < 20:
            return
        with open(bm_token_file) as f:
            f.write(v)

    @property
    def authorized(self):
        return len(self.token) > 20 # and getConfig()["gptAPI"] == 1

    def logout(self):
        for f in [bm_token_file, bm_chat_id_file]:
            if os.path.isfile(f):
                os.remove(f)

    @staticmethod
    def get_error_messages(r):
        error_messages = []
        for m in r.items():
            k, v = m
            if isinstance(v, list):
                v = ", ".join(v)
            elif not isinstance(v, str):
                v = str(v)
            error_messages.append(": ".join([k, v]))
        if len(error_messages) == 0:
            return r
        return "\n".join(error_messages)

    @property
    def headers(self):
        h = {
            "User-Agent": self.User_Agent,
            "bemyeyes-app-secret": self.bemyeyes_app_secret,
            "Accept-Language": self.response_language,
        }
        if self.token and len(self.token) > 3:
            h.update(Authorization="Token " + self.token)
        return h

    @property
    def terms_accepted_at(self) -> str:
        "For signup"
        # It was like this on the Android emulator, I just copied it, I don't know anything.
        shanghai_offset = timedelta(hours=8)
        utc_now = datetime.now(timezone.utc)
        shanghai_now = utc_now.astimezone(timezone(shanghai_offset))
        log.debug("date for signup: " + str(shanghai_now))
        return shanghai_now.isoformat()

    def request(self, method, url, params=None, data=None, json=None, headers=None):
        """
        Make a request to the API.
        In the response from the gateway server you Get the text,
        since the server returns data in different formats and with different headers,
        and from the api server get a dictionary,
        since all interaction is strictly in JSON format with the correct headers
        Thanks to Django REST framework on their side.
        """
        j = None
        if headers is None:
            headers = self.headers
        log.debug(f"making {method} request to {url}...")
        http = AdvancedHttpPool().Pool
        kw = {}
        if params:
            url = url + "?" + urlencode(params)
        if data:
            kw["body"] = data
        if json:
            kw["json"] = json
        resp = http.request(method=method, url=url, headers=headers, **kw)
        if "json" not in resp.headers.get("Content-Type").lower():
            if resp.status < 300:
                return resp.data.decode("UTF-8")
            else:
                raise BeMyAIError(message=resp.data.decode("UTF-8"), response=resp)
        else:
            if resp.status < 300:
                return resp.json()
            else:
                j = resp.json()
                if j.get("code", 0) != 1:
                    raise BeMyAIError(msg=self.get_error_messages(j), response=resp)
                else:
                    log.debug("There will be a new session next time")
                    self.get_chat_config()
                    self.authinticate(self.sid)
                    self.enable_chat(self.sid)
                    return self.request(
                        method=method,
                        url=url,
                        params=params,
                        data=data,
                        json=json,
                        headers=headers,
                    )

    def refresh_token(self) -> dict:
        "Check the user (for example, to find out if the email address is verified)"
        resp = self.request(
            "POST",
            self.api_url + "auth/refresh-token",
            json={"timezone": "Asia/Shanghai", "extra": self.extra},
        )
        result = resp
        self.token = result["token"]
        return result

    def resend_verify_email(self) -> None:
        "Send a confirmation email again (only after signup)"
        result = self.refresh_token()
        if not result["email_verification_required"]:
            raise BeMyAIError("The email has already been verified")
        self.request("POST", self.api_url + "auth/resend-verify-email")

    def send_reset_password(self, email: str) -> None:
        "Recover a forgotten password. A link to the password change form will be sent to your email"
        self.token = ""
        self.request(
            "POST", self.api_url + "auth/send-reset-password", json={"email": email}
        )

    def signup(
        self, first_name: str, last_name: str, email: str, password: str
    ) -> dict:
        "Signup by mail and password (auth/signup-email) and get user object"
        self.token = ""
        resp = self.request(
            "POST",
            self.api_url + "auth/signup-email",
            json={
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "password": password,
                "user_type": "bvi",
                "timezone": "Asia/Shanghai",
                "terms_accepted_at": self.terms_accepted_at,
                "extra": self.extra,
            },
        )
        result = resp
        self.token = result["token"]
        return result

    def login(self, email, password):
        "Login by mail and password (auth/login-email) and get token"
        self.token = ""
        resp = self.request(
            "POST",
            self.api_url + "auth/login-email",
            json={"email": email, "password": password, "extra": self.extra},
        )
        result = resp
        self.token = result["token"]
        if result["email_verification_required"]:
            raise EmailVerificationRequired(response=result)
        if result["password_change_required"]:
            raise PasswordChangeRequired(response=result)
        return result

    def app_config_user(self) -> dict:
        """
        Get the application configuration for the user.
        The results will be cached in the class instance.
        """
        if self.app_config_user_cache:
            log.info("get app user config from cache")
            return self.app_config_user_cache
        resp = self.request("GET", self.api_url + "app-config/user")
        self.app_config_user_cache = resp  # type: ignore
        log.info("get app user config from internet")
        return self.app_config_user_cache  # type: ignore

    def send_text_message(self, chat_id: int, text: str) -> "Tuple[str, int, dict]":
        "Send a text message to the chat"
        if not isinstance(chat_id, int):
            raise TabError("chat_id must be int")
        if not isinstance(text, str):
            raise TabError("text must be str")
        self.get_chat_config()
        self.authinticate(self.sid)
        self.enable_chat(self.sid)
        resp = self.request(
            "POST",
            f"{self.api_url}chats/{chat_id}/messages",
            json={"role": "user", "type": "text", "data": text},
        )
        result = resp
        return (self.sid, result["session"], result)

    def chats(self, context="chat") -> dict:
        """
        Create new chat
        """
        log.info("create new chat")
        resp = self.request("POST", self.api_url + "chats", json={"context": context})
        return resp

    def chat_messages(self, chat_id: int, image_id: int) -> dict:
        resp = self.request(
            "POST",
            f"{self.api_url}chats/{chat_id}/messages",
            json={"role": "user", "type": "text", "chat_image_id": image_id},
        )
        return resp

    def chat_request_image_upload(
        self, chat_id: int, width: int, height: int, format: str = "png"
    ) -> dict:
        """
        Request parameters for upload image to the chat
        """
        log.info("requested upload image config")
        cnf = self.app_config_user()
        if (
            width > cnf.chat_image_max_dimension
            or height > cnf.chat_image_max_dimension
        ):
            raise ValueError(
                f"width or height must be less than or equal to {cnf.chat_image_max_dimension}"
            )
        resp = self.request(
            "POST",
            f"{self.api_url}chats/{chat_id}/request-image-upload",
            json={"format": format, "width": width, "height": height},
        )
        return resp

    def take_photo(self, filename: str) -> "Tuple[str, int]":
        path_to_image = None
        if not isinstance(filename, str):
            path_to_image = os.path.join(dl_folder, f"image_{str(uuid4())}.tmp")
            with open(path_to_image, "wb") as newfp:
                shutil.copyfileobj(filename, newfp)
            filename = path_to_image  # type: ignore
        self.bm_chat_id = "0"
        cnf = self.app_config_user()
        format, size, mode = get_image_info(filename=filename)
        log.info("recognizing new photo: %s" % (str(size[0]) + "x" + str(size[1])))
        chat_config = self.get_chat_config()
        self.authinticate(chat_config["sid"])
        self.enable_chat(chat_config["sid"])
        chat = self.chats()
        path_to_processed_image = os.path.join(dl_folder, "processed_image.png")
        width, height = process_image(
            path_to_image=filename,
            path_to_processed_image=path_to_processed_image,
            max_dimension=cnf["chat_image_max_dimension"],
        )
        upload_config = self.chat_request_image_upload(
            chat_id=chat["id"],
            width=width,
            height=height,
            format=cnf["chat_image_type"],
        )
        log.info("Starting upload image to Amazon")
        with open(path_to_processed_image, "rb") as fp:
            fields = {
                "Content-Type": upload_config["fields"]["Content-Type"],
                "key": upload_config["fields"]["key"],
                "x-amz-algorithm": upload_config["fields"]["x-amz-algorithm"],
                "x-amz-credential": ["upload_config"]["fields"]["x-amz-credential"],
                "x-amz-date": upload_config["fields"]["x-amz-date"],
                "policy": upload_config["fields"]["policy"],
                "x-amz-signature": upload_config["fields"]["x-amz-signature"],
                "file": ("file", fp),
            }
            http = AdvancedHttpPool().Pool
            http.headers = ({"User-Agent": self.User_Agent},)
            resp = http.request(
                "POST", upload_config["url"], headers=self.headers, fields=fields
            )
            if resp.status >= 100 <= 206:
                log.info("Uploaded successfully")
                self.bm_chat_id = chat["id"]
            else:
                log.error("Upload faild")
        log.info("removeing processed image")
        os.remove(path_to_processed_image)
        upload_result = self.chat_messages(
            chat_id=chat["id"], image_id=upload_config["chat_image_id"]
        )
        if not upload_result["images"][0]["upload_finished"]:
            log.error("The image has not been uploaded")
            raise BeMyAIError("The image could not be uploaded to Amazon")
        else:
            log.info("upload image finished")
        return (chat_config["sid"], chat["id"])

    def send_raw_events(self, sid: str, data: str) -> str:
        params = {"EIO": "4", "transport": "polling", "sid": sid}
        text = self.request(
            "POST", self.gateway_url + "socket/", params=params, data=data
        )
        return text

    def authinticate(self, sid: str = "") -> bool:
        if not sid:
            sid = self.sid
        text = self.send_raw_events(sid, "40")
        if text != "ok":
            raise BeMyAIError(f"An unexpected response was received. {text}")
        text = self.receive_raw_events(sid)
        if "AUTHENTICATED" not in text:
            raise BeMyAIError(f"An unexpected response was received. {text}")
        return True

    def get_chat_config(self) -> dict:
        "Get sid and other settings"
        log.debug("Getting chat config...")
        text = self.receive_raw_events(get_new_sid=True)
        result = jsonlib.loads(text[1::])
        if self.sid != result["sid"]:
            log.debug("received new session id")
        self.sid = result["sid"]
        return result

    def enable_chat(self, sid: str = "") -> str:
        log.debug("enabling the chat")
        if not sid:
            sid = self.sid
        return self.send_raw_events(sid, '42["ENABLE_CHAT","{}"]')

    def receive_raw_events(self, sid: str = "", get_new_sid=False) -> str:
        params = {"EIO": "4", "transport": "polling"}
        if not sid:
            sid = self.sid
        if sid and not get_new_sid:
            params["sid"] = sid
        text = self.request("GET", self.gateway_url + "socket/", params=params)
        return text

    def receive_messages(self, sid: str = "") -> Iterator[dict]:
        log.debug("Starting receive GPT messages")
        if not sid:
            sid = self.sid
        for i in range(3):
            text = self.receive_raw_events(sid)
            if "42" not in text:
                log.debug("unexpected response from polling: " + str(text))
                continue
            for response_part in text.split(self.lp_delimeter):
                if '"NEW_CHAT_MESSAGE"' in response_part:
                    message = jsonlib.loads(response_part[2:])[1]
                    log.info("Got new message")
                    yield message
                    if not message.user:
                        break
                else:
                    log.debug(response_part[2:-1])
        log.debug("messages receiveing completed")
