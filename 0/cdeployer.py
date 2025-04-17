#!/usr/bin/env python3
#-*- coding: utf-8 -*-
"""
На основе данных из кофигурационного файла cdeployer-config.yml выполняются операции по развертыванию новой версии прилодений СЖ и ЦП
- копирование на целевые сервера исполняемых файлов и конфигураций
- останов запущеных модулей
- останов процесса и ожидание ввода Y (заглавное) и нажатия Enter
- выполнение дополнительных заданий
- запуск модулей
- "коротки" пререндинг фронтов
- копирование на целевые сервера результата пререндинга
- "длинный" пререндинг фронтов 
- копирование на целевые сервера результата пререндинга
- выполнений дополнительных заданий

Любой из этапов может быть отключен путем закоментирования строки 'Enabled: True' в конфиг-файле, или происывания значени False в эту строку


Непосредственно операции осуществляются путем вызова набора ansible playbook'ов. Эти плейбуки можно вызывать и без Cdeployer, просто 
из командной строки shell

Таким образом  cdeployer - это просто "обертка" или Mini оркестратор над этими плейбуками

Пароли необходимые плейбукам для подключения к целевым серверам и поднятия приоритета (become) берется из vault файла.
Имя файла:  <имя_пользователя>_password.yml
пароль запрашивается при старте деплоера

Usage:  cdeployer.py <--help> <--user user_name> <--config config_file> <--vars vars file> <--log log_level> <--order> <--debug> <--dry>
Default:
 User name   : tarasov-dl
 Config file : cdeployer-config.yml
 Vars file   : vars-prom.yml

Введутся журналы  cdeployer.log и cdeployer_json.log
Журналы ротируется по достижении размера 1 МБ. Храниться 5 исторических копий

"""
import yaml
import sys
import subprocess
import os
import re
import pty, select
import time
import getpass
import logging
import curses

from collections import deque
from ansible_vault import Vault

#from logging.handlers import TimedRotatingFileHandler
from logging.handlers import RotatingFileHandler

try:
    import fcntl
except ModuleNotFoundError:
    pass

__author__ = "Dmitry Tarasov <tarasovdl@intech.rshb.ru>"
__date__ = "05 May 2022"
__version__ = "0.5.0"

verbose = ""
apass = ""
bpass = ""
auser = "tarasov-dl"
rcode = -1
cfname = "cdeployer-config.yml"
vfname = "vars-prom.yml"
is_verbose = False

padl = None
#padm = None
padr = None

hall = 0
wl = 0
wr = 0

vars_prom = {}
config = {}

FORMATTER = logging.Formatter("%(asctime)s — %(name)s — %(levelname)s — %(message)s", datefmt='%Y-%m-%d %H:%M:%S%z')
FORMATTER_JSON = logging.Formatter('{"time": "%(asctime)s", "name": "%(name)s", "level": "%(levelname)s", "message": "%(message)s"}', datefmt='%Y-%m-%d %H:%M:%S%z')
FORMATTER_CON = logging.Formatter("%(message)s")
LOG_FILE = "cdeployer.log"
LOG_FILE_JSON = "cdeployer_json.log"


def print_left (text, end=None):
    global hall
    global wl
    global wr
    global padl
    global dl
    if end == '':
        padl.addstr(text)
    else:
        padl.addstr("{}\n".format(text))
    padl.refresh(0, 0, 0, 0, hall-1, wl)
    if is_debug:
        dl.append(text.rstrip())


def print_right (text, end=None):
    global hall
    global wl
    global wr
    global padr
    global dr
    _add_line(padr, text)
    if end != '':
        padr.addstr("\n")
    padr.refresh(0, 0, 0, wl + 1, hall-1, wl + wr )
    if is_debug:
        dr.append(text.rstrip())

#def get_console_handler():
#    console_handler = logging.StreamHandler(sys.stdout)
#    console_handler.setFormatter(FORMATTER_CON)
#    return console_handler


def get_file_handler():
    # file_handler = TimedRotatingFileHandler(LOG_FILE, when='midnight', backupCount=5)
    file_handler = RotatingFileHandler(LOG_FILE, maxBytes=1024*1024, backupCount=5)
    file_handler.setFormatter(FORMATTER)
    return file_handler


