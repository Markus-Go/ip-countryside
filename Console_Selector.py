#from . import ip_countryside_downloader as dwn

from ip_countryside_downloader import *
from ip_countryside_utilities import *


def CallUpdate(forced=False):
    if(forced):
        print("Forcing Update!")
        #download_del_files(True)
    else:
        print("Check if files are old enough for update.")
        #download_del_files()

def CallParse(ip):
    return get_record_by_ip(ip)

def CallTrace(ip):
    return traceIP(ip)