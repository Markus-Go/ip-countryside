from copy import copy
from multiprocessing.reduction import duplicate
import re
import os
import shutil
import fileinput
import ipaddress
import time
from datetime import datetime
import multiprocessing as mp
from csvsort import csvsort
import csv 

from config import *;
from ip_countryside_db import *;
from ip_countryside_utilities import *;
from ip_countryside_conflicts_resolver import *; 

# ==============================================================================
# Delegation parsing methods 


def parse_del_files():

    try:

        with open(STRIPPED_DEL_FILE, "w") as f:

            for line in fileinput.input(MERGED_DEL_FILE):
                
                # get rid of all lines without "ip entry" before parsing
                if re.search(IPV4_PATTERN, line) or re.search(IPV6_PATTERN, line):

                    # actual parsing of a line is done in parse_del_line
                    record = parse_del_line(line)
                    
                    if record:

                        line = "|".join(map(str, record))
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
    mask        = record[4]
    date        = record[5]
    status      = record[6].rstrip("\n").upper()
    record_type = "D"

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
    if status == 'RESERVED' or status == "AVAILABLE":
        country = "ZZ"
    
    if not date:
        date = "19700101"

    return [range_start, range_end, country, registry, date, record_type, status]


# ==============================================================================
# Inetnum parsing methods

# Parses merged_inet file and writes it into stripped_inet_file
def parse_inet_files_single():
    
    with open(MERGED_INET_FILE, 'r', encoding='utf-8', errors='ignore') as merged, open (STRIPPED_INET_FILE, 'w', encoding='utf-8', errors='ignore') as stripped:
        
        for group in get_inet_group(merged, ["inetnum", "inet6num"]):
            
            record = parse_inet_group(group)
            
            if record:
                
                line = "|".join(map(str, record))
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
        if (line.startswith(group_by[0]) or line.startswith(group_by[1]) or data) and not line.startswith("\n"):
            
            # don't remove spaces from description lines
            if line.startswith("descr") or line.startswith("status"):
                
                line = line.replace("\n", "")
                line = line.replace("|", "")
            
            else :
                
                line = line.replace(" ","").replace("\n", "")
            
            data.append(line)
            
        # note that empty lines are used as a seperator between
        # inetnum objects. So if line starts with empty line
        # then yield the data object first and then
        # reset the object to store next object's data
        elif line.startswith("\n") and data:
            yield data
            data = []


def parse_inet_files_multicore(kb = 5):

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
        results = []
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
                               
                # get current file location
                end = fh.tell()

                # add chunk to process pool, save reference to get results
                proc = pool.apply_async(parse_inet_chunk, [MERGED_INET_FILE, cursor, end])
                results.append(proc)

                 # terminate when no more chunks are needed
                if split_size > end - cursor:
                    break
 
                # setup next chunk
                cursor = end
               

        # close and wait for pool to finish
        pool.close()
        pool.join()

        with open(STRIPPED_INET_FILE, 'w', encoding='utf-8', errors='ignore') as parsed:
           # write parsed lines to file
           for proc in results:
                chunk_result = proc.get()
                for entry in chunk_result:
                    entry_string = '|'.join(map(str, entry))
                    entry_string += '\n'
                    parsed.write(entry_string)


