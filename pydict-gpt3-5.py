import os
import string
import tkinter as tk
import requests
from tkinter.scrolledtext import ScrolledText
import json
from typing import Optional, Tuple

class Pydict:
    BASE_URL = "https://api.wordnik.com/v4/word.json/{}/definitions?limit=20&api_key={}"
    CONFIG_FILE = "config.json"
    DEFAULT_FONT_SIZE = 8

    def __init__(self) -> None:
        self.API_KEY: Optional[str]
        self.font_size: Optional[int]
        self.API_KEY, self.font_size = self.read_config()

        self.root = tk.Tk()
        self.root.title("Pydict")
        self.root.geometry("600x400")

        self.create_widgets()
        self.create_menu()

        if self.API_KEY is None:
            self.result_box.insert(tk.END, "API key is not set. Please set the API key and try again.")

        self.font_size_scale = None  # Define font_size_scale as an instance variable

        self.root.mainloop()

    def create_widgets(self) -> None:
        main_frame = tk.Frame(self.root, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        search_label = tk.Label(main_frame, text="I want to look up:")
        search_label.pack()

        search_frame = tk.Frame(self.root)
        search_frame.pack(fill=tk.X)

        self.search_box = tk.Entry(main_frame)
        self.search_box.pack()
        self.search_box.bind("<Return>", self.on_search)

        search_button = tk.Button(main_frame, text="Search", command=self.on_search)
        search_button.pack(pady=10)

        self.result_box = ScrolledText(self.root, font=("TkDefaultFont", self.font_size))
        self.result_box.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def create_menu(self) -> None:
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)

        settings_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="API key", command=self.on_api_key_settings)
        settings_menu.add_command(label="Font size", command=self.on_font_size_settings)

    def read_config(self) -> Tuple[Optional[str], Optional[int]]:
        config_file = os.path.join(os.path.dirname(__file__), self.CONFIG_FILE)
        if os.path.exists(config_file):
            with open(config_file, "r") as f:
                config = json.load(f)
                return config.get("api_key"), config.get("font_size")
        else:
            return None, self.DEFAULT_FONT_SIZE

    def write_config(self, api_key: str, font_size: int) -> None:
        config_file = os.path.join(os.path.dirname(__file__), self.CONFIG_FILE)
        with open(config_file, "w") as f:
            json.dump({"api_key": api_key, "font_size": font_size}, f)

    def search_word(self, word: str) -> str:
        if self.API_KEY is None:
            return "API key is not set. Please set the API key and try again."
        if not all(c in string.printable for c in word):
            return "The word contains non-ASCII characters that are not supported by Wordnik."
        url = self.BASE_URL.format(word, self.API_KEY)
        response = requests.get(url)
        if response.status_code == 404:
            return "The word was not found."
        elif response.status_code == 401:
            return "The API key is invalid."
        else:
            definitions = [d['text'] for d in response.json() if 'text' in d]
            if not definitions:
                return "No definitions found."
            else:
                result_text = f"{word.capitalize()}:\n\n"
                for i, definition in enumerate(definitions, 1):
                    result_text += f"Definition {i}: {definition}\n\n"
                return result_text

    def on_search(self, event: Optional[tk.Event] = None) -> None:
        word = self.search_box.get().strip()
        result = self.search_word(word)
        self.result_box.delete("1.0", tk.END)
        self.result_box.insert(tk.END, result)
        self.result_box.config(font=("TkDefaultFont", self.font_size))

    def on_api_key_settings(self) -> None:
        settings_window = tk.Toplevel(self.root)
        settings_window.title("API key settings")
        settings_window.geometry("400x200")

        settings_frame = tk.Frame(settings_window, padx=10, pady=10)
        settings_frame.pack(fill=tk.BOTH, expand=True)

        api_key_label = tk.Label(settings_frame, text="API key:")
        api_key_label.pack()

        api_key_entry = tk.Entry(settings_frame)
        api_key_entry.pack()

        if self.API_KEY is not None:
            api_key_entry.insert(0, self.API_KEY)

        def save_settings() -> None:
            api_key = api_key_entry.get().strip()
            if api_key:
                self.API_KEY = api_key
                self.font_size = self.font_size_scale.get()
                self.write_config(self.API_KEY, self.font_size)
                settings_window.destroy()

        save_button = tk.Button(settings_frame, text="Save", command=save_settings)
        save_button.pack(pady=10)

    def on_font_size_settings(self) -> None:
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Font size settings")
        settings_window.geometry("400x200")

        settings_frame = tk.Frame(settings_window, padx=10, pady=10)
        settings_frame.pack(fill=tk.BOTH, expand=True)

        font_size_label = tk.Label(settings_frame, text="Font size:")
        font_size_label.pack()

        self.font_size_scale = tk.Scale(settings_frame, from_=8, to=20, orient=tk.HORIZONTAL)
        self.font_size_scale.pack()

        if self.font_size is not None:
            self.font_size_scale.set(self.font_size)

        def save_settings() -> None:
            self.font_size = self.font_size_scale.get()
            self.write_config(self.API_KEY, self.font_size)
            settings_window.destroy()

        save_button = tk.Button(settings_frame, text="Save", command=save_settings)
        save_button.pack(pady=10)

if __name__ == "__main__":
    Pydict()