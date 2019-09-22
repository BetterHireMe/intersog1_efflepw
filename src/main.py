import os
import time
import json

from lib_functions import append_log, read_config, check_file_name


class FileInfo:
    def __init__(self, path, name, stat, is_dir):
        self.path = path
        self.name = name
        self.stat = stat
        self.is_dir = is_dir
        self.last_status = 'created'

    # comparison input file with this file obj
    def is_the_same(self, another_file_info):

        if os.name == 'nt':
            return self.stat.st_ctime == another_file_info.stat.st_ctime
        elif os.name == 'posix':
            return self.stat.st_ino == another_file_info.stat.st_ino\
                and self.stat.st_dev == another_file_info.stat.st_dev
        else:
            # this is imposible
            append_log("Alert! Current os isn't posix or nt")
            exit()

    def __str__(self):
        return self.name


def get_current_state(dir_path, files_info):
    """
    dir_path: (string) path to scan
    files_info: (list) list with all files info

    Reqursive scaning directory for all files,
    and write into files info list
    """

    for element in os.scandir(dir_path):

        # create new file info object
        new_file_info = FileInfo(
            path=element.path,
            name=element.name,
            stat=element.stat(),
            is_dir=element.is_dir()
        )

        files_info.append(new_file_info)

        # reqursive call
        if element.is_dir():
            get_current_state(element.path, files_info)


def find_the_same(file_info, new_files_info):
    """
    file_prop: (FileInfo obj) file to search in all files info list
    new_files_info: (list) list with all files information

    Function for searching match for current file info
    with file info from last iteration

    return: (dict) returns status of current state the file
    """

    try:

        for new_file_info in new_files_info:

            # trying to find the same file
            if file_info.is_the_same(new_file_info):

                if file_info.path == new_file_info.path:
                    if new_file_info.stat.st_mtime == file_info.stat.st_mtime:
                        return {'status': 'no_changes'}
                    else:
                        append_log('element changed ' + file_info.path)
                        return {'status': 'edited'}

                # if for the same file path was changed,
                # that means file was moved or renamed
                else:

                    file_directory_path = file_info.path.replace(
                        file_info.name, '')
                    new_file_directory_path = new_file_info.path.replace(
                        new_file_info.name, '')

                    # if path to file was changed, but name isnt
                    if file_info.name == new_file_info.name \
                            and file_directory_path != new_file_directory_path:
                        append_log('moved element ' + file_info.path +
                                   ' to ' + new_file_info.path)
                        return {
                            'status': 'moved',
                            'new_path': new_file_info.path
                        }

                    # if path to file wasn't changed, but name is another
                    elif file_info.name != new_file_info.name\
                            and file_directory_path == new_file_directory_path:
                        append_log('renamed element ' + file_info.path +
                                   ' to ' + new_file_info.path)
                        return {
                            'status': 'renamed',
                            'new_path': new_file_info.path
                        }

                    else:
                        # if path to file, and file name was changed
                        append_log('moved and renamed element ' +
                                   file_info.path +
                                   ' to ' + new_file_info.path)
                        return {
                            'status': 'moved_and_renamed',
                            'new_path': new_file_info.path
                        }

    except Exception as e:
        append_log('Error! Exception in find_the_same_posix function ' +
                   str(e))
        return {'status': 'error'}

    # if file doesn't found - it's new file
    append_log('Element was deleted ' + file_info.path)
    return {'status': 'deleted'}


def check_handlers(files_info):
    """
    files_info: (list) list with all files info with change statuses

    function which iterates over all files name and status change,
    and search it in config file
    """

    from handlers import register_handlers

    configuration = read_config()

    # looks awful, but in my opinion this is the fastest way
    for file_info in files_info:

        for handler_function in register_handlers:
            try:
                func_conf = configuration[handler_function.__name__]
            except KeyError:
                append_log('For handler {0} does not found any configuration'
                           .format(handler_function.__name__))

            for file_conf in func_conf:
                check_file_name_result = check_file_name(
                    file_conf['file_name'], file_info.name)

                # checking config status
                value_comparison = file_conf['status_to_check']\
                    == file_info.last_status
                special_comparison = file_conf['status_to_check']\
                    == '*' and file_info.last_status != 'no_changes'

                status_is_good = value_comparison or special_comparison

                if check_file_name_result and status_is_good:

                    # if handler needs file info, pass this
                    if file_conf['need_file_properties']:
                        handler_function(file_conf['args'], file_info)
                    else:
                        handler_function(file_conf['args'])


def checking_files(dir_path, all_files_info):
    """
    dir_path: (string) working directory
    all_files_info: (list) list with all files info on previously iteration

    It make one iteration in working directory,
    for finding all files current state
    """

    current_files_info = []
    finded_old_files = []
    new_files = []

    # iteration for finding all files current state
    get_current_state(dir_path, current_files_info)

    # loop for finding files change status
    for file_info in all_files_info:

        try:
            search_result = find_the_same(file_info, current_files_info)

            # appending files path in list, which was in prev iter,
            # it need for finding new files
            if search_result['status'] in ('no_changes', 'edited', 'deleted'):
                finded_old_files.append(file_info.path)
                file_info.last_status = search_result['status']

            elif search_result['status'] in \
                    ('renamed', 'moved', 'moved_and_renamed'):
                finded_old_files.append(search_result['new_path'])
                file_info.last_status = search_result['status']

        except Exception as e:
            append_log('Error! Exception in checking_files function ' +
                       str(e) + ' ' + file_info.path)

    # it finding files which wasn't in prev iter
    for pot_file in current_files_info:
        if pot_file.path not in finded_old_files:
            all_files_info.append(pot_file)
            append_log('finded new file ' + pot_file.path)

    # check files for handlers
    check_handlers(all_files_info)

    return current_files_info


def test_config_file():

    # checking access to configuration file
    try:
        configuration = read_config()
    except FileNotFoundError:
        error_text = 'Configuration file config.json does not found'
        append_log(error_text)
        print(error_text)
        exit()

    # checking all required keys
    try:
        use_default_dir = configuration['use_default_dir']
        if use_default_dir:
            configuration['work_dir']

        configuration['frequency']

    except KeyError as key:
        error_text = 'Required configuration key {0} does not found'.format(
            key)
        append_log(error_text)
        print(error_text)
        exit()

    # checking configuration files for handlers

    from handlers import register_handlers

    for handler in register_handlers:

        try:
            handler_configs = configuration[handler.__name__]

            for handler_config in handler_configs:

                handler_config['file_name']
                handler_config['status_to_check']
                handler_config['need_file_properties']
                handler_config['args']

        except KeyError as key:

            error_text = 'Configuration key {0} does not found for {1} handler'
            error_text = error_text.format(key, handler.__name__)

            append_log(error_text)
            print(error_text)
            exit()


def start_app():
    """
    Function which start application
    It make first iteration in working directory, for finding all files
    """

    append_log('---------------- \nApplication start')

    append_log('Testing configuration file...', write_time=False)
    test_config_file()

    # reading config file
    configuration = read_config()

    if configuration['use_default_dir']:
        dir_path = os.path.dirname(
            os.path.realpath(__file__)) + '/folder_example/'
    else:
        dir_path = configuration['work_dir']

    append_log('Working directory ' + dir_path, write_time=False)

    files_info = []

    # get all files info in working directory, for this iteration
    get_current_state(dir_path, files_info)

    append_log('Finded {0} elements'.format(len(files_info)), write_time=False)

    while True:
        files_info = checking_files(dir_path, files_info)
        time.sleep(configuration['frequency'])


if __name__ == "__main__":

    start_app()