# process file chunk 
def parse_inet_chunk(file, start=0, stop=0):
    
    record = []
    
    with open(file, 'r', encoding='utf-8', errors='ignore') as inetnum_file:
    
        # Read only specified part of the file
        inetnum_file.seek(start)
        lines = inetnum_file.readlines(stop - start)      
    
        for group in get_inet_group(lines, ["inetnum", "inet6num"]):
            line = parse_inet_group(group)
            if line:
                record.append(line)
    
    return record


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
                value = item[1].strip()
                
                if key not in record:
                    record[key] = value
                    
                # merge all descriptio entries into one 
                elif key in record and key == "descr":
                    
                    record[key] = record[key] + " " + value 
                
                # for example: in ripe.db.inetnum some ip ranges with the description 
                # "IPV4 ADDRESS BLOCK NOT MANAGED BY THE RIPE NCC" may appear -> these 
                # don't need to be parsed at all.
                if key == "descr":

                     if ("THIS NETWORK RANGE IS NOT ALLOCATED TO APNIC"    in value.strip().upper() or
                         "NOT ALLOCATED BY APNIC"                          in value.strip().upper() or
                         "IPV4 ADDRESS BLOCK NOT MANAGED BY THE RIPE NCC"  in value.strip().upper() or
                         "TRANSFERRED TO THE ARIN REGION"                  in value.strip().upper() or                   
                         "TRANSFERRED TO THE RIPE REGION"                  in value.strip().upper() or
                         "EARLY REGISTRATION ADDRESSES"                    in value.strip().upper() or
                         "ASIA PACIFIC NETWORK INFORMATION CENTER"         in value.strip().upper() or
                         "ASIA PACIFIC NETWORK INFORMATION CENTRE"         in value.strip().upper() ):
                        return []

                # if a country line has comment, remove the comment
                if key == "country":
                    record[key] = value.split("#")[0]

                if key == "source" and value == "ripencc":
                    record[key] = "RIPE"
            
                if key == "last-modified":
                    record[key] = value

    # extract the ranges out of record
    if 'inetnum' in record:
         range = record['inetnum'].split("-")
         range_start   = int(ipaddress.ip_address(range[0]))
         range_end     = int(ipaddress.ip_address(range[1]))
    else:
        range = record['inet6num'].split("/")
        range_start = int(ipaddress.ip_address(range[0]))

        net = ipaddress.IPv6Network(range[0] + '/' + range[1], False)
        range_end = int(net.broadcast_address)
      
    if re.match(IPV4_PATTERN, range[0]):
        
        # check if ranges are not reserved
        is_reserved = not ipaddress.IPv4Network(range[0]).is_global
        if is_reserved:
            return []

    elif re.match(IPV6_PATTERN, range[0]):
        
        # check if ranges are not reserved
        is_reserved = not ipaddress.IPv6Network(range[0]).is_global
        if is_reserved:
            return []

    country       = record['country']
    registry      = record['source'].split("#")[0].upper().rstrip()
    last_modified = ""
    descr         = "" 
    status        = re.sub(' +', ' ', record['status'].split("#")[0].upper()).rstrip()
    record_type   = "I"

    if "last-modified" in record and record["last-modified"]:
        last_modified = str(datetime.strptime(record['last-modified'], "%Y-%m-%dT%H:%M:%S%fZ")) # returns YY-MM-DD HH:MM:SS
        last_modified = last_modified.split(" ")[0]     # returns YY-MM-DD 
        last_modified = last_modified.replace("-", "")  # returns YYMMDD
    else:
        last_modified = "19700101"

    if "descr" in record:
        descr = record["descr"]


    return [range_start, range_end, country, registry, last_modified, record_type, status, descr]


# ==============================================================================
# Methods used for all files ... 

def delete_temp_files():
    os.remove(MERGED_DEL_FILE)
    os.remove(STRIPPED_DEL_FILE)
    os.remove(MERGED_INET_FILE)
    os.remove(STRIPPED_INET_FILE)
    # @TODO add files that aren't needed 


def merge_files(output, files):

    try: 
        
        # merges the delegated files into a one file 
        with open(output, "wb") as f:
            
            for del_file in files:

                with open(del_file, "rb") as source:

                    shutil.copyfileobj(source, f)
                    #f.write(os.linesep.encode())
    
    except IOError as e:
        
        print(e)


def merge_successive():

    with ( open(IP2COUNTRY_DB, "r", encoding='utf-8', errors='ignore') as input, 
        open(os.path.join(DEL_FILES_DIR, "ip2country_temp.db"), "w", encoding='utf-8', errors='ignore') as output ):

        for group in get_successive_group(input):
            
            if len(group) > 1:

                ip_from     = group[0][0]
                ip_to       = group[-1][1]
                cc          = group[0][2]
                registry    = group[0][3]
                date        = group[0][4]
                type        = group[0][5]
                status      = group[0][6]
                descr       = ""

                if type == "I":
                    descr = group[0][7]

                record = [ip_from, ip_to, cc, registry, date, type, status, descr]
                
            else:

                record = group[0]

            if record:
                    
                    line = "|".join(map(str, record))
                    line = line + '\n'
                    output.write(line)
                    
    os.remove(IP2COUNTRY_DB)
    os.rename(os.path.join(DEL_FILES_DIR, "ip2country_temp.db"), IP2COUNTRY_DB)


