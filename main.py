import shutil
import json
import customtkinter as ctk
import tkinter.font as tkfont
from scr.server_manager import ServerManager, retriveMSJ
from scr.javaJDK_downloader import javaJDKUpdateAvailable
from scr.app_data import AppData
from scr.ui_functions import *
from scr.updater import checkForUpdates, downloadUpdate
downloadUpdate()

class App:
    def __init__(self, root):
        self.root = root
        self.root.geometry("862x519")
        self.root.title("Zenith")
        self.root.resizable(False, False)
        self.root.iconbitmap('resources/icon.ico')
        self.root.configure(bg='#F8FFE5')
        ctk.CTkFont(family="Aldrich-Regular.ttf", size=24)

        self.elements = self.resetElements()
        self.data = {
            "versions": retriveMSJ("vanilla", "", True),
            "servers": ServerManager.retriveServers(),
            "selected_server": None,
            "current_data": None
        }
        self.theme = self.loadTheme()

        self.page = ctk.CTkFrame(self.root)
        
        if javaJDKUpdateAvailable():
            self.loadPage("downloadJDK/downloadJDK")
        else:
            self.loadPage("home/home")

    def resetElements(self):
        return {"label": {}, "button": {}, "entry": {}, "optionmenu": {}, "list": {}, "switch": {}, "textbox": {}, "progressbar": {}, "segmentedbutton": {}, "slider": {}}

    def loadTheme(self):
        path = f'data/themes/{AppData.getAppData("theme")}.json'
        with open(path, "r") as f:
            data = json.load(f)
        return data

    def unpackText(self, text):
        parts = []
        current_part = ""
        in_brackets = False

        i = 0
        while i < len(text):
            char = text[i]

            if char == "$" and i + 1 < len(text) and text[i + 1] == "{":
                if current_part:
                    parts.append(current_part)
                    current_part = ""
                in_brackets = True
                i += 1
            elif char == "}" and in_brackets:
                current_part = f"%%%{current_part}"
                parts.append(current_part)
                current_part = ""
                in_brackets = False
            elif char == " " and not in_brackets:
                if current_part:
                    parts.append(current_part)
                    current_part = ""
            else:
                current_part += char

            i += 1

        if current_part:
            parts.append(current_part)

        output = ""
        for part in parts:
            if part.startswith("%%%"):
                output += f'{str(self.data[part[3:]])} '
            else:
                output += f'{part} '

        return output[:-1]

    def selectServer(self, name):
        self.data["selected_server"] = name
        self.loadPage("server/server")

    def loadPage(self, page):
        self.data["servers"] = ServerManager.retriveServers()
        self.elements = self.resetElements()
        ServerManager.servers = ServerManager.retriveServers()
        page_path = f"data/pages/{page}.json"
        with open(page_path, "r") as f:
            data = json.load(f)
        
        self.entries = {}
        
        for widget in self.page.winfo_children():
            widget.destroy()

        self.page.pack_forget()
        self.page.pack(fill="both", expand=True)

        if "on_load_function" in data:
            exec(data["on_load_function"])

        use_grid = data["use_grid"] if "use_grid" in data else False
        if use_grid:
            self.page.grid_columnconfigure(0, weight=1)
            self.page.grid_rowconfigure(0, weight=1)

        for element in data["elements"]:
            if "show" in element:
                if isinstance(element["show"], dict):
                    if not eval(element["show"]["condition"]):
                        continue
                else:
                    if not element["show"]:
                        continue
            side = "top" if "align" not in element else element["align"]

            if element["type"] == "label":
                font = ctk.CTkFont(family="resources/font/Aldrich-Regular.ttf", size=element["size"])

                label = ctk.CTkLabel(self.page, text=self.unpackText(element["text"]), font=font)
                if use_grid:
                    label.grid(column=element["grid"]["column"], row=element["grid"]["row"], sticky=element["grid"]["sticky"], padx=element["grid"]["padx"], pady=element["grid"]["pady"])
                else:
                    label.pack(pady=element["pad"], side=side)
                self.elements["label"][element["id"]] = label

            if element["type"] == "button":
                theme = self.theme["button"]
                f = element["function"]
                
                s = "normal"
                if "state" in element:
                    if isinstance(element["state"], dict):
                        if eval(element["state"]["condition"]):
                            s = "normal"
                        else:
                            s = "disabled"
                    else:
                        s = element["state"]

                button = ctk.CTkButton(self.page, text=element["text"], state=s, command=lambda f=f: eval(f), fg_color=theme["fg_color"], hover_color=theme["hover_color"], text_color=theme["text_color"])
                if use_grid:
                    button.grid(column=element["grid"]["column"], row=element["grid"]["row"], sticky=element["grid"]["sticky"], padx=element["grid"]["padx"], pady=element["grid"]["pady"])
                else:
                    button.pack(pady=element["pad"], side=side)
                self.elements["button"][element["id"]] = button

            if element["type"] == "entry":
                theme = self.theme["entry"]

                enable_button = True if "button" in element else False
                if enable_button:
                    eframe = ctk.CTkFrame(self.page)

                    btheme = self.theme["button"]
                    f = element["button"]["function"]
                    
                    s = "normal"
                    if "state" in element["button"]:
                        if isinstance(element["button"]["state"], dict):
                            if eval(element["button"]["state"]["condition"]):
                                s = "normal"
                            else:
                                s = "disabled"
                        else:
                            s = element["button"]["state"]

                    button = ctk.CTkButton(eframe, text=element["button"]["text"], state=s, command=lambda f=f: eval(f), fg_color=btheme["fg_color"], hover_color=btheme["hover_color"], text_color=btheme["text_color"])
                    button.pack(pady=element["button"]["pad"], padx=5, side="right")
                    self.elements["button"][element["button"]["id"]] = button

                width = element["width"] if "width" in element else 200
                height = element["height"] if "height" in element else 30

                parent = eframe if enable_button else self.page
                entry = ctk.CTkEntry(parent, placeholder_text=element["text"], width=width, height=height, fg_color=theme["fg_color"])
                if not enable_button:
                    if use_grid:
                        entry.grid(column=element["grid"]["column"], row=element["grid"]["row"], sticky=element["grid"]["sticky"], padx=element["grid"]["padx"], pady=element["grid"]["pady"])
                    else:
                        entry.pack(pady=element["pad"], side=side)
                else:
                    entry.pack(pady=5, padx=5, side="left")

                if "default" in element:
                    default = element["default"]
                    if isinstance(default, dict):
                        default = eval(element["default"]["function"])

                    entry.insert(0, default)

                if enable_button:
                    eframe.pack(pady=element["pad"], side=side)

                self.elements["entry"][element["id"]] = entry

            if element["type"] == "optionmenu":
                theme = self.theme["optionmenu"]
                v = self.data[element["data"]] if not isinstance(element["data"], list) else element["data"]
                optionmenu_frame = ctk.CTkFrame(self.page)
                optionmenu_label = ctk.CTkLabel(optionmenu_frame, text=element["text"])
                optionmenu_label.pack(side="left", padx=5)
                optionmenu = ctk.CTkOptionMenu(optionmenu_frame, values=v, fg_color=theme["fg_color"], button_color=theme["button_color"], button_hover_color=theme["button_hover_color"], dropdown_fg_color=theme["dropdown_fg_color"], dropdown_hover_color=theme["dropdown_hover_color"], dropdown_text_color=theme["dropdown_text_color"], text_color=theme["text_color"])
                optionmenu.pack(side="left")
                if use_grid:
                    optionmenu_frame.grid(column=element["grid"]["column"], row=element["grid"]["row"], sticky=element["grid"]["sticky"], padx=element["grid"]["padx"], pady=element["grid"]["pady"])
                else:
                    optionmenu_frame.pack(pady=element["pad"])
                self.elements["optionmenu"][element["id"]] = optionmenu

            if element["type"] == "list":
                list_frame = ctk.CTkFrame(self.page)
                list_label = ctk.CTkLabel(list_frame, text=element["text"])
                list_label.pack(padx=5)
                elist = ctk.CTkScrollableFrame(list_frame, width=element["width"], height=element["height"], fg_color="#242424")
                elist.pack(side="left")
                if use_grid:
                    list_frame.grid(column=element["grid"]["column"], row=element["grid"]["row"], sticky=element["grid"]["sticky"], padx=element["grid"]["padx"], pady=element["grid"]["pady"])
                else:
                    list_frame.pack(pady=element["pad"])

                data = element["data"]
                if data["type"] == "appdata":
                    data = self.data[data["key"]]
                elif data["type"] == "function":
                    data = eval(data["function"])

                for d in data:
                    self.data["current_data"] = d
                    f = element["function"]

                    t = eval(element["button_text"])

                    theme = self.theme["button"]
                    button = ctk.CTkButton(elist, text=t, command=lambda f=f: eval(f), fg_color=theme["fg_color"], hover_color=theme["hover_color"], text_color=theme["text_color"])
                    button.pack(pady=5)
                self.elements["list"][element["id"]] = elist

            if element["type"] == "switch":
                theme = self.theme["switch"]
                switch = ctk.CTkSwitch(self.page, text=element["text"], fg_color=theme["fg_color"], progress_color=theme["progress_color"], button_color=theme["button_color"], button_hover_color=theme["button_hover_color"])
                if use_grid:
                    switch.grid(column=element["grid"]["column"], row=element["grid"]["row"], sticky=element["grid"]["sticky"], padx=element["grid"]["padx"], pady=element["grid"]["pady"])
                else:
                    switch.pack(pady=element["pad"], side=side)

                ef = None if "enable_function" not in element else element["enable_function"]
                df = None if "disable_function" not in element else element["disable_function"]

                enabled = True
                if "enabled" in element:
                    if isinstance(element["enabled"], dict):
                        if eval(element["enabled"]["condition"]):
                            enabled = True
                        else:
                            enabled = False
                    else:
                        enabled = element["enabled"]

                switch.select() if enabled else switch.deselect()

                self.elements["switch"][element["id"]] = {"obj": switch, "enable_function": ef, "disable_function": df, "state": switch.get()}

            if element["type"] == "textbox":
                font = ("Arial", element["font_size"])
                width = element["width"] if "width" in element else 200
                height = element["height"] if "height" in element else 30
                textbox = ctk.CTkTextbox(self.page, width=width, height=height, font=font)
                if use_grid:
                    textbox.grid(column=element["grid"]["column"], row=element["grid"]["row"], sticky=element["grid"]["sticky"], padx=element["grid"]["padx"], pady=element["grid"]["pady"])
                else:
                    textbox.pack(pady=element["pad"], side=side)
                if "default" in element:
                    textbox.insert("0.0", element["default"])
                self.elements["textbox"][element["id"]] = {"obj": textbox, "update_with_function": element["update_with_function"]}

            if element["type"] == "progressbar":
                theme = self.theme["progressbar"]
                width = element["width"] if "width" in element else 300
                height = element["height"] if "height" in element else 20

                progressbar = ctk.CTkProgressBar(self.page, width=width, height=height, fg_color=theme["fg_color"], progress_color=theme["progress_color"])
                progressbar.set(0)
                if use_grid:
                    progressbar.grid(column=element["grid"]["column"], row=element["grid"]["row"], sticky=element["grid"]["sticky"], padx=element["grid"]["padx"], pady=element["grid"]["pady"])
                else:
                    progressbar.pack(pady=element["pad"], side=side)
                self.elements["progressbar"][element["id"]] = {"obj": progressbar, "value": element["value"]}

            if element["type"] == "segmentedbutton":
                theme = self.theme["segmentedbutton"]
                v = self.data[element["data"]] if not isinstance(element["data"], list) else element["data"]
                segmentedbutton_frame = ctk.CTkFrame(self.page)
                segmentedbutton_label = ctk.CTkLabel(segmentedbutton_frame, text=element["text"])
                segmentedbutton_label.pack(side="left", padx=5)

                function = None if "function" not in element else element["function"]

                segmentedbutton = ctk.CTkSegmentedButton(segmentedbutton_frame, values=v, command=lambda v, f=function: eval(f) if f is not None else None, fg_color=theme["fg_color"], selected_color=theme["selected_color"], selected_hover_color=theme["selected_hover_color"], text_color=theme["text_color"])
                segmentedbutton.set(v[0])
                segmentedbutton.pack(side="left")

                if use_grid:
                    segmentedbutton_frame.grid(column=element["grid"]["column"], row=element["grid"]["row"], sticky=element["grid"]["sticky"], padx=element["grid"]["padx"], pady=element["grid"]["pady"])
                else:
                    segmentedbutton_frame.pack(pady=element["pad"])

                self.elements["segmentedbutton"][element["id"]] = segmentedbutton

            if element["type"] == "slider":
                theme = self.theme["slider"]
                slider_frame = ctk.CTkFrame(self.page)
                
                width = element["width"] if "width" in element else 300
                height = element["height"] if "height" in element else 20

                minimum = element["min"] if "min" in element else 0
                maximum = element["max"] if "max" in element else 100

                if isinstance(maximum, dict):
                    if "variable" in maximum:
                        maximum = eval(maximum["variable"])

                slider = ctk.CTkSlider(slider_frame, width=width, height=height, from_=minimum, to=maximum, number_of_steps=maximum-1, progress_color=theme["progress_color"], button_color=theme["button_color"], button_hover_color=theme["button_hover_color"])
                slider.set(element["default"])
                slider.pack(pady=element["pad"], side=side)

                slider_value_label = ctk.CTkLabel(slider_frame, text=0)
                slider_value_label.pack(padx=5)

                if use_grid:
                    slider_frame.grid(column=element["grid"]["column"], row=element["grid"]["row"], sticky=element["grid"]["sticky"], padx=element["grid"]["padx"], pady=element["grid"]["pady"])
                else:
                    slider_frame.pack(pady=element["pad"])

                suffix = element["suffix"] if "suffix" in element else ""
                prefix = element["prefix"] if "prefix" in element else ""
                rnd = element["round"] if "round" in element else False
                self.elements["slider"][element["id"]] = {"obj": slider, "value_label": slider_value_label, "prefix": prefix, "suffix": suffix, "rnd": rnd}

    def checks(self):
        for switch in self.elements["switch"]:
            switch_data = self.elements["switch"][switch]
            switch_obj = switch_data["obj"]
            switch_state = switch_data["state"]

            if switch_obj.get() == 1 and not switch_state:
                if switch_data["enable_function"] is not None:
                    eval(switch_data["enable_function"])
                switch_data["state"] = True

            elif switch_obj.get() == 0 and switch_state:
                if switch_data["disable_function"] is not None:
                    eval(switch_data["disable_function"])
                switch_data["state"] = False

        for textbox in self.elements["textbox"]:
            textbox_data = self.elements["textbox"][textbox]
            if textbox_data["update_with_function"] is not None:
                text = eval(textbox_data["update_with_function"])
                current_scroll = textbox_data["obj"].yview() 
                
                current_text = textbox_data["obj"].get("0.0", "end").strip()
                if current_text != text.strip():
                    textbox_data["obj"].delete("0.0", "end")
                    textbox_data["obj"].insert("0.0", text)
                
                    textbox_data["obj"].yview_moveto(current_scroll[0])

        for progressbar in self.elements["progressbar"]:
            progressbar_data = self.elements["progressbar"][progressbar]
            progressbar_obj = progressbar_data["obj"]
            progressbar_value = eval(progressbar_data["value"])
            progressbar_obj.set(progressbar_value)

        for slider in self.elements["slider"]:
            slider_data = self.elements["slider"][slider]
            slider_value = slider_data["obj"].get()

            if slider_data["rnd"]:
                slider_value = round(slider_value)

            slider_value_label = slider_data["value_label"]
            text = f'{slider_data["prefix"]}{slider_value}{slider_data["suffix"]}'
            slider_value_label.configure(text=text)

        self.root.after(16, self.checks)

root = ctk.CTk()
app = App(root)

app.root.after(16, app.checks)

root.mainloop()

if ServerManager.running_servers != {} and not AppData.getAppData("keep_servers_online"):
    servers = ServerManager.running_servers
    for server in servers:
        ServerManager.stopServer(server)
shutil.rmtree("temp/versions")