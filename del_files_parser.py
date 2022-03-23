from ast import And
from itertools import count
from DBRangeEntry import DBRangeEntry
import re
import os
import shutil
import fileinput
import ipaddress
import math

from config import *;

# Klasse vereint alle Files und erstellt eine IP_von IP_zu Ländercode Textdatei
# 1. Dateien zussamenfügen 
# 2. Alle Zeilen die keine IPv4 oder IPv6 Adresse haben verwerfen (v4 und v6 in verschiedene Dateien?)
# IP Von Zu Bereich berechnen
# Zeile in Textfile ablegen 

# später: durch die Files iterieren und Ländercode finden
# noch später: Methoden zur Optimierung

# Simple version ohne Optimierung oder Ipv6 und Städte unterstützung

COUNTRY_DICTIONARY = {}


def merge_del_files(merged_del_file = "merged_del_files.txt"):

   # Fuses the delegated files into a txt file 
    try: 
        
        with open(os.path.join(DEL_FILES_DIR, merged_del_file), "wb") as f:
            for del_file in [ 
                    os.path.join(DEL_FILES_DIR, AFRINIC['fname']), 
                    os.path.join(DEL_FILES_DIR, LACNIC['fname']),
                    os.path.join(DEL_FILES_DIR, ARIN['fname']),
                    os.path.join(DEL_FILES_DIR, APNIC['fname']), 
                    os.path.join(DEL_FILES_DIR, RIPE['fname'])
                    ]:

                with open(del_file,'rb') as source:

                    shutil.copyfileobj(source, f)

                    f.write(os.linesep.encode())
    
    except IOError as e:
        
        print(e)


def strip_del_files(stipped_del_file = "stipped_del_files.txt"):

    ipv4_pattern = "[0-9]+(?:\.[0-9]+){3}"
    ipv6_pattern = ""

    # Removes all IPv6 and other lines 
    for line in fileinput.input(os.path.join(DEL_FILES_DIR, "merged_del_files.txt"), inplace = True):
        
        if re.search(ipv4_pattern, line):
            
            list = parse_ipv4(line)
 
            print(*list, end='\n')

        if re.search(ipv6_pattern, line):

            # @TODO IPv6 ... Do Something here ...
            list = parse_ipv6(line)

            # print(*list, end='\n')


def parse_ipv4(line):

    # registry|cc|type|start|value|date|status[|extensions...]

    record = line.split("|")

    # if line doesn't have any country 
    if record[6] == 'reserved':
        record[1] = "N/A"

    cidr = int(get_subnet_mask(record[4]))
    
    addr = [int(x) for x in record[3].split('.')]
    
    mask = [( ((1<<32)-1) << (32-cidr) >> i ) & 255 for i in reversed(range(0, 32, 8))]
    
    netw = [addr[i] & mask[i] for i in range(4)]
    
    bcas = [(addr[i] & mask[i]) | (255^mask[i]) for i in range(4)]

    ranges = [ipv4_to_int(netw), ipv4_to_int(bcas)]
    
    ranges = map(str, ranges) 
    
    ranges = ','.join(ranges)
    
    record = ranges, record[1]

    return record



def ipv4_to_int(ip):
    return (ip[0] * 16777216) + (ip[1] * 65536) + (ip[2] * 256 ) + (ip[3] * 1)


def ipv4_in_range(min, max, ip):
    return min <= ip <= max


def parse_ipv6(line):
    return ""



def get_country_code(ip):
   
    ip = ip.split('.')
    ip = [int(x) for x in ip]
    ip = ipv4_to_int(ip)

    with open(os.path.join(DEL_FILES_DIR, "del_merged.txt")) as file:
        
        for line in file: 

           item = line.split(" ")

           [ranges, country] = item 

           [minIP, maxIP] = ranges.split(",")

           if ipv4_in_range(int(minIP), int(maxIP), ip):
                country = country.rstrip('\n')
                return COUNTRY_DICTIONARY[country], country


    return 'No Country Found!' 

      
def get_subnet_mask(hosts):
    
    hosts = math.log2(int(hosts))      
    hosts_aufg = math.ceil(hosts)     
    newzahl = int(math.pow(2, hosts_aufg))

    hosts = str(newzahl)
    if(hosts in SUBNETMASK):

        return SUBNETMASK[hosts]

    return "0"



def createCountryDic():
  
    with open(os.path.join("countries.txt"), 'r') as f:
        for line in f:
            line = line.rstrip('\n')
            (val, key) = line.split(";")
            COUNTRY_DICTIONARY[key] = val


  


def main():
    createCountryDic()
    #merge_del_files()    # Fügt del Dateien in del_merged.txt zusammen
    #strip_del_files()    # formatiert und filtert Textdatei
    print(str(get_country_code("80.142.194.176"))) 
    
    

main()