import tkinter as tk
from tkinter import ttk, scrolledtext
import requests
import re
import threading
import os

HISTORY_FILE = "chat_history.txt"

def send_query():
    user_input = entry.get("1.0", tk.END).strip()
    if not user_input:
        return
    
    entry.delete("1.0", tk.END)
    display_message("Você", user_input, "blue")
    output_text.insert(tk.END, "\nAI: Digitando...\n", "gray")
    output_text.yview(tk.END)
    
    thread = threading.Thread(target=fetch_response, args=(user_input,))
    thread.start()

def fetch_response(user_input):
    response = query_ollama(user_input)
    output_text.config(state=tk.NORMAL)
    output_text.delete("end-2l", "end-1l")  # Remove "Digitando..."
    display_message("AI", response, "green")
    save_to_history(f"Você: {user_input}\nAI: {response}\n")
    output_text.yview(tk.END)

def display_message(sender, message, color):
    output_text.config(state=tk.NORMAL)
    output_text.insert(tk.END, f"\n{sender}: ", color)
    output_text.insert(tk.END, message + "\n")
    output_text.config(state=tk.DISABLED)

def query_ollama(prompt):
    url = "http://localhost:11434/api/generate"
    data = {"model": "deepseek-r1:7b", "prompt": prompt, "stream": False}
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        return clean_response(response.json().get("response", "Erro ao obter resposta."))
    except requests.exceptions.RequestException as e:
        return f"Erro: {str(e)}"

def clean_response(text):
    return re.sub(r"<.*?>", "", text).strip()

def save_to_history(message):
    with open(HISTORY_FILE, "a", encoding="utf-8") as file:
        file.write(message + "\n")

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as file:
            output_text.config(state=tk.NORMAL)
            output_text.insert(tk.END, file.read())
            output_text.config(state=tk.DISABLED)
            output_text.yview(tk.END)

def handle_enter(event):
    send_query()
    return "break"

def clear_chat():
    output_text.config(state=tk.NORMAL)
    output_text.delete("1.0", tk.END)
    output_text.config(state=tk.DISABLED)
    with open(HISTORY_FILE, "w", encoding="utf-8") as file:
        file.truncate()

def check_commands(event):
    user_input = entry.get("1.0", tk.END).strip()
    if user_input == "/limpar":
        clear_chat()
        entry.delete("1.0", tk.END)
        return "break"

# Criar janela principal
root = tk.Tk()
root.title("Assistente Virtual - DeepSeek R1-7B")
root.geometry("600x500")
root.configure(bg="#f0f0f0")

# Layout
entry = scrolledtext.ScrolledText(root, height=4, wrap=tk.WORD)
entry.grid(row=0, column=0, padx=10, pady=10, columnspan=2, sticky="ew")
entry.bind("<Return>", handle_enter)
entry.bind("<KeyRelease>", check_commands)

send_button = ttk.Button(root, text="Enviar", command=send_query)
send_button.grid(row=1, column=0, pady=5, sticky="ew")

clear_button = ttk.Button(root, text="Limpar", command=clear_chat)
clear_button.grid(row=1, column=1, pady=5, sticky="ew")

output_text = scrolledtext.ScrolledText(root, height=20, wrap=tk.WORD, state=tk.DISABLED)
output_text.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

# Cores das mensagens
output_text.tag_config("blue", foreground="blue")
output_text.tag_config("green", foreground="green")
output_text.tag_config("gray", foreground="gray")

# Ajustar proporções
root.grid_rowconfigure(2, weight=1)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)

# Carregar histórico
load_history()

# Iniciar loop da interface gráfica
root.mainloop()
