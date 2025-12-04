import os
import threading
import time
import tkinter as tk
from tkinter import ttk

import yaml

import util
from acrally import ACRally
from editor import Editor


class Main:
    root = None
    stages = None
    voices = None
    call_earliness = None
    acrally = None
    btn_start = None
    btn_stop = None
    config = None


    def on_button_start(self):
        print(self.stages.get())
        self.acrally = ACRally(
            str(self.stages.get()),
            self.config.get("voice", "English"),
            float(self.config.get("call_distance", 1.0)),
            self.config.get("start_button", "space"),
            self.config.get("handbrake", None)
        )
        self.acrally.start()
        self.btn_start["state"] = "disabled"
        self.btn_stop["state"] = "normal"


    def on_button_exit(self):
        if self.acrally:
            self.acrally.exit()
        self.btn_start["state"] = "normal"
        self.btn_stop["state"] = "disabled"

    def on_button_distance(self):
        distance_window = tk.Toplevel(self.root)
        distance_window.title("Odometer")
        distance_window.iconbitmap(util.resource_path("icon.ico"))
        distance_window.geometry("200x100")
        distance_window.attributes("-topmost", True)
        distance_var = tk.StringVar()
        distance_var.set("----")
        distance_label = ttk.Label(distance_window, textvariable=distance_var, font=("sans-serif", 40))
        distance_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        stop = False

        def retrieve_distance():
            nonlocal stop
            while not stop:
                if self.acrally:
                    if distance := self.acrally.get_distance():
                        distance_var.set(str(int(distance)))
                    else:
                        distance_var.set("----")
                time.sleep(0.05)

        def on_close():
            nonlocal stop
            stop = True
            distance_window.destroy()

        worker = threading.Thread(target=retrieve_distance, daemon=True)
        worker.start()
        distance_window.protocol("WM_DELETE_WINDOW", on_close)

    def on_button_pacenotes(self):
        editor = Editor()
        editor.main()

    def on_button_settings(self):
        import subprocess
        subprocess.Popen(['notepad.exe', 'config.yml'])

    def __init__(self):
        self.config = yaml.safe_load(open("config.yml"))

        root = tk.Tk()
        root.title("AC Rally Pacenote Pal")
        root.iconbitmap(util.resource_path("icon.ico"))
        root.geometry("340x230")
        self.root = root

        stages = os.listdir("pacenotes")
        stages = [file.replace(".yml", "") for file in stages]

        ttk.Label(root, text="Select a stage:").pack(pady=(20, 5))
        self.stages = ttk.Combobox(root, values=stages, width=50)
        self.stages.pack(pady=5, padx=15, fill="x")

        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)

        self.btn_start = ttk.Button(btn_frame, text="Start", command=self.on_button_start)
        self.btn_start.pack(side=tk.LEFT, padx=10)

        self.btn_stop = ttk.Button(btn_frame, text="Stop", command=self.on_button_exit, state="disabled")
        self.btn_stop.pack(side=tk.LEFT, padx=10)

        btn_distance = ttk.Button(btn_frame, text="Odometer", command=self.on_button_distance)
        btn_distance.pack(side=tk.LEFT, padx=10)

        ttk.Label(root, text=f"Click start and press {self.config.get("start_button", "space")} when the countdown starts!").pack(pady=(20, 5))

        btn_frame2 = tk.Frame(root)
        btn_frame2.pack(pady=10)

        btn_editor = ttk.Button(btn_frame2, text="Pacenote Editor", command=self.on_button_pacenotes)
        btn_editor.pack(side=tk.LEFT, padx=10)

        btn_settings = ttk.Button(btn_frame2, text="Settings", command=self.on_button_settings)
        btn_settings.pack(side=tk.LEFT, padx=10)

        root.mainloop()

if __name__ == '__main__':
    app = Main()
