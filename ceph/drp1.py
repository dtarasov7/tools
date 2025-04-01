Скорректируй пожалуйста в код так , чтобы между каждым чтением, каждым изменение и каждым добавлением выдерживалась пауза, такая, чтобы операции в каждом потоке завершались примерно в одно и тоже время. В первой итерации эта задержка равна нулю, а в следущей они высчитывалась на основании временной стаистики в предыдущей итерации.
Пример (цифры случайные).
в одной итерации:
-  100 чтений , каждое из которых длится 1 сек
- 10 изменений каждое длится 6 сек
- 5 добавлений, каждое длиться 8 секунд
В это случае между чтениями нет пауз, между изменениями пауза 4 секунды, между добавлениями пауза 12 секунд. Тогда 100 чтений будет длиться 100 секунд. 10 изменений с паузами будет длиться тоже 100 секунд. И 5 добавлений с паузами будет длиться тоже 100 секунд.


ChatGPT сказал:
Вот обновленный код с динамической паузой между операциями, чтобы все потоки завершались примерно одновременно.

Основные улучшения:
✅ Динамическое вычисление паузы на основе времени выполнения операций в предыдущей итерации.
✅ Синхронизация потоков, чтобы все операции (чтение, запись, обновление) завершались одновременно.
✅ Первая итерация выполняется без пауз, но со второй итерации паузы высчитываются автоматически.

Как работает алгоритм паузы?
В первой итерации нет пауз, записывается время выполнения операций.

В следующих итерациях рассчитываются паузы:

Берется максимальное время выполнения одной операции в каждой категории.

Рассчитывается необходимая пауза между операциями так, чтобы самый медленный процесс определял общее время выполнения.

Например, если чтение занимает 1 сек, обновление 6 сек, а запись 8 сек, то паузы будут:

Чтения: 0 сек

Обновления: 4 сек

Записи: 12 сек

Обновленный код:
python
Копировать
Редактировать
import boto3
import os
import random
import time
import sys
import threading
import signal
import termios
import tty
import argparse
from botocore.exceptions import BotoCoreError, ClientError

stop_flag = False  # Глобальный флаг для выхода

def signal_handler(sig, frame):
    global stop_flag
    stop_flag = True
    print("\nЗавершение работы...")

signal.signal(signal.SIGINT, signal_handler)  # Перехват Ctrl-C

def safe_call(func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except (BotoCoreError, ClientError) as e:
        return e

def key_listener():
    global stop_flag
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)
        while not stop_flag:
            ch = sys.stdin.read(1)
            if ch.lower() in ["q", "й"]:
                stop_flag = True
                print("\nЗавершение работы...")
                break
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

