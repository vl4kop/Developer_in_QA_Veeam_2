import filecmp
import os
import shutil
import csv
import time


def script():
    """Функция  запрашивает каталог-источник, каталог-реплику, интервал синхронизации, путь к файлу логирования.
    В цикле происходит запуск функции сравнения каталогов на первом уровне вложенности"""

    # пользовательский ввод
    source_path = input('Enter path to the source directory: ').replace('\\', '/')
    replica_path = input('Enter path to the replica directory: ')
    interval_sync = int(input('Enter sync interval: '))
    log_path = input('Enter path to the log file: ').replace('\\', '/')

    #  создаем csv файл для логов, заносим названия столбцов
    log_file_path = f"{log_path}/log_{time.strftime('%Y%m%d_%H%M%S')}.csv"
    data = ['Date', 'Action', 'Path']
    add_change(data, log_file_path, console=False)

    # цикл синхронизации каталога реплики с заданным интервалом
    while True:
        compare_dir(source_path, replica_path, log_file_path)
        print('Waiting...')
        time.sleep(interval_sync)


def compare_dir(path_source, path_replica, log_file_path):
    """Функция сравнивает каталоги на текущем уровне вложенности, рекурсивно углубляясь внутрь"""

    #  инициализируем адрес текущего уровня,
    #  каталоги на уровне в источнике и реплике,
    #  файлы на уровне в источнике и реплике
    path_dir, list_dir, list_file = next(os.walk(path_source))
    path_dir = path_dir.replace('\\', '/')
    path_dir_replica, list_dir_replica, list_file_replica = next(os.walk(path_replica))
    path_dir_replica = path_dir_replica.replace('\\', '/')

    #  Удаляем лишние каталоги и файлы из реплики на текущем уровне
    for replica_dir in list_dir_replica:
        if replica_dir not in list_dir:
            del_dir(f'{path_dir_replica}/{replica_dir}', log_file_path)
    for replica_file in list_file_replica:
        if replica_file not in list_file:
            del_file(f'{path_dir_replica}/{replica_file}', log_file_path)

    # ищем отсутствующие папки в реплике на текущем уровне и добавляем их
    for source_dir in list_dir:
        # если каталог есть в реплики запускаем для этого каталога функцию сравнения каталогов
        if source_dir in list_dir_replica:
            compare_dir(f'{path_dir}/{source_dir}', f'{path_dir_replica}/{source_dir}', log_file_path)
        # если каталога нет, создаем и запускаем функцию сравнения каталогов
        else:
            create_dir(f'{path_dir_replica}/{source_dir}', log_file_path)
            compare_dir(f'{path_dir}/{source_dir}', f'{path_dir_replica}/{source_dir}', log_file_path)

    # ищем отсутствующие файлы в реплике на текущем уровне и добавляем их, заменяем устаревшие файлы
    for source_file in list_file:
        if source_file in list_file_replica and \
                filecmp.cmp(f'{path_dir}/{source_file}', f'{path_dir_replica}/{source_file}') is False:
            copy_file(f'{path_dir}/{source_file}', f'{path_dir_replica}/{source_file}', log_file_path)
        elif source_file not in list_file_replica:
            copy_file(f'{path_dir}/{source_file}', f'{path_dir_replica}/{source_file}', log_file_path)


def create_dir(path, log_file_path):
    """Функция создает каталог"""

    try:
        os.mkdir(path)
        data = [time.strftime("%Y%m%d_%H%M%S"), 'Create directory', path]
        add_change(data, log_file_path)
    except Exception as Exc:
        print(Exc)


def copy_file(path_source, path_replica, log_file_path):
    """Функция копирует файл"""

    try:
        shutil.copyfile(path_source, path_replica)
        data = [time.strftime("%Y%m%d_%H%M%S"), 'Copy file', path_replica]
        add_change(data, log_file_path)
    except Exception as Exc:
        print(Exc)


def del_dir(path, log_file_path):
    """Функция удаляет каталог"""

    try:
        shutil.rmtree(path)
        data = [time.strftime("%Y%m%d_%H%M%S"), 'Delete directory', path]
        add_change(data, log_file_path)
    except Exception as Exc:
        print(Exc)


def del_file(path, log_file_path):
    """Функция удаляет файл"""

    try:
        os.remove(path)
        data = [time.strftime("%Y%m%d_%H%M%S"), 'Delete file', path]
        add_change(data, log_file_path)
    except Exception as Exc:
        print(Exc)


def add_change(data, data_file, console=True):
    """Функция записывает лог в файл csv и выводит его в консоль"""

    with open(data_file, 'a', encoding='utf-8') as table:
        writer = csv.writer(table, delimiter=",", lineterminator="\r")
        writer.writerow(data)
    if console:
        print(*data, sep=' ')


if __name__ == '__main__':
    script()
