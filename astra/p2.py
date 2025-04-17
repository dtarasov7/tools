Конечно! Вот **полный скрипт**, который:

---

### ✅ Что делает:

1. **Запрашивает пароль** при запуске  
2. **Расшифровывает файл**, закодированный с помощью **`ansible-vault`** (с помощью модуля `ansible_vault`)
3. Использует **расшифрованный текст** как `TYPE_TEXT`
4. Уходит в **фон (демон)**
5. **Ждёт нажатия `Shift + Break`**
6. **Впечатывает текст** в активное окно
7. **Защита от повторного срабатывания при удержании клавиш**

---

## 📦 Зависимости (установить один раз):

```bash
pip3 install ansible-vault pynput
```

---

## 📁 Пример зашифрованного файла

Создай файл:
```bash
ansible-vault encrypt_string 'Секретная строка' --name secret_var > secret.vault
```

---

## ✅ Полный код: `vault_typing_daemon.py`

```python
#!/usr/bin/env python3
import os
import sys
import time
import getpass
from pynput import keyboard
from ansible_vault import Vault

# Файл с зашифрованными данными
VAULT_FILE = 'secret.vault'
LOG_FILE = '/tmp/type_daemon.log'
PID_FILE = '/tmp/type_daemon.pid'

# Клавиши для активации: Shift + Break
COMBINATION = {keyboard.Key.shift, keyboard.Key.break_key}
current_keys = set()
already_triggered = False

# Контроллер клавиатуры
kbd_controller = keyboard.Controller()

# Расшифрованный текст будет здесь
TYPE_TEXT = ""


def log(msg):
    with open(LOG_FILE, "a") as f:
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")


def decrypt_vault_file(password):
    try:
        with open(VAULT_FILE, 'r', encoding='utf-8') as f:
            encrypted = f.read()
        vault = Vault(password)
        decrypted = vault.load(encrypted)
        log("Успешно расшифровано содержимое файла")
        return decrypted['secret_var']
    except Exception as e:
        log(f"Ошибка при расшифровке: {e}")
        sys.exit("Неверный пароль или формат файла")


def type_secret():
    try:
        global already_triggered
        if already_triggered:
            return
        kbd_controller.type(TYPE_TEXT)
        already_triggered = True
    except Exception as e:
        log(f"Ошибка ввода текста: {e}")


def on_press(key):
    global already_triggered
    if key in COMBINATION:
        current_keys.add(key)
        if COMBINATION.issubset(current_keys) and not already_triggered:
            log("Перехват: Shift + Break — впечатываем строку")
            type_secret()
    else:
        current_keys.clear()


def on_release(key):
    global already_triggered
    if key in current_keys:
        current_keys.remove(key)
    if not COMBINATION.issubset(current_keys):
        already_triggered = False


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
    global TYPE_TEXT
    print("🔐 Введите пароль для расшифровки:")
    password = getpass.getpass()

    TYPE_TEXT = decrypt_vault_file(password)
    log("Текст загружен, запускаем демон")

    daemonize()

    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()


if __name__ == "__main__":
    main()
```

---

## 🧪 Как использовать:

1. Подготовь `secret.vault`, как выше.
2. Запусти скрипт:
   ```bash
   chmod +x vault_typing_daemon.py
   ./vault_typing_daemon.py
   ```
3. Введи пароль при запуске.
4. Перейди в текстовое окно, нажми `Shift + Break` — текст будет вписан.

---

## 🛑 Как остановить:

```bash
kill $(cat /tmp/type_daemon.pid)
```

---

Хочешь — добавлю поддержку **множественных горячих клавиш**, **сигнала перезапуска**, или **автозапуск в X-сессии**.
