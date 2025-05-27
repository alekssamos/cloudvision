# CloudVision
# Author: alekssamos
# Copyright 2020, released under GPL.
# Add-on that gets description of current navigator object based on visual features,
# the computer vision heavy computations are made in the cloud.
# VISIONBOT.RU
CloudVisionVersion = "3.3"
import sys
import json
import time
import os
import os.path
import controlTypes
import tempfile
import subprocess

sys.path.insert(0, os.path.dirname(__file__))
import socks
import sockshandler
import advanced_http_pool
from advanced_http_pool import AdvancedHttpPool

del sys.path[0]
from ctypes import windll
from .bm import account_gui as bmgui
from glob import glob
from xml.parsers import expat
from collections import namedtuple

try:
    from cBytesIO import BytesIO  ## 2
    from cStringIO import StringIO  ## 2
except ImportError:
    from io import BytesIO  ## 3
    from io import StringIO  ## 3

from .cvconf import getConfig, supportedLocales
from .bemyai import BeMyAI, BeMyAIError
import tones
import wx
import config
import globalVars
import globalPluginHandler
import gui
import scriptHandler
import queueHandler
from threading import Timer
import speech
import api
from logHandler import log
import languageHandler
import addonHandler
import versionInfo

is_new_nvda = versionInfo.version_year >= 2021 and versionInfo.version_major >= 1
if is_new_nvda:
    from comtypes.client import CreateObject as COMCreate
    from .MyOCREnhance import totalCommanderHelper
    import winUser
    import ctypes

addonHandler.initTranslation()

import textInfos.offsets
import ui

if is_new_nvda:
    from globalCommands import SCRCAT_OBJECTNAVIGATION
from time import sleep
from math import sqrt

import base64

if sys.version_info.major == 2:
    import urllib as ur, urllib as up
elif sys.version_info.major == 3:
    import urllib.request as ur, urllib.parse as up

## for Windows XP
import socket

socket.setdefaulttimeout(60)

filePath = ""
fileExtension = ""
fileName = ""
suppFiles = ["png", "jpg", "gif", "tiff", "tif", "jpeg", "webp"]


def get_image_from_clipboard():
    # Open the clipboard
    if wx.TheClipboard.Open():
        # Check if the clipboard has a bitmap
        if wx.TheClipboard.IsSupported(wx.DataFormat(wx.DF_BITMAP)):
            # Create a bitmap data object
            bmp_data = wx.BitmapDataObject()
            wx.TheClipboard.GetData(bmp_data)  # Get the bitmap data
            # Convert wx.BitmapDataObject to wx.Bitmap
            bitmap = bmp_data.GetBitmap()
            wx.TheClipboard.Close()
            return bitmap
        else:
            log.error("The clipboard does not contain a bitmap.")
            wx.TheClipboard.Close()
            queueHandler.queueFunction(
                queueHandler.eventQueue,
                ui.message,
                _("There is no image in the clipboard"),
            )
            return None
    else:
        log.error("Could not open the clipboard.")
        return None


def find_desktop_obj():
    a = api.getForegroundObject()
    for _i in range(4):
        _a = a.parent
        if _a is None:
            break
        a = _a
    return a


def say_message_thr(type):
    queueHandler.queueFunction(queueHandler.eventQueue, speech.cancelSpeech)
    if type == 1:
        queueHandler.queueFunction(
            queueHandler.eventQueue, ui.message, _("Analyzing selected file")
        )
    elif type == 2:
        # Translators: Reported when screen curtain is enabled.
        queueHandler.queueFunction(
            queueHandler.eventQueue,
            ui.message,
            _("Please disable screen curtain before using CloudVision add-on."),
        )
    elif type == 3:
        queueHandler.queueFunction(
            queueHandler.eventQueue, ui.message, _("Analyzing navigator object")
        )
    elif type == 4:
        queueHandler.queueFunction(
            queueHandler.eventQueue, ui.message, _("Analyzing full screen")
        )
    elif type == 5:
        queueHandler.queueFunction(
            queueHandler.eventQueue, ui.message, _("Analyzing image from clipboard")
        )
    else:
        log.error(f"1, 2, 3, 4 or 5. You passed {type}")


