from del_files_downloader import *
from del_files_parser import *
from Constants import *

import re

def interpreter(input):
    inputList = re.split("\s", input)
    print(inputList)

    isCommand = CheckForCommandKey(inputList[LOC_KEY])
    print("Is Command? " + str(isCommand))

    if(not isCommand):
        return False
    elif(inputList[LOC_CMD] == CMD_EXIT):
        return False

    EvaluateCommand(inputList)

    return bool(1)

def CheckForCommandKey(cmd):
    if(cmd == KEY_CMD):
        return True
    else:
        return False

def CheckForExtensionKey(cmd):
    char_array = list(cmd)
    if(char_array[0] == KEY_EX):
        return True
    else:
        return False

def EvaluateCommand(input):
    if(input[LOC_CMD] == CMD_DB):
        print("Update Database")
        EvaluateUpdateCommand(input)
    elif(input[LOC_CMD] == CMD_PARSE):
        print("Parse Input")
        EvaluateParseCommand(input)
    else:
        print("Invalid Command")

def EvaluateUpdateCommand(input):
    if(CheckForExtensionKey(input[LOC_EX])):
        print("Command is extension")
        EvaluateUpdateExtension(input)
    else: print("Command has no extension")

def EvaluateParseCommand(input):
    if(CheckForExtensionKey(input[LOC_EX])):
        print("Command is extension")
        EvaluateParseExtension(input)
    else: print("Command has no extension")

def EvaluateUpdateExtension(input):
    ext = adaptExtension(input[LOC_EX])

    if(ext == CMD_EX_FORCE):
        print("Forcing Update")
    elif(ext == CMD_EX_HELP):
        print("Help for update function")
    else:
        print("Invalid Extension")

def EvaluateParseExtension(input):
    ext = adaptExtension(input[LOC_EX])

    if(ext == CMD_EX_HELP):
        print("Help for parse function")
    else:
        print("Invalid Extension")

def adaptExtension(extension):
    extension = ''.join(extension.split(KEY_EX, 1))
    return extension