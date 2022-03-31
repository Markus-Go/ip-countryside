import re
import os
import shutil
import fileinput
import ipaddress
import time
import multiprocessing as mp
#import locationtagger

from config import *;
from ip_countryside_db import *;
from ip_countryside_utilities import *;

# Release 0.9.0 coming soon ... 


# @TODO handle_ranges_overlapp() have now a structure to modify the data                    # Aufwand 5
# base records. (The PDF can be helpful)           
# Info: we need to know which entries should be removed. 
# One can also take date into consideration.

# @TODO Bugfix in parse_inet_group() -> see todo there ...                                  # Auufwand 5 

# @TODO vergleichen der Ergebnisse mit den von dem alten Tool                               # Aufwand 5

# @TODO comment and write description for each method & clean code                          # Aufwand 5 

# @TODO later add parameters for the command line interpreter (cli)                         # Aufwand 5

# @TODO Flussdiagramm vom Parser erstellen                                                  # Aufwand 5

# @TODO MAX MindDB API importieren zum testen und anschauen benutzen                        # Aufwand 8
# wie sie die Objekte einer Datenbank aufbauen ....

# @TODO Speed up parsing process of inetnum files                                           # Aufwand 13/20
    # 01. External Sorting Method (Merge Sort) 
    # 02. Parsing should be done by multiple threads

# @TODO add city information (when available) to the method parse_inet parse_inet_group     # Aufwand 21

#def get_city(string, countryCode):

#    place_entity = locationtagger.find_locations(text = string)
    
#    # getting all country cities
#    #print("The countries cities in text : ")
#    #print(place_entity.country_cities)

#    for c in place_entity.country_cities:
#        if c.upper() == COUNTRY_DICTIONARY[countryCode]:
#            #print(place_entity.country_cities[c], "is in",COUNTRY_DICTIONARY[countryCode])
#            return place_entity.country_cities[c][0]  
#    return "No City information"      

#string = "Dalian Ulm Bureau"
string = "Ulm Dalian"
#string = "Munich, London etc. Pakistan and Bangladesh share its borders Dalian"
countryCode = "CN"
#print(get_city(string, countryCode))

# ==============================================================================
# Delegation parsing methods 


def merge_del_files():

    try: 
        
        # merges the delegated files into a one file 
        with open(MERGED_DEL_FILE, "wb") as f:
            
            for del_file in [ 
                    os.path.join(DEL_FILES_DIR, AFRINIC['del_fname']), 
                    os.path.join(DEL_FILES_DIR, LACNIC['del_fname']),
                    os.path.join(DEL_FILES_DIR, ARIN['del_fname']),
                    os.path.join(DEL_FILES_DIR, APNIC['del_fname']), 
                    os.path.join(DEL_FILES_DIR, RIPE['del_fname'])
                    ]:

                with open(del_file, "rb") as source:

                    shutil.copyfileobj(source, f)

                    f.write(os.linesep.encode())
    
    except IOError as e:
        
        print(e)


def parse_del_files():

    try:

        with open(STRIPPED_DEL_FILE, "w") as f:

            for line in fileinput.input(MERGED_DEL_FILE):
                
                # get rid of all lines without "ip entry" before parsing
                if re.search(IPV4_PATTERN, line) or re.search(IPV6_PATTERN, line):

                    # actual parsing of a line is done in parse_del_line
                    line = parse_del_line(line)

                    line = "|".join(map(str, line))
                    line = line + '\n'
                    f.write(line)

    except IOError as e:
        
        print(e)


def parse_del_line(line):          
    
    # record index:     0      1   2    3     4     5    6
    # record format: registry|cc|type|start|value|date|status[|extensions...]

    record = []
    record = line.split("|")

    # extract infromation from line
    registry    = record[0].upper()
    country     = record[1].upper()
    type        = record[2]
    network_ip  = record[3]
    date        = record[5]
    mask        = record[4]
    status      = record[6]

    # calculate int value of network ip
    range_start = int(ipaddress.ip_address(network_ip))
    range_end   = 0

    # parse ipv4 
    if type == "ipv4":
        
        is_reserved = not ipaddress.IPv4Network(range_start).is_global
        if is_reserved:
            return []

        range_end = range_start + int(mask) - 1
        

    # parse ipv6 
    if  type == "ipv6":

        net = ipaddress.IPv6Network(network_ip + "/" + mask)
        is_reserved = not net.is_global
        if is_reserved:
            return []
        
        range_end = int(net.broadcast_address)

    # convert registry from RIPENCC to RIPE (parser compatibilty) 
    if registry == 'RIPENCC':
        registry = "RIPE"

    # if line doesn't have any country
    if status == 'reserved' or status == "available":
        country = "ZZ"
    

    return [range_start, range_end, country, registry, date]


