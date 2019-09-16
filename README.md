# Intersog: Junior Python Developer task

Create an application for monitoring file system events in a certain directory. 

The app has to read config (e.g. `config.ini`, `settings.py`) and setup configurations.
The application must detect events that occur in the file system. For example file or folder was created/deleted/changed.
When event occurs -> certain Handler (registered in config) should be used to process that event. 
It's up to you which handlers to implement. It can be anything (compiling/renaming/deleting...).
Map handlers and patterns in the config file. 

##### Example: 
`Workdir:`
- `<filename1>.<file_extention_to_delete>` -> delete it
- `<filename2>.c` -> compile it
- `<filename3>.jpg` -> convert to .png
- `<filename4>.doc` -> to .pdf
 
##### Requirements: 
- application must not use all CPU time of one or more cores.
- implement a minimum of 3 different event handlers. 
- possibility to add or remove handlers.
 
##### Not required but will be a very big plus: 
1. Daemonization of app process. +
1. Concurrency. ++ 
1. Docker containerization. ++ 
1. Implement a module for notifying the user about events that have occured. +++ 
1. Readme.md ++++ 

### To submit your solution just push your code to this repo 😎

Happy coding! 😉