def get_file_handler_json():
    # file_handler_json = TimedRotatingFileHandler(LOG_FILE, when='midnight', backupCount=5)
    file_handler_json = RotatingFileHandler(LOG_FILE_JSON, maxBytes=1024*1024, backupCount=5)
    file_handler_json.setFormatter(FORMATTER_JSON)
    return file_handler_json


def get_logger(logger_name):
    logger1 = logging.getLogger(logger_name)
    #logger1.setLevel(logging.DEBUG)   # better to have too much log than not enough
    #logger1.setLevel(logging.INFO)   # better to have too much log than not enough
    #####logger1.addHandler(get_console_handler())
    logger1.addHandler(get_file_handler())
    logger1.addHandler(get_file_handler_json())
    # with this pattern, it's rarely necessary to propagate the error up to parent
    logger1.propagate = False
    return logger1


COLOR_PAIRS_CACHE = {}


class TerminalColors(object):
    MAGENTA = '[0;35'
    BLUE = '[0;34'
    GREEN = '[0;32'
    CYAN = '[0;36'
    YELLOW = '[0;33'
    RED = '[0;31'
    WHITE = '[0;37'
    LMAGENTA = '[1;35'
    LBLUE = '[1;34'
    LGREEN = '[1;32'
    LCYAN = '[1;36'
    LYELLOW = '[1;33'
    LRED = '[1;31'
    LWHITE = '[1;37'
    END = '[0'
    LIGHT = '[1'
    DMAGENTA = '[35'
    DBLUE = '[34'
    DGREEN = '[32'
    DCYAN = '[36'
    DYELLOW = '[33'
    DRED = '[31'
    DWHITE = '[37'

#    MAGENTA = '[95'
#    BLUE = '[94'
#    GREEN = '[92'
#    YELLOW = '[93'
#    RED = '[91'
#    END = '[0'


# Translates between the terminal notation of a color, to it's curses color number
TERMINAL_COLOR_TO_CURSES = {
    TerminalColors.RED: curses.COLOR_RED,
    TerminalColors.GREEN: curses.COLOR_GREEN,
    TerminalColors.YELLOW: curses.COLOR_YELLOW,
    TerminalColors.CYAN: curses.COLOR_CYAN,
    TerminalColors.BLUE: curses.COLOR_BLUE,
    TerminalColors.MAGENTA: curses.COLOR_MAGENTA,
    TerminalColors.LWHITE: curses.COLOR_WHITE,
    TerminalColors.LRED: curses.COLOR_RED,
    TerminalColors.LGREEN: curses.COLOR_GREEN,
    TerminalColors.LYELLOW: curses.COLOR_YELLOW,
    TerminalColors.LCYAN: curses.COLOR_CYAN,
    TerminalColors.LBLUE: curses.COLOR_BLUE,
    TerminalColors.LMAGENTA: curses.COLOR_MAGENTA,
    TerminalColors.LWHITE: curses.COLOR_WHITE,
    TerminalColors.DRED: curses.COLOR_RED,
    TerminalColors.DGREEN: curses.COLOR_GREEN,
    TerminalColors.DYELLOW: curses.COLOR_YELLOW,
    TerminalColors.DCYAN: curses.COLOR_CYAN,
    TerminalColors.DBLUE: curses.COLOR_BLUE,
    TerminalColors.DMAGENTA: curses.COLOR_MAGENTA,
    TerminalColors.DWHITE: curses.COLOR_WHITE
}


def _get_color(fg, bg):
    key = (fg, bg)
    if key not in COLOR_PAIRS_CACHE:
        # Use the pairs from 101 and after, so there's less chance they'll be overwritten by the user
        pair_num = len(COLOR_PAIRS_CACHE) + 1
        curses.init_pair(pair_num, fg, bg)
        COLOR_PAIRS_CACHE[key] = pair_num
        #my_logger.debug( "add cp:" + str(pair_num)+" fg:"+ str(fg) + " key :" + str (key) )
    #my_logger.debug( "ret cache:" + str(COLOR_PAIRS_CACHE[key])+" key :" + str (key) )
    return COLOR_PAIRS_CACHE[key]


def _color_str_to_color_pair(color):
    if color == TerminalColors.END:
        fg = curses.COLOR_WHITE
    elif color == TerminalColors.LIGHT:
        fg = curses.COLOR_WHITE
    else:
        try: 
            fg = TERMINAL_COLOR_TO_CURSES[color]
        except KeyError:
            # Если управляющая цветовая последовательность не найдена, то цвет - белый
            fg = curses.COLOR_WHITE
    color_pair = _get_color(fg, curses.COLOR_BLACK)
    return color_pair


