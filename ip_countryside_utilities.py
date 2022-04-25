from config import *;
from ip_countryside_parser import *
import ipaddress

# @TODO Method should call read_db() to get records in form of list     -> Aufwand 1
# Use a filter instead  

def get_record_by_ip(ip):
    
    with open(IP2COUNTRY_DB, encoding='utf-8', errors='ignore') as file:

        for line in file:

            item = line.split("|")

            range_start = int(item[0])
            range_end   = int(item[1])
            country     = item[2].rstrip('\n')
            if not item[4] =="":
                print(item[3])
                print(item[4])
            try:
                city = get_city(item[4], country)
            except:
                city = "-"
            if not city == "-":
                print(city)
                print(country)
            
            if ip_in_range(ip, range_start, range_end):

                return COUNTRY_DICTIONARY[country], country, city
            

    return False
    

def ip_in_range(ip, start, end):
    
    ip = ipaddress.ip_address(ip)
    ip_int = int(ip)

    return start <= ip_int <= end 
