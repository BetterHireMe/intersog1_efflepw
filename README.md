# Application for monitoring file system events

## Introduction
At this moment application work only on Windows 10.
I have tried to import into Linux system, but in Linux file.stat().st_ctime (create time) changed when i change file, but in Windows 10 it isn't. I have no time to reworks everything.


## Requirements
You need to install win10toast, and convertapi. 
```
    pip install win10toast==0.9
    pip install convertapi==1.1.0
```

## Configuration
The basic configuration is specified in the **config.json**.

    "use_default_dir": true (by default) - if sets true, workdir is /folder_example/, if sets false, value takes from "work_dir" key;
    "frequency": 1 (by default) - this is the frequency of checking the working directory.

Next config values, is required in config

    "file_notifier": it is the name of handler function, it contain list of different handlers values dictionary. Every key value require for next keys: file_name, status_to_check, need_file_properties, args.

        "file_name" - file name at which this handler will trigger, may contain * as in the file name, as in extension. That is *.* describes any file name with any extension.
        "status_to_check" - the status of the event being processed. The following events occur:
            'no_changes', 'edited', 'moved', 'renamed', 'moved_and_renamed', 'new', 'error', 'deleted'
        "need_file_properties" - true or false, if value is true, an additional argument is passed to the handler, with information about the triggered file. Be careful, if the handler does not expect to receive an additional argument, but you pass it to it, it will raise exception.
        "args" - require dictionary, with information which will be pass into handler function. 

Example:

    
    "file_notifier": [ # handler name
        {
            "file_name": "errors.txt", # file name at which this handler will trigger
            "status_to_check": "edited", # event status at which this handler will trigger
            "need_file_properties": false, # this handler does not require additional file info
            "args": { # this handler requires dict with notification message header and message content
                "header": "Attention!",
                "content": "File errors.txt was changed"
            }
        }
    ]

## Handlers

Currently, 3 handlers have been created:

    1. file_notifier - shows notifications that are specified into arg dictionary
    2. create_new_folder - creates a folder in the path that are specified into arg dictionary
    3. convert_docx_to_pdf - converts a dock file to pdf using convertapi, convert api secret key must be sets into config arg

To add a new handler, you need to do 3 steps:
    
    1. Create function in the handlers.py
    2. Register function in register_handlers list, which is at the end of the handlers.py file
    3. In the configuration file, add the necessary settings for this handler.

## Start

To start, run the following command inside the **/src/** directory:

```
python main.py
```

Good luck!

