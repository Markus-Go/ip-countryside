from ip_countryside_downloader import *

def CallUpdate(forced=False):
    if(forced):
        print("Forcing Update!")
        #download_del_files(True)
    else:
        print("Check if files are old enough for update.")
        #download_del_files()

def CallParse(ip):
    print("Calling parser with ip: ")