# ==============================================================================
# Inetnum Parsing methods 

def merge_inet_files():
    
    try: 
        
        with open(MERGED_INET_FILE, "wb") as f:
            
            for inet_file in [ 
                    os.path.join(DEL_FILES_DIR, APNIC['inet_fname']), 
                    os.path.join(DEL_FILES_DIR, RIPE['inet_fname'])
                    ]:

                with open(inet_file, "rb") as source:

                    shutil.copyfileobj(source, f)

                    f.write(os.linesep.encode())
    
    except IOError as e:
        
        print(e)


# Parses merged_ine file and writes it into stripped_ine_file
def parse_inet_files_single():
    
    with open(MERGED_INET_FILE, 'r', encoding='utf-8', errors='ignore') as merged, open (STRIPPED_INET_FILE, 'w', encoding='utf-8', errors='ignore') as stripped:
        
        for group in get_inet_group(merged, "inetnum"):
            
            line = parse_inet_group(group)
            line = "|".join(map(str, line))
            line = line + '\n'
            stripped.write(line)


# Returns block of data
def get_inet_group(seq, group_by):
    
    data = []
    
   
    for line in seq:
        
        # escape comments (starts with '#')
        # escape unrelevant data in ripe.inetnum (starts with '%')
        if line.startswith("#") or line.startswith("%"): 
            continue

        # every inetnum object starts with an entry -> inetnum: ...
        # so start grouping if a line starts with 'inetnum'
        # if an object has already been initialized then scann also the
        # next lines (or data) 
        if (line.startswith(group_by) or data) and not line.startswith("\n"):
        
            line = line.replace(" ", "").replace("\n", "")
            data.append(line)
            
        # note that empty lines are used as a seperator between
        # inetnum objects. So if line starts with empty line
        # then yield the data object first and then
        # reset the object to store next object's data
        elif line.startswith("\n") and data:
            yield data
            data = []


# Parses in entry
def parse_inet_group(entry):
    
    record = {}
    
    # remove all empty elements in the entry
    entry = [item for item in entry if item] 

    # split each element (e.g. ["source:APNIC" in the entry to  ["source", "APNIC"]
    entry = [item.split(':', maxsplit = 1) for item in entry]
    
    # create a dictionary
    # if there are dupplicate items append their values ..
    # this will prevent deleting items with same key (e.g. descr)
    for item in entry:
            
            # @TODO viele Einträge mit nur einem Index
            # Warum ? -> parser-bug ? investigate ... 
            if(len(item) > 1):
                

                key = item[0]
                value = item[1]
                
                if key not in record:
                    record[key] = value
                
                if key == "descr":
                    
                    if value.split() == "ThisnetworkrangeisnotallocatedtoAPNIC":
                        return []
                    
                    record[key] = record[key] + " " + value
                    

                # if a country line has comment, remove the comment
                if key == "country":
                    record[key] = value.split("#")[0]

                if key == "source" and value == "ripencc":
                    record[key] = "RIPE"
            

    # extract the ranges out of record
    range = record['inetnum'].split("-")

    if re.match(IPV4_PATTERN, range[0]):
        
        is_reserved = not ipaddress.IPv4Network(range[0]).is_global
        if is_reserved:
            return []

    elif re.match(IPV6_PATTERN, range[0]):
        
        is_reserved = not ipaddress.IPv6Network(range[0]).is_global
        if is_reserved:
            return []


    range_start = int(ipaddress.ip_address(range[0]))
    range_end   = int(ipaddress.ip_address(range[1]))
    
    country     = record['country']
    registry    = record['source']

    if 'descr' in record:
        descr = record['descr']
        return [range_start, range_end, country, registry, descr]

    return [range_start, range_end, country, registry]



