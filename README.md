# Application for monitoring file system events

## Requirements
You need to install convertapi
```
    pip install convertapi==1.1.0
```

If you are Windows 10 user, also you must to install win10toast
```
    pip install win10toast==0.9
```


## Configuration
The basic configuration is specified in the **config.json**.

    "use_default_dir": true (by default) - if set true, workdir is /folder_example/, if set false, value takes from "work_dir" key;
    "frequency": 1 (by default) - this is the frequency of checking the working directory.

Next config values, is required in config

    "file_notifier": it is the name of handler function, it contain list of different handlers values dictionary. Every key value require for next keys: file_name, status_to_check, need_file_properties, args.

        "file_name" - file name at which this handler will trigger, may contain * as in the file name, as in extension. That is *.* describes any file name with any extension.
        "status_to_check" - the status of the event being processed. The following events occur:
            'no_changes', 'edited', 'moved', 'renamed', 'moved_and_renamed', 'created', 'error', 'deleted', '*'
        "need_file_properties" - true or false, if value is true, an additional argument is passed to the handler, with information about the triggered file. Be careful, if the handler does not expect to receive an additional argument, but you pass it to it, it will raise exception.
        "args" - require dictionary, with information which will be pass into handler function, it can be empty 


Example:
    
    "file_notifier": [ # handler name
        {
            "file_name": "*.*", # file name at which this handler will trigger
            "status_to_check": "*", # event status at which this handler will trigger, * - it will trigger any status except no_changes
            "need_file_properties": true, # this handler require additional file info
            "args": { # this handler requires dict with notification message header and message content
                "header": "New notification!",
                "content": "File {0} was {1}"
            }
        }
    ]

## Handlers

Currently, 3 handlers have been created:

    1. file_notifier - shows notifications that are specified into arg dictionary
    2. create_new_folder - creates a folder in the path that are specified into arg dictionary
    3. convert_docx_to_pdf - converts a docx file to pdf using convertapi, convert api secret key must be sets into config arg

To add a new handler, you need to do 3 steps:
    
    1. Create function in the handlers.py
    2. Register function in register_handlers list, which is at the end of the handlers.py file
    3. In the configuration file, add the necessary settings for this handler.

## Start

To start, run the following command inside the **/src/** directory:

```
python main.py
```
or for linux users
```
python3 main.py
```

### **Attention!** Before starting the project, change **path_to_folder** for **create_new_folder** handler in **config.json** file.

Good luck!

