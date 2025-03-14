import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog
import asyncio
import aiohttp
import sqlite3
import re
import os
import threading
import fitz  # PyMuPDF

HISTORY_FILE = "chat_history.txt"
CACHE_DB = 'chat_cache.db'
async_loop = None

# Funções de banco de dados e histórico (mantidas intactas)
def create_db():
    conn = sqlite3.connect(CACHE_DB)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS chat_cache (question TEXT PRIMARY KEY, answer TEXT)''')
    conn.commit()
    conn.close()

def check_cache(user_input):
    conn = sqlite3.connect(CACHE_DB)
    c = conn.cursor()
    c.execute("SELECT answer FROM chat_cache WHERE question=?", (user_input,))
    result = c.fetchone()
    conn.close()
    return result

def save_to_cache(user_input, response):
    conn = sqlite3.connect(CACHE_DB)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO chat_cache (question, answer) VALUES (?, ?)", (user_input, response))
    conn.commit()
    conn.close()

# Funções de PDF adicionadas
def open_pdf():
    file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
    if not file_path:
        return
    
    text = extract_text_from_pdf(file_path)
    if text:
        preview = text[:1000] + "..." if len(text) > 1000 else text
        display_message("PDF", f"Prévia do documento ({os.path.basename(file_path)}):\n{preview}", "purple")
        entry.insert(tk.END, text)

def extract_text_from_pdf(file_path):
    try:
        doc = fitz.open(file_path)
        text = "\n".join([page.get_text("text") for page in doc])
        return text.strip() or "Nenhum texto encontrado no PDF."
    except Exception as e:
        return f"Erro ao processar PDF: {str(e)}"

# Funções de interface mantidas com melhorias
def display_message(sender, message, color):
    output_text.config(state=tk.NORMAL)
    output_text.insert(tk.END, f"\n{sender}: ", color)
    output_text.insert(tk.END, message + "\n")
    output_text.config(state=tk.DISABLED)
    output_text.yview(tk.END)

def clear_chat():
    output_text.config(state=tk.NORMAL)
    output_text.delete("1.0", tk.END)
    output_text.config(state=tk.DISABLED)
    with open(HISTORY_FILE, "w", encoding="utf-8") as file:
        file.truncate()

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as file:
            output_text.config(state=tk.NORMAL)
            output_text.insert(tk.END, file.read())
            output_text.config(state=tk.DISABLED)
            output_text.yview(tk.END)

# Funções assíncronas e de processamento
async def query_ollama(prompt):
    cache_response = check_cache(prompt)
    if cache_response:
        return cache_response[0]

    url = "http://localhost:11434/api/generate"
    data = {"model": "deepseek-r1:7b", "prompt": prompt, "stream": False}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data) as response:
                response.raise_for_status()
                response_text = await response.json()
                return re.sub(r"<.*?>", "", response_text.get("response", "")).strip()
    except Exception as e:
        return f"Erro: {str(e)}"

def process_response(response, user_input, typing_start, typing_end):
    output_text.config(state=tk.NORMAL)
    output_text.delete(typing_start, typing_end)
    display_message("AI", response, "green")
    save_to_history(f"Você: {user_input}\nAI: {response}\n")
    save_to_cache(user_input, response)

async def fetch_response(user_input, typing_start, typing_end):
    response = await query_ollama(user_input)
    root.after(0, lambda: process_response(response, user_input, typing_start, typing_end))

def send_message():
    user_input = entry.get("1.0", tk.END).strip()
    if not user_input:
        return
    
    if user_input == "/limpar":
        clear_chat()
        entry.delete("1.0", tk.END)
        return
    
    entry.delete("1.0", tk.END)
    display_message("Você", user_input, "blue")
    
    output_text.config(state=tk.NORMAL)
    typing_start = output_text.index("end-1c")
    output_text.insert(tk.END, "\nAI: Digitando...\n", "gray")
    typing_end = output_text.index("end-1c")
    output_text.config(state=tk.DISABLED)
    output_text.yview(tk.END)
    
    asyncio.run_coroutine_threadsafe(fetch_response(user_input, typing_start, typing_end), async_loop)

def handle_enter(event):
    if not event.state & 0x1:
        send_message()
        return "break"

# Configuração da interface gráfica
root = tk.Tk()
root.title("Assistente Virtual com PDF - DeepSeek R1-7B")
root.geometry("720x600")
root.configure(bg="#f0f0f0")

entry = scrolledtext.ScrolledText(root, height=4, wrap=tk.WORD)
entry.grid(row=0, column=0, padx=10, pady=10, columnspan=3, sticky="ew")
entry.bind("<Return>", handle_enter)

send_button = ttk.Button(root, text="Enviar", command=send_message)
send_button.grid(row=1, column=0, pady=5, sticky="ew")

clear_button = ttk.Button(root, text="Limpar", command=clear_chat)
clear_button.grid(row=1, column=1, pady=5, sticky="ew")

pdf_button = ttk.Button(root, text="Abrir PDF", command=open_pdf)
pdf_button.grid(row=1, column=2, pady=5, sticky="ew")

output_text = scrolledtext.ScrolledText(root, height=20, wrap=tk.WORD, state=tk.DISABLED)
output_text.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

output_text.tag_config("blue", foreground="blue")
output_text.tag_config("green", foreground="green")
output_text.tag_config("gray", foreground="gray")
output_text.tag_config("purple", foreground="#800080")

root.grid_rowconfigure(2, weight=1)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure(2, weight=1)

create_db()
load_history()

def start_async_loop():
    global async_loop
    async_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(async_loop)
    async_loop.run_forever()

threading.Thread(target=start_async_loop, daemon=True).start()

root.mainloop()