#def _add_line(y, x, window, line):
def _add_line(window, line):
    # split but \033 which stands for a color change
    color_split = line.split('\033')

    # Print the first part of the line without color change
    default_color_pair = _get_color(curses.COLOR_WHITE, curses.COLOR_BLACK)
    #window.addstr(y, x, color_split[0], curses.color_pair(default_color_pair))
    window.addstr(color_split[0], curses.color_pair(default_color_pair))
    #my_logger.debug("First:"+ color_split[0] + ": Color:" + str( curses.color_pair(default_color_pair)))
    #x += len(color_split[0])

    # Iterate over the rest of the line-parts and print them with their colors
    for substring in color_split[1:]:
        color_str = substring.split('m')[0]
        substring = substring[len(color_str)+1:]
        color_pair = _color_str_to_color_pair(color_str)
        #window.addstr(y, x, substring, curses.color_pair(color_pair))
        window.addstr(substring, curses.color_pair(color_pair))
        #my_logger.debug("Next:" + substring + " Color pair:" + str(curses.color_pair(color_pair)) + "color: " + color_str)
        #x += len(substring)

"""
def _inner_addstr(window, string, y=-1, x=-1):
    assert curses.has_colors(), "Curses wasn't configured to support colors. Call curses.start_color()"

    #cur_y, cur_x = window.getyx()
    #if y == -1:
    #    y = cur_y
    #if x == -1:
    #    x = cur_x
    for line in string.split(os.linesep):
        _add_line(y, x, window, line)
        # next line
        ##y += 1


def addstr(*args):
"""
"""
    Adds the color-formatted string to the given window, in the given coordinates
    To add in the current location, call like this:
        addstr(window, string)
    and to set the location to print the string, call with:
        addstr(window, y, x, string)
    Only use color pairs up to 100 when using this function,
    otherwise you will overwrite the pairs used by this function
"""
"""
    if len(args) != 2 and len(args) != 4:
        raise TypeError("addstr requires 2 or 4 arguments")

    if len(args) == 4:
        window = args[0]
        y = args[1]
        x = args[2]
        string = args[3]
    else:
        window = args[0]
        string = args[1]
        y = -1
        x = -1

    return _inner_addstr(window, string, y, x)

"""


def instance_already_running(label="default"):
    """
    Detect if an an instance with the label is already running, globally
    at the operating system level.

    Using `os.open` ensures that the file pointer won't be closed
    by Python's garbage collector after the function's scope is exited.

    The lock will be released when the program exits, or could be
    released if the file pointer were closed.
    """

    lock_file_pointer = os.open(f"/tmp/instance_{label}.lock", os.O_WRONLY|os.O_CREAT)

    try:
        fcntl.lockf(lock_file_pointer, fcntl.LOCK_EX | fcntl.LOCK_NB)
        already_running = False
    except IOError:
        already_running = True

    return already_running


def get_version(module):
    """
    Поиск версии модуля в данных прочитаных из файла с переменными vars. 
    Если номер версии не найден, возвращается ??.??.??
    """
    if re.search( 'ssr_.*', module) != None:
        # для SSR модулф версия совпадает с версией front статики
        key = 'front_'+  re.sub(r'ssr_(.*)', r'\g<1>', module) +'_version'
    else:
        key = module+'_version'

    try:
        return vars_prom[key]
    except KeyError:
        pass
    return "??.??.??"


def run_process(exe):
    """
    запуск процесса с аргументами с перехватом stdout и stderr
    При каждом последующем вызове возвращает строку из перехваченного stdout
    при завершении процесс записывает код завершения в глобальную переменную rcode
    """
    global rcode

    env = os.environ.copy()
    p = subprocess.Popen(exe, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE , stdin=subprocess.PIPE) #, start_new_session=True)
#    p = subprocess.Popen(exe, env=env, stdout=slave, stderr=slave, close_fds=True, stdin=subprocess.PIPE)
    while True:
        # returns None while subprocess is running
        retcode = p.poll()
        line = p.stdout.readline()
        yield line
        if retcode is not None:
            rcode = p.returncode
            break

