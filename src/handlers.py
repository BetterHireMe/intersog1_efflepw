from lib_functions import append_log, read_config


def file_notifier(args, file_prop):
    """
    message: (dict) which content message header, and message content text
    Function for creating new notification in Windows 10
    """

    message_header = args['header']
    message_content = args['content'].format(
        file_prop.name, file_prop.last_status)

    import os

    # if you are using Windows
    if os.name == 'nt':
        try:
            from win10toast import ToastNotifier

            toaster = ToastNotifier()
            toaster.show_toast(message_header, message_content)

        except ImportError:
            append_log('Error! win10toast module not found')

        except Exception as e:
            append_log('Error! In function file_notifier ' +
                       str(e))

    # if you are using Linux
    elif os.name == 'posix':
        os.system('notify-send "{0}" "{1}"'
                  .format(message_header, message_content))


def create_new_folder(args, file_prop):
    """
    args: (dict) must contain path_to_folder
    file_prop: (dict) file info
    This handler creates a new folder
    """
    try:
        import os

        validate_path = file_prop.path.replace('\\', '/') + '/'

        if file_prop.is_dir and validate_path == args['path_to_folder']:

            import os

            os.mkdir(validate_path)

    except OSError:
        append_log('Cannot create directory ' +
                   file_prop.path)

    except Exception as e:
        append_log('Error! Exception in create_new_folder - ' +
                   str(e))


def convert_docx_to_pdf(args, file_prop):
    """
    args: (dict) must contain convertapi secret key
    file_prop: (dict) file info
    Handler for convert docx to pdf, using convertapi api
    """

    try:

        import convertapi

        convertapi.api_secret = args['convert_api_secret']

        result = convertapi.convert(
            'pdf', {'File': file_prop.path})

        if args['use_default_new_pdf_path']:
            new_pdf_file_path_to_save = file_prop.path.replace(
                '.docx', '.pdf')
        else:
            new_pdf_file_path_to_save = args['new_pdf_path']

        result.file.save(new_pdf_file_path_to_save)

    except ImportError:
        append_log(
            'Cannot import convertapi, type in cmd: pip install convertapi')

    except Exception as e:
        append_log('Error! Exception in convert_docx_to_pdf - ' +
                   str(e))


register_handlers = [
    file_notifier,
    create_new_folder,
    convert_docx_to_pdf
]
