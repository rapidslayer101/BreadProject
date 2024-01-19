from base64 import b64decode
kv_payload = """# You can edit this file to change the UI. 
# To see what can be edited visit the wiki at https://kivy.org/doc/stable/api-kivy.lang.html
# Programming Guide: https://kivy.org/doc/stable/guide/lang.html

#:import WipeTransition kivy.uix.screenmanager.WipeTransition
#:import Factory kivy.factory.Factory
    
    
### Templates ### 
# editing templates will change key elements of the UI

<GreyFloatLayout@FloatLayout>:
    canvas.before:
        Color:
            rgba: app.col['bk_grey_1']
        Rectangle:
            pos: self.pos
            size: self.size    

# rounded elements
<RoundedButton@Button>
    background_color: 0,0,0,0
    size_hint: 0.3, 0.1
    canvas.before:
        Color:
            rgba: app.col['bread_purple'] if self.state == 'normal' else app.col['bread_purple_dark']
        RoundedRectangle:
            size: self.size
            pos: self.pos
            radius: [10]
            
<RoundedBackingButton@Button>
    background_color: 0,0,0,0
    canvas.before:
        Color:
            rgba: app.col['bk_grey_3'] if self.state == 'normal' else app.col['bk_grey_2']
        RoundedRectangle:
            size: self.size
            pos: self.pos
            radius: [10]
            
<RoundedTxtInp@TextInput>:
    font_size: '16dp'
    multiline: False
    halign: "center"
    hint_text_color: app.col['bread_cyan'][:3]+[0.6]
    foreground_color: app.col['bread_cyan']
    size_hint: 0.3, 0.1
    padding: [0, self.height/2.0-(self.line_height/2.0)*len(self._lines), 0, 0]
    write_tab: False
    background_color: 0,0,0,0
    cursor_color: app.col['bread_cyan']
    canvas.after:
        Color:
            rgba: 0,0,0,0
        Ellipse:
            angle_start:180
            angle_end:360
            pos:(self.pos[0]-self.size[1]/2.0, self.pos[1])
            size: (self.size[1], self.size[1])
        Ellipse:
            angle_start:360
            angle_end:540
            pos: (self.size[0]+self.pos[0]-self.size[1]/2.0, self.pos[1])
            size: (self.size[1], self.size[1])
        Color:
            rgba: app.col['bread_purple']
        Line:
            points: self.pos[0], self.pos[1], self.pos[0]+self.size[0], self.pos[1]
        Line:
            points: self.pos[0], self.pos[1]+self.size[1], self.pos[0]+self.size[0], self.pos[1]+self.size[1]
        Line:
            ellipse: self.pos[0]-self.size[1]/2.0, self.pos[1], self.size[1], self.size[1], 180, 360
        Line:
            ellipse: self.size[0]+self.pos[0]-self.size[1]/2.0, self.pos[1], self.size[1], self.size[1], 360, 540
            
<SizeLabel@Label>:  # label with a size hint
    size_hint: 0.1, 0.05
    
<ErrorPopup@Popup>:
    title: "Invalid Entry"
    size_hint: 0.32, 0.27
    GreyFloatLayout:
        Label:
            text: app.popup_text
            font_size: "16dp"
            color: app.col['orange']
            size_hint: 0.9, 0.9
            pos_hint: {"x": 0.05, "top": 1.1}
            
<TermsPopup@Popup>:
    title: "BreadClient Terms and Conditions"
    auto_dismiss: False
    size_hint: 0.75, 0.75
    GreyFloatLayout:
        ScrollView:
            size_hint: 1, 0.8
            pos_hint: {"x": 0, "top": 1}
            scroll_type: ['bars']
            GreyFloatLayout:
                size_hint_y: None
                height: root.height
                Label:
                    text: app.t_and_c
                    size_hint: 0.9, 0.9
                    pos_hint: {"x": 0.05, "top": 1.2}
        RoundedButton:
            text: 'Close'
            size_hint: 0.4, 0.1
            pos_hint: {"x": 0.3, "top": 0.15}
            on_release: root.dismiss()
               
<InvalidCodePopup@Popup>:
    title: "Claim Code"
    auto_dismiss: False
    size_hint: 0.6, 0.6
    GreyFloatLayout:
        Label:
            text: app.popup_text
            size_hint: 0.9, 0.9
            pos_hint: {"x": 0.05, "top": 1.2}
        RoundedButton:
            text: 'Close'
            size_hint: 0.3, 0.1
            pos_hint: {"x": 0.35, "top": 0.2}
            on_release: root.dismiss()
            
<SuccessPopup@Popup>:
    title: "Success"
    size_hint: 0.32, 0.27
    GreyFloatLayout:
        Label:
            text: app.popup_text
            font_size: "16dp"
            color: app.col['green']
            size_hint: 0.9, 0.9
            pos_hint: {"x": 0.05, "top": 1.1}
            
# colored labels
<GreyLabel@SizeLabel>
    canvas.before:
        Color:
            rgba: app.col['grey']
        Rectangle:
            size: self.size
            pos: self.pos

<YellowLabel@SizeLabel>
    color: 0,0,0,1
    size_hint: 0.1, 0.05
    canvas.before:
        Color:
            rgba: app.col['yellow']
        Rectangle:
            size: self.size
            pos: self.pos

<OrangeLabel@YellowLabel>
    canvas.before:
        Color:
            rgba: app.col['orange']
        Rectangle:
            size: self.size
            pos: self.pos
            
<GreenLabel@YellowLabel>
    canvas.before:
        Color:
            rgba: app.col['green']
        Rectangle:
            size: self.size
            pos: self.pos
            
<BackingLabel@SizeLabel>:
    canvas.before:
        Color: 
            rgba: app.col['bk_grey_3']
        RoundedRectangle:
            size: self.size
            pos: self.pos
            radius: [10]
    

### Screens ###

<AttemptConnection>:
    GreyFloatLayout:
        Label:
            text: "Attempting to connect to server..."
            font_size: '18dp'
            size_hint: 0.3, 0.1
            pos_hint: {"x": 0.35, "top": 0.6}

<IpSet>:
    GreyFloatLayout:
        SizeLabel:
            text: "Enter server IP address"
            pos_hint: {"x": 0.45, "top": 0.8}
        RoundedTxtInp:
            hint_text: "0.0.0.0:1337"
            pos_hint: {"x": 0.35, "top": 0.65}
            on_text_validate: root.try_connect(self.text)
        RoundedButton:
            text: "Connect"
            pos_hint: {"x": 0.35, "top": 0.45}
            on_press: root.try_connect()

<LogInOrSignUp>:
    GreyFloatLayout:
        SizeLabel:
            text: "Welcome to BreadClient!"
            font_size: "18dp"
            pos_hint: {"x": 0.45, "top": 0.8}
        RoundedButton:
            text: "Login"
            pos_hint: {"x": 0.35, "top": 0.55}
            on_release:
                root.manager.current = 'ReCreateKey'
                root.manager.transition.direction = "left"
        RoundedButton:
            text: "Create Account"
            pos_hint: {"x": 0.35, "top": 0.35}
            on_release:
                root.manager.current = 'CreateKey'
                root.manager.transition.direction = "left"

<KeyUnlock>:
    pwd: pwd
    GreyFloatLayout:
        SizeLabel:
            text: root.passcode_prompt_text
            pos_hint: {"x": 0.45, "top": 0.75}
        RoundedTxtInp:
            id: pwd
            hint_text: "Password"
            password: True
            pos_hint: {"x": 0.35, "top": 0.65}
            on_text_validate: root.login()
        RoundedButton:
            text: "LOGIN"
            pos_hint: {"x": 0.35, "top": 0.5}
            on_release: root.login()

<CreateKey>:
    GreyFloatLayout:
        Label:
            text: root.pass_code_text
            size_hint: 0.3, 0.1
            pos_hint: {"x": 0.35, "top": 0.9}
        Label:
            text: root.pin_code_text
            size_hint: 0.3, 0.1
            pos_hint: {"x": 0.35, "top": 0.8}
        Label:
            text: f"Your Account Key and Pin are REQUIRED to access your account on another device.\\nIf you lose these YOU WONT be able to login to your account or recover it.\\nYou may want to write these down or SAVE TO A USB on the next screen."
            color: (37/255, 190/255, 150/255, 1)
            size_hint: 0.3, 0.1
            pos_hint: {"x": 0.35, "top": 0.7}
        Label:
            text: root.rand_confirm_text
            size_hint: 0.3, 0.1
            pos_hint: {"x": 0.35, "top": 0.6}
        Button:
            text: "View Terms and Conditions"
            color: app.col['link_blue']
            background_color: (1/255, 1/255, 1/255,0)
            size_hint: 0.1, 0.05
            pos_hint: {"x": 0.45, "top": 0.51}
            on_release: Factory.TermsPopup().open()
        RoundedTxtInp:
            pos_hint: {"x": 0.35, "top": 0.4}
            on_text: root.continue_confirmation(self.text)
        YellowLabel:
            text: "User Keys >>"
            pos_hint: {"x": 0.3,  "top": 1}
        GreyLabel:
            text: "CAPTCHA >>"
            pos_hint: {"x": 0.4,  "top": 1}
        GreyLabel:
            text: "Password >>"
            pos_hint: {"x": 0.5,  "top": 1}
        GreyLabel:
            text: "2FA"
            pos_hint: {"x": 0.6,  "top": 1}
            
<UsbSetup>:
    GreyFloatLayout:
        Label:
            text: root.usb_text
            color: (37/255, 190/255, 150/255, 1)
            size_hint: 0.3, 0.1
            pos_hint: {"x": 0.35, "top": 0.7}
        RoundedButton:
            text: root.skip_text
            pos_hint: {"x": 0.35, "top": 0.45}
            on_press:
                root.manager.current = 'Captcha'
                root.manager.transition.direction = "left"
        OrangeLabel:
            text: "User Keys >>"
            pos_hint: {"x": 0.3,  "top": 1}
        GreyLabel:
            text: "CAPTCHA >>"
            pos_hint: {"x": 0.4,  "top": 1}
        GreyLabel:
            text: "Password >>"
            pos_hint: {"x": 0.5,  "top": 1}
        GreyLabel:
            text: "2FA"
            pos_hint: {"x": 0.6,  "top": 1}
                    
<ReCreateKey>:
    name_or_uid: name_or_uid
    pass_code: pass_code
    pin_code: pin_code
    GreyFloatLayout:
        Button:
            text: "<< Back"
            size_hint: 0.1, 0.05
            pos_hint: {"x": 0, "top": 1}
            on_press:
                root.manager.current = 'LogInOrSignUp'
                root.manager.transition.direction = "right"
        Button:
            id: load_from_usb_button
            text: root.load_text
            size_hint: 0.12, 0.05
            pos_hint: {"x": 0.88, "top": 1}
            on_press: root.load_from_usb()
        Label:
            text: "Enter Username or User ID (UID)"
            size_hint: 0.3, 0.1
            pos_hint: {"x": 0.35, "top": 0.9}
        RoundedTxtInp:
            id: name_or_uid
            hint_text: "Username or UID"
            size_hint: 0.3, 0.05
            pos_hint: {"x": 0.35, "top": 0.8}
            on_text: 
                self.text = self.text[:28]
                root.toggle_button()
            on_text_validate: pass_code.focus = True
        Label:
            text: "Enter Account Key"
            size_hint: 0.3, 0.1
            pos_hint: {"x": 0.35, "top": 0.7}
        RoundedTxtInp:
            id: pass_code
            hint_text: "Account Key"
            size_hint: 0.3, 0.05
            password: True
            pos_hint: {"x": 0.35, "top": 0.6}
            on_text: 
                self.text = self.text[:15].upper().replace("-", "") 
                root.toggle_button()
            on_text_validate: pin_code.focus = True
        Label:
            text: "Enter Account Pin"
            size_hint: 0.3, 0.1
            pos_hint: {"x": 0.35, "top": 0.5}
        RoundedTxtInp:
            id: pin_code
            hint_text: "Account Pin"
            size_hint: 0.3, 0.05
            password: True
            pos_hint: {"x": 0.35, "top": 0.4}
            on_text: root.toggle_button()
            on_text_validate: root.start_regeneration()
        RoundedButton:
            id: start_regen_button
            text: "Continue"
            disabled: True
            pos_hint: {"x": 0.35, "top": 0.25}
            on_press: root.start_regeneration()
        Button:
            text: "<< Back"
            size_hint: 0.1, 0.05
            pos_hint: {"x": 0, "top": 1}
            on_press:
                root.manager.current = 'LogInOrSignUp'
                root.manager.transition.direction = "right"
        YellowLabel:
            text: "User Keys >>"
            pos_hint: {"x": 0.3,  "top": 1}
        GreyLabel:
            text: "CAPTCHA >>"
            pos_hint: {"x": 0.4,  "top": 1}
        GreyLabel:
            text: "Password >>"
            pos_hint: {"x": 0.5,  "top": 1}
        GreyLabel:
            text: "2FA"
            pos_hint: {"x": 0.6,  "top": 1}
    
<ReCreateGen>:
    GreyFloatLayout:
        Label:
            text: root.gen_left_text
            size_hint: 0.3, 0.1
            pos_hint: {"x": 0.35, "top": 0.8}
        OrangeLabel:
            text: "User Keys >>"
            pos_hint: {"x": 0.3,  "top": 1}
        GreyLabel:
            text: "CAPTCHA >>"
            pos_hint: {"x": 0.4,  "top": 1}
        GreyLabel:
            text: "Password >>"
            pos_hint: {"x": 0.5,  "top": 1}
        GreyLabel:
            text: "2FA"
            pos_hint: {"x": 0.6,  "top": 1}

<Captcha>:
    captcha_inp: captcha_inp
    GreyFloatLayout:
        Label:
            text: root.captcha_prompt_text
            size_hint: 0.3, 0.1
            pos_hint: {"x": 0.35, "top": 0.85}
        Image:
            id: captcha_image
            source: 'resources/blank_captcha.jpg'
            pos_hint: {"x": 0, "top": 1.15}
        RoundedTxtInp:
            id: captcha_inp
            pos_hint: {"x": 0.35, "top": 0.5}
            on_text: self.text = self.text[:10].upper()
            on_text_validate: root.try_captcha()
        RoundedButton:
            text: "Next"
            pos_hint: {"x": 0.35, "top": 0.35}
            on_press: root.try_captcha()
        GreenLabel:
            text: "User Keys >>"
            pos_hint: {"x": 0.3,  "top": 1}
        YellowLabel:
            text: "CAPTCHA >>"
            pos_hint: {"x": 0.4,  "top": 1}
        GreyLabel:
            text: "Password >>"
            pos_hint: {"x": 0.5,  "top": 1}
        GreyLabel:
            text: "2FA"
            pos_hint: {"x": 0.6,  "top": 1}

<NacPass>:
    nac_password_1: nac_password_1
    nac_password_2: nac_password_2
    GreyFloatLayout:
        Label:
            text: "Enter new password"
            size_hint: 0.3, 0.1
            pos_hint: {"x": 0.35, "top": 0.8}
        RoundedTxtInp:
            id: nac_password_1
            password: True
            pos_hint: {"x": 0.35, "top": 0.7}
            on_text_validate: nac_password_2.focus = True
        Label:
            text: "Repeat password"
            size_hint: 0.3, 0.1
            pos_hint: {"x": 0.35, "top": 0.6}
        RoundedTxtInp:
            id: nac_password_2
            password: True
            pos_hint: {"x": 0.35, "top": 0.5}
            on_text_validate: root.set_nac_password()
        RoundedButton:
            text: "Next"
            pos_hint: {"x": 0.35, "top": 0.3}
            on_press: root.set_nac_password()
        GreenLabel:
            text: "User Keys >>"
            pos_hint: {"x": 0.3,  "top": 1}
        GreenLabel:
            text: "CAPTCHA >>"
            pos_hint: {"x": 0.4,  "top": 1}
        YellowLabel:
            text: "Password >>"
            pos_hint: {"x": 0.5,  "top": 1}
        GreyLabel:
            text: "2FA"
            pos_hint: {"x": 0.6,  "top": 1}
            
<AccountPicker>:
    GreyFloatLayout:
        Label:
            text: "Pick Account"
            size_hint: 0.3, 0.1
            pos_hint: {"x": 0.35, "top": 0.8}
                    
<LogUnlock>:
    pwd: pwd
    GreyFloatLayout:
        Label:
            text: root.passcode_prompt_text
            size_hint: 0.3, 0.1
            pos_hint: {"x": 0.35, "top": 0.8}
        RoundedTxtInp:
            id: pwd
            password: True
            pos_hint: {"x": 0.35, "top": 0.65}
            on_text_validate: root.login()
        RoundedButton:
            text: "LOGIN"
            pos_hint: {"x": 0.35, "top": 0.5}
            on_release:
                root.login()
        GreenLabel:
            text: "User Keys >>"
            pos_hint: {"x": 0.3,  "top": 1}
        GreenLabel:
            text: "CAPTCHA >>"
            pos_hint: {"x": 0.4,  "top": 1}
        YellowLabel:
            text: "Password >>"
            pos_hint: {"x": 0.5,  "top": 1}
        GreyLabel:
            text: "2FA"
            pos_hint: {"x": 0.6,  "top": 1}

<TwoFacSetup>:
    two_fac_code: two_fac_code
    GreyFloatLayout:
        Label:
            text: root.two_fac_wait_text
            size_hint: 0.3, 0.1
            pos_hint: {"x": 0.35, "top": 0.93}
        AsyncImage:
            id: two_fac_qr
            source: 'resources/blank_qr.png'
            pos_hint: {"x": 0, "top": 1.10}
        RoundedTxtInp:
            id: two_fac_code
            hint_text: "2FA code"
            size_hint: 0.3, 0.05
            pos_hint: {"x": 0.35, "top": 0.34}
            on_text: self.text = self.text[:6].replace(" ", "")
            on_text_validate: root.confirm_2fa()
        RoundedButton:
            text: "Confirm"
            pos_hint: {"x": 0.35, "top": 0.25}
            on_press: root.confirm_2fa()
        GreenLabel:
            text: "User Keys >>"
            pos_hint: {"x": 0.3,  "top": 1}
        GreenLabel:
            text: "CAPTCHA >>"
            pos_hint: {"x": 0.4,  "top": 1}
        GreenLabel:
            text: "Password >>"
            pos_hint: {"x": 0.5,  "top": 1}
        YellowLabel:
            text: "2FA"
            pos_hint: {"x": 0.6,  "top": 1}
            
<TwoFacLog>:
    two_fac_code: two_fac_code
    GreyFloatLayout:
        Label:
            text: "Enter 2FA code"
            size_hint: 0.3, 0.1
            pos_hint: {"x": 0.35, "top": 0.8}
        RoundedTxtInp:
            id: two_fac_code
            input_filter: 'int'
            pos_hint: {"x": 0.35, "top": 0.65}
            on_text: self.text = self.text[:6].replace(" ", "")
            on_text_validate: root.confirm_2fa()
        RoundedButton:
            text: "Confirm"
            pos_hint: {"x": 0.35, "top": 0.4}
            on_press: root.confirm_2fa()
        GreenLabel:
            text: "User Keys >>"
            pos_hint: {"x": 0.3,  "top": 1}
        GreenLabel:
            text: "CAPTCHA >>"
            pos_hint: {"x": 0.4,  "top": 1}
        GreenLabel:
            text: "Password >>"
            pos_hint: {"x": 0.5,  "top": 1}
        YellowLabel:
            text: "2FA"
            pos_hint: {"x": 0.6,  "top": 1}
            
<HomeButton@Button>:
    text: "Home"
    size_hint: 0.09, 0.05
    pos_hint: {"x": 0.01, "top": 0.99}
    
<ConsoleButton@Button>:
    text: "Console"
    size_hint: 0.14, 0.05
    pos_hint: {"x": 0.1, "top": 0.99}
    
<StoreButton@Button>:
    text: "Store"
    size_hint: 0.14, 0.05
    pos_hint: {"x": 0.24, "top": 0.99}

<PlaceholderButton@Button>:
    text: "Placeholder"
    size_hint: 0.14, 0.05
    pos_hint: {"x": 0.38, "top": 0.99}
    
<MeshButton@Button>:
    text: "GPU Mesh"
    size_hint: 0.10, 0.05
    pos_hint: {"x": 0.56, "top": 0.99}
    
<SettingsButton@Button>:
    text: "Settings/Info"
    size_hint: 0.11, 0.05
    pos_hint: {"x": 0.66, "top": 0.99}
    
<R_coin_label@BackingLabel>:
    color: app.col['rcoin_orange']
    pos_hint: {"x": 0.89, "top": 0.99}
    
<D_coin_label@BackingLabel>:
    color: app.col['dcoin_blue']
    pos_hint: {"x": 0.78, "top": 0.99}
            
<Home>:
    GreyFloatLayout:
        HomeButton:
            disabled: True
        ConsoleButton:
            on_press: 
                root.manager.transition = WipeTransition(clearcolor=app.col['bk_grey_1'])
                root.manager.current = 'Console'
        StoreButton:
            on_press: 
                root.manager.transition = WipeTransition(clearcolor=app.col['bk_grey_1'])
                root.manager.current = 'Store'
        PlaceholderButton:
            #on_press: 
                #root.manager.transition = WipeTransition(clearcolor=app.col['bk_grey_1'])
                #root.manager.current = 'Games'
        MeshButton:
            on_press: 
                root.manager.transition = WipeTransition(clearcolor=app.col['bk_grey_1'])
                root.manager.current = 'Mesh'
        SettingsButton:
            on_press: 
                root.manager.transition = WipeTransition(clearcolor=app.col['bk_grey_1'])
                root.manager.current = 'Settings'
        R_coin_label:
            text: root.r_coins
        D_coin_label:
            text: root.d_coins
        BackingLabel:
            size_hint: 0.32, 0.6
            pos_hint: {"x": 0.01, "top": 0.92}
        Label:
            text: "Blank Canvas"
            size_hint: 0.1, 0.1
            pos_hint: {"x": 0.12, "top": 0.92}
        BackingLabel:
            text: root.welcome_text
            size_hint: 0.32, 0.15
            pos_hint: {"x": 0.34, "top": 0.92}
        BackingLabel:
            size_hint: 0.32, 0.6
            pos_hint: {"x": 0.34, "top": 0.76}
        SizeLabel:
            text: "Latest News"
            pos_hint: {"x": 0.45, "top": 0.74}
        SizeLabel:
            text: "No news."
            pos_hint: {"x": 0.45, "top": 0.58}
        BackingLabel:
            size_hint: 0.32, 0.13
            pos_hint: {"x": 0.34, "top": 0.15}
        BackingLabel:
            size_hint: 0.32, 0.23
            pos_hint: {"x": 0.67, "top": 0.92}
        SizeLabel:
            #text: "Level 0"
            text: "Blank canvas"
            pos_hint: {"x": 0.78, "top": 0.9}
        Label:
            id: level_bar
            size_hint: 0.29, 0.05
            pos_hint: {"x": 0.69, "top": 0.83}
        SizeLabel:
            id: level_bar_text
            color: (0, 0, 0, 1)
            text: "1/100 XP"
            pos_hint: {"x": 0.78, "top": 0.83}
        BackingLabel:
            size_hint: 0.32, 0.66
            pos_hint: {"x": 0.67, "top": 0.68}
        SizeLabel:
            text: "Request History (This session)"
            pos_hint: {"x": 0.78, "top": 0.66}
        ScrollView:
            id: request_hist_scroll
            size_hint: 0.32, 0.53
            pos_hint: {"x": 0.67, "top": 0.59}
            scroll_type: ['bars']
            FloatLayout:
                id: request_hist
                canvas.before:
                    Color:
                        rgba: app.col['bk_grey_2']
                    Rectangle:
                        pos: self.pos
                        size: self.size    
                size_hint_y: None
                height: root.height
        BackingLabel:
            size_hint: 0.32, 0.29
            pos_hint: {"x": 0.01, "top": 0.31}
        SizeLabel:
            text: "Blank Canvas"
            pos_hint: {"x": 0.12, "top": 0.29}
            
<Console>:
    public_room_inp: public_room_inp
    GreyFloatLayout:
        HomeButton:
            on_press: root.manager.current = 'Home'
        ConsoleButton:
            disabled: True
        StoreButton:
            on_press: root.manager.current = 'Store'
        PlaceholderButton:
            #on_press: root.manager.current = 'Games'
        MeshButton:
            on_press: root.manager.current = 'Mesh'
        SettingsButton:
            on_press: root.manager.current = 'Settings'
        R_coin_label:
            text: root.r_coins
        D_coin_label:
            text: root.d_coins
        BackingLabel:
            size_hint: 0.5, 0.88
            pos_hint: {"x": 0.25, "top": 0.9}
        Label:
            text: "Console" 
            size_hint: 0.3, 0.1
            pos_hint: {"x": 0.35, "top": 0.9}
        ScrollView:
            id: public_room_scroll
            size_hint: 0.5, 0.62
            pos_hint: {"x": 0.25, "top": 0.8}
            scroll_type: ['bars']
            FloatLayout:
                id: public_chat
                canvas.before:
                    Color:
                        rgba: app.col['bk_grey_2']
                    Rectangle:
                        pos: self.pos
                        size: self.size    
                size_hint_y: None
                height: root.height
        RoundedTxtInp:
            id: public_room_inp
            size_hint: 0.4, 0.1
            pos_hint: {"x": 0.3, "top": 0.15}
            text_validate_unfocus: False
            on_text_validate: root.send_public_message()   
            
<Store>:
    GreyFloatLayout:
        HomeButton:
            on_press: root.manager.current = 'Home'
        ConsoleButton:
            on_press: root.manager.current = 'Console'
        StoreButton:
            disabled: True
        PlaceholderButton:
            #on_press: root.manager.current = 'Games'
        MeshButton:
            on_press: root.manager.current = 'Mesh'
        SettingsButton:
            on_press: root.manager.current = 'Settings'
        R_coin_label:
            text: root.r_coins
        D_coin_label:
            text: root.d_coins
        
<Games>:
    GreyFloatLayout:
        HomeButton:
            on_press: root.manager.current = 'Home'
        ConsoleButton:
            on_press: root.manager.current = 'Console'
        StoreButton:
            on_press: root.manager.current = 'Store'
        PlaceholderButton:
            disabled: True
        MeshButton:
            on_press: root.manager.current = 'Mesh'
        SettingsButton:
            on_press: root.manager.current = 'Settings'
        R_coin_label:
            text: root.r_coins
        D_coin_label:
            text: root.d_coins
            
<Mesh>:
    GreyFloatLayout:
        HomeButton:
            on_press: root.manager.current = 'Home'
        ConsoleButton:
            on_press: root.manager.current = 'Console'
        StoreButton:
            on_press: root.manager.current = 'Store'
        PlaceholderButton:
            #on_press: root.manager.current = 'Games'
        MeshButton:
            disabled: True
        SettingsButton:
            on_press: root.manager.current = 'Settings'
        R_coin_label:
            text: root.r_coins
        D_coin_label:
            text: root.d_coins
        Label:
            text: "GPU Mesh Network (Coming Soon)"
            size_hint: 0.3, 0.1
            pos_hint: {"x": 0.35, "top": 0.7}
            
<Settings>:
    uname_to: uname_to
    n_pass: n_pass
    GreyFloatLayout:
        HomeButton:
            on_press: root.manager.current = 'Home'
        ConsoleButton:
            on_press: root.manager.current = 'Console'
        StoreButton:
            on_press: root.manager.current = 'Store'
        PlaceholderButton:
            #on_press: root.manager.current = 'Games'
        MeshButton:
            on_press: root.manager.current = 'Mesh'
        SettingsButton:
            disabled: True
        R_coin_label:
            text: root.r_coins
        D_coin_label:
            text: root.d_coins
        BackingLabel:
            size_hint: 0.36, 0.5
            pos_hint: {"x": 0.01, "top": 0.92}
        SizeLabel:
            text: "User Settings"
            pos_hint: {"x": 0.14, "top": 0.9}
        SizeLabel:
            text: f"Name:"
            pos_hint: {"x": -0.01, "top": 0.82}
        RoundedTxtInp:
            id: uname_to
            text: root.uname[:-4]
            size_hint: 0.14, 0.05
            pos_hint: {"x": 0.08, "top": 0.82}
            on_text: self.text = self.text.replace("  ", " ").replace("#", "")[:24]
            on_text_validate: root.change_name()
        RoundedButton:
            text: "Change"
            size_hint: 0.05, 0.05
            pos_hint: {"x": 0.31, "top": 0.82}
            on_press: root.change_name()
        SizeLabel:
            text: f"Tag: {root.uname[-4:]}"
            pos_hint: {"x": 0.22, "top": 0.82}
        SizeLabel:
            text: f"UID: {root.uid}"
            pos_hint: {"x": 0.14, "top": 0.73}
        SizeLabel:
            text: f"Change Password"
            pos_hint: {"x": 0.14, "top": 0.65}
        RoundedTxtInp:
            id: n_pass
            hint_text: f"Old Password"
            password: True
            size_hint: 0.23, 0.05
            pos_hint: {"x": 0.05, "top": 0.6}
        RoundedButton:
            text: "Change"
            size_hint: 0.05, 0.05
            pos_hint: {"x": 0.31, "top": 0.6}
            on_press: root.change_pass()
        RoundedBackingButton:
            size_hint: 0.25, 0.5
            pos_hint: {"x": 0.38, "top": 0.92}
            on_press: root.manager.current = 'ColorSettings'
        SizeLabel:
            text: "Color settings"
            pos_hint: {"x": 0.455, "top": 0.9}
        AsyncImage:
            source: "https://i.pinimg.com/originals/46/df/8a/46df8ac05dae334c4b473987f2d90574.png"
            size_hint: 0.2, 0.35
            pos_hint: {"x": 0.405, "top": 0.83}
        RoundedButton:
            text: "T's and C's"
            size_hint: 0.1, 0.05
            pos_hint: {"x": 0.89, "top": 0.07}
            on_press: Factory.TermsPopup().open()
            

<RoundedColorButton@RoundedButton>:
    size_hint: 0.1, 0.05
    
<ColorSettings>:
    GreyFloatLayout:
        Button:
            text: "<< Settings"
            size_hint: 0.1, 0.05
            pos_hint: {"x": 0, "top": 1}
            on_press: root.manager.current = 'Settings'
        SizeLabel:
            text: "BreadClient Purple:"
            pos_hint: {"x": 0.1, "top": 0.96}
        RoundedColorButton:
            id: bread_purple_btn
            pos_hint: {"x": 0.22, "top": 0.96}
            on_press: root.select_color("bread_purple")
            canvas.before:
                Color:
                    rgba: app.col['bread_purple']
                RoundedRectangle
                    pos: self.pos
                    size: self.size
                    radius: [10]
        SizeLabel:
            text: "BreadClient Purple Dark:"
            pos_hint: {"x": 0.1, "top": 0.9}
        RoundedColorButton:
            id: bread_purple_dark_btn
            pos_hint: {"x": 0.22, "top": 0.9}
            on_press: root.select_color("bread_purple_dark")
            canvas.before:
                Color:
                    rgba: app.col['bread_purple_dark']
                RoundedRectangle
                    pos: self.pos
                    size: self.size
                    radius: [10]
        SizeLabel:
            text: "BreadClient Cyan:"
            pos_hint: {"x": 0.1, "top": 0.84}
        RoundedColorButton:
            id: bread_cyan_btn
            pos_hint: {"x": 0.22, "top": 0.84}
            on_press: root.select_color("bread_cyan")
            canvas.before:
                Color:
                    rgba: app.col['bread_cyan']
                RoundedRectangle
                    pos: self.pos
                    size: self.size
                    radius: [10]
        SizeLabel:
            text: "R Coin Orange:"
            pos_hint: {"x": 0.1, "top": 0.78}
        RoundedColorButton:
            id: rcoin_orange_btn
            pos_hint: {"x": 0.22, "top": 0.78}
            on_press: root.select_color("rcoin_orange")
            canvas.before:
                Color:
                    rgba: app.col['rcoin_orange']
                RoundedRectangle
                    pos: self.pos
                    size: self.size
                    radius: [10]
        SizeLabel:
            text: "D Coin Blue:"
            pos_hint: {"x": 0.1, "top": 0.72}
        RoundedColorButton:
            id: dcoin_blue_btn
            pos_hint: {"x": 0.22, "top": 0.72}
            on_press: root.select_color("dcoin_blue")
            canvas.before:
                Color:
                    rgba: app.col['dcoin_blue']
                RoundedRectangle
                    pos: self.pos
                    size: self.size
                    radius: [10]
        SizeLabel:
            text: "Link Blue:"
            pos_hint: {"x": 0.1, "top": 0.66}
        RoundedColorButton:
            id: link_blue_btn
            pos_hint: {"x": 0.22, "top": 0.66}
            on_press: root.select_color("link_blue")
            canvas.before:
                Color:
                    rgba: app.col['link_blue']
                RoundedRectangle
                    pos: self.pos
                    size: self.size
                    radius: [10]
        SizeLabel:
            text: "Green:"
            pos_hint: {"x": 0.1, "top": 0.6}
        RoundedColorButton:
            id: green_btn
            pos_hint: {"x": 0.22, "top": 0.6}
            on_press: root.select_color("green")
            canvas.before:
                Color:
                    rgba: app.col['green']
                RoundedRectangle
                    pos: self.pos
                    size: self.size
                    radius: [10]
        SizeLabel:
            text: "Yellow:"
            pos_hint: {"x": 0.1, "top": 0.54}
        RoundedColorButton:
            id: yellow_btn
            pos_hint: {"x": 0.22, "top": 0.54}
            on_press: root.select_color("yellow")
            canvas.before:
                Color:
                    rgba: app.col['yellow']
                RoundedRectangle
                    pos: self.pos
                    size: self.size
                    radius: [10]   
        SizeLabel:
            text: "Orange:"
            pos_hint: {"x": 0.1, "top": 0.48}
        RoundedColorButton:
            id: orange_btn
            pos_hint: {"x": 0.22, "top": 0.48}
            on_press: root.select_color("orange")
            canvas.before:
                Color:
                    rgba: app.col['orange']
                RoundedRectangle
                    pos: self.pos
                    size: self.size
                    radius: [10]
        SizeLabel:
            text: "Red:"
            pos_hint: {"x": 0.1, "top": 0.42}
        RoundedColorButton:
            id: red_btn
            pos_hint: {"x": 0.22, "top": 0.42}
            on_press: root.select_color("red")
            canvas.before:
                Color:
                    rgba: app.col['red']
                RoundedRectangle
                    pos: self.pos
                    size: self.size
                    radius: [10]
        SizeLabel:
            text: "Grey:"
            pos_hint: {"x": 0.1, "top": 0.36}
        RoundedColorButton:
            id: grey_btn
            pos_hint: {"x": 0.22, "top": 0.36}
            on_press: root.select_color("grey")
            canvas.before:
                Color:
                    rgba: app.col['grey']
                RoundedRectangle
                    pos: self.pos
                    size: self.size
                    radius: [10]
        SizeLabel:
            text: "Backing Grey 1:"
            pos_hint: {"x": 0.1, "top": 0.30}
        RoundedColorButton:
            id: bk_grey_1_btn
            pos_hint: {"x": 0.22, "top": 0.30}
            on_press: root.select_color("bk_grey_1")
            canvas.before:
                Color:
                    rgba: app.col['bk_grey_1']
                RoundedRectangle
                    pos: self.pos
                    size: self.size
                    radius: [10]
        SizeLabel:
            text: "Backing Grey 2:"
            pos_hint: {"x": 0.1, "top": 0.24}
        RoundedColorButton:
            id: bk_grey_2_btn
            pos_hint: {"x": 0.22, "top": 0.24}
            on_press: root.select_color("bk_grey_2")
            canvas.before:
                Color:
                    rgba: app.col['bk_grey_2']
                RoundedRectangle
                    pos: self.pos
                    size: self.size
                    radius: [10]
        SizeLabel:
            text: "Backing Grey 3:"
            pos_hint: {"x": 0.1, "top": 0.18}
        RoundedColorButton:
            id: bk_grey_3_btn
            pos_hint: {"x": 0.22, "top": 0.18}
            on_press: root.select_color("bk_grey_3")
            canvas.before:
                Color:
                    rgba: app.col['bk_grey_3']
                RoundedRectangle
                    pos: self.pos
                    size: self.size
                    radius: [10]
        RoundedColorButton:
            text: "Reset All"
            pos_hint: {"x": 0.05, "top": 0.1}
            on_press: root.reset_colors()
            canvas.before:
                Color:
                    rgba: app.col['red']
                RoundedRectangle
                    pos: self.pos
                    size: self.size
                    radius: [10]                   
        RoundedColorButton:
            text: "Reset Current"
            pos_hint: {"x": 0.16, "top": 0.1}
            on_press: root.reset_colors("selected")
            canvas.before:
                Color:
                    rgba: app.col['orange']
                RoundedRectangle
                    pos: self.pos
                    size: self.size
                    radius: [10]                    
        RoundedColorButton:
            text: "Apply Colors"
            pos_hint: {"x": 0.27, "top": 0.1}
            on_press: root.reload()
            canvas.before:
                Color:
                    rgba: app.col['green']
                RoundedRectangle
                    pos: self.pos
                    size: self.size
                    radius: [10]                   
        RoundedColorButton:
            text: "Save Colors"
            pos_hint: {"x": 0.38, "top": 0.1}
            on_press: root.save_colors()
            canvas.before:
                Color:
                    rgba: app.col['green']
                RoundedRectangle
                    pos: self.pos
                    size: self.size
                    radius: [10]
        RoundedColorButton:
            text: "Purple"
            pos_hint: {"x": 0.54, "top": 0.1}
            on_press: root.default_theme("purple")
            canvas.before:
                Color:
                    rgba: [104/255, 84/255, 252/255, 1]
                RoundedRectangle
                    pos: self.pos
                    size: self.size
                    radius: [10]
        RoundedColorButton:
            text: "Pink"
            pos_hint: {"x": 0.65, "top": 0.1}
            on_press: root.default_theme("pink")
            canvas.before:
                Color:
                    rgba: [1.0, 0.27843, 0.44706, 1.0]
                RoundedRectangle
                    pos: self.pos
                    size: self.size
                    radius: [10]     
        RoundedColorButton:
            text: "Green"
            pos_hint: {"x": 0.76, "top": 0.1}
            on_press: root.default_theme("green")
            canvas.before:
                Color:
                    rgba: [0.0, 0.62745, 0.44314, 1.0]
                RoundedRectangle
                    pos: self.pos
                    size: self.size
                    radius: [10]
        RoundedColorButton:
            text: "Lime"
            pos_hint: {"x": 0.87, "top": 0.1}
            on_press: root.default_theme("lime")
            canvas.before:
                Color:
                    rgba: [0.60358, 0.75294, 0.22389, 1.0]
                RoundedRectangle
                    pos: self.pos
                    size: self.size
                    radius: [10]                            
        ColorPicker:
            id: color_picker
            size_hint: 0.6, 0.8
            pos_hint: {"x": 0.4, "top": 0.95}
            on_color: root.change_color()
            canvas.before:
                Color:
                    rgba: [0, 0, 0, 0]
                RoundedRectangle
                    pos: self.pos
                    size: self.size
                    radius: [10]
        
<Reloading>
    GreyFloatLayout:
        SizeLabel:
            text: root.reload_text
            font_size: "20dp"
            pos_hint: {"x": 0.45, "top": 0.65}
        
"""


