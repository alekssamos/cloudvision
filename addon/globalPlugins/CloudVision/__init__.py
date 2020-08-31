# CloudVision
# Author: alekssamos
# Copyright 2020, released under GPL.
# Add-on that gets description of current navigator object based on visual features,
# the computer vision heavy computations are made in the cloud.
# VISIONBOT.RU
CloudVisionVersion = "2.0.3"
import sys
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
from  threading import Timer
import speech
import api
from logHandler import log
import languageHandler
import addonHandler
addonHandler.initTranslation()
import textInfos.offsets
import ui
from globalCommands import SCRCAT_OBJECTNAVIGATION
from time import sleep
from math import sqrt

import base64
if sys.version_info.major == 2:
	import urllib as ur, urllib as up
elif sys.version_info.major == 3:
	import urllib.request as ur, urllib.parse as up

class SettingsDialog(gui.SettingsDialog):
	title = _("CloudVision Settings")

	def makeSettings(self, sizer):
		settingsSizerHelper = gui.guiHelper.BoxSizerHelper(self, sizer=sizer)

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

	def beep_start(self, thrc=False):
		if thrc and not self.isWorking: return False
		self.isWorking = True
		tones.beep(500, 100)
		self.bp = Timer(1, self.beep_start, [True])
		self.bp.start()
		return True

	def beep_stop(self):
		self.isWorking = False
		self.bp.cancel()
		return True


	def thr_analyzeObject(self, gesture, api_url, img_str, lang, s=0, n=0, t=0, q=0):
		if s: self.beep_start()
		for ii in range(2):
			try:
				resp = ur.urlopen(api_url, up.urlencode({"v":CloudVisionVersion, "n":n, "t":t, "s":s, "q":q, "lang":lang, "img_str":img_str}).encode('utf-8'), timeout=60).read().decode('utf-8')
				break
			except:
				resp = ""
		self.isWorking = False
		if resp: self.last_resp = resp
		if not resp.strip(): resp = _("Error")
		if s: self.beep_stop()
		if not self.isVirtual:
			speech.cancelSpeech()
			ui.message(_('Analysis completed: ') + resp)
		else:
			ui.browseableMessage(resp, _("CloudVision result"))
		self.isVirtual = False

	def script_analyzeObject(self, gesture):
		if not self.isVirtual: self.isVirtual = scriptHandler.getLastScriptRepeatCount()>0
		if self.isVirtual: return True
		if self.isWorking: return False
		self.isWorking = True
		api_url = "https://visionbot.ru/addon/index.php"
		if self.tmr: self.tmr.cancel()
		speech.cancelSpeech()
		ui.message(_("Analyzing navigator object"))
		try: nav = api.getNavigatorObject()
		except: return False

		if not nav.location:
			speech.cancelSpeech()
			ui.message(_("This navigator object is not analyzable"))
			return
		left, top, width, height = nav.location

		bmp = wx.EmptyBitmap(width, height)
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

		sound = getConfig()['sound']
		s=0
		if sound: s=1
		textonly = getConfig()['textonly']
		imageonly = getConfig()['imageonly']
		n=0
		if textonly and not imageonly: n=1
		if not textonly and imageonly: n=2
		trtext = getConfig()['trtext']
		t=0
		if trtext: t=1
		qronly = getConfig()['qronly']
		q=0
		if qronly: q=1
		lang = getConfig()['language']

		self.tmr = Timer(0.1, self.thr_analyzeObject, [gesture, api_url, img_str, lang, s, n, t, q])
		self.tmr.start()

	script_analyzeObject.__doc__ = _("Gives a description on how current navigator object looks like visually,\n"
	"if you press twice quickly, a virtual viewer will open.")
	script_analyzeObject.category = _('Cloud Vision')

	def script_copylastresult(self, gesture):
		if not self.last_resp:
			ui.message(_("Text Not Found."))
			return False
		try: unc = unicode
		except NameError: unc = str
		if api.copyToClip(unc(self.last_resp)):
			ui.message(_("Result copyed in clipboard.\n") + self.last_resp)
			return True
		return False

	script_copylastresult.__doc__ = _('Copy last result in clipboard.')
	script_copylastresult.category = _('Cloud Vision')

	__gestures = {
		"kb:NVDA+Control+I": "analyzeObject",
	}

supportedLocales = [
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
	"hu",
	"id",
	"it",
	"ja",
	"ko",
	"lt",
	"lv",
	"nb_r",
	"nl",
	"pl",
	"pt",
	"ro",
	"ru",
	"sk",
	"sl",
	"sr",
	"sv",
	"tg",
	"tr",
	"uk",
	"vi",
	"zh_CN"
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