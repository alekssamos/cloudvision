# CloudVision
# Author: alekssamos
# Copyright 2020, released under GPL.
# Add-on that gets description of current navigator object based on visual features,
# the computer vision heavy computations are made in the cloud.
# VISIONBOT.RU
CloudVisionVersion = "3.0.1"
import sys
import json
import time
import os
import tempfile
import subprocess
from xml.parsers import expat
from collections import namedtuple
try:
	from cBytesIO import BytesIO ## 2
	from cStringIO import StringIO ## 2
except ImportError:
	from io import BytesIO ## 3
	from io import StringIO ## 3

## for Windows XP
if sys.version_info.major == 2:
	sys.path.insert(0, ".")
	import myconfigobj as configobj
	del sys.path[0]
else:
	import configobj

import tones
try:
	import validate
except ImportError:
	import configobj.validate as validate
import wx
import config
import globalPluginHandler
import gui
import scriptHandler
import queueHandler
from  threading import Timer
import speech
import api
from logHandler import log
import languageHandler
import addonHandler
import versionInfo
is_new_nvda = (versionInfo.version_year >= 2021 and versionInfo.version_major>=1)
if is_new_nvda:
	from comtypes.client import CreateObject as COMCreate
	from .MyOCREnhance import totalCommanderHelper

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

class SettingsDialog(gui.SettingsDialog):
	title = _("CloudVision Settings")

	def makeSettings(self, sizer):
		settingsSizerHelper = gui.guiHelper.BoxSizerHelper(self, sizer=sizer)

		self.prefer_navigator = wx.CheckBox(self, label=_("Pre&fer a navigator object instead of a file"))
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

		self.qronly = wx.CheckBox(self, label=_("Read &QR / bar code"))
		self.qronly.SetValue(getConfig()["qronly"])
		settingsSizerHelper.addItem(self.qronly)

		self.trtext = wx.CheckBox(self, label=_("Translate text"))
		self.trtext.SetValue(getConfig()["trtext"])
		settingsSizerHelper.addItem(self.trtext)

		langs = sorted(supportedLocales)
		curlang = getConfig()['language']
		try:
			select = langs.index(curlang)
		except ValueError:
			select = langs.index('en')
		choices = [languageHandler.getLanguageDescription(locale) or locale for locale in supportedLocales]
		self.language = settingsSizerHelper.addLabeledControl(_("Select image description language, other languages than english are more prone to translation errors"), wx.Choice, choices=choices)
		self.language.SetSelection(select)
		def on_open_visionbot_ru_button(self):
			import webbrowser as wb
			wb.open("https://visionbot.ru/?fromaddon=1&addonversion="+CloudVisionVersion)
		self.open_visionbot_ru_button = wx.Button(self, label=_("Open site")+" VISIONBOT.RU")
		self.open_visionbot_ru_button.Bind(wx.EVT_BUTTON, on_open_visionbot_ru_button)
		settingsSizerHelper.addItem(self.open_visionbot_ru_button)
		
	def postInit(self):
		self.sound.SetFocus()

	def onOk(self, event):
		if not self.textonly.IsChecked() and not  self.imageonly.IsChecked():
			self.textonly.SetValue(True)
			self.imageonly.SetValue(True)
		getConfig()["prefer_navigator"] = self.prefer_navigator.IsChecked()
		getConfig()["sound"] = self.sound.IsChecked()
		getConfig()["textonly"] = self.textonly.IsChecked()
		getConfig()["imageonly"] = self.imageonly.IsChecked()
		getConfig()["trtext"] = self.trtext.IsChecked()
		getConfig()["qronly"] = self.qronly.IsChecked()
		getConfig()["language"] = supportedLocales[self.language.GetSelection()]

		try:
			getConfig().write()
		except IOError:
			log.error("Error writing CloudVision configuration", exc_info=True)
			gui.messageBox(e.strerror, _("Error saving settings"), style=wx.OK | wx.ICON_ERROR)

		super(SettingsDialog, self).onOk(event)

