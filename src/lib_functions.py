import datetime
import os
import json


def append_log(log_text, write_time=True):
    """
    Function for append log text into log.txt file
    """

    path_to_logs_txt = os.path.dirname(
        os.path.realpath(__file__)) + '/logs.txt'

    if write_time:
        text = log_text + ' at ' + str(datetime.datetime.now()) + '\n'
    else:
        text = log_text + '\n'

    with open(path_to_logs_txt, 'a', encoding='utf-8') as logs_file:
        logs_file.write(text)


def read_config():
    """
    Function which read config json
    Return configuration dictionary
    """
    path_to_config = os.path.dirname(
        os.path.realpath(__file__)) + '/config.json'

    with open(path_to_config, 'r') as config_file:
        data = json.load(config_file)

    return data


def check_file_name(expected_file_name, checked_file_name):
    """
    Сompares file names
    *.XX - means any file name
    XXXX.* - means any file extension
    *.* - any file name and extension
    """

    name_is_good = False
    extension_is_good = False

    if '.' in expected_file_name:
        # if file name contains two or more dots, it will be work corectly :)
        *expected_file_name_list, expected_file_extension = \
            expected_file_name.split('.')
        expected_file_name_string = '.'.join(expected_file_name_list)
    else:
        expected_file_name_string = expected_file_name
        expected_file_extension = None

    if '.' in checked_file_name:
        *checked_file_name_list, checked_file_extension = \
            checked_file_name.split('.')
        checked_file_name_string = '.'.join(checked_file_name_list)
    else:
        checked_file_name_string = checked_file_name
        checked_file_extension = None

    if expected_file_name_string == checked_file_name_string \
            or expected_file_name_string == '*':
        name_is_good = True

    if (expected_file_extension == '*' and checked_file_extension is not None)\
            or (expected_file_extension == checked_file_extension):
        extension_is_good = True

    return True if name_is_good and extension_is_good else False