def run_process_with_tail(exe, mod):
    """
    Запускает процесс с аргументами с перехватом stdout и stderr
    Параллельно запускается процесс tail, для наблюдения за журналом выполнения основгого процесса
    Выводятся на экран строки как перехваченный у основгого процесса , так и перехваченный у tail
    При завершении основного процесса записывает код завершения в глобальную переменную rcode и завершается tail
    """
    global rcode
    global wr
    global hall
    # tailcmd = ['tail', '-n', '-1', '-s', '-f', f'/data/opt/prerender/prerender-{mod}.log']
    tailcmd = ['tail', '-f', f'/data/opt/prerender/prerender-{mod}.log']

    env = os.environ.copy()
    env["COLUMNS"]= str(wr)
    env["LINES"]= str(hall)

    if is_debug:
        log_right("+ run_process_tail\n")

    if is_debug:
        print_without_password(tailcmd)

    p = subprocess.Popen(exe, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)

    os.set_blocking(p.stdout.fileno(), False)

    # my_logger.info(f'Run Process with tail mod = {mod}')
    log_right(f'+ Run Process with tail mod = {mod}')

    ptail = subprocess.Popen(tailcmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    os.set_blocking(ptail.stdout.fileno(), False)

    while True:
        # first iteration always produces empty byte string in non-blocking mode
        while True:
            line = p.stdout.readline().decode('utf-8').rstrip()
            if line != '':
                print_right(line)
                my_logger.debug(line)
            else:
                break
        while True:
            line = ptail.stdout.readline().decode('utf-8').rstrip()
            if line != '':
                my_logger.debug("tail: {}".format(line))
                # print("tail: ", line, end='')
                print_right("tail: {}".format(line))
                #print_right(line)
            else:
                break
        time.sleep(0.5)
        retcode = p.poll()
        if retcode is not None:
            rcode = p.returncode
            if is_debug:
                print_left("rc: {}\n".format(rcode))
            break

    # дочитываем
    # my_logger.info('Дочитываем выходные буфера - 2 sec')
    log_right('Дочитываем выходные буфера - 2 sec')

    start = time.time()
    while True:
        while True:
            line = p.stdout.readline().decode('utf-8').rstrip()
            if line != '':
                print_right(line)
                my_logger.debug(line)
            else:
                break
        while True:
            line = ptail.stdout.readline().decode('utf-8').rstrip()
            if line != '':
                my_logger.debug("tail: {}".format(line))
                # print("tail: ", line, end='')
                print_right("tail: {}".format(line))
            else:
                break
        time.sleep(0.5)
        if time.time() > start + 2:
            break
    ptail.terminate()


def run_process_2(exe):
    """
    Запускает процесс с аргументами с перехватом stdout и stderr
    Параллельно запускается процесс tail, для наблюдения за журналом выполнения основгого процесса
    Выводятся на экран строки как перехваченный у основгого процесса , так и перехваченный у tail
    При завершении основного процесса записывает код завершения в глобальную переменную rcode и завершается tail
    """
    global rcode
    global wr
    global hall
    env = os.environ.copy()
    env["COLUMNS"]= str(wr)
    env["LINES"]= str(hall)
    # p = subprocess.Popen(exe, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, start_new_session=True)
    if is_debug:
        log_right("run_process_2\n")
    p = subprocess.Popen(exe, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    os.set_blocking(p.stdout.fileno(), False)

    while True:
        # first iteration always produces empty byte string in non-blocking mode
        while True:
            line = p.stdout.readline().decode('utf-8').rstrip()
            if line != '':
                print_right(line)
            else:
                break
        time.sleep(0.5)
        retcode = p.poll()
        if retcode is not None:
            rcode = p.returncode
            if is_debug:
                print_left("rc: {}\n".format(rcode))
            break

    # дочитываем
    # my_logger.info('Дочитываем выходные буфера - 2 sec')
    log_right('Дочитываем выходные буфера - 2 sec')

    start = time.time()
    while True:
        while True:
            line = p.stdout.readline().decode('utf-8').rstrip()
            if line != '':
                print_right(line)
            else:
                break
        time.sleep(0.2)
        if time.time() > start + 2:
            break

    rcode = p.returncode


def print_without_password(list_for_print):
    """
    В журнал выводится сообщение, в котором слова после password= заменены на xxxxx (маскирование паролей)
    """
    outstr = ""
    for item in list_for_print:
        # print(re.sub(r'(.*)password=.*', r'\g<1>password=xxxxxx', item), end=' ')
        outstr += re.sub(r'(.*)password=.*', r'\g<1>password=xxxxxx', item) + " "
    # my_logger.info(outstr)
    log_right(outstr)


def common_cmd(sp_deploy, prefix, playbook, group=None, suffix=None):
    """
    Формирование списка строк для запуска ansible-palybook с аргументами , запуск процесса,
    вывод перехваченного stdout и ожидание завершения

    ansible-playbook запускается один раз с указанием тегов всех модулей.
    модули обрабатываются в порядке, в котором они перечислены в playbook
    """
    global rcode

    if group is None:
        group = "backs"
    tcmd = ["ansible-playbook", "-e environ=prom", '-i', 'prom-ipoteka-inventory/hosts']
    tcmd.append(playbook)
    tcmd.append('-l ' + group)
    tcmd.append(f"-e ansible_user={auser}")
    tcmd.append(f"-e ansible_password={apass}")
    tcmd.append(f"-e become_password={bpass}")
    if verbose != "":
        tcmd.append(verbose)

    tags = "-t "
    # count = 0
    len_mod = len(sp_deploy)
    for count, mod in enumerate(sp_deploy, 1):
        # my_logger.info(" - " + mod + " : " + get_version(mod))
        log_left("-" + mod + ":" + get_version(mod))
        tags += prefix + mod
        if suffix is not None:
            tags += suffix
        # count += 1
        if count != len_mod:
            tags += ","
    tcmd.append(tags)

    if is_debug:
        print_without_password(tcmd)
    if not is_dry:
        rcode = 0
        # print (tcmd)
        run_process_2(tcmd)
#        for line in run_process(tcmd):
#            #print(line.decode('utf-8'), end='')
#            print_right(line.decode('utf-8'))
        if is_debug:
            # my_logger.info("rcode = " + str(rcode))
            log_left("rcode = " + str(rcode))
        if rcode != 0:
            my_logger.error("Run Process return error code " + str(rcode))
            print_left("Run Process return error:" + str(rcode))
            print_without_password(tcmd)
            return(False)
    return(True)


def common_order_cmd(sp_deploy, prefix, playbook, group=None, suffix=None, tail=False ):
    """
    Формирование списка строк для запуска ansible-palybook с аргументами ,
    запуск процесса, вывод перехваченного stdout и ожидание завершения
    ansible-playbook запускается для каждого модуля по отдельности в том порядке,
    в котором они перечислены в файле конигурации
    """

    global rcode
    if group is None:
        group = "backs"
    scmd = ["ansible-playbook", "-e environ=prom", '-i', 'prom-ipoteka-inventory/hosts']
    scmd.append(playbook)
    scmd.append('-l ' + group)
    scmd.append(f"-e ansible_user={auser}")
    scmd.append(f"-e ansible_password={apass}")
    scmd.append(f"-e become_password={bpass}")

    if verbose != "":
        tcmd.append(verbose)

    for mod in sp_deploy:
        tcmd = scmd.copy()
        tags = "-t "
        # my_logger.info(" - " + mod + " : " + get_version(mod))
        log_left("-" + mod + ":" + get_version(mod))
        tags += prefix + mod
        if suffix is not None:
            tags += suffix
        tcmd.append(tags)
        if is_debug:
            print_without_password(tcmd)
        if not is_dry:
            rcode = 0
            if tail:
                # my_logger.info(f'Run Process with tail ')
                log_right("Run Process with tail")
                run_process_with_tail(tcmd, re.sub(r'front_(.*)', r'\g<1>', mod))
            else:
                run_process_2(tcmd)
                #for line in run_process(tcmd):
                #    #print(line.decode('utf-8'), end='')
                #    print_right(line.decode('utf-8'))
            if is_debug:
                #my_logger.info("rcode = " + str(rcode))
                log_left("rcode = " + str(rcode))
            if rcode != 0:
                my_logger.error("Run Process return error code " + str(rcode))
                print_left("Run Process return error code " + str(rcode))
                print_without_password(tcmd)
                return(False)
                #sys.exit(1)
    return(True)


def deploy(to_deploy):
    # my_logger.info("Deploy :")
    log_left("Deploy :")
    return common_cmd(to_deploy, "install_", f'main.yml')


def stop(to_deploy):
    # my_logger.info("Stop :")
    log_left("Stop :")
    if is_order:
        return common_order_cmd(to_deploy, "stop_", f'main_start_stop.yml')
    else:
        return common_cmd(to_deploy, "stop_", f'main_start_stop.yml')


def start(to_deploy):
    # my_logger.info("Start :")
    log_left("Start :")
    if is_order:
        return common_order_cmd(to_deploy, "start_", f'main_start_stop.yml')
    else:
        return common_cmd(to_deploy, "start_", f'main_start_stop.yml')


def prerender(to_deploy):
    # my_logger.info("prerender :")
    log_left("prerender :")
    return common_order_cmd(to_deploy, "prerender_", f'main.yml', "sgo-ap758", tail=True)


def deploy_front(to_deploy):
    # my_logger.info("deploy_front :")
    log_left("deploy_front :")
    return common_cmd(to_deploy, "install_", f'main.yml', "sgo-ap944")


def prerender_full(to_deploy):
    # my_logger.info("prerender_full :")
    log_left("prerender_full :")
    return common_order_cmd(to_deploy, "prerender_", f'main.yml', "sgo-ap758", suffix="_full", tail=True)


def deploy_front_full(to_deploy):
    log_left("deploy_front_full :")
    # my_logger.info("deploy_front_full :")
    return common_cmd(to_deploy, "install_", f'main.yml', "sgo-ap944", "_full")


def log_left(text):
    """
    вывод текста на левую панель и в журнал
    """
    print_left(text)
    my_logger.info(text)


def log_right(text):
    """
    вывод текста на правую панель и в журнал
    """
    print_right(text)
    my_logger.info(text)

def main():
    global apass
    global bpass
    global rcode
    global vars_prom
    global hall
    global wl
    global wr
    global padr
    global padl
    global config
    global dr
    global dl

    my_logger.info(f' User name   : {auser}')
    my_logger.info(f' Config file : {cfname}')
    my_logger.info(f' Vars file   : {vfname}')
    print(f' User name   : {auser}')
    print(f' Config file : {cfname}')
    print(f' Vars file   : {vfname}')

    if not is_dry:
        apass = getpass.getpass(prompt=f'Enter password for vault file {auser}-password.yml: ')
        print("")

        vault = Vault(apass)

        try:
            with open(f'{auser}-password.yml') as f:
                vdata = vault.load(f.read())
        except:
            my_logger.error(f'Error decrypt vault file {auser}-password.yml')
            print(f'Error decrypt vault file {auser}-password.yml')
            sys.exit(2)

        apass = vdata['ansible_password']
        bpass = vdata['become_password']

    try:
        with open(cfname) as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
    except:
        my_logger.error(f'Error load config file {cfname}')
        print(f'Error load config file {cfname}')
        sys.exit(2)

    try:
        with open(vfname) as f:
            vars_prom = yaml.load(f, Loader=yaml.FullLoader)
    except:
        my_logger.error(f'Error load vars file {vfname}')
        print(f'Error load vars file {vfname}')
        sys.exit(2)

    try:
        curses.wrapper(main_curses)
    except KeyboardInterrupt:
        pass

    # вывод на экран сохраненных двнныз, который выводились в правую и левую области
    if is_debug:
        for elem in dr:
            print(elem)
        for elem in dl:
            print(elem)


def main_curses(stdscr):
    global apass
    global bpass
    global rcode
    global vars_prom
    global hall
    global wl
    global wr
    global padr
    global padl
    global config

    stdscr.keypad(True)
    stdscr.refresh() # This is the necessary initial refresh
    stdscr.scrollok(True)
    # stdscr.timeout(10)

    hall, ncols = stdscr.getmaxyx()
    wl = 31
    wr = ncols - wl - 2

    padm = curses.newpad(hall, 1)
    padm.scrollok(True)
    for i in range(hall):
        padm.addstr("|")
    padm.refresh(0, 0, 0, wl, hall - 1, wl)

    padl = curses.newpad(hall, wl)
    padl.scrollok(True)

    padr = curses.newpad(hall, wr)
    padr.scrollok(True)

    try:
        is_enable = config['deploy']['enabled']
    except KeyError:
        pass
    else:
        if is_enable:
            if not isinstance(config.get('deploy', {}).get('modules'), list):  # Если это НЕ list
                if config['deploy']['modules'].lower() == 'all':
                    rc = deploy(config['modules'])
                else:
                    rc = deploy(config['deploy']['modules'])
            elif 'all' in ( item.lower() for item in config['deploy']['modules']):
                rc = deploy(config['modules'])
            else:
                rc = deploy(config['deploy']['modules'])
        if not rc:
            print_left("Err:Press Enter to close :", end='')
            cmd = stdscr.getstr()
            return 1
            #sys.exit(1)

    try:
        is_enable = config['stop']['enabled']
    except KeyError:
        pass
    else:
        if is_enable:
            if not isinstance(config.get('stop', {}).get('modules'), list):  # Если это НЕ list
                if config['stop']['modules'].lower() == 'all':
                    rc = stop(config['modules'])
                else:
                    rc = stop(config['stop']['modules'])
            elif 'all' in ( item.lower() for item in config['stop']['modules']):
                rc = stop(config['modules'])
            else:
                rc = stop(config['stop']['modules'])
        if not rc:
            print_left("Err:Press Enter to close :", end='')
            cmd = stdscr.getstr()
            return 1
#            sys.exit(1)

    try:
        if config['wait']['enabled']:
            #print(config['wait']['text'])
            print_left(config['wait']['text'])
            print_left("Enter 'Y': ", end='')
            if not is_dry:
                while True:
                    # ans = input()
                    ans = stdscr.getstr()
                    #cmd = stdscr.getch()
                    #if cmd == ord('Y'):
                    if ans == "Y":
                        break
                    else:
                        # print("Enter 'Y' (Upper Case): ", end='')
                        print_left("")
                        print_left("Enter 'Y' (Upper Case): ", end='')
            print_left("")
    except KeyError:
        pass

    for jobs in config['run']:
        try:
            if jobs['enabled']:
                # my_logger.info("Run : " + jobs['name'])
                log_left("Run: " + jobs['name']+"-"+jobs['version'])
                ready_cmd = [sub.replace('$1', jobs['version']) for sub in jobs['cmd']]
                if is_debug:
                    print_without_password(ready_cmd)
                if not is_dry:
                    rcode = -1
                    run_process_2(ready_cmd)
                    #for line in run_process(ready_cmd):
                    #    print(line.decode('utf-8'), end='')
                    if rcode != 0:
                        my_logger.info("Return error code " + str(rcode))
                        print_without_password(ready_cmd)
                        print_left("Err:Press Enter to close :", end='')
                        cmd = stdscr.getstr()
        except KeyError:
            pass

    try:
        if config['wait_after']['enabled']:
            print_left(config['wait_afetr']['text'])
            print_left("Enter 'Y': ", end='')
            if not is_dry:
                while True:
                    # ans = input()
                    ans = stdscr.getstr()
                    #cmd = stdscr.getch()
                    #if cmd == ord('Y'):
                    if ans == "Y":
                        break
                    else:
                        # print("Enter 'Y' (Upper Case): ", end='')
                        print_left("")
                        print_left("Enter 'Y' (Upper Case): ", end='')
            print_left("")
    except KeyError:
        pass


    try:
        is_enable = config['start']['enabled']
    except KeyError:
        pass
    else:
        if is_enable:
            if not isinstance(config.get('start', {}).get('modules'), list):  # Если это НЕ list
                if config['start']['modules'].lower() == 'all':
                    rc = start(config['modules'])
                else:
                    rc = start(config['start']['modules'])
            elif 'all' in ( item.lower() for item in config['start']['modules']):
                rc = start(config['modules'])
            else:
                rc = start(config['start']['modules'])
        if not rc:
            print_left("Err:Press Enter to close :", end='')
            cmd = stdscr.getstr()
            return 1
#            sys.exit(1)

    try:
        if config['prerender']['enabled']:
            if not prerender(config['prerender']['modules']):
                print_left("Err: Press Enter to close :", end='')
                cmd = stdscr.getstr()
                return 1
#               sys.exit(1)
    except KeyError:
        pass
    except:
        return 1

    try:
        if config['deploy_front']['enabled']:
            if not deploy_front(config['deploy_front']['modules']):
                print_left("Err: Press Enter to close :", end='')
                cmd = stdscr.getstr()
                return 1
#                sys.exit(1)
    except KeyError:
        pass
    except:
        return 1

    try:
        if config['prerender_full']['enabled']:
            if not prerender_full(config['prerender_full']['modules']):
                print_left("Err: Press Enter to close :", end='')
                cmd = stdscr.getstr()
                return 1
    except KeyError:
        pass
    except:
        return 1

    try:
        if config['deploy_front_full']['enabled']:
            if not deploy_front_full(config['deploy_front_full']['modules']):
                print_left("Err: Press Enter to close :", end='')
                cmd = stdscr.getstr()
                return 1
    except KeyError:
        pass
    except:
        return 1

    try:
        for jobs in config['run_after']:
            if jobs['enabled']:
                # my_logger.info("Run After : " + jobs['name'])
                log_left("Run After:" + jobs['name'])
                # ready_cmd = [sub.replace('$1', jobs['version']) for sub in jobs['cmd']]
                ready_cmd = jobs['cmd']
                if is_debug:
                    print_without_password(ready_cmd)
                if not is_dry:
                    rcode = -1
                    run_process_2(ready_cmd)
                    # for line in run_process(ready_cmd):
                        # print(line.decode('utf-8'), end='')
                        # print_right(line.decode('utf-8'))
                    if rcode != 0:
                        my_logger.error("Return error code " + str(rcode))
                        print_without_password(ready_cmd)
                        print_left("Err:Press Enter to close :", end='')
                        cmd = stdscr.getstr()
    except KeyError:
        pass


    print_left("Ok:Press Enter to close :", end='')
    cmd = stdscr.getstr()
    return 0
    #sys.exit(0)



def usage():
    print("Cdeployer. Version ", __version__, "  ", __date__)
    print("Usage: ", sys.argv[0], "<--help> <--user user_name> <--config config_file> <--vars vars_file> <--log log_level> <--order> <--debug> <--dry>")
    print("Default: ")
    print(f' User name   : {auser}')
    print(f' Config file : {cfname}')
    print(f' Vars file   : {vfname}')


if __name__ == '__main__':
    if os.name != 'nt':
        if instance_already_running("cdeployer"):
            print("Process already running. Exiting")
            usage()
            sys.exit()
    #logging.basicConfig(level=logging.INFO)
    my_logger = get_logger("cdeployer-" + __version__)
    my_logger.setLevel(logging.INFO) 
    my_logger.info(f'Start process {__version__}')

    temps = sys.argv[1:]

    is_order = False
    is_debug = False
    is_dry = False
    is_log = False
    is_user = False
    is_cfname = False
    is_vfname = False

    for arg in temps:
        # print ( arg )
        if is_user:
            auser = arg
            my_logger.info(f'Parse command line: Set user name : {auser}')
            is_user = False
            continue
        if is_cfname:
            cfname = arg
            my_logger.info(f'Parse command line: Set config file name : {cfname}')
            is_cfname = False
            continue
        if is_vfname:
            vfname = arg
            my_logger.info(f'Parse command line: Set vars file name : {vfname}')
            is_vfname = False
            continue
        if is_verbose:
            verbose = arg
            my_logger.info(f'Parse command line: Set verbose : {verbose}')
            is_verbose = False
            continue
        if is_log:
            level=logging.getLevelName(arg)
            my_logger.setLevel(level)
            my_logger.info(f'Parse command line: Set Log level : {arg} ' + str( my_logger.getEffectiveLevel()) )
            is_log = False
            continue
        if arg in ('-h', '--help'):
            usage()
            sys.exit()
        if arg in ('--debug'):
            is_debug = True
            dl = deque(maxlen=100)
            dr = deque(maxlen=1000)
            my_logger.info("Parse command line: Set Debug mode")
        elif arg in ('--dry'):
            is_dry = True
            my_logger.info("Parse command line: Set Dry mode")
        elif arg in ('--order'):
            is_order = True
            my_logger.info("Parse command line: Set Order mode")
        elif arg in ('--user'):
            is_user = True
        elif arg in ('--config'):
            is_cfname = True
        elif arg in ('--vars'):
            is_vfname = True
        elif arg in ('--log'):
            is_log = True
        elif arg in ('--verbose'):
            is_verbose = True
#    is_dry = True   # Для отладки и разработки
    main()

