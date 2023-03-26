import tkinter as tk
import requests
import json
import string
import os
import re
from typing import List, Optional


class Pydict:
    API_KEY: Optional[str] = None
    BASE_URL: str = "https://api.wordnik.com/v4/word.json/{}/definitions?limit=200&includeRelated=true&useCanonical=true&includeTags=false&api_key={}"
    CONFIG_FILE: str = os.path.join(os.path.dirname(__file__), 'config.json')

    def __init__(self):
        self._read_config()
        self._create_gui()

    def _read_config(self) -> None:
        try:
            with open(self.CONFIG_FILE, 'r') as f:
                config = json.load(f)
            self.API_KEY = config.get('api_key', None)
        except FileNotFoundError:
            pass

    def _write_config(self, api_key: str) -> None:
        with open(self.CONFIG_FILE, 'w') as f:
            json.dump({'api_key': api_key}, f)

    def _search_word(self, word: str) -> None:
        if self.API_KEY is None:
            self._show_result("API key is not set. Please set the API key and try again.")
            return
        if not all(c in string.printable for c in word):
            self._show_result("The word contains non-ASCII characters that are not supported by Wordnik.")
            return
        url = self.BASE_URL.format(word, self.API_KEY)
        try:
            response = requests.get(url)
            response.raise_for_status()
            definitions = [re.sub(r'<[^>]+>', '', d['text']) for d in response.json() if 'text' in d]
            if not definitions:
                self._show_result("No definitions found.")
            else:
                result_text = f"{word.capitalize()}:\n\n"
                for i, definition in enumerate(definitions, 1):
                    result_text += f"Definition {i}: {definition}\n\n"
                self._show_result(result_text)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                self._show_result("The word was not found.")
            elif e.response.status_code == 401:
                self._show_result("The API key is invalid.")
            else:
                self._show_result("An error occurred while fetching the data.")

    def _show_result(self, text: str) -> None:
        self.result_box.delete("1.0", tk.END)
        self.result_box.insert(tk.END, text)

    def _on_search(self, event=None) -> None:
        word = self.search_box.get().strip()
        if word:
            self._search_word(word)

    def _on_keypress(self, event) -> None:
        if event.char == '\r':
            self._on_search()

    def _create_gui(self) -> None:
        root = tk.Tk()
        root.title("Pydict")
        root.geometry("600x400")

        main_frame = tk.Frame(root, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        search_label = tk.Label(main_frame, text="I want to look up:")
        search_label.pack()

        search_frame = tk.Frame(root)
        search_frame.pack(fill=tk.X)

        self.search_box = tk.Entry(main_frame)
        self.search_box.pack()

        search_button = tk.Button(main_frame, text="Search", command=self._on_search)
        search_button.pack(pady=10)

        self.result_box = tk.Text(root, wrap=tk.WORD)
        self.result_box.pack(fill=tk.BOTH, expand=True, padx=10)

        if self.API_KEY is None:
            self._show_result("API key is not set. Please set the API key and try again.")

        root.bind('<Return>', self._on_keypress)
        root.mainloop()


if __name__ == "__main__":
    Pydict()