def say_message(type):
    _tmr = Timer(
        0.6,
        say_message_thr,
        [
            type,
        ],
    )
    _tmr.start()
    queueHandler.queueFunction(queueHandler.eventQueue, speech.cancelSpeech)


class SettingsDialog(gui.SettingsDialog):
    title = _("CloudVision Settings")

    def makeSettings(self, sizer):
        self.SetName("cvsettings")
        settingsSizerHelper = gui.guiHelper.BoxSizerHelper(self, sizer=sizer)

        self.ahp = AdvancedHttpPool()
        self.ahp._loadSettings()

        self.prefer_navigator = wx.CheckBox(
            self, label=_("Pre&fer a navigator object instead of a file")
        )
        self.prefer_navigator.SetValue(getConfig()["prefer_navigator"])
        settingsSizerHelper.addItem(self.prefer_navigator)

        self.sound = wx.CheckBox(self, label=_("&Play sound during recognition"))
        self.sound.SetValue(getConfig()["sound"])
        settingsSizerHelper.addItem(self.sound)

        self.textonly = wx.CheckBox(self, label=_("Recognize &text"))
        self.textonly.SetValue(getConfig()["textonly"])
        settingsSizerHelper.addItem(self.textonly)

        self.imageonly = wx.CheckBox(self, label=_("Recognize &images"))
        self.imageonly.SetValue(getConfig()["imageonly"])
        settingsSizerHelper.addItem(self.imageonly)

        self.bm = wx.CheckBox(self, label="&Be My AI")
        self.bm.SetValue(getConfig()["bm"])
        self.bm.Disable()
        settingsSizerHelper.addItem(self.bm)

        self.qronly = wx.CheckBox(self, label=_("Read &QR / bar code"))
        self.qronly.SetValue(getConfig()["qronly"])
        settingsSizerHelper.addItem(self.qronly)

        self.trtext = wx.CheckBox(self, label=_("Translate text"))
        self.trtext.SetValue(getConfig()["trtext"])
        settingsSizerHelper.addItem(self.trtext)

        langs = sorted(supportedLocales)
        curlang = getConfig()["language"]
        try:
            select = langs.index(curlang)
        except ValueError:
            select = langs.index("en")
        choices = [
            languageHandler.getLanguageDescription(locale) or locale
            for locale in supportedLocales
        ]
        self.language = settingsSizerHelper.addLabeledControl(
            _(
                "Select image description language, other languages than english are more prone to translation errors"
            ),
            wx.Choice,
            choices=choices,
        )
        self.language.SetSelection(select)
        self.manage_account_button = wx.Button(
            self, label=_("Manage Be My Eyes account")
        )
        self.manage_account_button.Bind(wx.EVT_BUTTON, self.on_manage_account_button)
        self.manage_account_button.Disable()
        settingsSizerHelper.addItem(self.manage_account_button)

        self.open_visionbot_ru_button = wx.Button(
            self, label=_("Open site") + " VISIONBOT.RU"
        )
        self.open_visionbot_ru_button.Bind(
            wx.EVT_BUTTON, self.on_open_visionbot_ru_button
        )
        settingsSizerHelper.addItem(self.open_visionbot_ru_button)
        self.useProxy = wx.CheckBox(self, label=_("&Use proxy server"))
        self.useProxy.SetValue(self.ahp.proxyEnabled)
        self.useProxy.Bind(wx.EVT_CHECKBOX, self.onUseProxy)
        settingsSizerHelper.addItem(self.useProxy)

        self.proxy_protocol = settingsSizerHelper.addLabeledControl(
            _("Proxy &protocol:"), wx.Choice, choices=self.ahp._proxy_protocols
        )

        self.proxy_protocol.SetStringSelection(self.ahp.proxyProtocol)

        self.proxy_host = settingsSizerHelper.addLabeledControl(
            _("Proxy &host:"), wx.TextCtrl, value=self.ahp.proxyHost
        )
        self.proxy_port = settingsSizerHelper.addLabeledControl(
            _("Proxy p&ort:"), wx.SpinCtrl, value=str(self.ahp.proxyPort)
        )
        self.proxy_port.SetRange(1, 65535)
        self.proxy_username = settingsSizerHelper.addLabeledControl(
            _("Proxy &login:"), wx.TextCtrl, value=self.ahp.proxyLogin
        )
        self.proxy_password = settingsSizerHelper.addLabeledControl(
            _("Proxy p&assword:"),
            wx.TextCtrl,
            value=self.ahp.proxyPassword,
            style=wx.TE_PASSWORD,
        )

    def postInit(self):
        self.sound.SetFocus()
        self.onUseProxy(None)

    def onUseProxy(self, event):
        items = frozenset(
            [
                self.proxy_host,
                self.proxy_password,
                self.proxy_port,
                self.proxy_protocol,
                self.proxy_username,
            ]
        )
        if self.useProxy.Value:
            for elem in items:
                elem.Enable()
        else:
            for elem in items:
                elem.Disable()

    def on_manage_account_button(self, event):
        if event:
            event.Skip()
        self.manage_account_button.Disable()
        queueHandler.queueFunction(
            queueHandler.eventQueue, ui.message, _("Please wait...")
        )
        account_dialog = bmgui.MainDialog(
            self.FindWindowByName("cvsettings"),
        )
        account_dialog.ShowModal()
        self.manage_account_button.Enable()

    def on_open_visionbot_ru_button(self, event):
        event.Skip()
        import webbrowser as wb

        wb.open("https://visionbot.ru/?fromaddon=1&addonversion=" + CloudVisionVersion)

    def onOk(self, event):
        event.Skip()
        self.ahp.proxyEnabled = self.useProxy.IsChecked()
        self.ahp.proxyAuth = (
            self.proxy_username.GetValue().strip() != ""
            and self.proxy_password.GetValue().strip() != ""
        )
        self.ahp.proxyProtocol = self.proxy_protocol.GetStringSelection() or "http"
        self.ahp.proxyLogin = self.proxy_username.GetValue().strip()
        self.ahp.proxyPassword = self.proxy_password.GetValue().strip()
        self.ahp.proxyHost = self.proxy_host.GetValue().strip()
        self.ahp.proxyPort = int(self.proxy_port.GetValue())
        self.ahp.save()
        if (
            not self.textonly.IsChecked()
            and not self.imageonly.IsChecked()
            and not self.bm.IsChecked()
        ):
            self.textonly.SetValue(True)
            self.imageonly.SetValue(True)
        getConfig()["prefer_navigator"] = self.prefer_navigator.IsChecked()
        getConfig()["sound"] = self.sound.IsChecked()
        getConfig()["textonly"] = self.textonly.IsChecked()
        getConfig()["imageonly"] = self.imageonly.IsChecked()
        getConfig()["trtext"] = self.trtext.IsChecked()
        getConfig()["bm"] = self.bm.IsChecked()
        getConfig()["qronly"] = self.qronly.IsChecked()
        getConfig()["language"] = supportedLocales[self.language.GetSelection()]

        try:
            getConfig().write()
        except IOError:
            log.error("Error writing CloudVision configuration", exc_info=True)
            gui.messageBox(
                e.strerror, _("Error saving settings"), style=wx.OK | wx.ICON_ERROR
            )

        super(SettingsDialog, self).onOk(event)


