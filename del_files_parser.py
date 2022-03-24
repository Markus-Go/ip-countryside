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

    ipv4_pattern = "[0-9]+(?:\.[0-9]+){3}"
    # @TODO ipv6 ...
    ipv6_pattern = ""

    # Removes all IPv6 and other lines 
    for line in fileinput.input(os.path.join(DEL_FILES_DIR, "merged_del_files.txt"), inplace = True):
        
        if re.search(ipv4_pattern, line):
            
            list = parse_ipv4(line)
 
            print(*list, end='\n')

        if re.search(ipv6_pattern, line):

            # @TODO IPv6 ... Do Something here ...
            list = ""

           
def parse_ipv4(line):

    # registry|cc|type|start|value|date|status[|extensions...]

    record = []
    
    line = line.split("|")

    # if ip range is reserved 
    if line[6] == 'reserved':
        # record doesn't have any country 
        line[1] = "N/A"

    # country code
    coutnry = line[1]

    # subnetmask short e.g. 24 or 12 ...
    nr_max_hosts = line[4]
    mask = get_subnet_mask(nr_max_hosts)

    # start ip adress of the network  
    network = line[3]
    network = ipaddress.IPv4Network(network + '/' + mask, False)

    # casting in integer works only with ip_address not with IPv4Network ...
    # therefore need to create this variable 
    network_ip = ipaddress.ip_address(line[3])

    # end ip adress of the network (broadcast)  
    broadcast = network.broadcast_address

    record = [int(network_ip), int(broadcast), coutnry]
    
    return record


def ipv4_in_range(ip, network, mask):
    return ipaddress.ip_address(ip) in ipaddress.ip_network(network + "/" +  mask) 


def get_country_code(ip):
   
    with open(os.path.join(DEL_FILES_DIR, "stipped_del_file.txt")) as file:
        
        for line in file: 

           item = line.split("|")

           network = item[3]
           nr_max_hosts = item[4]
           mask = get_subnet_mask(nr_max_hosts)

           if ipv4_in_range(ip, network, mask):
                country = country.rstrip('\n')
                return COUNTRY_DICTIONARY[country], country

    return False 

      
def get_subnet_mask(hosts):
    
    hosts = math.log2(int(hosts))      
    hosts_aufg = math.ceil(hosts)     
    newzahl = int(math.pow(2, hosts_aufg))

    hosts = str(newzahl)
    if(hosts in SUBNETMASK):

        return SUBNETMASK[hosts]

    return "0"


def main():

    merge_del_files()    # Fügt del Dateien in del_merged.txt zusammen
    strip_del_files()    # formatiert und filtert Textdatei
    print(get_country_code("45.4.16.10"))

main()
