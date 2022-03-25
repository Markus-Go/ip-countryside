import re
import os
import shutil
import fileinput
import ipaddress
import math

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

   # Fuses the delegated files into a txt file 
    try: 
        
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

    with open(STRIPPED_DEL_FILE, "w") as striped_file:
        
        for line in fileinput.input(MERGED_DEL_FILE):

            if re.search(IPV4_PATTERN, line) or re.search(IPV6_PATTERN, line):

                line = parse_ip(line)
                line = "|".join(map(str, line))
                line = line + '\n'
                striped_file.write(line)

           
def parse_ip(line):          
    
    # record index:     0      1   2    3     4     5    6
    # record format: registry|cc|type|start|value|date|status[|extensions...]

    record = []

    # extract infromation from line
    record = line.split("|")
    network_ip = record[3]
    
    range_start = int(ipaddress.ip_address(network_ip))
    range_end = 0
    country = record[1]
    mask = record[4]

    # if line doesn't have any country
    if record[6] == 'reserved' or record[6] == 'available':
        country = "N/A"
    
    # parse ipv4 
    if re.match(IPV4_PATTERN, network_ip):
        range_end = int(record[4]) + range_start - 1

    # parse ipv6 
    if re.match(IPV6_PATTERN, network_ip):
        net = ipaddress.IPv6Network(network_ip + "/" + mask)
        range_end = int(net.broadcast_address)

    return [range_start, range_end, country]


def ip_in_range(ip, start, end):
    
    ip = ipaddress.ip_address(ip)
    ip_int = int(ip)

    return start <= ip_int <= end  


def get_country_code(ip):

    with open(STRIPPED_DEL_FILE) as file:

        for line in file:

            item = line.split("|")

            start = int(item[0])
            end = int(item[1])
            country = item[2].rstrip('\n')

            if ip_in_range(ip, start, end):

                if country == 'N/A':
                    return country
                
                return COUNTRY_DICTIONARY[country], country
    
    return False


def run_parser():
    
    merge_del_files()      # Fügt del Dateien in del_merged.txt zusammen
    strip_del_files()      # formatiert und filtert Textdatei


# merge_in_files
def merge_in_files():
    
    try: 
        
        with open(os.path.join(DEL_FILES_DIR, "merged_ine_file.txt"), "wb") as f:
            for in_file in [ 
                    os.path.join(DEL_FILES_DIR, "apnic.db.inetnum"), 
                    os.path.join(DEL_FILES_DIR, "ripe.db.inetnum")
                    ]:

                with open(in_file, "rb") as source:

                    shutil.copyfileobj(source, f)

                    f.write(os.linesep.encode())
    
    except IOError as e:
        
        print(e)


# Returns block of data
def get_groups(seq, group_by):
    data = []
    for line in seq:
        if line.startswith(group_by):
            if data:
                if not data[0].startswith(group_by):
                    data = []
                else:
                    yield data[:-1]
                    data = []
        data.append(line.replace(" ", "").replace('\n', ""))

    if data:
        yield data


# Parses in entry
def get_parsed_in_entry(entry):
    y = []
    description = ""
    for item in entry:
    
        if any(str(item[0]) in s for s in PARSE_ITEMS):

            if not item[0] == "descr":
                y.append(item[1])
            else:
                description += item[1] + ' '
    y.append(description[:-1])

    return y



 




# Parses merged_ine file and writes it into stripped_ine_file
def parse_in_files():
    with open(os.path.join(os.path.join(DEL_FILES_DIR, "merged_ine_file.txt")), 'r', encoding='utf-8', errors='ignore') as merged, open (os.path.join(DEL_FILES_DIR, "stripped_ine_file.txt"), 'w', encoding='utf-8', errors='ignore') as stripped:
        for i, group in enumerate(get_groups(merged, "inetnum"), start=1):
            
            entry = [item.split(':') for item in group]
            #entry = [re.split(r': +', item) for item in group] # funktioniert nicht warum?
            stripped.write("|".join(get_parsed_in_entry(entry)) + '\n')

    #os.remove(os.path.join(DEL_FILES_DIR, "merged_ine_file.txt"))


 
parse_in_files()        

# l = ['202.6.91.0-202.6.91.255', 'NLA', 'AU', 'ASSIGNEDPORTABLE', '2008-09-04T06', 'APNIC', ['NationalLibraryofAustralia ParkesPlace CanberraACT2600']]
