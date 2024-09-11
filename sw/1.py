������������):
sudo apt install python3-pip
sudo pip3 install setuptools
sudo pip3 install pyperclip pyautogui xlib
sudo apt install python3-tk python3-dev

�� �, �������, ����� ������� �� ������ ����� ����. � �������� ��� ��� open source � �������, ��� ��� �������� ����-�� ����� �/��� ������ �� �����������. ��������� ���� ����� � ���� � ����������� "py", ����������� ��� �������� �� Python, �������� "Swtchr.py":

#! /usr/bin/python3

"""
# ���� ������ ������� �� Python 3.
# ��� ���������� ������ XNeur � PuntoSwitcher, ������� �������� � ����������� � Wine ������������
#
# �������������: ��������� � ������� ���������� ������ (���� [Ctrl]+[R_Win]) �� ������
#                � ��������� � ��� ������� ������������ ��������� � �������� ��������� ������.
#
# ����������: ��������� ������������ ������ ������ � ������� ������
#               'pyperclip',
#             � ����� ������ ������������� ������
#               'pyautogui' � 'xlib'
#
# ������ �������, 2019-06-14
# 2019-08-01: ��������� ����������� ������� � ����������� -lastword � -selected
"""

import pyautogui, time, sys

no_pyperclip = False

clpbrd_strg = ""
layout_01 = "`~@#$%^&" +\
            "qwertyuiop[]QWERTYUIOP{}asdfghjkl;'\\ASDFGHJKL:\"|zxcvbnm,./ZXCVBNM<>?"
layout_02 = "��\"�;%:?" +\
            "�����������������������������������\\�����������/���������.���������,"

try:                                    # ������� �������������� ������������ ������
    import pyperclip                    # � ������ ������� ���������� ������� ������������
except ImportError:
    no_pyperclip = True

def computing():
    if no_pyperclip == True:
        print("��������� ������ ������ � ������� ������: pyperclip")
        quit()
    elif len(layout_01) != len(layout_02):
        print("������ �������� ��������� (layout_01 � layout_02) �� ��������� �� �����!")
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
        print("����������� �������� �������:", sys.argv[1])
        quit()
    fixed_text = magic(pyperclip.paste())
    pyperclip.copy(fixed_text)
    time.sleep(.1)
    pyautogui.hotkey("ctrl", "v")

def magic(text):
    if len(text) < 1:
        quit()
    elif len(text) < 3:                 # ������� ����� �������� ������
        first_x = 1                     # ��� ��������� ���������� �������� �����
    else:
        first_x = 3

    chars_01, chars_02 = 0, 0
    for i in range(first_x):            # ����� ��������� ������ �������� ������: 01 ��� 02?
        if text[i] in layout_01:
            chars_01 += 1
        elif text[i] in layout_02:
            chars_02 += 1
    if chars_01 > chars_02:             # ������ ������������������, ������ �� �����������
        layout = layout_01 + layout_02 + layout_01
    else:
        layout = layout_02 + layout_01 + layout_02

    new_text = ""
    for c in range(len(text)):          # ������� ��������, ������� "��� � ����������"
        if not text[c] in layout:
            new_text = new_text + text[c]
        else:
            new_text = new_text + layout[layout.find(text[c])+len(layout_01)]
    return new_text

clpbrd_strg = pyperclip.paste()         # ���������� �������� ����������� ������ ������
computing()
pyperclip.copy(clpbrd_strg)             # �������������� ����������� ������ ������
clpbrd_strg = ""

���������, ��� � ������������ ��� Wine ����� ���������� ������� "��������" ������ ������� [Ctrl], ������� � ��������� � ���������� ��� ������. �������� ������� ������ ������� ��������� �������������� ����� � ����� �������. ��� ��������� ������� � ���������� ������ ������� [Ctrl]:

# ��� ���������� �������� � ���������� ������� [Ctrl]
pyautogui.keyDown("ctrlright")
time.sleep(.1)
pyautogui.keyUp("ctrlright")

����� ������� � ������� ������, ����� ���������� ����� ����� �� ������� � �� ������ ������ (�������� ��������� �������� [Shift] + [Home]), ������������� ����������� ������� � �����������:
� "-lastword" � ��� ���������� ���� ����� ��������
� "-selected" � ��� ������� ����������� ��������� ������

