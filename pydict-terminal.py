import requests
import sys
import json
import argparse
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
    global API_KEY, BASE_URL
    if API_KEY is None:
        print("API key is not set. Please run the program with the --api-key option to set the API key.\nExample: python pydict.py --api-key abczxy")
        return
    if not all(c in string.printable for c in word):
        print("The word contains non-ASCII characters that are not supported by Wordnik.")
        return
    if len(word.split()) > 1:
        print("Please enter only one word at a time.")
        return
    url = BASE_URL.format(word, API_KEY)
    response = requests.get(url)
    if response.status_code == 404:
        print("The word was not found.")
    elif response.status_code == 401:
        print("The API key is invalid.")
    else:
        definitions = [d['text'] for d in response.json() if 'text' in d]
        if not definitions:
            print("No definitions found.")
        else:
            print(f"{word.capitalize()}:\n")
            for i, definition in enumerate(definitions, 1):
                print(f"Definition {i}: {definition}\n")

def main():
    global API_KEY
    parser = argparse.ArgumentParser(description="Pydict - A command line dictionary tool.")
    parser.add_argument("--api-key", help="set the API key for Wordnik")
    args = parser.parse_args()
    config_api_key = read_config()
    if args.api_key is not None:
        API_KEY = args.api_key
        write_config(API_KEY)
    elif config_api_key is not None:
        API_KEY = config_api_key
    else:
        print("API key is not set. Please run the program with the --api-key option to set the API key.")
        sys.exit(1)

    print("Welcome to Pydict!\n")

    try:
        while True:
            word = input("I want to look up: ")
            search_word(word)
    except KeyboardInterrupt:
        print("\nExiting Pydict.")
        sys.exit(0)

if __name__ == "__main__":
    main()
