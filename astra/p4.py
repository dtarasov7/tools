#!/usr/bin/env python3
import os
import sys
import time
import getpass
import subprocess
import threading
from ansible_vault import Vault
from pynput.keyboard import Controller

# === НАСТРОЙКИ ===
VAULT_FILE = "secret.vault"
PID_FILE = "/tmp/keyinject_xinput.pid"
LOG_FILE = "/tmp/keyinject_xinput.log"
TARGET_KEYSYM = "Pause"  # Целевая клавиша (можно заменить на другую)
MODIFIERS_REQUIRED = {"Shift"}  # Требуемые модификаторы

# === ГЛОБАЛЬНЫЕ ===
TYPE_TEXT = ""
keyboard = Controller()

def log(msg):
    with open(LOG_FILE, "a") as f:
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")

def daemonize():
    if os.fork() > 0:
        sys.exit(0)
    os.setsid()
    if os.fork() > 0:
        sys.exit(0)

    sys.stdin.close()
    sys.stdout.close()
    sys.stderr.close()

    with open(PID_FILE, "w") as f:
        f.write(str(os.getpid()))

def decrypt_vault_file(password):
    try:
        with open(VAULT_FILE, "r", encoding="utf-8") as f:
            encrypted = f.read()
        vault = Vault(password)
        decrypted = vault.load(encrypted)
        return decrypted["secret_var"]
    except Exception as e:
        log(f"Ошибка при расшифровке: {e}")
        sys.exit(1)

def type_secret():
    global TYPE_TEXT
    log("Вставляем текст в активное окно")
    keyboard.type(TYPE_TEXT)

def monitor_keyboard():
    log("Запуск мониторинга клавиш через xinput")

    # Получаем ID клавиатурных устройств
    try:
        output = subprocess.check_output(["xinput", "list"], universal_newlines=True)
    except subprocess.CalledProcessError as e:
        log(f"Ошибка xinput list: {e}")
        sys.exit(1)

    device_ids = []
    for line in output.splitlines():
        if "keyboard" in line.lower():
            parts = line.split("id=")
            if len(parts) > 1:
                device_id = parts[1].split()[0]
                device_ids.append(device_id)

    if not device_ids:
        log("Клавиатурные устройства не найдены.")
        sys.exit(1)

    for device_id in device_ids:
        t = threading.Thread(target=listen_to_device, args=(device_id,))
        t.daemon = True
        t.start()

    while True:
        time.sleep(1)

def listen_to_device(device_id):
    log(f"Мониторим устройство ID {device_id}")
    proc = subprocess.Popen(
        ["xinput", "test", device_id],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )

    pressed_keys = set()

    for line in proc.stdout:
        line = line.strip()
        if "key press" in line:
            key_code = line.split()[-1]
            key_name = get_key_name(key_code)
            if key_name:
                pressed_keys.add(key_name)

                if TARGET_KEYSYM in pressed_keys and MODIFIERS_REQUIRED.issubset(pressed_keys):
                    log(f"Обнаружено: {MODIFIERS_REQUIRED} + {TARGET_KEYSYM}")
                    type_secret()
                    pressed_keys.clear()

        elif "key release" in line:
            key_code = line.split()[-1]
            key_name = get_key_name(key_code)
            if key_name and key_name in pressed_keys:
                pressed_keys.remove(key_name)

def get_key_name(key_code):
    try:
        output = subprocess.check_output(["xmodmap", "-pke"], universal_newlines=True)
        for line in output.splitlines():
            if line.startswith(f"keycode {key_code}"):
                parts = line.strip().split()
                if len(parts) >= 3:
                    return parts[2].strip()
    except Exception as e:
        log(f"Ошибка получения имени клавиши: {e}")
    return None

def main():
    global TYPE_TEXT
    print("🔐 Введите пароль для расшифровки:")
    password = getpass.getpass()
    TYPE_TEXT = decrypt_vault_file(password)

    daemonize()
    log("Демон запущен")
    monitor_keyboard()

if __name__ == "__main__":
    main()

