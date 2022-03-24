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



# @TODO define merged_del_file as global name 
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


# @TODO define stipped_del_file as global name 
def strip_del_files(stipped_del_file = "stipped_del_files.txt"):

    with open(os.path.join(DEL_FILES_DIR, "ipv4_del.txt"), 'w') as ip4, open(os.path.join(DEL_FILES_DIR, "ipv6_del.txt"), 'w') as ip6:
        for fileline in fileinput.input(os.path.join(DEL_FILES_DIR, "merged_del_files.txt")):

            if re.search(IPV4_PATTERN, fileline):

                fileline = parse_ipv4(fileline)
                fileline = " ".join(map(str, fileline))
                ip4.write(str(fileline)+'\n')

            elif re.search(IPV6_PATTERN, fileline):

                fileline = parse_ipv6(fileline)
                fileline = " ".join(map(str, fileline))
                ip6.write(str(fileline)+'\n')



def parse_ipv6(line):

    record = line.split("|")
    if record[6] == 'reserved':
        record[1] = "N/A"

    return [record[3], record[4], record[1]]

def parse_ipv4(line):           # Diese Klasse verwerfen und die ipaddr Klasse verwenden?
                                # @TODO Muss noch verändert werden dass nur ip + cidr + country code in textdatei steht

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
    
    record = [ranges, record[1]]

    return record



def ipv4_to_int(ip):
    return (ip[0] * 16777216) + (ip[1] * 65536) + (ip[2] * 256 ) + (ip[3] * 1)


def ipv4_in_range(min, max, ip):
    return min <= ip <= max


def ip_in_range(ip, network, mask):
    return ipaddress.ip_address(ip) in ipaddress.ip_network(network + "/" + mask)


def get_country_code(ip):

    expr = re.match(IPV4_PATTERN, ip)

    if expr:
        ip = ip.split('.')              # 3 Zeilen brauchen wir nicht mehr?
        ip = [int(x) for x in ip]
        ip = ipv4_to_int(ip)
        with open(os.path.join(DEL_FILES_DIR, "ipv4_del.txt")) as file:

            for line in file:

                item = line.split("|")

                network = item[3]
                nr_max_hosts = item[4]
                mask = get_subnet_mask(nr_max_hosts)

                if ip_in_range(ip, network, mask):
                    country = country.rstrip('\n')
                    return COUNTRY_DICTIONARY[country], country
        return 'No Country Found!'
    else:
        with open(os.path.join(DEL_FILES_DIR, "ipv6_del.txt")) as file:

            for line in file:

                item = line.split()

                network = item[0]
                mask = item[1]

                if ip_in_range(ip, network, mask):
                    country = item[2].rstrip('\n')
                    return COUNTRY_DICTIONARY[country], country
        return 'No Country Found!'



      
def get_subnet_mask(hosts):     # @TODO Nicht immer aufrunden?
    
    hosts = math.log2(int(hosts))      
    hosts_aufg = math.ceil(hosts)     
    newzahl = int(math.pow(2, hosts_aufg))

    hosts = str(newzahl)
    if(hosts in SUBNETMASK):

        return SUBNETMASK[hosts]

    return "0"


def main():

    #merge_del_files()    # Fügt del Dateien in del_merged.txt zusammen
    #strip_del_files()    # formatiert und filtert Textdatei
    #print(int(ipaddress.ip_address("2001::")))

    #print(ipaddress.ip_address('2001:0db8:1234::') in ipaddress.ip_network('2001:0db8::/32'))
    #print(('691634176,691650559', 'ZA').join)

    print(get_country_code("2001:43f8:1d0::"))


main()


