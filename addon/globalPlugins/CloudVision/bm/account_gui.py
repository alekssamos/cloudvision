# -*- coding: utf-8 -*-
import json
import sys
import os
import os.path
import time
import globalVars
from threading import Timer, Lock

if sys.version_info.major == 2:
    import urllib as ur, urllib as up
elif sys.version_info.major == 3:
    import urllib.request as ur, urllib.parse as up

import socket

socket.setdefaulttimeout(60)

import wx
import ui
from logHandler import log
import queueHandler
import addonHandler
from ..bemyai import BeMyAI, BeMyAIError
from ..piccy_bot import lastImageFilePath, piccyBot, PBAPIError
from ..cvconf import getConfig, promptInputLimit

addonHandler.initTranslation()


class FocusedStaticText(wx.StaticText):
    def AcceptsFocus(self):
        return True


LOGGED_IN_TEXT = _("You are logged in to your account:")


class LoginPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        email_sizer = wx.BoxSizer(wx.HORIZONTAL)
        email_label = wx.StaticText(self, label=_("Email:"))
        self.email_input = wx.TextCtrl(self)
        self.email_input.SetMaxLength(100)
        email_sizer.Add(email_label, 0, wx.ALL, 5)
        email_sizer.Add(self.email_input, 1, wx.EXPAND | wx.ALL, 5)
        password_sizer = wx.BoxSizer(wx.HORIZONTAL)
        password_label = wx.StaticText(self, label=_("Password:"))
        self.password_input = wx.TextCtrl(self, style=wx.TE_PASSWORD)
        self.password_input.SetMaxLength(100)
        restore_button = wx.Button(self, label=_("Recover"))
        restore_button.Bind(wx.EVT_BUTTON, self.on_restore)
        password_sizer.Add(password_label, 0, wx.ALL, 5)
        password_sizer.Add(self.password_input, 1, wx.EXPAND | wx.ALL, 5)
        password_sizer.Add(restore_button, 1, wx.EXPAND | wx.ALL, 5)
        login_button = wx.Button(self, label=_("Log in"))
        login_button.Bind(wx.EVT_BUTTON, self.on_login)
        show_register_button = wx.Button(self, label=_("Create account"))
        show_register_button.Bind(wx.EVT_BUTTON, self.on_show_register_btn)
        main_sizer.Add(email_sizer, 0, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(password_sizer, 0, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(login_button, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        main_sizer.Add(show_register_button, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        self.SetSizer(main_sizer)

    def on_restore(self, event):
        event.Skip()
        email = self.email_input.GetValue().strip()
        if not email or "@" not in email or "." not in email:
            wx.MessageBox(
                _(
                    "Enter your email address here and click on the button to reset your password."
                )
            )
            self.email_input.SetFocus()
            return
        f = self.FindWindowByName("lrframe1")
        b = BeMyAI()
        try:
            b.send_reset_password(email=email).strip()
            wx.MessageBox(
                _(
                    "A link has been sent to your email. Click on it, set a new password in the form, and then enter the password here."
                )
            )
        except BeMyAIError:
            log.exception("Be My AI API error")
            wx.MessageBox(str(sys.exc_info()[1]))
        self.password_input.SetFocus()

    def on_login(self, event):
        event.Skip()
        email = self.email_input.GetValue()
        password = self.password_input.GetValue()
        f = self.FindWindowByName("lrframe1")
        b = BeMyAI()
        try:
            res = b.login(email=email, password=password)
        except BeMyAIError:
            log.exception("Be My AI API error")
            wx.MessageBox(str(sys.exc_info()[1]))
        f.Close()

    def on_show_register_btn(self, event):
        event.Skip()
        self.Hide()
        f = self.FindWindowByName("lrframe1")
        f.register_panel.Show()
        f.Layout()
        f.register_panel.SetFocus()


class LoggedInPannel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self.logged_in_h_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.logged_in_label = FocusedStaticText(self, wx.ID_ANY, LOGGED_IN_TEXT)
        self.logged_in_h_sizer.Add(self.logged_in_label, 0, 0, 0)
        self.logout_button = wx.Button(self, wx.ID_ANY, _("Logout"))
        self.logged_in_h_sizer.Add(self.logout_button, 0, 0, 0)
        self.SetSizer(self.logged_in_h_sizer)
        self.logout_button.Bind(wx.EVT_BUTTON, self.on_logout)

    def on_logout(self, event):
        event.Skip()
        BeMyAI().logout()
        f = self.FindWindowByName("lrframe1")
        self.Hide()
        f.login_panel.Show()
        f.login_panel.email_input.SetFocus()


class RegisterPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        name_sizer = wx.BoxSizer(wx.HORIZONTAL)
        name_label = wx.StaticText(self, label=_("Name:"))
        self.name_input = wx.TextCtrl(self)
        self.name_input.SetMaxLength(100)
        name_sizer.Add(name_label, 0, wx.ALL, 5)
        name_sizer.Add(self.name_input, 1, wx.EXPAND | wx.ALL, 5)
        surname_sizer = wx.BoxSizer(wx.HORIZONTAL)
        surname_label = wx.StaticText(self, label=_("Surname:"))
        self.surname_input = wx.TextCtrl(self)
        self.surname_input.SetMaxLength(100)
        surname_sizer.Add(surname_label, 0, wx.ALL, 5)
        surname_sizer.Add(self.surname_input, 1, wx.EXPAND | wx.ALL, 5)
        email_sizer = wx.BoxSizer(wx.HORIZONTAL)
        email_label = wx.StaticText(self, label=_("Email:"))
        self.email_input = wx.TextCtrl(self)
        self.email_input.SetMaxLength(100)
        email_sizer.Add(email_label, 0, wx.ALL, 5)
        email_sizer.Add(self.email_input, 1, wx.EXPAND | wx.ALL, 5)
        password_sizer = wx.BoxSizer(wx.HORIZONTAL)
        password_label = wx.StaticText(self, label=_("Password:"))
        self.password_input = wx.TextCtrl(self, style=wx.TE_PASSWORD)
        self.password_input.SetMaxLength(100)
        password_sizer.Add(password_label, 0, wx.ALL, 5)
        password_sizer.Add(self.password_input, 1, wx.EXPAND | wx.ALL, 5)
        register_button = wx.Button(self, label=_("Register"))
        register_button.Bind(wx.EVT_BUTTON, self.on_register)
        show_login_button = wx.Button(self, label=_("Log in"))
        show_login_button.Bind(wx.EVT_BUTTON, self.on_show_login_btn)
        main_sizer.Add(name_sizer, 0, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(surname_sizer, 0, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(email_sizer, 0, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(password_sizer, 0, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(register_button, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        main_sizer.Add(show_login_button, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        self.SetSizer(main_sizer)

    def on_show_login_btn(self, event):
        event.Skip()
        self.Hide()
        f = self.FindWindowByName("lrframe1")
        f.login_panel.Show()
        f.Layout()
        f.login_panel.SetFocus()

    def on_register(self, event):
        event.Skip()
        name = self.name_input.GetValue()
        surname = self.surname_input.GetValue()
        email = self.email_input.GetValue()
        password = self.password_input.GetValue()
        f = self.FindWindowByName("lrframe1")
        try:
            b = BeMyAI()
            res = b.signup(
                first_name=name,
                last_name=surname,
                email=email,
                password=password,
            )
        except BeMyAIError:
            log.exception("Be My AI API error")
            wx.MessageBox(str(sys.exc_info()[1]))
        f.Close()


class AskPanel(wx.Panel):
    ask_tmr = None

    def __init__(self, parent):
        super().__init__(parent)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        messages_sizer = wx.BoxSizer(wx.VERTICAL)
        self.messages_aria = wx.TextCtrl(
            self, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2
        )
        self.messages_aria.SetMinSize((600, 400))  # Увеличиваем размер окна ответа
        messages_sizer.Add(self.messages_aria, 1, wx.EXPAND | wx.ALL, 5)
        question_sizer = wx.BoxSizer(wx.HORIZONTAL)
        question_label = wx.StaticText(self, label=_("Question:"))
        self.question_input = wx.TextCtrl(
            self, style=wx.TE_MULTILINE | wx.TE_PROCESS_ENTER
        )
        self.question_input.SetMaxLength(promptInputLimit)
        question_sizer.Add(question_label, 0, wx.ALL, 5)
        question_sizer.Add(self.question_input, 1, wx.EXPAND | wx.ALL, 5)
        send_close_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.send_button = wx.Button(self, label=_("Send"))
        self.send_button.Bind(wx.EVT_BUTTON, self.on_send)
        self.send_button.SetToolTip("CTRL+Enter")
        close_button = wx.Button(self, label=_("Close"))
        close_button.Bind(wx.EVT_BUTTON, self.on_close)
        close_button.SetToolTip("ESCAPE")
        send_close_sizer.Add(self.send_button)
        send_close_sizer.Add(close_button)
        main_sizer.Add(messages_sizer, 1, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(question_sizer, 0, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(send_close_sizer)
        self.SetSizer(main_sizer)
        self.messages_aria.SetValue("")  # Очищаем текстовое поле при инициализации

        for s in (
            self.send_button,
            close_button,
            self.messages_aria,
            self.question_input,
        ):
            s.Bind(wx.EVT_KEY_DOWN, self.on_key_down)

    def format_text(self, text):
        sentences = []
        current_sentence = ""
        for char in text:
            current_sentence += char
            if char in ".!?":
                sentences.append(current_sentence.strip())
                current_sentence = ""
        if current_sentence:
            sentences.append(current_sentence.strip())
        return "\n".join(sentences)

    def add_message(self, who, text, report=True):
        formatted_text = self.format_text(text)
        if report:
            queueHandler.queueFunction(
                queueHandler.eventQueue, ui.message, f"{who}: {text}"
            )
        with Lock():
            current_text = self.messages_aria.GetValue()
            self.messages_aria.SetValue(f"{current_text}\n{who}: {formatted_text}")
        self.Layout()

    def on_send(self, event):
        event.Skip()
        self.send_button.Disable()
        if self.ask_tmr and self.ask_tmr.is_alive():
            self.ask_tmr.cancel()
        self.ask_tmr = Timer(0.1, self._on_send, [event])
        queueHandler.queueFunction(
            queueHandler.eventQueue,
            ui.message,
            _("Wait for the Bot to type the message"),
        )
        self.ask_tmr.start()

    def on_key_down(self, event):
        key = event.GetKeyCode()
        if event.ControlDown() and key in [10, 13, 32]:
            self.on_send(event)
        elif key == wx.WXK_ESCAPE:
            self.on_close(event)
        elif (key == wx.WXK_F2 and event.GetEventObject() == self.messages_aria) or (
            event.ControlDown() and key in [83, 115]
        ):
            self.save_dialog()
        else:
            event.Skip()

    def _bm_ask_process(self, message):
        b = BeMyAI()
        res = ""
        sid, chat_id, result = b.send_text_message(chat_id=b.bm_chat_id, text=message)
        for x in range(3):
            if res != "":
                break
            for message in b.receive_messages(sid):
                if message.get("user"):
                    continue
                res = message["data"]
                break
        return res

    def _on_send(self, event):
        message = self.question_input.GetValue()
        f = self.FindWindowByName("askframe1")
        try:
            self.question_input.SetValue("")
            self.add_message(_("You"), message)
            if BeMyAI().authorized:
                res = self._bm_ask_process(message)
            else:
                res = piccyBot(None, getConfig()["language"], message)
        except (BeMyAIError, PBAPIError, urllib3.exceptions.TimeoutError):
            log.exception("API error")
            wx.MessageBox(str(sys.exc_info()[1]), style=wx.ICON_ERROR)
            return False
        finally:
            self.send_button.Enable()
        self.add_message("Be My Eyes" if BeMyAI().authorized else "PiccyBot", res)
        self.messages_aria.SetFocus()

    def on_close(self, event):
        f = self.FindWindowByName("askframe1")
        f.Hide()

    def save_dialog(self):
        with wx.FileDialog(
            self,
            "Save dialog",
            wildcard="Text files (*.txt)|*.txt",
            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
        ) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            pathname = fileDialog.GetPath()
            try:
                with open(pathname, "w") as file:
                    file.write(self.messages_aria.GetValue())
            except IOError:
                wx.LogError(f"Cannot save current data in file '{pathname}'.")


class MainDialog(wx.Dialog):
    def __init__(self, parent=None, lang="en"):
        super().__init__(parent=parent, title="Manage Be My Eyes Account")
        self.SetName("lrframe1")
        self.login_panel = LoginPanel(self)
        self.register_panel = RegisterPanel(self)
        self.logged_panel = LoggedInPannel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.login_panel, 1, wx.EXPAND)
        sizer.Add(self.logged_panel, 1, wx.EXPAND)
        sizer.Add(self.register_panel, 1, wx.EXPAND)
        for o in (self, self.login_panel, self.logged_panel, self.register_panel):
            o.Bind(wx.EVT_KEY_UP, self.OnKeyUp)
        self.register_panel.Hide()
        if BeMyAI().authorized:
            self.login_panel.Hide()
            refresh_result = ""
            try:
                res = BeMyAI().refresh_token()
                refresh_result = "{} {} \n {}".format(
                    res["user"]["first_name"],
                    res["user"]["last_name"],
                    res["user"]["email"],
                )
            except BeMyAIError:
                log.exception("Error get BM Account data")
                refresh_result = "..."
            self.logged_panel.logged_in_label.SetLabel(LOGGED_IN_TEXT + refresh_result)
            self.logged_panel.logged_in_label.SetFocus()
        else:
            self.logged_panel.Hide()
        self.SetSizer(sizer)
        self.Layout()

    def OnKeyUp(self, e):
        key = e.GetKeyCode()
        e.Skip()
        if key == 27:
            self.Close()


class AskFrame(wx.Frame):
    def __init__(self, parent=None, lang="en"):
        super().__init__(parent=None, style=wx.MAXIMIZE)
        self.SetTitle("Ask a question")
        self.SetName("askframe1")
        self.ask_panel = AskPanel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.ask_panel, 1, wx.EXPAND)
        self.SetSizer(sizer)
        self.Layout()
        self.Bind(wx.EVT_CLOSE, self.on_close)
        return
        if not BeMyAI().authorized:
            _t = "\n".join(
                [
                    _("First you need to log in or register"),
                    _(
                        "Open NVDA Menu, Preferences, CloudVision Settings, Manage Be My Eyes account"
                    ),
                ]
            )
            self.ask_panel.messages_aria.SetValue(_t)
            queueHandler.queueFunction(queueHandler.eventQueue, ui.message, _t)

    def postInit(self):
        self.Layout()
        field = (
            self.ask_panel.question_input
            if BeMyAI().authorized
            else self.ask_panel.messages_aria
        )
        field.SetFocus()
        cvaskargs = getattr(globalVars, "cvaskargs", None)
        if cvaskargs:
            self.ask_panel.add_message(*cvaskargs)
            globalVars.cvaskargs = None

    def on_close(self, event):
        self.Hide()


if __name__ == "__main__":
    app = wx.App()
    dialog = MainDialog()
    dialog.Bind(wx.EVT_KEY_UP, dialog.OnKeyUp)
    dialog.ShowModal()
    app.MainLoop()
