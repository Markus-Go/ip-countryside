#from . import ip_countryside_downloader as dwn

from ip_countryside_downloader import *
from ip_countryside_utilities import *
from ip_countryside_parser import *


def CallUpdate(forced=False):
    if(forced):
        print("Forcing Update!")
        #download_del_files(True)
    else:
        print("Check if files are old enough for update.")
        #download_del_files()
    run_parser(multicore=True)

def CallParse(ip):

    record = get_record_by_ip(ip)
    output = ""
    
    if record:

        cc = record[2]

        output = "\n" + record[0].__str__() + " - " + record[1].__str__() + "\n" + "Country: " + COUNTRY_DICTIONARY[cc]

    return output

def CallTrace(ip):

    records = traceIP(ip)
    
    output = ""

    for record in records:

        record[0] = record[0].__str__() 
        record[1] = record[1].__str__()

        output = output + "\n" + str(record)

    return output