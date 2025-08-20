from threading import Lock
import os
import os.path
import json
import urllib3
import globalVars
from urllib3.util import make_headers
from urllib3.contrib.socks import SOCKSProxyManager


class AdvancedHttpPool:
    _lock = Lock()
    _proxy_protocols = ("http", "https", "socks4", "socks5")
    _data_fields = (
        "proxyProtocol",
        "proxyAuth",
        "proxyLogin",
        "proxyPassword",
        "proxyEnabled",
        "proxyHost",
        "proxyPort",
    )
    # proxyProtocol: str = ""
    # proxyEnabled: bool = False
    # proxyAuth: bool = False
    # proxyHost: str = ""
    # proxyPort: int = 0
    # proxyLogin: str = ""
    # proxyPassword: str = ""

    def __init__(self):
        self._proxyData = {
            "proxyProtocol": self._proxy_protocols[0],
            "proxyAuth": False,
            "proxyEnabled": False,
            "proxyHost": "",
            "proxyPort": 0,
            "proxyLogin": "",
            "proxyPassword": "",
        }
        self.proxyfile = os.path.join(globalVars.appArgs.configPath, "proxydata.json")

        self._loadSettings()

    def __getattr__(self, item):
        if item in self._data_fields and item in self._proxyData.keys():
            return self._proxyData[item]
        if hasattr(self.Pool, item):
            return getattr(self.Pool, item)
        super().__getattribute__(item)
        # raise AttributeError(
        # f"'{self.__class__.__name__}' object has no attribute '{item}'"
        # )

    def __setattr__(self, key, value):
        if key == "proxyProtocol":
            value = value.strip(":/ \r\n\t").lower()
            if value not in self._proxy_protocols:
                raise ValueError("incorrect protocol")
        if key == "proxyPort":
            value = int(value)
            if value < 1 or value > 65535:
                raise ValueError("incorrect port")
        if key in ("proxyEnabled", "proxyAuth") and not isinstance(value, bool):
            raise ValueError(f"incorrect value. {key} must be True or False")
        if key in self._data_fields:
            if isinstance(value, str):
                value = value.strip()
            self._proxyData[key] = value
        else:
            super().__setattr__(key, value)

    def _loadSettings(self):
        with self._lock:
            if not os.path.isfile(self.proxyfile):
                return
            try:
                with open(self.proxyfile, "r", encoding="UTF-8") as f:
                    self._proxyData = json.load(f)
            except (ValueError, json.JSONDecodeError):
                return

    def save(self):
        with self._lock:
            with open(self.proxyfile, "w", encoding="UTF-8") as fp:
                json.dump(self._proxyData, fp)
        return True

    @property
    def proxyURL(self) -> str:
        if not self.proxyEnabled:
            return ""
        url = ""
        if self.proxyProtocol == "socks5":
            url = f"{self.proxyProtocol}h://"
        else:
            url = f"{self.proxyProtocol}://"
        if self.proxyAuth:
            url = url + f"{self.proxyLogin}:{self.proxyPassword}@"
        url = url + f"{self.proxyHost}:{self.proxyPort}/"
        return url

    @property
    def Pool(self):
        proxy_headers = None
        if not self.proxyEnabled:
            return urllib3.PoolManager()
        if self.proxyProtocol in ("http", "https"):
            if self.proxyAuth:
                proxy_headers = make_headers(
                    proxy_basic_auth=f"{self.proxyLogin}:{self.proxyPassword}"
                )
            return urllib3.ProxyManager(self.proxyURL, proxy_headers=proxy_headers)
        if self.proxyProtocol in ("socks4", "socks5"):
            return SOCKSProxyManager(self.proxyURL)
        raise ValueError("incorrect proxy configuration")
