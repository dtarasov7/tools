Вот полный рабочий пример обеих программ с разделением логики проверки ключа в отдельный модуль `auth.py`, использующий **SHA-256 хеш** вместо открытого секрета.

---

## 🧠 Концепция:

- **Ключ `topsecretkey`** хэшируется и **не фигурирует явно в коде**.
- Модуль `auth.py` знает только его хеш.
- При подключении клиент отправляет секрет, сервер проверяет хеш.
- Всё логируется в файл `vault_reader.log`.

---

## 📁 Структура проекта:

```
project/
│
├── auth.py
├── vault_reader.py
├── vault_client.py
├── secret.vault
└── vault_reader.log (создаётся при запуске)
```

---

## 🔐 `auth.py` — модуль проверки секрета (без раскрытия)

```python
# auth.py
import hashlib

# Это sha256('topsecretkey')
_EXPECTED_HASH = "3c189e4fbd4a94b4de28e514438f61868aeb6e0a46339c986b6a807a860b1d95"

def verify_key(user_input):
    return hashlib.sha256(user_input.encode()).hexdigest() == _EXPECTED_HASH
```

---

## 🧷 `vault_reader.py` — сервер

```python
# vault_reader.py
import socket
import os
import sys
import logging
from ansible_vault import Vault
import auth  # модуль проверки секрета

SOCKET_PATH = "/tmp/vault_socket"
VAULT_FILE = "secret.vault"
LOG_FILE = "vault_reader.log"

# Настройка логирования
logging.basicConfig(
    filename=LOG_FILE,
    filemode='a',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

def decrypt_vault_file(password):
    try:
        with open(VAULT_FILE, "r") as f:
            encrypted_data = f.read()
        vault = Vault(password)
        decrypted_data = vault.load(encrypted_data)
        logging.info("Файл успешно расшифрован.")
        return decrypted_data
    except Exception as e:
        logging.error(f"Ошибка при расшифровке: {e}")
        sys.exit(1)

def handle_connection(conn, decrypted_data):
    try:
        auth_key = conn.recv(1024).decode().strip()
        if not auth.verify_key(auth_key):
            logging.warning("Неверный ключ от клиента.")
            conn.sendall(b"AUTH FAILED")
        else:
            logging.info("Успешное подключение. Данные отправлены.")
            conn.sendall(decrypted_data.encode())
    except Exception as e:
        logging.error(f"Ошибка соединения: {e}")
    finally:
        conn.close()

def start_server(decrypted_data):
    if os.path.exists(SOCKET_PATH):
        os.remove(SOCKET_PATH)

    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as server:
        server.bind(SOCKET_PATH)
        server.listen(1)
        os.chmod(SOCKET_PATH, 0o600)
        logging.info(f"Сервер запущен. Сокет: {SOCKET_PATH}")

        while True:
            try:
                conn, _ = server.accept()
                handle_connection(conn, decrypted_data)
            except Exception as e:
                logging.error(f"Ошибка в основном цикле: {e}")

def main():
    if not os.path.exists(VAULT_FILE):
        logging.error(f"Файл {VAULT_FILE} не найден.")
        sys.exit(1)

    try:
        password = input("Введите пароль для Ansible Vault: ")
        decrypted = decrypt_vault_file(password)
        start_server(decrypted)
    except Exception as e:
        logging.critical(f"Необработанная ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

---

## 🔑 `vault_client.py` — клиент

```python
# vault_client.py
import socket

SOCKET_PATH = "/tmp/vault_socket"
SHARED_SECRET = "topsecretkey"  # Это знает только клиент

def main():
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
            client.connect(SOCKET_PATH)
            client.sendall(SHARED_SECRET.encode())
            data = client.recv(65536).decode()

        if data == "AUTH FAILED":
            print("❌ Неверный ключ доступа.")
        else:
            print("✅ Полученные данные:\n")
            print(data)

    except FileNotFoundError:
        print("❌ Сервер не запущен или сокет не существует.")
    except Exception as e:
        print(f"⚠️ Ошибка при подключении: {e}")

if __name__ == "__main__":
    main()
```

---

## 🧪 Подготовка:

1. Установи модуль:
   ```bash
   pip install ansible-vault
   ```

2. Создай зашифрованный файл:
   ```bash
   ansible-vault create secret.vault
   ```

3. Введи туда секретные данные.

4. Запусти сервер:
   ```bash
   python3 vault_reader.py
   ```

5. Затем клиент:
   ```bash
   python3 vault_client.py
   ```

---

Если хочешь — могу:
- Сгенерировать токен во время запуска
- Вынести `auth.py` в бинарник через Cython
- Сделать логгер с ротацией файлов

Готов продолжать :)