def kv():
    with open("resources/bread.kv", "w", encoding="utf-8") as f:
        f.write(kv_payload)


def t_and_c():  # iloominAI bread client terms and conditions
    return """
Section 1 - Conditions for these Terms and Conditions:
1.1 - iloominAI can make changes to the Terms and Conditions at any time without prior notice.
        These changes can be for any section or condition.
1.2 - If a below term implies a term that is not listed, the implied term is to be considered as a part of the Terms and Conditions.

Section 2 -  General Terms:
2.1 - iloominAI is not responsible for any damage caused to a user's device or account due to the use of the bread client.

Section 3 -  Monetary Terms:
3.1 - iloominAI is not responsible for any loss of money or currency due to the use of the bread client and its services."""


def w_images():
    blank_qr = "iVBORw0KGgoAAAANSUhEUgAAASwAAAEsCAYAAAB5fY51AAAAAXNSR0IArs4c6QAADktJREFUeF7t3ety3EQQBlD7/d85S5EUJCnH8" \
               "UiaS18OP0Ga6Tnd+la7oeD99Xq93vxFgACBBALvAitBl5RIgMB3AYFlEJIL/PsF4T35GZQ/KiCwRqVcR4DAcQGBdbwFCrgu4K3qul" \
               "mNO4oGloGuMZ5OQeB3gaKBpc0EOgvU/cAWWJ3n2tkJJBMQWMkaplwCnQUEVpju132ND0OskPQCAit9Cx2AQB8BgfWh1950+oy/k2Y" \
               "TEFjZOqZeAo0FBFbj5js6gWwCAitbx9RLoLGAwGrcfEcnkE1AYGXrmHoJlBQY+8MugVWy+Q5FoKaAwKrZV6ciUFLg08Aae0EraeJQ" \
               "BAiMCBwICW9YI41xDQECIQQEVog2KGKnwIEXg53HK72XwCrd3gmHO/x0H95+AqAlZgoIrJma1iJAYKmAwFrKa3ECBGYKCKyZmtYiQ" \
               "GCpgMBaymtxAgRmCgismZpX1vJr8hUt10YX2DTPAiv6IKiPAIH/BQTWpk+GtTNX4hBriUZXRzkqdeQ6gXWE3aYzBWTMTM3Da31o5u" \
               "9/Q2Ad7o/t/xUQOeZgTEBgjTm5igCBAAICK0ATlECAwJiAwBpzchWBpAK1vm4LrKRjqGwCHQUEVseuRz1zrZeBqMqp6xJYqduneAK" \
               "9BNYFlk/Lv08Sn15PmtNOEVgXWFPKswgBAgR+CgisLNPgjSxLp9S5UEBgLcS1NAECcwUE1lxPqxEgsFCgQWD5LrVwfixNYKtAg8Da" \
               "6mkzAu0Edr4SCKx24xXxwDtHPuL51TQqILBGpVx3XECsHW/B8QIE1vEWKIBARYE1Hy/1AmuNU8WJanomA5K58fUCK3M31E6AwF8FB" \
               "JYB6SngRStl3wVWyrZFLFoCROxKtZoEVrWOOg+BwgICK3FzvdMkbp7SbwkIrFtsbiJA4ISAwDqhbk8CBG4JCKxbbG4iQOCEgMA6oW" \
               "5PAgRuCQisW2xuIkDghIDAOqFuTwIEbgkIrFtskW/yLztE7o7angnMDSzPyrNuuHtYwKgNU+2/8HFzPl9gbmDtp/mx42OgU4Vn3Bd" \
               "2xq5VqblGYFXphnM8FBCmDwHD3y6worWo6jNX9VzR5qd4PfEDy6AXH0HHIzAusCewhM54R1xJgMCnAnsCq2ADZHDBpjpSeAGBFb5F" \
               "CiRA4D+BJIG1831m514GkQCBKwJJAuvKkVxLgEBVgY2B5c2l6hA5F4FdAhcD69fQEUC7mmQfAgR+CFwMLGwECBA4JyCwztnbmQCBi" \
               "wIC6yKYywkQOCcgsM7Z25kAgYsCAuszsAN/pnBgy4vj4nICZwXSBJaH+eyg2J1ABIE0gRUBK3wNUj18i/oUuGYYBVafCXLSqgJrsi" \
               "GklsAK2ZY8RZ16Vk7tm6czNSsVWAn6OvXhnLpYAjwllhIQWKXa6TAEagsIrNr9zXs6b4KBe3euOQIr8FgojQCB3wUaB9a5T4mpQ1j" \
               "kGFNNLFZWoHFgle2pg3UTaPShJbC6DbfzEkgsILASN0/pBLoJCKxuHXfe5AKNvv/94agCK/n4Kp9AJwGB1anbzkogucCPwMrylpml" \
               "zgRDgTJBk5T4QcAblqEgQCCNQLvA8maRZjYHC9XRQagSl7ULrBJdcwgCTQUmBZZPuabz49hPBDw2l/UmBdblfd1AgACBywIC6zKZG" \
               "wgQOCUgsE7J39zXt4ibcG4rIfD+7fV6vZc4ikNME5CK0ygtNFcg4RuWp2nuCFjtuYCZfG44tkLCwBo7mKsqCAiCK13soCWwrkyEa/" \
               "cJdHj69mmW2UlglWmlgxCoLyCw6vfYCQmUERBYZVrpIATqCwwElh8T6o/B21ua/8RQiWZ4pu62cSCw7i7tPgIECMwVEFhzPa1GgMB" \
               "CgRCB5QV5YYctTaCQQIjAKuTpKAQILBQQWAtxLU2AwEeBJ9+oYgbWkxNNnZAwhUw9lcUIxBC4/nzFDKwImtctI1StBgKlBXoGljAq" \
               "PdQOd0Eg2bPQM7Au9NOlBAjEERBYcXqhEgJ5BTa9qQmsvCOicgLtBARWu5Y7MIG8AgIrb+/qVb7pa0U9uD4nmhtYUwdu6mJ9OuqkB" \
               "AoLzA2swlCORuB/gfafpecABFal5/DcHFVSdJbAAgLrSXMEhP/u35P5ce9lAYF1mcwNBAicEmgWWF6JTg1axX1N0/6uNgus/cB2zC" \
               "8gmOL08P3b6/V6j1OPSn4V8KSYBwK/CXjDejwQUuUxoQUIDAoIrEEolxEgcF5AYJ3vgQoIEBgUEFiDUC4jQOC8gMA63wMVECAwKCC" \
               "wBqFcRoDAeQGBdb4HKiBAYFBAYA1CuYwAgfMCAut8D2JX4F8zi92fZtUJrGYNd1wCmQUEVubuqZ1AMwGB1azhjksgs8DcwPJ7R+ZZ" \
               "UDuB8AJzAyv8cRVIgEBmAYGVuXtqJ9BMQGBFaPiBr9IHtowgrYbkAgIreQOVT6CTgMDq1G1nJZBcIH5gRfjuEqGG5IOmfAIzBD4NL" \
               "M/oDF5rECAwT+D1Fv8Na/i0InaYyoUEkgoUCqygHZCjQRujrIwCAitj19RMoKmAwGraeMcmkFFAYGXsmpoJNBUQWE0b79g/BDr/xJ" \
               "jx7ALLk0uAQBoBgZWmVQolQEBgmQECBNIICKwLrcr4nf/C8VxKYKLAmqdFYE1s0dKl1vR/ackWPyBQfE4E1oGZsiUBAvcEBNY9N3c" \
               "RIHBAQGAdQLclAQL3BATWPTd3EUgiUOtHLYG1euxqzctqLev/UcAQ/ccisDwiBAjEEfgimwXWplb5jNwEbZvSAgKrdHsdjkAtgYuB" \
               "5T2hVvvXncakrLPtvPLFwOpM5ewECJwWEFinO2B/AgSGBXoGlu8rwwPiQgKRBHoGVqQOqIUAgWEBgTVM5UIC+QWyf7kQWPln0AkIt" \
               "BEQWG1a7aAE8gsIrPw9bH+C7F9z2jfwAoDAuoDlUgIEzgoIrLP+dt8i4B1sC/OGTQTWBmRb/FlAjJiMqwIC66qY6w8JiLdD8BO2He" \
               "vdyFUC63s7Rqgm9M0SBAg8ErgcWB7tR95bbtajLcw2OSBwObAO1GhLAgQIfBcQWMsG4Q/vOV59lmlbuIfA3wPLA9ZjCpySQBIBb1h" \
               "JGqVMAgR8JTQDBAgkEvCGlahZSo0l4BeT/f0QWPvNt+7oodrKbbPFAgJrMbDlCawU6PaBJLCmTlO38ZmKZzECXwqcDSzP95cNcgEB" \
               "Aj8FzgaWThAgQOCCQLPAuv5Kd/2OC/rFLg1jFaaQYg0OcJxmgRVAXAkECNwWEFi36dxIgMBuAYG1W9x+BAjcFhBYt+l63ehnoV79j" \
               "npagRW1M+oiQOCDgMAyFAQIzBVY+Dr+/u31er3PLddqBAgQWCLgDWsJq0UJEFghILBWqH5Yc+E78pb6bUIghoDAitGHWFX8NV+Fb6" \
               "xm9aqmZ2B55npNudOWEQgWWJKkzGQFO4jJCtaQm+UEC6ybp3AbgW4CTRNYYHUbdOclkFhAYCVuntIJdBMQWN067rwEEgsIrMTNUzq" \
               "B+wI5fwQTWPc77k4CBDYLCKzN4LYj8KVAzpefL4814wKBNUPRGgQIbBEQWFuYbUJgp0DdVzSBtXOO7EWAwCMBgfWI75Ob637ArdCa" \
               "s2Yj80ZH/TAbAmvO42IVAgQ2CAisDci2IEBgjoDAmuNoFQLpBD77ahn5K6fASjdmCibQV0Bg9e29kxNIJyCw0rVMwdMFVn8HWr3+d" \
               "JC4CwqsuL1RGQECb29vv+a9wDISBAikERBYaVqlUAIEBNaKGfCbxQpVaxJ4E1iGgACBNAICK02rFEqAgMBqOQO+s7Zse4FDC6wCTX" \
               "QEAl0EBFaXTjsngQICAqtAEx2BQBeBQ4HlN5QuA+acBGYKHAqsmUewFgECXQSOBZZ3rC4j5pwE5gkcC6x5R0i0kpRO1CylRhQQWBG" \
               "7oiYCBP4oILCeDIY3pid67iVwWUBgXSZzQwSBMJ8VYQqJ0JX1NQis9cZ2IEBgkoDAmgRpGQIE1gsIrPXGdiBAYJKAwJoEaRkCBNYL" \
               "CKz1xnbYKOA38I3YB7YSWAfQbblKIOP/y/iZRbeAzhtY3Tr1bK7dfUlg03Bt2ubS0YNfnDewgsMq7y8CTR/Upsee+igIrKmcFhsX8" \
               "PiOW7nyPwGBZRYIEEgjILDStEqhJQS8WD5qo8B6xOdmApUF4qWrwKo8b85GoJiAwKrU0HgfiJV0nSWAgMAK0AQlECAwJiCwxpxcRY" \
               "BAAAGBFaAJSiBAYExAYI05Bb/Kj1fBG6S8SQICaxKkZQgQWC8gsNYb2+GIwOS3zsnLHSG5u2mgswusu0103yKBQE/HohNa9r6AwLp" \
               "v504CBDYLCKzN4LYjUEHg1HuwwKowPc5AoLDAr+EosAo32tEIRBR48nYmsCJ2VE0ECPxRQGA9GYwnHxVP9nUvgaYCAqtp47cfe1O4" \
               "b9pmO58NfwgILJNAgEAaAYGVplUJC/W6k7BpN0ve1GuBdbM/biNAYL+AwNpvnmTHTR+ZSTSUGUNAYMXow60qRMottpQ36bUf3ZMMr" \
               "lFN0qjYZRYZI29YscdMdf8LFHnidPSRgMB6xOdmAgR2CrQOLJ/ZO0fNXgSeC7QOrPt8ou6+nTsJ3BcQWPft3EmAwGaB9IHlXWfzxN" \
               "iOwEGB9IH13e5Wat266WCrbP1TQO+mTUMYyrFCQgfW2BGmtc5CBOIJeAh+60nowIo3PSoiQOCkgMA6qW9vAgQuCQisS1wuJkDgpID" \
               "AOqlvbwIELgkIrEtcLiZA4KTA2cDyJyAne29vAukEzgZWOi4FEyBwUmB5YHmJOtlee28VMOzLuZcH1vIT2IAAgTYCAqtNqyMc1CtI" \
               "hC5krkFgZe6e2hMJCOsZzRJYMxStQYDAFgGBtYXZJgRGBLyFfaUksL4S8s8JEAgjILDCtKJRIV4kGjV77lEF1lxPqxEgsFDgHyi8l" \
               "ce3oyHnAAAAAElFTkSuQmCC"

    blank_captcha = "/9j/4AAQSkZJRgABAQAAAQABAAD/4gIoSUNDX1BST0ZJTEUAAQEAAAIYAAAAAAQwAABtbnRyUkdCIFhZWi"+"A"*16+"BhY3" \
                    "Nw"+"A"*37+"QAA9tYAAQAAAADTLQ"+"A"*68+"lkZXNjAAAA8AAAAHRyWFlaAAABZAAAABRnWFlaAAABeAAAABRiWFlaAAA" \
                    "BjAAAABRyVFJDAAABoAAAAChnVFJDAAABoAAAAChiVFJDAAABoAAAACh3dHB0AAAByAAAABRjcHJ0AAAB3AAAADxtbHVjAAA" \
                    "AAAAAAAEAAAAMZW5VUwAAAFgAAAAcAHMAUgBHAEI"+"A"*106+"FhZWiAAAAAAAABvogAAOPUAAAOQWFlaIAAAAAAAAGKZAA" \
                    "C3hQAAGNpYWVogAAAAAAAAJKAAAA+EAAC2z3BhcmEAAAAAAAQAAAACZmYAAPKnAAANWQAAE9AAAApbAAAAAAAAAABYWVogAA" \
                    "AAAAAA9tYAAQAAAADTLW1sdWMAAAAAAAAAAQAAAAxlblVTAAAAIAAAABwARwBvAG8AZwBsAGUAIABJAG4AYwAuACAAMgAwAD" \
                    "EANv/bAEMAAwICAwICAwMDAwQDAwQFCAUFBAQFCgcHBggMCgwMCwoLCw0OEhANDhEOCwsQFhARExQVFRUMDxcYFhQYEhQVFP" \
                    "/bAEMBAwQEBQQFCQUFCRQNCw0U"+"FBQU"*16+"FP/AABEIAFoBGAMBIgACEQEDEQH/xAAWAAEBAQ"+"A"*19+"Qn/xAAWEA" \
                    "EBAQ"+"A"*19+"RH/xAAUAQE"+"A"*21+"/8QAFBEB"+"A"*21+"P/aAAwDAQACEQMRAD8A1T"+"A"*143+"BJdVJMU" + \
                    "A"*70+"H/2Q=="

    with open("resources/blank_qr.png", "wb") as f:
        f.write(b64decode(blank_qr))
    with open("resources/blank_captcha.jpg", "wb") as f:
        f.write(b64decode(blank_captcha))
