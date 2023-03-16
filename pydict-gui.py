import tkinter as tk
import requests
import json
import string
import os

API_KEY = None
BASE_URL = "https://api.wordnik.com/v4/word.json/{}/definitions?limit=200&includeRelated=true&useCanonical=true&includeTags=false&api_key={}"


def read_config():
    try:
        with open(os.path.join(os.path.dirname(__file__), 'config.json'), 'r') as f:
            config = json.load(f)
        return config.get('api_key', None)
    except FileNotFoundError:
        return None

def write_config(api_key):
    with open(os.path.join(os.path.dirname(__file__), 'config.json'), 'w') as f:
        json.dump({'api_key': api_key}, f)

def search_word(word):
    global API_KEY, BASE_URL, result_box
    if API_KEY is None:
        result_box.delete("1.0", tk.END)
        result_box.insert(tk.END, "API key is not set. Please set the API key and try again.")
        return
    if not all(c in string.printable for c in word):
        result_box.delete("1.0", tk.END)
        result_box.insert(tk.END, "The word contains non-ASCII characters that are not supported by Wordnik.")
        return
    url = BASE_URL.format(word, API_KEY)
    response = requests.get(url)
    if response.status_code == 404:
        result_box.delete("1.0", tk.END)
        result_box.insert(tk.END, "The word was not found.")
    elif response.status_code == 401:
        result_box.delete("1.0", tk.END)
        result_box.insert(tk.END, "The API key is invalid.")
    else:
        definitions = [d['text'] for d in response.json() if 'text' in d]
        if not definitions:
            result_box.delete("1.0", tk.END)
            result_box.insert(tk.END, "No definitions found.")
        else:
            result_text = f"{word.capitalize()}:\n\n"
            for i, definition in enumerate(definitions, 1):
                result_text += f"Definition {i}: {definition}\n\n"
            result_box.delete("1.0", tk.END)
            result_box.insert(tk.END, result_text)

def on_search(event=None):
    word = search_box.get().strip()
    if word:
        search_word(word)

def on_keypress(event):
    if event.char == '\r':
        on_search()

def main():
    global API_KEY, search_box, result_box

    config_api_key = read_config()
    if config_api_key is not None:
        API_KEY = config_api_key

    root = tk.Tk()
    root.title("Pydict")
    root.geometry("600x400")

    main_frame = tk.Frame(root, padx=10, pady=10)
    main_frame.pack(fill=tk.BOTH, expand=True)

    search_label = tk.Label(main_frame, text="I want to look up:")
    search_label.pack()

    search_frame = tk.Frame(root)
    search_frame.pack(fill=tk.X)

    search_box = tk.Entry(main_frame)
    search_box.pack()

    search_button = tk.Button(main_frame, text="Search", command=on_search)
    search_button.pack(pady=10)

    result_box = tk.Text(root, wrap=tk.WORD)
    result_box.pack(fill=tk.BOTH, expand=True, padx=10)

    if API_KEY is None:
        result_box.config(text="API key is not set. Please set the API key and try again.")

    root.mainloop()

if __name__ == "__main__":
    main()