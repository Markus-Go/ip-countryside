from socket import IP_TOS
from  ip_countryside_downloader import *
from  ip_countryside_parser import *
from Console_Interpreter import interpreter

isExitCmd = False

def main():

    isExitCmd = bool(1)

    while isExitCmd:
        command = input("Type in your command:\n\n")
        command
        isExitCmd = interpreter(command)
    return 0 
main()