def get_successive_group(file):

    data = []

    for line in file:

        record = read_db_record(line)

         # if data array is empty then append current record
        if len(data) == 0:

            data.append(record)
            continue

        elif (record[0] == data[-1][1] or record[0]-1 == data[-1][1]) and record[2] == data[-1][2]:
            
            data.append(record)

        else:
 
            temp = record

            # retrun current duplicate sequence to be proccessed
            yield data

            # clean data to begin with next duplicates group
            data = []

            # write the record which ends a duplicates sequence
            data.append(temp)

    # if we finished the file we still may have record in data 
    # return this one also 
    if data:

        yield data
        data = []


## ==============================================================================
## Parser Entry Method
 
def splitdb(records):

    ipv4 = []
    ipv6 = []


    for entry in records:
        if len(str(entry[0])) < 11:
            ipv4.append(entry)
        else:
            ipv6.append(entry)

    write_db(ipv4, IP2COUNTRY_DB_IPV4)
    write_db(ipv6, IP2COUNTRY_DB_IPV6)
    
    return


def run_parser(save_conflicts_param=False, multicore=True):

    start_time = time.time()
    print("parsing started\n")

    del_files = [
        os.path.join(DEL_FILES_DIR, AFRINIC['del_fname']), 
        os.path.join(DEL_FILES_DIR, LACNIC['del_fname']),
        os.path.join(DEL_FILES_DIR, ARIN['del_fname']),
        os.path.join(DEL_FILES_DIR, APNIC['del_fname']), 
        os.path.join(DEL_FILES_DIR, RIPE['del_fname'])
    ]
    merge_files(MERGED_DEL_FILE, del_files)          
     
    
    inet_files = [
        os.path.join(DEL_FILES_DIR, APNIC['inet_fname']), 
        os.path.join(DEL_FILES_DIR, RIPE['inet_fname']),
        os.path.join(DEL_FILES_DIR, APNIC['inet_fname_ipv6']),
        os.path.join(DEL_FILES_DIR, RIPE['inet_fname_ipv6'])
    ]
    merge_files(MERGED_INET_FILE, inet_files)          



    print("parsing del files ...")
    parse_del_files()           


    print("parsing inetnum files ...")
    if multicore:
          parse_inet_files_multicore()

    else:
        parse_inet_files_single()


    stripped_files = [
        os.path.join(STRIPPED_DEL_FILE), 
        os.path.join(STRIPPED_INET_FILE),
    ]
    merge_files(IP2COUNTRY_DB, stripped_files)


    print("splitting")
    split_records()

    print("sorting")
    sort_db()

    if(save_conflicts_param):
        save_conflicts()

    print("removing duplicates")
    remove_duplicates()

    merge_successive()

    print(f"checking if there are stil any overlaps in final database ... -> {records_overlap(read_db())}")


    #delete_temp_files()
    print("finished\n")

    end_time = time.time()
    print("total time needed was:", f'{end_time - start_time:.3f}', "s\n") 
    
    return 0


# Needed if for multiprocessing not to crash
if __name__ == "__main__":   

 
    # @TODOs
    # 10. Abgleich mit anderen Branchen
    # 05. Code aufräumen und Methods documentieren
    # 06. Spliting Records to find overlaps Strategy dokumentieren
    # 03. Grenzen richtig abschneiden (split_files())
    # 07. Update README.md
    # 08. Update run.ps1
    # 09. Optimize downloader script

    t = [
        
        [1,50,'DE','RIPE', '20161012', 'I', 'ALLOCATED PA', 'TELEX SRL'],
        [10,20,'ES','RIPE', '20161012', 'I', 'ASSIGNED', 'TELEX SRL'],
        [50,60,'DE','RIPE', '20161012', 'I', 'ASSIGNED', 'TELEX SRL'],

        # [20,55,'BE','RIPE', '20161012', 'I', 'TELEX SRL'],
        # [40,60,'SY','RIPE', '20161012', 'I', 'TELEX SRL'],
        # [45,55,'AT','RIPE', '20161012', 'I', 'TELEX SRL'],
        # [60,100,'TE','RIPE', '20161012', 'I', 'TELEX SRL'],
        # [70,100,'TE','RIPE', '20161012', 'I', 'TELEX SRL'],
        # [40,100,'TE','RIPE', '20161012', 'I', 'TELEX SRL'],
        # [ 17842175, 17986560, "KR", "APNIC", "20100512", "D", "ALLOCATED"]
    ]

    run_parser(multicore=True)

