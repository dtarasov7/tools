пользователя):
sudo apt install python3-pip
sudo pip3 install setuptools
sudo pip3 install pyperclip pyautogui xlib
sudo apt install python3-tk python3-dev

Ну и, конечно, текст скрипта вы можете найти ниже. Я размещаю его как open source в надежде, что это облегчит кому-то жизнь и/или работу за компьютером. Сохраните этот текст в файл с расширением "py", стандартным для скриптов на Python, например "Swtchr.py":

#! /usr/bin/python3

"""
# Этот скрипт написан на Python 3.
# Это упрощённый аналог XNeur и PuntoSwitcher, который работает с запущенными в Wine приложениями
#
# Использование: Назначить в системе комбинацию клавиш (типа [Ctrl]+[R_Win]) на скрипт
#                и применять её для ручного переключения введённого в неверной раскладке текста.
#
# Требования: необходим подключённый модуль работы с буфером обмена
#               'pyperclip',
#             а также модули автоматизации работы
#               'pyautogui' и 'xlib'
#
# Михаил Винаков, 2019-06-14
# 2019-08-01: Добавлена возможность запуска с параметрами -lastword и -selected
"""

import pyautogui, time, sys

no_pyperclip = False

clpbrd_strg = ""
layout_01 = "`~@#$%^&" +\
            "qwertyuiop[]QWERTYUIOP{}asdfghjkl;'\\ASDFGHJKL:\"|zxcvbnm,./ZXCVBNM<>?"
layout_02 = "ёЁ\"№;%:?" +\
            "йцукенгшщзхъЙЦУКЕНГШЩЗХЪфывапролджэ\\ФЫВАПРОЛДЖЭ/ячсмитьбю.ЯЧСМИТЬБЮ,"

try:                                    # Пробное импортирование необходимого модуля
    import pyperclip                    # В случае неудачи выполнение скрипта бессмысленно
except ImportError:
    no_pyperclip = True

def computing():
    if no_pyperclip == True:
        print("Требуется модуль работы с буфером обмена: pyperclip")
        quit()
    elif len(layout_01) != len(layout_02):
        print("Наборы символов раскладок (layout_01 и layout_02) не совпадают по длине!")
        quit()
    else:
        workaround()

def workaround():
    pyperclip.copy("")
    time.sleep(.1)
    if len(sys.argv) < 2:
        pyautogui.hotkey("shift", "home")
        time.sleep(.3)
        pyautogui.hotkey("ctrl", "x")
    elif sys.argv[1] == "-selected":
        pyautogui.hotkey("ctrl", "x")
    elif sys.argv[1] == "-lastword":
        pyautogui.hotkey("shift", "ctrl", "left")
        time.sleep(.3)
        pyautogui.hotkey("ctrl", "x")
    else:
        print("Неизвестный параметр запуска:", sys.argv[1])
        quit()
    fixed_text = magic(pyperclip.paste())
    pyperclip.copy(fixed_text)
    time.sleep(.1)
    pyautogui.hotkey("ctrl", "v")

def magic(text):
    if len(text) < 1:
        quit()
    elif len(text) < 3:                 # Сравним каких символов больше
        first_x = 1                     # Для сравнения желательны нечётные числа
    else:
        first_x = 3

    chars_01, chars_02 = 0, 0
    for i in range(first_x):            # Какой раскладки первых символов больше: 01 или 02?
        if text[i] in layout_01:
            chars_01 += 1
        elif text[i] in layout_02:
            chars_02 += 1
    if chars_01 > chars_02:             # Разные последовательности, исходя из полученного
        layout = layout_01 + layout_02 + layout_01
    else:
        layout = layout_02 + layout_01 + layout_02

    new_text = ""
    for c in range(len(text)):          # Пропуск символов, которых "нет в раскладках"
        if not text[c] in layout:
            new_text = new_text + text[c]
        else:
            new_text = new_text + layout[layout.find(text[c])+len(layout_01)]
    return new_text

clpbrd_strg = pyperclip.paste()         # Сохранение текущего содержимого буфера обмена
computing()
pyperclip.copy(clpbrd_strg)             # Восстановление содержимого буфера обмена
clpbrd_strg = ""

Обнаружил, что с приложениями под Wine после выполнения скрипта "залипает" правая клавиша [Ctrl], которую я использую в комбинации для вызова. Проблему удалось решить добавив несколько дополнительных строк в конец скрипта. Они имитируют нажатие и отпускание правой клавиши [Ctrl]:

# Для устранения проблемы с залипанием правого [Ctrl]
pyautogui.keyDown("ctrlright")
time.sleep(.1)
pyautogui.keyUp("ctrlright")

Кроме запуска в обычном режиме, когда изменяется текст слева от курсора и до начала строки (имитация выделения нажатием [Shift] + [Home]), предусмотрена возможность запуска с параметрами:
– "-lastword" – для последнего слов перед курсором
– "-selected" – для заранее выделенного фрагмента текста

