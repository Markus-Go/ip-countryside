# Klasse vereint alle Files und erstellt eine IP_von IP_zu Ländercode Textdatei
# 1. Dateien zussamenfügen 
# 2. Alle Zeilen die keine IPv4 oder IPv6 Adresse haben verwerfen (v4 und v6 in verschiedene Dateien?)
# IP Von Zu Bereich berechnen
# Zeile in Textfile ablegen 

# später: durch die Files iterieren und Ländercode finden
# noch später: Methoden zur Optimierung


# Simple version ohne Optimierung oder Ipv6 und Städte unterstützung

import shutil
import os
import re
import fileinput
import ipaddress






def mergedelFiles(del_destination_file_name = "del_merged.txt"):

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




def stripdelFiles(del_destination_stripped_name = "del_merged_stripped.txt"):
    ipv4_pattern = "[0-9]+(?:\.[0-9]+){3}"

    # Removes all IPv6 and other lines 
    for line in fileinput.input(os.path.join("del_files", "del_merged.txt"), inplace = True):
        if re.search(ipv4_pattern, line):
            list = line.split("|")
            #list[4] = subnetmask[list[4]]      # Subnetzmaske hier zu berechnen funktioniert auch nicht
            list = list[1], list[3], list[4]
            print(*list, end='\n')
        
           
    

def checkIp(ip, network = '192.168.0.0/24'):
    return ipaddress.ip_address(ip) in ipaddress.ip_network()    
            
def getSubnetmask(hosts):
    subnetmask = {
    32: 27,
	64: 26,
    128: 25,
    256: 24,
    512: 23,
    1024: 22,
    2048: 21,
    4094: 20,
    8192: 19,
    16384: 18,
    32768: 17,
    65536: 16,
    131072: 15,
    262144: 14,
    524290: 13,
    1048576: 12,
    2097152: 11,
    4194304: 10,
    8388608: 9,
    16777216: 8
    }
    
    return subnetmask[hosts]



def getCountryCode(ip):

    with open(os.path.join("del_files", "del_merged.txt")) as file:
        
        for line in file: 
           item = line.split()
           country = item[0]
           listip = item[1]
           hosts = item[2]

           if(checkIp(ip, listip + "/" + getSubnetmask(hosts))):
              return country
    

mergedelFiles()    # Fügt del Dateien in del_merged.txt zusammen
stripdelFiles()    # formatiert und filtert Textdatei
#print(getCountryCode("30.142.194.176"))     # Fehler beim "berechnen" der Subnetzmaske

#print("192.212.211.222" + "/" + str(getSubnetmask(1024)))          # manuell die Zahl eingeben funktioniert ohne Probleme 
print("done")





















