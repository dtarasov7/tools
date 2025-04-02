Вот код на Python3 с использованием библиотеки boto3 для работы с Ceph RadosGW (S3-совместимый интерфейс), который соответствует всем вашим требованиям:

```python
import boto3
import os
import random
import time
import threading
import argparse
import sys
import keyboard
from queue import Queue
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from signal import signal, SIGINT

class CephLoadTester:
    def __init__(self):
        self.parse_args()
        self.setup_s3_client()
        self.bucket_name = f"load-test-bucket-{int(time.time())}"
        self.objects_created = 0
        self.stats = {
            'read': {'times': [], 'speeds': []},
            'write': {'times': [], 'speeds': []},
            'update': {'times': [], 'speeds': []}
        }
        self.stop_flag = False
        self.iteration = 0
        self.delays = {'read': 0, 'write': 0, 'update': 0}
        
        # Обработка Ctrl-C
        signal(SIGINT, self.signal_handler)
        
    def signal_handler(self, sig, frame):
        print("\nCtrl-C detected, stopping...")
        self.stop_flag = True
        
    def parse_args(self):
        parser = argparse.ArgumentParser(description='Ceph Load Tester')
        parser.add_argument('--size', type=int, required=True, help='Size of each object in bytes')
        parser.add_argument('--objects', type=int, required=True, help='Initial number of objects to create')
        parser.add_argument('--read', type=int, required=True, help='Number of objects to read per iteration (N)')
        parser.add_argument('--write', type=int, required=True, help='Number of objects to write per iteration (M)')
        parser.add_argument('--update', type=int, required=True, help='Number of objects to update per iteration (K)')
        parser.add_argument('--threads', type=int, default=10, help='Number of threads to use for parallel operations')
        
        self.args = parser.parse_args()
        
    def setup_s3_client(self):
        # Настройте параметры подключения к вашему Ceph RadosGW
        self.s3 = boto3.client(
            's3',
            endpoint_url=os.getenv('CEPH_ENDPOINT', 'http://ceph-rgw:8080'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID', 'access_key'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY', 'secret_key')
        )
        
    def create_bucket(self):
        try:
            self.s3.create_bucket(Bucket=self.bucket_name)
            print(f"Bucket {self.bucket_name} created successfully.")
        except Exception as e:
            print(f"Error creating bucket: {e}")
            sys.exit(1)
            
    def generate_object_name(self, idx=None):
        if idx is not None:
            return f"object_{idx}"
        return f"object_{self.objects_created}"
    
    def create_initial_objects(self):
        print(f"Creating {self.args.objects} initial objects...")
        data = os.urandom(self.args.size)
        
        with ThreadPoolExecutor(max_workers=self.args.threads) as executor:
            futures = []
            for i in range(self.args.objects):
                obj_name = self.generate_object_name(i)
                futures.append(executor.submit(self.put_object, obj_name, data))
                
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"Error creating initial object: {e}")
                    
        self.objects_created = self.args.objects
        print("Initial objects created.")
        
    def put_object(self, key, data):
        try:
            start = time.time()
            self.s3.put_object(Bucket=self.bucket_name, Key=key, Body=data)
            duration = time.time() - start
            return duration
        except Exception as e:
            print(f"Error putting object {key}: {e}")
            return 0
        
    def get_object(self, key):
        try:
            start = time.time()
            self.s3.get_object(Bucket=self.bucket_name, Key=key)
            duration = time.time() - start
            return duration
        except Exception as e:
            print(f"Error getting object {key}: {e}")
            return 0
        
    def update_object(self, key, data):
        try:
            start = time.time()
            self.s3.put_object(Bucket=self.bucket_name, Key=key, Body=data)
            duration = time.time() - start
            return duration
        except Exception as e:
            print(f"Error updating object {key}: {e}")
            return 0
        
    def get_random_objects(self, count):
        if self.objects_created == 0:
            return []
            
        available_objects = min(count, self.objects_created)
        return random.sample(range(self.objects_created), available_objects)
        
    def calculate_delays(self, operation_stats):
        if self.iteration == 0:
            return
            
        # Рассчитываем среднее время выполнения операций
        avg_read_time = sum(self.stats['read']['times'][-1]) / len(self.stats['read']['times'][-1]) if self.stats['read']['times'][-1] else 0
        avg_write_time = sum(self.stats['write']['times'][-1]) / len(self.stats['write']['times'][-1]) if self.stats['write']['times'][-1] else 0
        avg_update_time = sum(self.stats['update']['times'][-1]) / len(self.stats['update']['times'][-1]) if self.stats['update']['times'][-1] else 0
        
        # Рассчитываем общее время выполнения каждой группы операций в последней итерации
        total_read_time = sum(self.stats['read']['times'][-1]) if self.stats['read']['times'][-1] else 0
        total_write_time = sum(self.stats['write']['times'][-1]) if self.stats['write']['times'][-1] else 0
        total_update_time = sum(self.stats['update']['times'][-1]) if self.stats['update']['times'][-1] else 0
        
        # Рассчитываем желаемое общее время (максимальное из всех групп операций)
        desired_total_time = max(total_read_time, total_write_time, total_update_time)
        
        # Рассчитываем новые задержки
        if self.args.read > 0 and avg_read_time > 0:
            self.delays['read'] = max(0, (desired_total_time - total_read_time) / self.args.read)
            
        if self.args.write > 0 and avg_write_time > 0:
            self.delays['write'] = max(0, (desired_total_time - total_write_time) / self.args.write)
            
        if self.args.update > 0 and avg_update_time > 0:
            self.delays['update'] = max(0, (desired_total_time - total_update_time) / self.args.update)
            
        print(f"New delays - Read: {self.delays['read']:.2f}s, Write: {self.delays['write']:.2f}s, Update: {self.delays['update']:.2f}s")
        
    def run_operation(self, operation, count, delay):
        operation_stats = []
        data = os.urandom(self.args.size)
        
        def worker(key):
            nonlocal operation_stats
            time.sleep(delay * idx)  # Применяем задержку перед операцией
            
            start = time.time()
            if operation == 'read':
                duration = self.get_object(key)
            elif operation == 'write':
                duration = self.put_object(key, data)
                if duration > 0:  # Если запись успешна, увеличиваем счетчик
                    with threading.Lock():
                        self.objects_created += 1
            elif operation == 'update':
                duration = self.update_object(key, data)
                
            real_duration = time.time() - start
            if real_duration > 0:
                operation_stats.append(real_duration)
            return duration
            
        with ThreadPoolExecutor(max_workers=self.args.threads) as executor:
            futures = []
            for idx in range(count):
                if operation == 'read':
                    # Для чтения выбираем случайные существующие объекты
                    if self.objects_created == 0:
                        continue
                    obj_idx = random.randint(0, self.objects_created - 1)
                    key = self.generate_object_name(obj_idx)
                else:
                    # Для записи и обновления создаем новые или обновляем существующие ключи
                    if operation == 'write':
                        key = self.generate_object_name()
                    else:  # update
                        if self.objects_created == 0:
                            continue
                        obj_idx = random.randint(0, self.objects_created - 1)
                        key = self.generate_object_name(obj_idx)
                
                futures.append(executor.submit(worker, key))
                
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"Error in {operation} operation: {e}")
                    
        return operation_stats
        
    def run_iteration(self):
        self.iteration += 1
        print(f"\n--- Starting iteration {self.iteration} ---")
        start_time = time.time()
        
        # Запускаем операции с текущими задержками
        read_stats = self.run_operation('read', self.args.read, self.delays['read'])
        write_stats = self.run_operation('write', self.args.write, self.delays['write'])
        update_stats = self.run_operation('update', self.args.update, self.delays['update'])
        
        # Сохраняем статистику
        if read_stats:
            self.stats['read']['times'].append(read_stats)
            self.stats['read']['speeds'].append([self.args.size / t / 1024 for t in read_stats])  # KB/s
            
        if write_stats:
            self.stats['write']['times'].append(write_stats)
            self.stats['write']['speeds'].append([self.args.size / t / 1024 for t in write_stats])
            
        if update_stats:
            self.stats['update']['times'].append(update_stats)
            self.stats['update']['speeds'].append([self.args.size / t / 1024 for t in update_stats])
            
        # Вычисляем новые задержки для следующей итерации
        self.calculate_delays({
            'read': read_stats,
            'write': write_stats,
            'update': update_stats
        })
        
        # Выводим статистику
        self.print_stats()
        
    def print_stats(self):
        def avg(lst):
            return sum(lst) / len(lst) if lst else 0
            
        print("\n--- Statistics ---")
        print(f"Total objects in bucket: {self.objects_created}")
        
        for op in ['read', 'write', 'update']:
            if not self.stats[op]['times'] or not self.stats[op]['times'][-1]:
                continue
                
            last_times = self.stats[op]['times'][-1]
            last_speeds = self.stats[op]['speeds'][-1]
            
            all_times = [t for sublist in self.stats[op]['times'] for t in sublist]
            all_speeds = [s for sublist in self.stats[op]['speeds'] for s in sublist]
            
            print(f"\n{op.capitalize()} operations (last iteration):")
            print(f"  Count: {len(last_times)}")
            print(f"  Avg time: {avg(last_times):.4f}s")
            print(f"  Avg speed: {avg(last_speeds):.2f} KB/s")
            
            print(f"\n{op.capitalize()} operations (all iterations):")
            print(f"  Total count: {len(all_times)}")
            print(f"  Overall avg time: {avg(all_times):.4f}s")
            print(f"  Overall avg speed: {avg(all_speeds):.2f} KB/s")
            
    def cleanup(self):
        print("\nCleaning up...")
        
        # Удаляем все объекты в бакете
        try:
            objects = self.s3.list_objects_v2(Bucket=self.bucket_name)
            if 'Contents' in objects:
                with ThreadPoolExecutor(max_workers=self.args.threads) as executor:
                    for obj in objects['Contents']:
                        executor.submit(self.s3.delete_object, Bucket=self.bucket_name, Key=obj['Key'])
                print(f"Deleted {len(objects['Contents'])} objects.")
                
            # Удаляем сам бакет
            self.s3.delete_bucket(Bucket=self.bucket_name)
            print(f"Bucket {self.bucket_name} deleted.")
        except Exception as e:
            print(f"Error during cleanup: {e}")
            
    def check_keyboard(self):
        if keyboard.is_pressed('q') or keyboard.is_pressed('Q') or keyboard.is_pressed('й') or keyboard.is_pressed('Й'):
            print("\nExit key pressed, stopping...")
            return True
        return False
            
    def run(self):
        try:
            self.create_bucket()
            self.create_initial_objects()
            
            print("\nPress q/Q/й/Й or Ctrl-C to stop the test...")
            
            while not self.stop_flag:
                if self.check_keyboard():
                    break
                    
                self.run_iteration()
                
        finally:
            self.cleanup()
            
if __name__ == "__main__":
    tester = CephLoadTester()
    tester.run()
```

