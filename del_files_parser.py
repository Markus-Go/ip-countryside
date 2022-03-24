from ast import And
from http.client import NETWORK_AUTHENTICATION_REQUIRED
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

    with open(STRIPPED_DEL_FILE_IPV4, "w") as ip4, open(STRIPPED_DEL_FILE_IPV6, "w") as ip6:
        
        for line in fileinput.input(MERGED_DEL_FILE):

            if re.search(IPV4_PATTERN, line):

                line = parse_ipv4(line)
                line = " ".join(map(str, line))
                line = line + '\n'
                ip4.write(line)

            elif re.search(IPV6_PATTERN, line):

                line = parse_ipv6(line)
                line = " ".join(map(str, line))
                line = line + '\n'
                ip6.write(line)


def parse_ipv6(line):

    # record format: registry|cc|type|start|value|date|status[|extensions...]
    record = line.split("|")

    # if line doesn't have any country
    if record[6] == 'reserved':
        record[1] = "N/A"

    return [record[3], record[4], record[1]]


def parse_ipv4(line):          

    # record format: registry|cc|type|start|value|date|status[|extensions...]
    record = line.split("|")

    # if line doesn't have any country
    if record[6] == 'reserved':
        record[1] = "N/A"

    # get subnetmask from number of hosts (value)
    mask = get_subnet_mask(record[4])

    return [record[3], mask, record[1]]


def ip_in_range(ip, network, mask, strict = True):
    return ipaddress.ip_address(ip) in ipaddress.ip_network(network + "/" + mask, strict)


def get_country_code(ip):

    expr = re.match(IPV4_PATTERN, ip)

    if expr:
      
        with open(STRIPPED_DEL_FILE_IPV4) as file:

            for line in file:

                item = line.split()

                network = item[0]
                mask = item[1]
                
                if ip_in_range(ip, network, mask, False):
                    country = item[2].rstrip('\n')
                    return COUNTRY_DICTIONARY[country], country

    else:
        
        with open(STRIPPED_DEL_FILE_IPV6) as file:

            for line in file:

                item = line.split()

                network = item[0]
                mask = item[1]

                if ip_in_range(ip, network, mask):
                    country = item[2].rstrip('\n')
                    return COUNTRY_DICTIONARY[country], country
    
    return False


# @TODO Nicht immer aufrunden (aber wann?)
def get_subnet_mask(hosts):
    
    hosts = math.log2(int(hosts))      
    hosts_aufg = math.ceil(hosts)     
    newzahl = int(math.pow(2, hosts_aufg))

    hosts = str(newzahl)
    if(hosts in SUBNETMASK):

        return SUBNETMASK[hosts]

    return False


def run_parser():
    
    merge_del_files()      # Fügt del Dateien in del_merged.txt zusammen
    strip_del_files()      # formatiert und filtert Textdatei

# Tests
#print(get_country_code("2001:43f8:1d0::")) -> ('SENEGAL', 'SN')
#print(get_country_code("45.4.16.10"))      -> ('BRAZIL', 'BR')


 


