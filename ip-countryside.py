from socket import IP_TOS

from Console_Interpreter import interpreter

def main():

    isExitCmd = bool(1)

    while isExitCmd:
        command = input("Type in your command:\n\n")
        command
        isExitCmd = interpreter(command)
    return 0 
main()