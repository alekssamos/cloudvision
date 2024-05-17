import wx

class LoginPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        email_sizer = wx.BoxSizer(wx.HORIZONTAL)
        email_label = wx.StaticText(self, label="Email:")
        self.email_input = wx.TextCtrl(self)
        email_sizer.Add(email_label, 0, wx.ALL, 5)
        email_sizer.Add(self.email_input, 1, wx.EXPAND | wx.ALL, 5)

        password_sizer = wx.BoxSizer(wx.HORIZONTAL)
        password_label = wx.StaticText(self, label="Password:")
        self.password_input = wx.TextCtrl(self, style=wx.TE_PASSWORD)
        password_sizer.Add(password_label, 0, wx.ALL, 5)
        password_sizer.Add(self.password_input, 1, wx.EXPAND | wx.ALL, 5)

        login_button = wx.Button(self, label="Login")
        login_button.Bind(wx.EVT_BUTTON, self.on_login)

        show_register_button = wx.Button(self, label="Create account")
        show_register_button.Bind(wx.EVT_BUTTON, self.on_show_register_btn)

        main_sizer.Add(email_sizer, 0, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(password_sizer, 0, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(login_button, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        main_sizer.Add(show_register_button, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        self.SetSizer(main_sizer)

    def on_login(self, event):
        event.Skip()
        email = self.email_input.GetValue()
        password = self.password_input.GetValue()
        print(f"Login: Email={email}, Password={password}")

    def on_show_register_btn(self, event):
        event.Skip()
        self.Hide()
        f=self.FindWindowByName("lrframe1")
        f.register_panel.Show()
        f.Layout()
        f.register_panel.SetFocus()

class RegisterPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        name_sizer = wx.BoxSizer(wx.HORIZONTAL)
        name_label = wx.StaticText(self, label="Name:")
        self.name_input = wx.TextCtrl(self)
        name_sizer.Add(name_label, 0, wx.ALL, 5)
        name_sizer.Add(self.name_input, 1, wx.EXPAND | wx.ALL, 5)

        surname_sizer = wx.BoxSizer(wx.HORIZONTAL)
        surname_label = wx.StaticText(self, label="Surname:")
        self.surname_input = wx.TextCtrl(self)
        surname_sizer.Add(surname_label, 0, wx.ALL, 5)
        surname_sizer.Add(self.surname_input, 1, wx.EXPAND | wx.ALL, 5)

        email_sizer = wx.BoxSizer(wx.HORIZONTAL)
        email_label = wx.StaticText(self, label="Email:")
        self.email_input = wx.TextCtrl(self)
        email_sizer.Add(email_label, 0, wx.ALL, 5)
        email_sizer.Add(self.email_input, 1, wx.EXPAND | wx.ALL, 5)

        password_sizer = wx.BoxSizer(wx.HORIZONTAL)
        password_label = wx.StaticText(self, label="Password:")
        self.password_input = wx.TextCtrl(self, style=wx.TE_PASSWORD)
        password_sizer.Add(password_label, 0, wx.ALL, 5)
        password_sizer.Add(self.password_input, 1, wx.EXPAND | wx.ALL, 5)

        register_button = wx.Button(self, label="Register")
        register_button.Bind(wx.EVT_BUTTON, self.on_register)

        show_login_button = wx.Button(self, label="Login")
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
        f=self.FindWindowByName("lrframe1")
        f.login_panel.Show()
        f.Layout()
        f.login_panel.SetFocus()

    def on_register(self, event):
        event.Skip()
        name = self.name_input.GetValue()
        surname = self.surname_input.GetValue()
        email = self.email_input.GetValue()
        password = self.password_input.GetValue()
        print(f"Register: Name={name}, Surname={surname}, Email={email}, Password={password}")

class MainDialog(wx.Dialog):
    def __init__(self, parent=None):
        super().__init__(parent=parent, title="Manage Be My Eyes Account")

        self.SetName("lrframe1")

        self.login_panel = LoginPanel(self)
        self.register_panel = RegisterPanel(self)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.login_panel, 1, wx.EXPAND)
        sizer.Add(self.register_panel, 1, wx.EXPAND)

        self.register_panel.Hide()

        self.SetSizer(sizer)
        self.Layout()


if __name__ == "__main__":
    app = wx.App()
    dialog = MainDialog()
    dialog.ShowModal()
    app.MainLoop()
