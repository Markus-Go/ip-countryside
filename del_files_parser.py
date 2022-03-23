from ast import And
from itertools import count
from DBRangeEntry import DBRangeEntry
import re
import os
import shutil
import fileinput
import ipaddress
import math

from config import SUBNETMASK;

# Klasse vereint alle Files und erstellt eine IP_von IP_zu Ländercode Textdatei
# 1. Dateien zussamenfügen 
# 2. Alle Zeilen die keine IPv4 oder IPv6 Adresse haben verwerfen (v4 und v6 in verschiedene Dateien?)
# IP Von Zu Bereich berechnen
# Zeile in Textfile ablegen 

# später: durch die Files iterieren und Ländercode finden
# noch später: Methoden zur Optimierung

# Simple version ohne Optimierung oder Ipv6 und Städte unterstützung


def merge_del_files(del_destination_file_name = "del_merged.txt"):

   # Fuses the delegated files into a txt file 
    with open(os.path.join("del_files", del_destination_file_name), "wb") as destination:
        for f in [ os.path.join("del_files", "delegated-afrinic-latest"), 
                  os.path.join("del_files", "delegated-apnic-latest"), 
                  os.path.join("del_files", "delegated-arin-extended-latest"),
                  os.path.join("del_files", "delegated-lacnic-latest"),
                  os.path.join("del_files", "delegated-ripencc-latest")]:
            with open(f,'rb') as source:
                shutil.copyfileobj(source, destination)
                destination.write(os.linesep.encode())


def parse_del_files(delName):
    
    dbRangeEntries = []

    del_files_dir = "del_files"
    os.chdir(del_files_dir)

    try:
        with open(delName) as fp:

            for line in fp:
                
                entry = create_dbRangeEntry(line)
                
                dbRangeEntries.append(entry)

    except IOError as e:
    
        print(e)

    os.chdir("../")

    return dbRangeEntries


def create_dbRangeEntry(strEntry):

    strEntry = strEntry.split("|")
    
    registry = strEntry[0]
    country = strEntry[1]
    
    ipFrom = re.sub('[^0-9]', '', strEntry[3])
    if(not ipFrom) :
        ipFrom = -1
    # python uses variable number of bits for integers -> no overflow
    ipFrom = int(ipFrom)

    ipTo = ipFrom + (int(strEntry[4]) - 1) 

    entry = DBRangeEntry(ipFrom, ipTo, country, registry)

    return entry


def strip_del_files(del_destination_stripped_name = "del_merged_stripped.txt"):
    # @TODO remove all un relevant lines for example 2|afrinic|20220317| .... 
    ipv4_pattern = "[0-9]+(?:\.[0-9]+){3}"

    # Removes all IPv6 and other lines 
    for line in fileinput.input(os.path.join("del_files", "del_merged.txt"), inplace = True):
        if re.search(ipv4_pattern, line):
            list = line.split("|")
            cidr = int(getSubnetmask(list[4]))
            addr = [int(x) for x in list[3].split('.')]
            mask = [( ((1<<32)-1) << (32-cidr) >> i ) & 255 for i in reversed(range(0, 32, 8))]
            netw = [addr[i] & mask[i] for i in range(4)]
            bcas = [(addr[i] & mask[i]) | (255^mask[i]) for i in range(4)]
            
            ranges = ipv4_to_int(netw, bcas)
            ranges = map(str, ranges) 
            ranges = ','.join(ranges)
            
            list = ranges, list[1]

            print(*list, end='\n')

def ipv4_to_int(minIP, maxIP):

    intIPMin = (minIP[0] * 16777216) + (minIP[1] * 65536) + (minIP[2] * 256 ) + (minIP[3] * 1)
    intIPMax = (maxIP[0] * 16777216) + (maxIP[1] * 65536) + (maxIP[2] * 256 ) + (maxIP[3] * 1)

    return [intIPMin, intIPMax]

def getCountryCode(ip):

    with open(os.path.join("del_files", "del_merged.txt")) as file:
        
        for line in file: 
           
           item = line.split(" ")

           [ranges, country] = item 

           [minIP, maxIP] = ranges.split(",")
           
           ip = [int(x) for x in ip.split('.')]

           ip = (ip[0] * 16777216) + (ip[1] * 65536) + (ip[2] * 256 ) + (ip[3] * 1)


           if ipv4_in_range(int(minIP), int(maxIP), ip):
                return country

           return 'No Country Found!' 

           
def ipv4_in_range(min, max, ip):
    return min <= ip <= max

            
def getSubnetmask(hosts):
    
    hosts = math.log2(int(hosts))      
    hosts_aufg = math.ceil(hosts)     
    newzahl = int(math.pow(2, hosts_aufg))

    hosts = str(newzahl)
    if(hosts in SUBNETMASK):

        return SUBNETMASK[hosts]

    return "0"

#merge_del_files()    # Fügt del Dateien in del_merged.txt zusammen
#strip_del_files()    # formatiert und filtert Textdatei

# print(getCountryCode("30.142.194.176"))     # Fehler beim "berechnen" der Subnetzmaske

#print(checkIp("30.142.194.176", "41.48.0.0"))

#print("192.212.211.222" + "/" + str(getSubnetmask(1024)))          # manuell die Zahl eingeben funktioniert ohne Probleme 


#print(getCountryCode("94.134.100.189"))

ip = [94, 134, 100, 189]
ip = (ip[0] * 16777216) + (ip[1] * 65536) + (ip[2] * 256 ) + (ip[3] * 1)

print(ip)