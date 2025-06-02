import os, os.path
import sys
import globalVars
import languageHandler
import config

try:
    from cBytesIO import BytesIO  ## 2
    from cStringIO import StringIO  ## 2
except ImportError:
    from io import BytesIO  ## 3
    from io import StringIO  ## 3

## for Windows XP
if sys.version_info.major == 2:
    sys.path.insert(0, ".")
    import myconfigobj as configobj

    del sys.path[0]
else:
    import configobj

try:
    import validate
except ImportError:
    import configobj.validate as validate

__all__ = [
    "getConfig",
    "CONFIGDIR",
    "bm_chat_id_file",
    "bm_token_file",
    "getDefaultLanguage",
    "supportedLocales",
]

CONFIGDIR = globalVars.appArgs.configPath
bm_token_file = os.path.join(CONFIGDIR, "bm_token.txt")
bm_chat_id_file = os.path.join(CONFIGDIR, "bm_chat_id.txt")

supportedLocales = [
    "am",
    "ar",
    "an",
    "af_ZA",
    "bg",
    "ca",
    "cs",
    "da",
    "de",
    "fa",
    "el",
    "en",
    "es",
    "fi",
    "fr",
    "hr",
    "hu",
    "hi",
    "id",
    "it",
    "ja",
    "ko",
    "lt",
    "lv",
    "my",
    "nl",
    "pl",
    "pt",
    "ro",
    "ru",
    "sk",
    "sl",
    "sr",
    "sv",
    "sq",
    "tg",
    "tr",
    "uk",
    "uz",
    "vi",
    "zh_CN",
    "zh_TW",
]


def getDefaultLanguage():
    lang = languageHandler.getLanguage()

    if lang not in supportedLocales and "_" in lang:
        lang = lang.split("_")[0]

    if lang not in supportedLocales:
        lang = "en"

    return lang


_config = None
configspec = StringIO(
    """
prefer_navigator=boolean(default=False)
sound=boolean(default=False)
textonly=boolean(default=True)
imageonly=boolean(default=True)
gptAPI=integer(default=0)
briefOrDetailed=integer(default=0)
promptInput=string(default="")
qronly=boolean(default=False)
trtext=boolean(default=False)
language=string(default={defaultLanguage})
""".format(defaultLanguage=getDefaultLanguage())
)


def getConfig():
    global _config
    if not _config:
        path = os.path.join(config.getUserDefaultConfigPath(), "CloudVision.ini")
        _config = configobj.ConfigObj(path, configspec=configspec)
        val = validate.Validator()
        _config.validate(val)
    return _config