def cloudvision_request(img_str, lang="en", target="all", bm=0, qr=0, translate=0):
    from .chrome_ocr_engine import chromeOCREngine
    from .piccy_bot import piccyBot
    from .cvhelpers import get_image_content_from_image

    result = {}
    if target in ["all", "image"]:
        if not BeMyAI().authorized:
            result["description"] = piccyBot(img_str, lang)
        else:
            img_content = get_image_content_from_image(img_str)
            img_file = os.path.join(os.path.dirname(__file__), "tempimage.png")
            with open(img_file) as fp:
                fp.write(img_content)
            bm = BeMyAI()
            sid, chat_id = bm.take_photo(img_content)
            os.remove(img_file)
            img_content = None
            res = ""
            for x in range(3):
                if res != "":
                    break
                for message in bm.receive_messages(sid):
                    if message.get("user"):
                        continue
                    res = message["data"]
                    break
            result["description"] = res
    if target in ["all", "text"]:
        result["text"] = chromeOCREngine(img_str, lang)
    return result


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
    def __init__(self):
        super(globalPluginHandler.GlobalPlugin, self).__init__()
        self.CloudVisionSettingsItem = gui.mainFrame.sysTrayIcon.preferencesMenu.Append(
            wx.ID_ANY, _("Cloud Vision settings...")
        )
        popupSettingsDialog = getattr(
            gui.mainFrame, "popupSettingsDialog", "_popupSettingsDialog"
        )
        gui.mainFrame.sysTrayIcon.Bind(
            wx.EVT_MENU,
            lambda evt: popupSettingsDialog(SettingsDialog),
            self.CloudVisionSettingsItem,
        )

    def terminate(self):
        globalVars.cvask = None
        globalVars.cvaskargs = None
        try:
            gui.mainFrame.sysTrayIcon.preferencesMenu.RemoveItem(
                self.CloudVisionSettingsItem
            )
        except:
            pass

    tmr = None
    last_resp = ""
    isVirtual = False
    isWorking = False

    def on_ask_bm(self, evt):
        if not self.last_resp:
            queueHandler.queueFunction(
                queueHandler.eventQueue,
                ui.message,
                _("There have been no recognitions yet"),
            )
            return
        if not getattr(globalVars, "cvask", None):
            gui.mainFrame.prePopup()
            d = bmgui.AskFrame(gui.mainFrame)
            d.Show()
            gui.mainFrame.postPopup()
            globalVars.cvask = d
        else:
            d = globalVars.cvask
            d.ask_panel.question_input.SetValue("")
            d.Show()
        d.postInit()

    def getFilePath(
        self,
    ):  # For this method thanks to some nvda addon developers ( code snippets and suggestion)
        fg = api.getForegroundObject()
        focus = api.getFocusObject()
        if not is_new_nvda:
            mod = focus.appModule
            if mod.appName.lower() in ["explorer", "totalcmd"]:
                queueHandler.queueFunction(
                    queueHandler.eventQueue,
                    ui.message,
                    _(
                        "To recognize files under the cursor without opening Update NVDA version to 2021.1 or higher"
                    ),
                )
            return False
        if getConfig()["prefer_navigator"]:
            return False
        global filePath
        global fileExtension
        global fileName

        # We check if we are in the Total Commander
        tcmd = totalCommanderHelper.TotalCommanderHelper()
        if tcmd.is_valid():
            filePath = tcmd.currentFileWithPath()
            if not filePath:
                return False
        elif fg.windowClassName == "Explorer++":
            fileName = focus.name
            addressbar = fg.children[1].children[2].children[0].children[0]
            ctypes.windll.user32.SendMessageW(addressbar.windowHandle, 256, 27, 0)
            ctypes.windll.user32.SendMessageW(addressbar.windowHandle, 257, 27, 65539)
            filePath = glob(os.path.join(addressbar.value, focus.name) + "*")[0]
            fileName = os.path.basename(filePath)
            log.info(f"filePath={filePath}; fileName={fileName}")
        else:
            # We check if we are in the Windows Explorer.
            if (
                fg.role == api.controlTypes.Role.PANE
                and fg.role == api.controlTypes.Role.WINDOW
            ) or fg.appModule.appName == "explorer":
                self.shell = COMCreate("shell.application")
                desktop = False
                # We go through the list of open Windows Explorers to find the one that has the focus.
                for window in self.shell.Windows():
                    if window.hwnd == fg.windowHandle:
                        focusedItem = window.Document.FocusedItem
                        break
                else:  # loop exhausted
                    desktop = True
                # Now that we have the current folder, we can explore the SelectedItems collection.
                if desktop:
                    desktopPath = desktop = os.path.join(
                        os.path.join(os.environ["USERPROFILE"]), "Desktop"
                    )
                    fileName = api.getDesktopObject().objectWithFocus().name
                    filePath = desktopPath + "\\" + fileName
                else:
                    filePath = str(focusedItem.path)
                    fileName = str(focusedItem.name)

        if not filePath or not fileName:
            return False

        # Getting the extension to check if is a supported file type.
        fileExtension = filePath[-5:].lower()  # Returns .jpeg or x.pdf
        if fileExtension.startswith("."):  # Case of a  .jpeg file
            fileExtension = fileExtension[1:]  # just jpeg
        else:
            fileExtension = fileExtension[2:]  # just pdf
        if fileExtension in suppFiles:
            return True  # Is a supported file format, so we can make OCR
        else:
            queueHandler.queueFunction(
                queueHandler.eventQueue, ui.message, _("File not supported")
            )
            return False  # It is a file format not supported so end the process.

    def beep_start(self, thrc=False):
        if thrc and not self.isWorking:
            return False
        self.isWorking = True
        tones.beep(500, 100)
        self.bp = Timer(1, self.beep_start, [True])
        self.bp.start()
        return True

    def beep_stop(self):
        self.isWorking = False
        try:
            self.bp.cancel()
        except:
            pass
        return True

    def thr_analyzeObject(
        self, gesture, img_str, lang, s=0, target="all", t=0, bm=0, q=0
    ):
        if s:
            self.beep_start()
        resp = ""
        try:
            resx = cloudvision_request(img_str, lang, target, bm, q, t)
            if "qr" in resx:
                resp = resp + resx["qr"] + "\r\n\r\n"
            if "text" in resx:
                resp = resp + resx["text"] + "\n"
            if "description" in resx:
                resp = resp + "\n" + resx["description"]
            resp = resp.strip()
            if not self.isVirtual:
                queueHandler.queueFunction(queueHandler.eventQueue, speech.cancelSpeech)
                queueHandler.queueFunction(
                    queueHandler.eventQueue,
                    ui.message,
                    _("Analysis completed: ") + resp,
                )
            else:
                queueHandler.queueFunction(
                    queueHandler.eventQueue,
                    ui.browseableMessage,
                    resp,
                    _("CloudVision result"),
                )
            self.isVirtual = False
        except:
            resp = ""
            queueHandler.queueFunction(
                queueHandler.eventQueue, ui.message, str(sys.exc_info()[1])
            )
            log.exception("error during recognition")
        self.isWorking = False
        self.last_resp = resp
        f = wx.FindWindowByName("askframe1")
        if BeMyAI().authorized:
            _t = ""
            if target == "nothing":
                _t = "Be My Eyes"
            else:
                _t = "Be My Eyes & Chrome OCR"
        else:
            _t = "PiccyBot"
            if self.last_resp and bm:
                globalVars.cvaskargs = (_t, self.last_resp, False)
        if not resp.strip():
            resp = _("Error")
        if s:
            self.beep_stop()

    def _script_analyzeObject(self, gesture, fullscreen=False, from_clipboard=False):
        if not self.isVirtual:
            self.isVirtual = scriptHandler.getLastScriptRepeatCount() > 0
        if self.isVirtual:
            return True
        if self.tmr:
            self.tmr.cancel()
        f = wx.FindWindowByName("askframe1")
        if f:
            f.ask_panel.messages_aria.SetValue("")
        global filePath, p, fileExtension
        is_url = False
        p = False
        if from_clipboard:
            p = True
        fg = api.getNavigatorObject()
        try:
            if (not fullscreen and not getConfig()["prefer_navigator"]) and (
                (
                    fg.role == api.controlTypes.Role.GRAPHIC
                    and getattr(fg, "IA2Attributes")
                )
                or (
                    (
                        fg.role == api.controlTypes.Role.LINK
                        or fg.role == api.controlTypes.Role.STATICTEXT
                    )
                    and len(fg.value or "") > 1
                )
            ):
                u = fg.IA2Attributes.get("src", fg.value)
                fileExtension = u.split("/")[-1].split("?")[0].split(".")[-1]
                if fileExtension in suppFiles:
                    if u.startswith("file:///"):
                        u = (
                            u.replace("file:///", "")
                            .replace("/", "\\")
                            .split("?")[0]
                            .split("#")[0]
                        )
                        p = True
                        filePath = u
                        u = ""
                        is_url = False
                    else:
                        if u.startswith("http://") or u.startswith("https://"):
                            is_url = True
                            body = u
        except AttributeError:
            pass
        p = p or self.getFilePath()
        if not fullscreen and (p == True or is_url == True):
            say_message(1 if not from_clipboard else 5)
        elif p == False and is_url == False:
            try:
                import vision
                from visionEnhancementProviders.screenCurtain import (
                    ScreenCurtainProvider,
                )

                screenCurtainId = ScreenCurtainProvider.getSettings().getId()
                screenCurtainProviderInfo = vision.handler.getProviderInfo(
                    screenCurtainId
                )
                isScreenCurtainRunning = bool(
                    vision.handler.getProviderInstance(screenCurtainProviderInfo)
                )
                if isScreenCurtainRunning and not from_clipboard:
                    say_message(2)
                    self.isWorking = False
                    self.isVirtual = False
                    return
            except:
                pass
            say_message(3 if not fullscreen else 4)

        if self.isWorking:
            return False
        self.isWorking = True

        try:
            nav = api.getNavigatorObject() if not fullscreen else find_desktop_obj()
        except:
            log.exception("get nav object")
            self.isWorking = False
            self.isVirtual = False
            return False

        if not nav.location and p == False and is_url == False:
            speech.cancelSpeech()
            queueHandler.queueFunction(
                queueHandler.eventQueue,
                ui.message,
                _("This navigator object is not analyzable"),
            )
            self.isWorking = False
            self.isVirtual = False
            return
        if p == False and is_url == False:
            left, top, width, height = nav.location
            if width < 16 or height < 16:
                nav = nav.parent
                log.warning("Small size, go to the parent element")
                left, top, width, height = nav.location

        if is_url == False and (p == False) and (width < 16 or height < 16):
            perferm_size = " {width}X{height}".format(width=width, height=height)
            """
            If you do and, not or, then an error * will occur
            * wx._core.wxAssertionError: C++ assertion ""w > 0 && h > 0"" failed at ..\..\src\msw\bitmap.cpp(752) in wxBitmap::DoCreate(): invalid bitmap size
            This happens in the Firefox browser in some posts on the VK social network at the time of April 1, 2023.
            """
            log.error("This navigator object is too small. " + perferm_size)
            speech.cancelSpeech()
            queueHandler.queueFunction(
                queueHandler.eventQueue,
                ui.message,
                _("This navigator object is too small") + perferm_size,
            )
            self.isWorking = False
            self.isVirtual = False
            return False
        if p == False and is_url == False:
            bmp = wx.Bitmap(width, height)
            mem = wx.MemoryDC(bmp)
            mem.Blit(0, 0, width, height, wx.ScreenDC(), left, top)
            image = bmp.ConvertToImage()
            try:
                body = BytesIO()
            except TypeError:
                body = StringIO()
            if (
                wx.__version__ == "3.0.2.0"
            ):  # Maintain compatibility with old version of WXPython
                image.SaveStream(body, wx.BITMAP_TYPE_PNG)
            else:  # Used in WXPython 4.0
                image.SaveFile(body, wx.BITMAP_TYPE_PNG)
            img_str = body.getvalue()
        if p == True and is_url == False:
            with open(filePath, "rb") as f:
                body = f.read()
            img_str = body
        if is_url == True:
            img_str = body

        sound = getConfig()["sound"]
        s = 0
        if sound:
            s = 1
        textonly = getConfig()["textonly"]
        imageonly = getConfig()["imageonly"]
        target = "all"
        if textonly and not imageonly:
            target = "text"
        if not textonly and imageonly:
            target = "image"
        if not textonly and not imageonly:
            target = "nothing"
        trtext = getConfig()["trtext"]
        t = 0
        if trtext:
            t = 1
        bm = 1 if getConfig()["bm"] else 0
        qronly = getConfig()["qronly"]
        q = 0
        if qronly:
            q = 1
        lang = getConfig()["language"]

        self.tmr = Timer(
            0.1, self.thr_analyzeObject, [gesture, img_str, lang, s, target, t, bm, q]
        )
        self.tmr.start()

    def script_analyzeObject(self, gesture):
        global filePath
        global fileExtension
        global fileName
        try:
            self._script_analyzeObject(gesture)
        except:
            log.exception("script error")
        finally:
            filePath = ""
            fileExtension = ""
            fileName = ""

            def restorework():
                if self.tmr is not None and self.tmr.is_alive():
                    return
                self.isWorking = False
                self.isVirtual = False

            Timer(3, restorework, []).start()

    script_analyzeObject.__doc__ = _(
        "Gives a description on how current navigator object or selected file in Explorer looks like visually,\n"
        "if you press twice quickly, a virtual viewer will open."
    )
    script_analyzeObject.category = _("Cloud Vision")

    def script_analyzeFullscreen(self, gesture):
        global filePath
        global fileExtension
        global fileName
        try:
            self._script_analyzeObject(gesture, fullscreen=True)
        except:
            log.exception("script error")
        finally:
            filePath = ""
            fileExtension = ""
            fileName = ""

            def restorework():
                if self.tmr is not None and self.tmr.is_alive():
                    return
                self.isWorking = False
                self.isVirtual = False

            Timer(3, restorework, []).start()

    script_analyzeFullscreen.__doc__ = _(
        "Analyze the full screen. Pressing twice will open the virtual viewer."
    )
    script_analyzeFullscreen.category = _("Cloud Vision")

    def script_analyzeClipboard(self, gesture):
        global filePath
        global fileExtension
        global fileName
        try:
            fileExtension = "png"
            tpng = tempfile.mkstemp(suffix="." + fileExtension)[1]
            filePath = tpng
            fileName = os.path.basename(filePath)
            b = get_image_from_clipboard()
            if not b:
                return False
            image = b.ConvertToImage()
            if not image.SaveFile(tpng):
                queueHandler.queueFunction(
                    queueHandler.eventQueue,
                    ui.message,
                    _("Couldn't save image from clipboard"),
                )
                return
            self._script_analyzeObject(gesture, fullscreen=False, from_clipboard=True)
        except:
            log.exception("script error")
        finally:
            if os.path.isfile(tpng):
                os.remove(tpng)
            filePath = ""
            fileExtension = ""
            fileName = ""
            tpng = ""

            def restorework():
                if self.tmr is not None and self.tmr.is_alive():
                    return
                self.isWorking = False
                self.isVirtual = False

            Timer(3, restorework, []).start()

    script_analyzeClipboard.__doc__ = _(
        "Analyzing an image from the clipboard. Pressing twice will open the virtual viewer."
    )
    script_analyzeClipboard.category = _("Cloud Vision")

    def script_copylastresult(self, gesture):
        if not self.last_resp:
            queueHandler.queueFunction(
                queueHandler.eventQueue, ui.message, _("Text Not Found.")
            )
            return False
        try:
            unc = unicode
        except NameError:
            unc = str
        if api.copyToClip(unc(self.last_resp)):
            queueHandler.queueFunction(
                queueHandler.eventQueue,
                ui.message,
                _("Result copyed in clipboard.\n") + self.last_resp,
            )
            return True
        return False

    script_copylastresult.__doc__ = _("Copy last result in clipboard.")
    script_copylastresult.category = _("Cloud Vision")

    def script_askBm(self, gesture):
        queueHandler.queueFunction(queueHandler.eventQueue, self.on_ask_bm, None)

    def _askBm(self, gesture):
        ask_frame = bmgui.AskFrame()
        ask_frame.Show()
        ask_frame.postInit()

    script_askBm.__doc__ = _("Ask the bot a question.")
    script_askBm.category = _("Cloud Vision")

    __gestures = {
        "kb:NVDA+Control+I": "analyzeObject",
        "kb:NVDA+Alt+F": "analyzeFullscreen",
        "kb:NVDA+Alt+C": "analyzeClipboard",
        "kb:NVDA+Alt+A": "askBm",
    }
