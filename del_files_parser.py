import re
import os
import shutil
import fileinput
import ipaddress

from config import *;


# Simple version ohne Optimierung und Städte unterstützung

# @TODO Aurunden Idee verbessern und genauer schauen in 
# der Dateien, ob vuekkecht ein Eintrag ein anderer 
# aufsummiert oder so ...

# @TODO MAX MindDB API anschauen benutzen 
# wie sie die Objekte einer Datenbank aufbauen ....

# @TODO vergleichen der Ergebnisse mit den von dem 
# alten Tool 

def merge_del_files():

    try: 
        
        # merges the delegated files into a one file 
        with open(MERGED_DEL_FILE, "wb") as f:
            
            for del_file in [ 
                    os.path.join(DEL_FILES_DIR, AFRINIC['fname']), 
                    os.path.join(DEL_FILES_DIR, LACNIC['fname']),
                    os.path.join(DEL_FILES_DIR, ARIN['fname']),
                    os.path.join(DEL_FILES_DIR, APNIC['fname']), 
                    os.path.join(DEL_FILES_DIR, RIPE['fname'])
                    ]:

                with open(del_file, "rb") as source:

                    shutil.copyfileobj(source, f)

                    f.write(os.linesep.encode())
    
    except IOError as e:
        
        print(e)


def strip_del_files():

    try:

        with open(STRIPPED_DEL_FILE, "w") as f:

            for line in fileinput.input(MERGED_DEL_FILE):
                
                # get rid of all lines without "ip entry" before parsing
                if re.search(IPV4_PATTERN, line) or re.search(IPV6_PATTERN, line):

                    line = parse_line(line)
                    line = "|".join(map(str, line))
                    line = line + '\n'
                    f.write(line)

    except IOError as e:
        
        print(e)

        
    


def parse_line(line):          
    
    # record index:     0      1   2    3     4     5    6
    # record format: registry|cc|type|start|value|date|status[|extensions...]

    record = []
    record = line.split("|")

    # extract infromation from line
    country     = record[1]
    type        = record[2]
    network_ip  = record[3]
    mask        = record[4]
    status      = record[6]

    # calculate int value of network ip
    range_start = int(ipaddress.ip_address(network_ip))
    range_end   = 0

    # if line doesn't have any country
    if status == "reserved" or status == "available":
        country = "N/A"
    
    # parse ipv4 
    if type == "ipv4":
        range_end = range_start + int(mask) - 1

    # parse ipv6 
    if  type == "ipv6":
        net = ipaddress.IPv6Network(network_ip + "/" + mask)
        range_end = int(net.broadcast_address)

    return [range_start, range_end, country]


def sort_stripped_del_files():

    records = []

    try:

        # save all records in stripped_del_file into a list
        with open(STRIPPED_DEL_FILE, "r") as f:
            
            for line in f:
               
                line = line.split("|")
                
                record = [
                    int(line[0]),   # get range_start
                    int(line[1]),   # get range_end
                    line[2].rstrip('\n')
                ]

                records.append(record)

        
        # sort this list
        records.sort()

        # write it back 
        with open(STRIPPED_DEL_FILE, "w") as f:
            
            for record in records:
               
               line = "|".join(map(str, record))
               line = line + '\n'
               f.write(line)
               

    except IOError as e:
        
        print(e)

    return records
    
    
def get_country_code(ip):

    with open(STRIPPED_DEL_FILE) as file:

        for line in file:

            item = line.split("|")

            range_start = int(item[0])
            range_end   = int(item[1])
            country     = item[2].rstrip('\n')

            if ip_in_range(ip, range_start, range_end):

                if country == 'N/A':
                    return country
                
                return COUNTRY_DICTIONARY[country], country
    
    return False


def ip_in_range(ip, start, end):
    
    ip = ipaddress.ip_address(ip)
    ip_int = int(ip)

    return start <= ip_int <= end 



def run_parser():
    
    print("Merging delegation files ...")
    #merge_del_files()          # Fügt del Dateien in del_merged.txt zusammen
    print("Delegation files merging finished\n")

    print("Striping merged file ...")
    strip_del_files()           # formatiert und filtert Textdatei
    print("Striping merged file finished\n")

    print("Sorting striped file ...")
    sort_stripped_del_files()
    print("Sorting striped files finished\n")

run_parser()