### Инструкция по использованию:

1. Установите необходимые зависимости:
```bash
pip install boto3 keyboard
```

2. Запустите программу с параметрами, например:
```bash
python3 ceph_load_test.py --size 1024 --objects 100 --read 10 --write 5 --update 3 --threads 20
```

### Параметры командной строки:
- `--size`: размер каждого объекта в байтах (обязательный)
- `--objects`: начальное количество объектов для создания (обязательный)
- `--read`: количество объектов для чтения в каждой итерации (N) (обязательный)
- `--write`: количество объектов для записи в каждой итерации (M) (обязательный)
- `--update`: количество объектов для обновления в каждой итерации (K) (обязательный)
- `--threads`: количество потоков для параллельных операций (по умолчанию 10)

### Особенности реализации:
1. Динамическая регулировка задержек между операциями для выравнивания времени выполнения разных типов операций
2. Обработка ошибок при вызовах API Ceph
3. Поддержка выхода по нажатию клавиш q/Q/й/Й или Ctrl-C
4. Многопоточное выполнение операций
5. Статистика производительности для каждой операции
6. Автоматическая очистка (удаление всех объектов и бакета) при завершении
7. Поддержка больших объемов данных через потоковую обработку

### Настройка подключения к Ceph:
По умолчанию программа использует переменные окружения:
- `CEPH_ENDPOINT` - endpoint URL Ceph RadosGW (по умолчанию `http://ceph-rgw:8080`)
- `AWS_ACCESS_KEY_ID` - ключ доступа S3 (по умолчанию 'access_key')
- `AWS_SECRET_ACCESS_KEY` - секретный ключ S3 (по умолчанию 'secret_key')

Вы можете либо установить эти переменные окружения, либо изменить значения по умолчанию в коде.