def s3_test(bucket_name, num_init_objects, object_size, num_read, num_write, num_update):
    global stop_flag

    s3 = boto3.client(
        "s3",
        endpoint_url="http://ceph-rgw.example.com",
        aws_access_key_id="your-access-key",
        aws_secret_access_key="your-secret-key"
    )

    response = safe_call(s3.create_bucket, Bucket=bucket_name)
    if isinstance(response, ClientError) and response.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
        print(f"Бакет {bucket_name} уже существует.")
    elif isinstance(response, ClientError):
        print(f"Ошибка при создании бакета: {response}")
        return

    object_keys = []
    iteration = 0
    read_times, write_times, update_times = [], [], []
    read_pause, write_pause, update_pause = 0, 0, 0  

    print(f"Заполняем бакет {bucket_name} {num_init_objects} объектами...")
    for i in range(num_init_objects):
        key = f"init-object-{i}"
        object_keys.append(key)
        data = os.urandom(object_size)
        safe_call(s3.put_object, Bucket=bucket_name, Key=key, Body=data)

    print("Исходные данные загружены.")

    key_thread = threading.Thread(target=key_listener, daemon=True)
    key_thread.start()

    while not stop_flag:
        iteration += 1
        print(f"\n=== Итерация {iteration} ===")

        current_read_times, current_write_times, current_update_times = [], [], []

        def write_objects():
            for i in range(num_write):
                key = f"object-{iteration}-{i}"
                object_keys.append(key)
                data = os.urandom(object_size)
                start_time = time.time()
                safe_call(s3.put_object, Bucket=bucket_name, Key=key, Body=data)
                current_write_times.append(time.time() - start_time)
                if i < num_write - 1:
                    time.sleep(write_pause)

        def read_objects():
            for i, key in enumerate(random.sample(object_keys, min(num_read, len(object_keys)))):
                start_time = time.time()
                safe_call(s3.get_object, Bucket=bucket_name, Key=key)
                current_read_times.append(time.time() - start_time)
                if i < num_read - 1:
                    time.sleep(read_pause)

        def update_objects():
            for i, key in enumerate(random.sample(object_keys, min(num_update, len(object_keys)))):
                data = os.urandom(object_size)
                start_time = time.time()
                safe_call(s3.put_object, Bucket=bucket_name, Key=key, Body=data)
                current_update_times.append(time.time() - start_time)
                if i < num_update - 1:
                    time.sleep(update_pause)

        threads = [
            threading.Thread(target=write_objects),
            threading.Thread(target=read_objects),
            threading.Thread(target=update_objects)
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        max_read_time = max(current_read_times) if current_read_times else 0
        max_write_time = max(current_write_times) if current_write_times else 0
        max_update_time = max(current_update_times) if current_update_times else 0

        max_operation_time = max(max_read_time * num_read, max_write_time * num_write, max_update_time * num_update)

        read_pause = (max_operation_time / num_read) - max_read_time if num_read > 0 else 0
        write_pause = (max_operation_time / num_write) - max_write_time if num_write > 0 else 0
        update_pause = (max_operation_time / num_update) - max_update_time if num_update > 0 else 0

        read_times.extend(current_read_times)
        write_times.extend(current_write_times)
        update_times.extend(current_update_times)

        avg_read = sum(read_times) / len(read_times) if read_times else 0
        avg_write = sum(write_times) / len(write_times) if write_times else 0
        avg_update = sum(update_times) / len(update_times) if update_times else 0

        print(f"Чтения: Среднее время {avg_read:.4f} сек, Пауза {read_pause:.4f} сек")
        print(f"Записи: Среднее время {avg_write:.4f} сек, Пауза {write_pause:.4f} сек")
        print(f"Обновления: Среднее время {avg_update:.4f} сек, Пауза {update_pause:.4f} сек")

    print("\nОчистка бакета...")
    for key in object_keys:
        safe_call(s3.delete_object, Bucket=bucket_name, Key=key)

    safe_call(s3.delete_bucket, Bucket=bucket_name)
    print(f"Бакет {bucket_name} удалён. Завершение работы.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ceph S3 тестирование.")
    parser.add_argument("--bucket", required=True, help="Имя бакета")
    parser.add_argument("--init-objects", type=int, required=True, help="Количество начальных объектов")
    parser.add_argument("--size", type=int, required=True, help="Размер объекта в байтах")
    parser.add_argument("--read", type=int, required=True, help="Количество объектов для чтения за итерацию")
    parser.add_argument("--write", type=int, required=True, help="Количество новых объектов за итерацию")
    parser.add_argument("--update", type=int, required=True, help="Количество объектов для обновления за итерацию")

    args = parser.parse_args()

    s3_test(
        bucket_name=args.bucket,
        num_init_objects=args.init_objects,
        object_size=args.size,
        num_read=args.read,
        num_write=args.write,
        num_update=args.update
    )
Как теперь работает код?
✅ Динамически рассчитываются паузы для синхронного завершения всех операций.
✅ Первая итерация без пауз, затем паузы адаптируются.
✅ Все операции теперь завершаются одновременно в каждой итерации.

Теперь программа эффективнее и точнее распределяет нагрузку. 🚀
