#!/usr/bin/env python3
import os
import sys
import time
import getpass
from ansible_vault import Vault
from pynput.keyboard import Controller
from Xlib import X, display
from Xlib.ext import record
from Xlib.protocol import rq

# ===== НАСТРОЙКИ =====
VAULT_FILE = 'secret.vault'
LOG_FILE = '/tmp/type_daemon.log'
PID_FILE = '/tmp/type_daemon.pid'
SHIFT_MASK = 1
keyboard = Controller()

# ===== ГЛОБАЛЬНЫЕ =====
TYPE_TEXT = ""
PAUSE_KEYCODE = None
local_dpy = display.Display()
record_dpy = display.Display()

def log(msg):
    with open(LOG_FILE, "a") as f:
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")

def decrypt_vault_file(password):
    try:
        with open(VAULT_FILE, 'r', encoding='utf-8') as f:
            encrypted = f.read()
        vault = Vault(password)
        decrypted = vault.load(encrypted)
        log("Успешно расшифрован файл")
        return decrypted['secret_var']
    except Exception as e:
        log(f"Ошибка при расшифровке: {e}")
        sys.exit("❌ Неверный пароль или повреждённый файл")

def type_text():
    try:
        log("Впечатываем текст...")
        keyboard.type(TYPE_TEXT)
    except Exception as e:
        log(f"Ошибка при вводе текста: {e}")

def record_callback(reply):
    if reply.category != record.FromServer:
        return
    if reply.client_swapped or not len(reply.data) or reply.data[0] < 2:
        return

    data = reply.data
    event_type = data[1]
    keycode = data[2]
    state = int.from_bytes(data[4:6], byteorder='little')

    if event_type == X.KeyPress and keycode == PAUSE_KEYCODE and (state & SHIFT_MASK):
        log("Нажата комбинация Shift + Pause")
        type_text()

def start_listener():
    if not record_dpy.has_extension("RECORD"):
        log("❌ RECORD extension не поддерживается")
        sys.exit(1)

    ctx = record_dpy.record_create_context(
        0,
        [record.AllClients],
        [{
            'core_requests': (0, 0),
            'core_replies': (0, 0),
            'ext_requests': (0, 0, 0, 0),
            'ext_replies': (0, 0, 0, 0),
            'delivered_events': (0, 0),
            'device_events': (X.KeyPress, X.KeyRelease),
            'errors': (0, 0),
            'client_started': False,
            'client_died': False,
        }]
    )

    log("Ожидание нажатия Shift + Pause...")
    record_dpy.record_enable_context(ctx, record_callback)
    record_dpy.record_free_context(ctx)

def daemonize():
    if os.fork() > 0:
        sys.exit(0)
    os.setsid()
    if os.fork() > 0:
        sys.exit(0)

    sys.stdout.flush()
    sys.stderr.flush()
    with open('/dev/null', 'rb', 0) as f:
        os.dup2(f.fileno(), sys.stdin.fileno())
    with open('/dev/null', 'ab', 0) as f:
        os.dup2(f.fileno(), sys.stdout.fileno())
        os.dup2(f.fileno(), sys.stderr.fileno())

    with open(PID_FILE, 'w') as f:
        f.write(str(os.getpid()))

def main():
    global TYPE_TEXT, PAUSE_KEYCODE

    print("🔐 Введите пароль для расшифровки:")
    password = getpass.getpass()
    TYPE_TEXT = decrypt_vault_file(password)

    PAUSE_KEYCODE = local_dpy.keysym_to_keycode(0xff13)  # XK_Pause
    log("Получен keycode клавиши Pause: {}".format(PAUSE_KEYCODE))

    log("Запуск демона")
    daemonize()
    start_listener()

if __name__ == "__main__":
    main()