class APIError(Exception): pass
def cloudvision_request(img_str, lang = "en", target = "all", qr = 0, translate = 0):
	params = {
		"lang": lang,
		"target": target,
		"qr": qr,
		"translate": translate
	}
	if isinstance(img_str, str):
		lnkstart = "http"
	else:
		lnkstart = b"http"
	if img_str.startswith(lnkstart):
		params["url"] = img_str
	else:
		params["body"] = img_str
	r1 = ur.urlopen("https://visionbot.ru/apiv2/in.php", data = up.urlencode(params).encode()
	)
	j1 = json.loads(r1.read())
	r1.close()
	del img_str # free memory
	if j1["status"] != "ok":
		raise APIError(j1["status"])
	
	for i in range(60):
		r2 = ur.urlopen("https://visionbot.ru/apiv2/res.php",
			data = up.urlencode({"id": j1["id"]}).encode())
		j2 = json.loads(r2.read())
		r2.close()
		if j2["status"] == "error":
			raise APIError(j2["status"])
		
		if j2["status"] == "ok":
			return j2
		
		if j2["status"] == "notready":
			time.sleep(1)
			continue

class GlobalPlugin(globalPluginHandler.GlobalPlugin):

	def __init__(self):
		super(globalPluginHandler.GlobalPlugin, self).__init__()
		self.CloudVisionSettingsItem = gui.mainFrame.sysTrayIcon.preferencesMenu.Append(wx.ID_ANY,
			_("Cloud Vision settings..."))
		gui.mainFrame.sysTrayIcon.Bind(
			wx.EVT_MENU, lambda evt: gui.mainFrame._popupSettingsDialog(SettingsDialog), self.CloudVisionSettingsItem)

	def terminate(self):
		try:
			gui.mainFrame.sysTrayIcon.preferencesMenu.RemoveItem(
				self.CloudVisionSettingsItem)
		except:
			pass

	tmr = None
	last_resp = ""
	isVirtual = False
	isWorking = False

	def getFilePath(self): #For this method thanks to some nvda addon developers ( code snippets and suggestion)
		if not is_new_nvda:
			focus=api.getFocusObject()
			mod=focus.appModule
			if mod.appName.lower() in ["explorer", "totalcmd"]:
				queueHandler.queueFunction(queueHandler.eventQueue, ui.message, _("To recognize files under the cursor without opening Update NVDA version to 2021.1 or higher"))
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
		else:
			# We check if we are in the Windows Explorer.
			fg = api.getForegroundObject()
			if (fg.role != api.controlTypes.Role.PANE and fg.role != api.controlTypes.Role.WINDOW) or fg.appModule.appName != "explorer":
				return False
			
			self.shell = COMCreate("shell.application")
			desktop = False
			# We go through the list of open Windows Explorers to find the one that has the focus.
			for window in self.shell.Windows():
				if window.hwnd == fg.windowHandle:
					focusedItem=window.Document.FocusedItem
					break
			else: # loop exhausted
				desktop = True
			# Now that we have the current folder, we can explore the SelectedItems collection.
			if desktop:
				desktopPath = desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
				fileName = api.getDesktopObject().objectWithFocus().name
				filePath = desktopPath + '\\' + fileName
			else:
				filePath = str(focusedItem.path)
				fileName = str(focusedItem.name)
		
		# Getting the extension to check if is a supported file type.
		fileExtension = filePath[-5:].lower() # Returns .jpeg or x.pdf
		if fileExtension.startswith("."): # Case of a  .jpeg file
			fileExtension = fileExtension[1:] # just jpeg
		else:
			fileExtension = fileExtension[2:] # just pdf
		if fileExtension in suppFiles:
			return True # Is a supported file format, so we can make OCR
		else:
			queueHandler.queueFunction(queueHandler.eventQueue, ui.message, _("File not supported"))
			return False # It is a file format not supported so end the process.

	def beep_start(self, thrc=False):
		if thrc and not self.isWorking: return False
		self.isWorking = True
		tones.beep(500, 100)
		self.bp = Timer(1, self.beep_start, [True])
		self.bp.start()
		return True

	def beep_stop(self):
		self.isWorking = False
		try: self.bp.cancel()
		except: pass
		return True

	def thr_analyzeObject(self, gesture, img_str, lang, s=0, target="all", t=0, q=0):
		if s: self.beep_start()
		resp = ""
		try:
			resx = cloudvision_request(img_str, lang, target, q, t)
			if "qr" in resx: resp = resp + resx["qr"] + "\r\n\r\n"
			if "text" in resx: resp = resp + resx["text"]
			if not self.isVirtual:
				queueHandler.queueFunction(queueHandler.eventQueue, speech.cancelSpeech)
				queueHandler.queueFunction(queueHandler.eventQueue, ui.message, _('Analysis completed: ') + resp)
			else:
				queueHandler.queueFunction(queueHandler.eventQueue, ui.browseableMessage, resp, _("CloudVision result"))
			self.isVirtual = False
		except:
			resp = ""
			queueHandler.queueFunction(queueHandler.eventQueue, ui.message, str(sys.exc_info()[1]))
		self.isWorking = False
		if resp: self.last_resp = resp
		if not resp.strip(): resp = _("Error")
		if s: self.beep_stop()

	def _script_analyzeObject(self, gesture):
		if not self.isVirtual: self.isVirtual = scriptHandler.getLastScriptRepeatCount()>0
		if self.isVirtual: return True
		if self.tmr: self.tmr.cancel()
		speech.cancelSpeech()
		global filePath, p, fileExtension
		is_url = False
		p = False
		fg = api.getNavigatorObject()
		try:
			if (not getConfig()["prefer_navigator"]) and (
				(fg.role == api.controlTypes.Role.GRAPHIC
					and getattr(fg, "IA2Attributes"))
				or ((fg.role == api.controlTypes.Role.LINK
						or fg.role == api.controlTypes.Role.STATICTEXT)
					and len(fg.value or "") > 1)
			):
				u = fg.IA2Attributes.get("src", fg.value)
				fileExtension = u.split("/")[-1].split("?")[0].split(".")[-1]
				if fileExtension in suppFiles:
					if u.startswith("file:///"):
						u = u.replace("file:///", "").replace("/", "\\").split("?")[0].split("#")[0]
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
		if p == True or is_url == True:
			queueHandler.queueFunction(queueHandler.eventQueue, ui.message, _("Analyzing selected file"))
		elif p == False and is_url == False:
			try:
				import vision
				from visionEnhancementProviders.screenCurtain import ScreenCurtainProvider
				screenCurtainId = ScreenCurtainProvider.getSettings().getId()
				screenCurtainProviderInfo = vision.handler.getProviderInfo(screenCurtainId)
				isScreenCurtainRunning = bool(vision.handler.getProviderInstance(screenCurtainProviderInfo))
				if isScreenCurtainRunning:
					# Translators: Reported when screen curtain is enabled.
					queueHandler.queueFunction(queueHandler.eventQueue, ui.message, _("Please disable screen curtain before using CloudVision add-on."))
					self.isWorking = False
					self.isVirtual = False
					return
			except:
				pass
			queueHandler.queueFunction(queueHandler.eventQueue, ui.message, _("Analyzing navigator object"))

		if self.isWorking:
			return False
		self.isWorking = True

		try:
			nav = api.getNavigatorObject()
		except:
			log.exception("get nav object")
			self.isWorking = False
			self.isVirtual = False
			return False

		if not nav.location and p == False and is_url == False:
			speech.cancelSpeech()
			queueHandler.queueFunction(queueHandler.eventQueue, ui.message, _("This navigator object is not analyzable"))
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
			queueHandler.queueFunction(queueHandler.eventQueue, ui.message, _("This navigator object is too small") + perferm_size)
			self.isWorking = False
			self.isVirtual = False
			return False
		if p == False and is_url == False:
			bmp = wx.Bitmap(width, height)
			mem = wx.MemoryDC(bmp)
			mem.Blit(0, 0, width, height, wx.ScreenDC(), left, top)
			image = bmp.ConvertToImage()
			try: body = BytesIO()
			except TypeError: body = StringIO()
			if wx.__version__ == '3.0.2.0': # Maintain compatibility with old version of WXPython
				image.SaveStream(body, wx.BITMAP_TYPE_PNG)
			else: # Used in WXPython 4.0
				image.SaveFile(body, wx.BITMAP_TYPE_PNG)
			img_str = base64.b64encode(body.getvalue())
		if p == True and is_url == False:
			with open(filePath, "rb") as f:
				body = f.read()
			img_str = base64.b64encode(body)
		if is_url == True:
			img_str = body

		sound = getConfig()['sound']
		s=0
		if sound: s=1
		textonly = getConfig()['textonly']
		imageonly = getConfig()['imageonly']
		target = "all"
		if textonly and not imageonly: target = "text"
		if not textonly and imageonly: target = "image"
		trtext = getConfig()['trtext']
		t=0
		if trtext: t=1
		qronly = getConfig()['qronly']
		q=0
		if qronly: q=1
		lang = getConfig()['language']

		self.tmr = Timer(0.1, self.thr_analyzeObject, [gesture, img_str, lang, s, target, t, q])
		self.tmr.start()

	def script_analyzeObject(self, gesture):
		try:
			self._script_analyzeObject(gesture)
		except:
			log.exception("script error")
		finally:
			def restorework():
				if self.tmr is not None and self.tmr.is_alive():
					return
				self.isWorking = False
				self.isVirtual = False
			Timer(3, restorework, []).start()
	script_analyzeObject.__doc__ = _("Gives a description on how current navigator object or selected file in Explorer looks like visually,\n"
	"if you press twice quickly, a virtual viewer will open.")
	script_analyzeObject.category = _('Cloud Vision')

	def script_copylastresult(self, gesture):
		if not self.last_resp:
			queueHandler.queueFunction(queueHandler.eventQueue, ui.message, _("Text Not Found."))
			return False
		try: unc = unicode
		except NameError: unc = str
		if api.copyToClip(unc(self.last_resp)):
			queueHandler.queueFunction(queueHandler.eventQueue, ui.message, _("Result copyed in clipboard.\n") + self.last_resp)
			return True
		return False

	script_copylastresult.__doc__ = _('Copy last result in clipboard.')
	script_copylastresult.category = _('Cloud Vision')

	__gestures = {
		"kb:NVDA+Control+I": "analyzeObject",
	}

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
	"vi",
	"zh_CN",
	"zh_TW"
]

def getDefaultLanguage():
	lang = languageHandler.getLanguage()

	if lang not in supportedLocales and "_" in lang:
		lang = lang.split("_")[0]
	
	if lang not in supportedLocales:
		lang = "en"

	return lang

_config = None
configspec = StringIO(u"""
prefer_navigator=boolean(default=False)
sound=boolean(default=False)
textonly=boolean(default=True)
imageonly=boolean(default=True)
qronly=boolean(default=False)
trtext=boolean(default=False)
language=string(default={defaultLanguage})
""".format(defaultLanguage=getDefaultLanguage()))
def getConfig():
	global _config
	if not _config:
		path = os.path.join(config.getUserDefaultConfigPath(), "CloudVision.ini")
		_config = configobj.ConfigObj(path, configspec=configspec)
		val = validate.Validator()
		_config.validate(val)
	return _config