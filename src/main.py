import os
import time
import json

from lib_functions import append_log, read_config, check_file_name


def get_current_state(dir_path, files_info):
    """
    dir_path: (string) path to scan
    files_info: (dict) dict with all files info

    Reqursive scaning directory for all files, and write files info into dict
    """

    for element in os.scandir(dir_path):

        if element.is_dir():
            # new directory path
            new_dir_path = dir_path + element.name + '/'

            # write file info into dict with another files info
            files_info[new_dir_path] = {
                'name': element.name,
                'create_time': element.stat().st_ctime,
                'update_time': element.stat().st_mtime,
                'is_dir': True
            }

            get_current_state(new_dir_path, files_info)

        else:
            # if element is file, just writing it info into dict

            files_info[element.path] = {
                'name': element.name,
                'create_time': element.stat().st_ctime,
                'update_time': element.stat().st_mtime,
                'is_dir': False
            }


def find_same(file_prop, all_files_info):
    """
    file_prop: (dict) file to look for in all files info dict
    all_files_info: (dict) dict with all files info

    function for finding file by path or create datetime

    return: (dict) returns status with the current state of the file
    """

    try:
        # trying to find file by path,
        # for cases if file edited or dont has any changes
        if file_prop['file_path'] in all_files_info.keys():
            finded_file = all_files_info[file_prop['file_path']]

            if finded_file['create_time'] == file_prop['create_time']\
                    and finded_file['update_time'] == file_prop['update_time']:
                return {'status': 'no_changes'}
            elif finded_file['create_time'] == file_prop['create_time']\
                    and finded_file['update_time'] != file_prop['update_time']:
                append_log('element changed ' + file_prop['file_path'])
                return {'status': 'edited'}

        # another case, searching file by create datetime
        for file_path in all_files_info.keys():

            if all_files_info[file_path]['create_time'] == \
                    file_prop['create_time']:

                old_file_name = all_files_info[file_path]['name']
                current_file_name = file_prop['name']

                old_directory_path = file_path.replace(
                    old_file_name, '')
                current_path = file_prop['file_path'].replace(
                    current_file_name, '')

                # if file name changed, but file path dont has changed,
                # so file was renamed
                # the case when nothing has changed is impossible
                if old_file_name == current_file_name \
                        and old_directory_path != current_path:
                    append_log('moved element ' + file_path +
                               ' to ' + file_prop['file_path'])
                    return {
                        'status': 'moved',
                        'previous_name': file_path
                    }

                # if file name dont changed, but file path was changed,
                # so file was moved
                elif old_file_name != current_file_name \
                        and old_directory_path == current_path:
                    append_log('renamed element ' + file_path +
                               ' to ' + file_prop['file_path'])
                    return {
                        'status': 'renamed',
                        'previous_name': file_path
                    }

                else:
                    # case, if file was moved, and renamed
                    append_log('moved and renamed element ' + file_path +
                               ' to ' + file_prop['file_path'])
                    return {
                        'status': 'moved_and_renamed',
                        'previous_name': file_path
                    }

    except Exception as e:
        append_log('Error! Exception in find_same function ' +
                   str(e))
        return {'status': 'error'}

    # if file dont finded by create datetime so - it's new file
    append_log('finded new element ' + file_prop['file_path'])
    return {'status': 'new'}


def check_handlers(files_info):
    """
    files_info: (dict) dict with all files info with change statuses

    function which iterates over all files name and status change,
    and search it in config file
    """

    from handlers import register_handlers

    configuration = read_config()

    # looks awful, but in my opinion this is the fastest way
    for file_info in files_info.keys():

        for handler_function in register_handlers:
            func_conf = configuration[handler_function.__name__]

            for file_conf in func_conf:
                check_file_name_result = check_file_name(
                    file_conf['file_name'], files_info[file_info]['name'])
                status_is_good = file_conf['status_to_check'] == \
                    files_info[file_info]['status']

                if check_file_name_result and status_is_good:

                    # if handler needs file info, pass this
                    if file_conf['need_file_properties']:

                        element_prop = {
                            'path': file_info,
                            'name': files_info[file_info]['name'],
                            'is_dir': files_info[file_info]['is_dir'],
                            'status': files_info[file_info]['status']
                        }

                        handler_function(file_conf['args'], element_prop)

                    else:
                        handler_function(file_conf['args'])


def checking_files(dir_path, files_info):
    """
    dir_path: (string) working directory
    files_info: (dict) dict with all files info on previously iteration

    It make one iteration in working directory,
    for finding all files current state
    """

    current_files_info = {}
    finded_old_files = []
    new_files = {}

    # iteration for finding all files current state
    get_current_state(dir_path, current_files_info)

    # loop for finding files change status
    for file_path in current_files_info.keys():

        try:
            # temp dict for find_same function
            file_prop_temp_dict = {
                'file_path': file_path,
                'name': current_files_info[file_path]['name'],
                'create_time': current_files_info[file_path]['create_time'],
                'update_time': current_files_info[file_path]['update_time'],
                'is_dir': current_files_info[file_path]['is_dir']
            }

            file_info = find_same(file_prop_temp_dict, files_info)

            # appending files name in list, which was in prev iter,
            # and which was in this iter
            # it need for finding removed files
            if file_info['status'] in ('no_changes', 'edited'):
                finded_old_files.append(file_path)
                files_info[file_path]['status'] = file_info['status']

            elif file_info['status'] in \
                    ('renamed', 'moved', 'moved_and_renamed'):
                finded_old_files.append(file_info['previous_name'])
                files_info[file_info['previous_name']
                           ]['status'] = file_info['status']

            elif file_info['status'] == 'new':
                new_files[file_path] = file_prop_temp_dict
                new_files[file_path]['status'] = 'new'

        except Exception as e:
            append_log('Error! Exception in checking_files function ' +
                       str(e) + ' ' + file_path)

    # files which was in previous iteration, but not in current,
    # this is removed from work directory
    for old_file in files_info.keys():
        if old_file not in finded_old_files:
            files_info[old_file]['status'] = 'deleted'  # file deleted
            append_log('element deleted ' + old_file)

    # check files for handlers
    check_handlers(files_info)
    check_handlers(new_files)

    return current_files_info


def start_app():
    """
    Function which start application
    It make first iteration in working directory, for finding all files
    """

    append_log('---------------- \nApplication start')

    # reading config file
    configuration = read_config()

    if configuration['use_default_dir']:
        dir_path = os.path.dirname(
            os.path.realpath(__file__)) + '/folder_example/'
    else:
        dir_path = configuration['work_dir']

    append_log('Working directory ' + dir_path, write_time=False)

    files_info = {}

    # get all files info in working directory, for this iteration
    get_current_state(dir_path, files_info)

    append_log('Finded {0} elements'.format(len(files_info)), write_time=False)

    while True:
        files_info = checking_files(dir_path, files_info)
        time.sleep(configuration['frequency'])


if __name__ == "__main__":

    start_app()