def parse_inet_multicore(kb = 5):

    # Fetch number of cpu cores
    cpu_cores = mp.cpu_count()

    # Clears the previous file
    if os.path.exists(STRIPPED_INET_FILE):
        file = open(STRIPPED_INET_FILE, "r+")
        file.truncate(0)
        file.close()

    # get file size and set chuck size
    filesize = os.path.getsize(MERGED_INET_FILE)
    split_size = 1024 * 1024 * kb

    # determine if it needs to be split
    if filesize > split_size:

        # create pool, initialize chunk start location (cursor)
        pool = mp.Pool(cpu_cores)
        cursor = 0
        with open(MERGED_INET_FILE, 'r', encoding='utf-8', errors='ignore') as fh:

            # for every chunk in the file...
            for chunk in range(filesize // split_size):

                # determine where the chunk ends, is it the last one?
                if cursor + split_size > filesize:
                    end = filesize
                else:
                    end = cursor + split_size

                # seek to end of chunk and read next line to ensure you 
                # pass entire lines to the processfile function
                fh.seek(end)
                fh.readline()
                
                s = fh.readline()
                while s != '\n' and s != "":    
                    s = fh.readline()
                    #print("Chunk: ", chunk , fh.tell(), '\n', s)           

                # get current file location
                end = fh.tell()

                # add chunk to process pool, save reference to get results
                proc = pool.apply_async(parse_inet_chunk, [MERGED_INET_FILE, cursor, end])
                
                 # terminate when no more chunks are needed
                if split_size > end - cursor:
                    break

                #Debug
                #fh.seek(cursor)
                #lines = fh.readlines(end - cursor)  
                #print(*lines, '\n----------------------------------------\n')

                # setup next chunk
                cursor = end

        # close and wait for pool to finish
        pool.close()
        pool.join()


# process file chunk 
def parse_inet_chunk(file, start=0, stop=0):
    i = 0
    with open(MERGED_INET_FILE, 'r', encoding='utf-8', errors='ignore') as inetnum_file, open (STRIPPED_INET_FILE, 'a', encoding='utf-8', errors='ignore') as parsed_file:
        # Read only specified part of the file
        inetnum_file.seek(start)
        lines = inetnum_file.readlines(stop - start)      

        for group in get_inet_group(lines, "inetnum"):
            line = parse_inet_group(group)
            line = "|".join(map(str, line))
            line = line + '\n'
            parsed_file.write(line)


# ==============================================================================
# Help Methods used for all files ... 


def sort_file(file=IP2COUNTRY_DB):

    records = []

    # get records from final db
    records = read_db(file)

    # sort this list
    records.sort()

    try:

        # write it back 
        with open(file, "w", encoding='utf-8', errors='ignore') as f:
            
            for record in records:
               
               line = "|".join(map(str, record))
               line = line + "\n"
               f.write(line)

    except IOError as e:
        
        print(e)

    return records


def check_for_overlaping(file=IP2COUNTRY_DB):
    
    records = []

    # get records from final db
    records = read_db(file)

    # check if two records overlapps
    # since that the list is sorted, overlapping
    # may only occur in successive records (record[i] and record[i+1])
    nr_of_overlapps = 0
    for i in range(1, len(records)):
            
        overlapp = ip_ranges_overlapp(records[i-1], records[i])
        
        if overlapp :
            
            nr_of_overlapps = nr_of_overlapps + 1
            handle_ranges_overlapp(records[i-1], records[i], records)
              
    #print(f"{nr_of_overlapps} overlapps detected")

    try:
    
        with open(file, "w", encoding='utf-8', errors='ignore') as f:
            
            for record in records:
                
                line = "|".join(map(str, record))
                line = line + '\n'
                f.write(line)

    except IOError as e:
        
        print(e)


def handle_ranges_overlapp(record_1, record_2, records):
    
        ip_from_1  = record_1[0]
        ip_to_1    = record_1[1]
        country_1  = record_1[2].upper()
        registry_1 = record_1[3].upper()

        ip_from_2  = record_2[0]
        ip_to_2    = record_2[1]
        country_2  = record_2[2].upper()
        registry_2 = record_2[3].upper()

        # case 1
        if ip_from_1 == ip_from_2 and ip_to_1 == ip_to_2:
            
            if country_1 != country_2:
                
                if registry_1 == registry_2:

                    # DS 
                    # no cases
                    pass

                else: 
                    
                    # DD
                    # [3393687552, 3393689599, 'DE', 'RIPE']
                    # [3393687552, 3393689599, 'IN', 'APNIC']
                    pass
    
                
            else:
                
                # SD
                # no cases !
                if registry_1 != registry_2:
                    pass

                # SS
                # no cases !
                else:
                    
                    pass

        # case 2
        if ip_from_1 == ip_from_2 and ip_to_1 < ip_to_2:
            
            if country_1 != country_2:
                
                if registry_1 == registry_2:

                    # DS 
                    # [18923520, 18925567, 'HK', 'APNIC']
                    # [18923520, 18939903, 'SG', 'APNIC']     
                    pass

                else: 
                    
                    # DD
                    # [18923520, 18925567, 'HK', 'APNIC']
                    # [18923520, 18939903, 'SG', 'APNIC']
                    pass

            else:
                
                # SD
                # [2344534016, 2344538111, 'EU', 'APNIC']
                # [2344534016, 2344550399, 'EU', 'RIPE']
                if registry_1 != registry_2:
                    pass
                
                # SS
                # [3105570816, 3105571071, 'LI', 'RIPE']
                # [3105570816, 3105571839, 'LI', 'RIPE']
                else:
                    pass
            
        # case 3
        if ip_from_1 < ip_from_2 and ip_to_1 < ip_to_2 and ip_to_1 > ip_from_2:
            
            if country_1 != country_2:
                
                if registry_1 == registry_2:

                    # DS 
                    # no cases
                    pass 

                else: 
                    
                    # DD
                    # [2919208960, 2928410623, 'EU', 'RIPE']
                    # [2919235584, 2936012799, 'AU', 'APNIC']
                    pass
                    
            else:
                
                # SD
                # no cases
                if registry_1 != registry_2:
                    pass
                    
                # SS
                # [3708228916, 3708228919, 'CN', 'APNIC']
                # [3708228918, 3708228959, 'CN', 'APNIC']
                else:
                    print(record_1)
                    print(record_2)
                    print("\n")
             
                    pass
                
        # case 4
        if ip_from_1 < ip_from_2 and ip_to_1 > ip_to_2:
            
            if country_1 != country_2:
                
                if registry_1 == registry_2:

                    # DS 
                    # [16777216, 33554431, 'AU', 'APNIC']
                    # [16777472, 16777727, 'CN', 'APNIC']
                    pass 

                else: 
                    
                    # DD
                    # [3743118080, 4294967295, 'EU', 'RIPE']
                    # [3743118336, 3743119359, 'JP', 'APNIC']
                    pass
                    
            else:
                
                # SD
                # no cases
                if registry_1 != registry_2:
                    pass
                    
                # SS
                # [3114714112, 3114715135, 'RU', 'RIPE']
                # [3114714624, 3114714879, 'RU', 'RIPE']

                else:
                    pass
        
        # case 5
        if ip_from_1 < ip_from_2 and ip_to_1 == ip_to_2:
            
            if country_1 != country_2:
                
                if registry_1 == registry_2:

                    # DS 
                    # [3706253824, 3706254335, 'JP', 'APNIC']
                    # [3706254080, 3706254335, 'HK', 'APNIC']
                    pass 

                else: 
                    
                    # DD
                    # [2193830912, 2193832959, 'EU', 'RIPE']
                    # [2193831936, 2193832959, 'NZ', 'APNIC']
                    pass
                    
            else:
                
                # SD
                # no cases
                if registry_1 != registry_2:
                    pass
                    
                # SS
                # [1029832704, 1029963775, 'KR', 'APNIC', '', '']
                # [1029898240, 1029963775, 'KR', 'APNIC', 'SKBroadbandCoLtd SKBroadbandCoLtd', '']
                else:
                    pass


def ip_ranges_overlapp(record_1, record_2):

    range_end_1     = record_1[1]
    range_start_2   = record_2[0]

    # case 1: [1, 3] [2, 4] -> 2 < 3 overlapping
    # case 2: [1, 3] [3, 4] -> 3 = 3 overlapping
    return  range_end_1 >= range_start_2 
 

def merge_stripped_files():
    
    try: 
        
        # merges the delegated files into a one file 
        with open(IP2COUNTRY_DB, "wb") as f:
            
            for del_file in [ 
                    os.path.join(STRIPPED_DEL_FILE), 
                    os.path.join(STRIPPED_INET_FILE),
                    ]:

                with open(del_file, "rb") as source:

                    shutil.copyfileobj(source, f)

                    f.write(os.linesep.encode())
 
    except IOError as e:
        
        print(e)


def delete_temp_files():
    os.remove(MERGED_DEL_FILE)
    os.remove(STRIPPED_DEL_FILE)
    os.remove(MERGED_INET_FILE)
    os.remove(STRIPPED_INET_FILE)


# ==============================================================================
# Parser Entry Method 

def run_parser():

    start_time = time.time()
    print("parsing Started\n")

    print("merging delegation files ...")
    merge_del_files()          
    print("merging finished\n")

    print("parsing delegation files ...")
    parse_del_files()           
    print("parsing finished\n")

    print("merging inetnum files ...")
    merge_inet_files()
    print("merging finished\n")

    start_parse = time.time()
    print("parsing inetnum files ...")
    parse_inet_files_single()
    #parse_inet_multicore()
    print("parsing finished\n")
    end_parse = time.time()
    print("Total time for parsing was:", f'{end_parse - start_parse:.3f}', "s\n") 
 
    print("creating the final database ...")
    merge_stripped_files()
    print("sorting the final data base\n")
    
    sort_file(IP2COUNTRY_DB)
    check_for_overlaping(IP2COUNTRY_DB)
    print("finished\n")

    extract_as_json(IP2COUNTRY_DB)
    delete_temp_files()
    
    end_time = time.time()
    print("Total time needed was:", f'{end_time - start_time:.3f}', "s\n") 
    
    return 0









# Needed if for multiprocessing not to crash
if __name__ == "__main__":   
    run_parser()