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

from config import *;
from ip_countryside_db import *;
from ip_countryside_utilities import *;

import pandas as pd
import dask.dataframe as dd
import numpy as np
import dask.array as da 
import csv 

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
    status      = record[6]
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
    if status == 'reserved' or status == "available":
        country = "ZZ"
    
    if not date:
        date = "19700101"

    return [range_start, range_end, country, registry, date, record_type]


# ==============================================================================
# Inetnum parsing methods

# Parses merged_ine file and writes it into stripped_ine_file
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
            if line.startswith('descr'):
                
                line = line.replace("\n", "")
            
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
                    #print("Chunk: ", chunk , fh.tell(), '\n', s)           


                # get current file location
                end = fh.tell()

                # print("Chunksize for chunk ",chunk,  str(end - cursor))


                # add chunk to process pool, save reference to get results
                proc = pool.apply_async(parse_inet_chunk, [MERGED_INET_FILE, cursor, end])
                results.append(proc)

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

        with open(STRIPPED_INET_FILE, 'w', encoding='utf-8', errors='ignore') as parsed:
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
                # -> otherwise 5430 conflicts 
                if key == "descr":

                    if ("THIS NETWORK RANGE IS NOT ALLOCATED TO APNIC"   in value.strip().upper() or
                        "NOT ALLOCATED BY APNIC"                         in value.strip().upper() or
                        "IPV4 ADDRESS BLOCK NOT MANAGED BY THE RIPE NCC" in value.strip().upper() or
                        "TRANSFERRED TO THE ARIN REGION"                 in value.strip().upper() or
                        "TRANSFERRED TO THE RIPE REGION"                 in value.strip().upper() or
                        "EARLY REGISTRATION ADDRESSES"                   in value.strip().upper() or
                        "ASIA PACIFIC NETWORK INFORMATION CENTER"        in value.strip().upper() or
                        "ASIA PACIFIC NETWORK INFORMATION CENTRE"        in value.strip().upper() ):

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
    registry      = record['source'].split("#")[0]
    last_modified = ""
    descr         = "" 
    record_type   = "I"

    if "last-modified" in record and record["last-modified"]:
        last_modified = str(datetime.strptime(record['last-modified'], "%Y-%m-%dT%H:%M:%S%fZ")) # returns YY-MM-DD HH:MM:SS
        last_modified = last_modified.split(" ")[0]     # returns YY-MM-DD 
        last_modified = last_modified.replace("-", "")  # returns YYMMDD
    else:
        last_modified = "19700101"

    if "descr" in record:
        descr = record["descr"]

    return [range_start, range_end, country, registry, last_modified, record_type, descr]


# ==============================================================================
# Methods used for resolving conflicts/overlaps ... 


def remove_duplicates(records=[]):

    if not records:
        records = read_db()

    duplicate_indicies = get_duplicate_indicies(records)
    
    records = empty_entry_by_idx(records, duplicate_indicies)

    return records


def get_duplicate_indicies(records):

    # if list is empty return
    if not records:
        return 
      
    P = [] 

    for i in range(len(records)):
        P.append([ records[i][0], "L", records[i][2], i ])
        P.append([ records[i][1], "R", records[i][2], i ])
        
    P.sort()

    duplicate_dict = {}
    duplicate_indicies = []
    added = False

    dict_L = {}
    dict_R = {}
    current = -1

    for i in range(len(P)-1):
        
        # L: if both have same ip start and same country 
        if (P[i][0] == P[i+1][0] and P[i][1] == P[i+1][1] == "L" ):

            if not added:
                dict_L[P[i][3]] = [P[i][3]]
                added = True
                current = P[i][3]

            dict_L[current].append(P[i+1][3])

        # R: if both have same ip end and same country
        # correct keys in dict_R
        elif (P[i][0] == P[i+1][0] and P[i][1] == P[i+1][1] == "R" ):

            if not added:
                dict_R[P[i][3]] = [P[i][3]]
                added = True
                current = P[i][3]

            dict_R[current].append(P[i+1][3])

        else:
            current = -1
            added = False
    
    # iterate over only the intersection of both dictionaries
    # Since that two records may have same start but not necessarily
    # the same end
    
    for key in dict_L.keys() & dict_R.keys():

        # keep last record always
        duplicate_dict[key] = list(set(dict_L[key]).intersection(dict_R[key])) 


    for key, value in duplicate_dict.items():
        
        for i in range(len(value)):
            
            # take inetnum and not EU if exists
            if records[value[i]][2] != "EU" and records[value[i]][5] != "D":

                duplicate_dict[key].pop(i)
                break
            
            # otherwise take inetnum
            elif records[value[i]][5] != "D":

                duplicate_dict[key].pop(i)
                break
            
            # if all are delegation take first one
            else:
                duplicate_dict[key].pop()
                break
            
        # join indexes of current duplicate sequence
        duplicate_indicies.extend(duplicate_dict[key])  


    return duplicate_indicies


def get_overlaps(records):
    """
    Search for all overlaps in a list of RIA records and returns list 
    (overlaps) of overlap lists (overlap_seq). The Algorithm has a 
    complexity of O(n log(n)) known as Sweep-Line Algorithm.
    More Info: https://www.baeldung.com/cs/finding-all-overlapping-intervals    

    Arguments
    ----------
    records: list 
        List of RIA entries with the follwoing format:
        [ 
          ...
          [ip_from, ip_to, cc, registry, last-modified, record_type, description],
          ...
        ]

    Returns
    ----------
    overlaps: list
        List of lists. Each child list contains a list of RIA records
        which are involed in an overlap case 
        Each entry of overlap_seq have the following format: 
            [ ...
            ,[ 
              ...
              [ip_from, ip_to, cc, ....]
              ...
            ],
            ...
            ]

        indicies: list
            contains all indicies of records involved in overlap cases

    """

    # if list is empty return 
    if not records:
        return 

    P = [] 
    currentOpen = -1
    added = False
    overlap_seq = []
    overlap_indicies = []
    overlaps = []
    overlaps_nr = 0

    for i in range(len(records)):
        P.append([records[i][0], "L", i])
        P.append([records[i][1], "R", i])

    P.sort()

    for i in range(len(P)):
    
        if P[i][1] == "L":
            if currentOpen == -1:
                currentOpen = P[i][2]
                added = False
            else:
                index = P[i][2]
                overlap_seq.append(records[index])
                overlap_indicies.append(index)
                overlaps_nr = overlaps_nr + 1
                if not added:
                    overlap_seq.append(records[currentOpen])
                    overlap_indicies.append(currentOpen)
                    added = True
                    overlaps_nr = overlaps_nr + 1
                if records[index][1] > records[currentOpen][1]:
                    currentOpen = index
                    added = True
        else:
            if P[i][2] == currentOpen:
                currentOpen = -1
                added = False
                overlaps.append(overlap_seq)
                overlap_seq = []

    # remove empty sequences
    overlaps = [overlap_seq for overlap_seq in overlaps if overlap_seq] 
    
    # sort sublists by their length
    overlaps.sort(key=lambda seq: len(seq))

    print(f"overlaps found {overlaps_nr}\n")

    return [overlaps, overlap_indicies]


def records_overlap(records):
    """
    Checks if any two records overlaps in the given list of RIA records 
    Note that complexity  O(n log(n))

    Arguments
    ----------
    records: list 
        List of RIA entries with the follwoing format:
        [ 
          ...
          [ip_from, ip_to, ...],
          ...
        ]

    Returns
    ----------
    boolean value
        if there is any overlap in the given list

    """

    # if list is empty return
    if not records:
        return 
      
    P = [] 

    for i in range(len(records)):
        P.append([records[i][0], "L", i])
        P.append([records[i][1], "R", i])
        
    P.sort()

    for i in range(len(P)-1):
    
        if P[i][1] == "L" and P[i+1][1] != "R":
            return True
        
    return False


# ==============================================================================
# Help Methods used for all files ... 


def sort_file(file=IP2COUNTRY_DB):

    records = []

    # get records from final db
    records = read_db(file)

    # sort this list
    records.sort()

    # write sorted list back into final db
    write_db(records, file)


def delete_temp_files():
    os.remove(MERGED_DEL_FILE)
    os.remove(STRIPPED_DEL_FILE)
    os.remove(MERGED_INET_FILE)
    os.remove(STRIPPED_INET_FILE)


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


## ==============================================================================
## Parser Entry Method 


def merge_successive(records):
    
    i = 0
    end = len(records)
    
    try : 
        while i < end - 1:
            temp_list = []
            if records[i][1] + 1 == records[i+1][0] and records[i][2] == records[i + 1][2] and records[i][5] == records[i+1][5]:
                while records[i][1] + 1 == records[i+1][0]:
                    if  records[i][2] == records[i + 1][2] and records[i][5] == records[i+1][5]:
                        entry = records.pop(i+1)
                        temp_list.append(entry[1])
                    else: 
                        break
                    if i < end - 1:
                        break
                newend = max(temp_list)
                records[i][1] = newend
                end = len(records)
            else:
                i += 1

    except TypeError:
        
        print(records[i])

    return records


def merge(records):
 
    # if list is empty return
    if not records:
        return

    records.sort(key=lambda x: x[0])
 
    merged = []
    for record in records:
        # Wenn merged nicht leer ist oder der letzte ZU eintrag von merged kleiner ist als der VON vom aktuellen 
        # Füge den aktuellen zu merged hinzu
        if not merged or merged[-1][1] < record[0]:
            merged.append(record)
        else:
        # Ersetze den ZU eintrag von merged mit dem max value aus dem letzen ZU von merged und dem aktuellen ZU 
            merged[-1][1] = max(merged[-1][1], record[1])
 
    return merged


class MultiSet(object):
   
    def __init__(self, intervals):
        self.intervals = intervals
        self.events = None

    def split_ranges(self):
        self.events = []
        for start, stop, symbol, registry, host, file, description in self.intervals:
            self.events.append((start, True, stop, symbol, host, file, description))
            self.events.append((stop, False, start, symbol, host, file, description))

        def event_key(event):
            key_endpoint, key_is_start, key_other, host, file, description, _ = event
            key_order = 0 if key_is_start else 1
            return key_endpoint, key_order, key_other, host, file, description

        self.events.sort(key=event_key)

        current_set = set()
        ranges = []
        current_start = -1

        for endpoint, is_start, other, symbol, host, file, description in self.events:
            if is_start:
                if current_start != -1 and endpoint != current_start and \
                       endpoint - 1 >= current_start:
                    for s in current_set:
                        ranges.append([current_start, endpoint - 1, s[0], s[1], s[2], s[3], s[4]])
                current_set.add((symbol, registry, host, file, description))
                current_start = endpoint
            else:
                if current_start != -1 and endpoint >= current_start:
                    for s in current_set:
                        ranges.append([current_start, endpoint, s[0], s[1], s[2], s[3], s[4]])
                if not current_set == set():
                    try:
                        
                        current_set.remove((symbol, registry, host, file, description))

                    except KeyError:
                        
                        pass

                current_start = endpoint + 1

        return ranges

              
def handle_overlaps(records=[]):
    
    # get db records
    if not records:
        records = read_db()
   
    print(f"Nr. of records before overlaps deletion {len(records)}")
    
    # get all records which overlap and their corresponding indicies
    [overlaps_temp, indicies] = get_overlaps(records)
    
    records = empty_entry_by_idx(records, indicies)
    overlaps = []

    print(f"number of records after overlaps deletion {len(records)}")

    length = 0
    with open("overlaping", 'w', encoding='utf-8', errors='ignore') as f:
   
        for item in overlaps_temp:

            f.write("[\n")

            for subitem in item:

                length += 1
                line = "|".join(map(str, subitem))
                line = line + '\n'
                f.write(line)
                    

            f.write("]\n")
            

    print(f"number of overlaps before {length}")

    print("\nFor a total of: ", str(length + len(records)))

    

    first_merge_top_before = 0
    first_merge_top_after = 0
    first_dup_top_after = 0

    same_country_merge_before = 0
    same_country_merge_after = 0

    dif_country_split_before = 0
    dif_country_split_split_after = 0
    dif_country_split_dup_after = 0
    dif_country_split_after = 0

    bottom_one_entry = 0


    
    

    

    with open("overlapping_split", 'w', encoding='utf-8', errors='ignore') as f, open("overlapping_top", 'w', encoding='utf-8', errors='ignore') as b: 
    

            with open("overlapping_same_country", 'w', encoding='utf-8', errors='ignore') as m:


                for overlap_seq in overlaps_temp:
        
                    b.write("/////////////////////////////////////////////\n\nBefore merge_successive\n")
                    for lap in overlap_seq:
                        b.write(str(lap))
                        b.write("\n")
                   

           
                    for item in overlap_seq:
                        first_merge_top_before += 1

                    ######################################
                    overlap_seq = merge_successive(overlap_seq)
                    ######################################

                    b.write("\n----------------------------------------\nBefore remove_duplicates\n")
                    for lap in overlap_seq:
                        b.write(str(lap))
                        b.write("\n")


                    for item in overlap_seq:
                        first_merge_top_after += 1


                    ######################################
                    overlap_seq = remove_duplicates(overlap_seq)
                    ######################################

                    first_dup_top_after += len(overlap_seq)

                    b.write("\n----------------------------------------\n")
                    for lap in overlap_seq:
                        b.write(str(lap))
                        b.write("\n")

                    b.write("\n\n")

                
                    if len(overlap_seq) > 1:
            

                

                        if sameCountry(overlap_seq):


                            for item in overlap_seq:
                                same_country_merge_before += 1


                            m.write("//////////////////////////////////////\n\nBefore merge\n")
                            for lap in overlap_seq:
                                m.write(str(lap))
                                m.write("\n")
                            

                            ######################################
                            overlap_seq = merge(overlap_seq)
                            ######################################

                            m.write("\n----------------------------------------\nAfter merge\n")
                            for lap in overlap_seq:
                                m.write(str(lap))
                                m.write("\n")

                            m.write("\n\n")


                            same_country_merge_after += len(overlap_seq)
                    
                            ######################################
                            records.extend(overlap_seq)
                            ######################################

                        else:

                            for item in overlap_seq:
                                dif_country_split_before += 1



                            f.write("///////////////////////////////////////////////\n\nBefore split\n")
                            for lap in overlap_seq:
                                f.write(str(lap))
                                f.write("\n")
                            
                            f.write("\n----------------------------------------\nAfter split\n")





                
                            ######################################
                            overlap_seq = split_records(overlap_seq)
                            ######################################

                            
                            for lap in overlap_seq:
                                f.write(str(lap))
                                f.write("\n")
                            

                            f.write("\n----------------------------------------\nAfter remove_duplicate\n")

                            dif_country_split_split_after += len(overlap_seq)

                            ######################################
                            overlap_seq = remove_duplicates(overlap_seq)
                            ######################################

                            for lap in overlap_seq:
                                f.write(str(lap))
                                f.write("\n")
                            

                            f.write("\n----------------------------------------\nAfter merge_successive\n")
                            



                            dif_country_split_dup_after += len(overlap_seq)

                            ######################################
                            overlap_seq = merge_successive(overlap_seq)
                            ######################################
                            for lap in overlap_seq:
                                f.write(str(lap))
                                f.write("\n")
                            
                            

                            f.write("\n\n")

                            dif_country_split_after += len(overlap_seq)

                            ######################################
                            overlaps.extend(overlap_seq)
                            ######################################


                    else:
                        bottom_one_entry += 1
                        ######################################
                        records.append(overlap_seq[0])
                        ######################################



    print(f"first_merge_top_before number of overlaps going into handle {first_merge_top_before}")
    print(f"first_merge_top_after number of overlaps AFTER top merge_successive {first_merge_top_after}")
    print(f"first_dup_top_after number of overlaps AFTER top duplicate removal {first_dup_top_after}")


    print('\n\n')

    print(f"same_country_merge_before number of overlaps going into same country merge dumb {same_country_merge_before}")
    print(f"same_country_merge_after number of overlaps AFTER going into same country merge dumb {same_country_merge_after}")

    print('\n\n')

    print(f"dif_country_split_before number of overlaps going into the split method {dif_country_split_before}")
    print(f"dif_country_split_split_after number of overlaps AFTER split method  {dif_country_split_split_after}")
    print(f"dif_country_split_dup_after number of overlaps AFTER duplicate method {dif_country_split_dup_after}")
    print(f"dif_country_split_after number of overlaps AFTER merge_successive {dif_country_split_after}")
    
    print('\n\n')

    print(f"bottom_one_entry number of overlaps that are not more than one bottom {bottom_one_entry}")


    print('\n\n')

    print("A total number of records in: ", str())





    print(f"len(records) number of records after handling {len(records)}")

    print(f"len(overlaps) number of solved overlaps after handling {len(overlaps)}")

    print("len(records) + len(overlaps) Number of final records: ", str(len(records) + len(overlaps)))

    


    return [records, overlaps]


def sameCountry(record):
    
    country = record[0][2]
    
    for r in record:
    
        if not country == r[2]:
    
            return False
    
    return True


def split_records(records=[]):

    if not records:
        records = read_db()

    P = []
    data = {}
    queue = set()
    
    # generate start and end edges for each record
    for i in range(len(records)):
        
        P.append( (records[i][0], "L", i) )
        P.append( (records[i][1], "R", i) )
    

    P = sorted(
        P, 
        key=lambda x:
            (
                x[0], x[1], x[2]) 
                if (x[1] == "L") 
                else (x[0], x[1], -x[2])
            )


    record_split = []

    for i in range(len(P)):
        
        current = P[i]

        # if current index is not in dictionary
        # then this is a new record to be processed
        if not current[2] in data: 

            # save index of the record in dict
            data[current[2]] = set()
            data[current[2]].add(current[0])

            # if loop at first record save its index to the queue 
            # and jump to next item in P 
            if i == 0:
                queue.add(current[2])
                continue
        
            else:
                
                # -> for each record's index in the queue
                # -> save a left edge (current[0]) 
                #    to split the affected records at this point later
                # worst case -> queue = [1,2,3,4,5,6,7,8,9, ...]
                # meaning records are nested successively (wount be the case)
                for idx in queue:

                    data[idx].add(current[0])

                queue.add(current[2])

        # if current index is in dictionary
        # then we arrived the right edge of a record
        else:

            # -> for each record's index in the queue
            # -> save right edge (current[0]) 
            #    to split the affected records at this point later
            # worst case -> queue = [1,2,3,4,5,6,7,8,9, ...]
            # meaning records are nested successively (wount be the case)
            for idx in queue:

                data[idx].add(current[0])

            # if we arrived at the right edge of current then 
            # we processed all overlap edges within this record 
            if current[1] == "R" and current[2] in data and current[2] in queue :
                
                # remove record index from queue
                queue.remove(current[2])

                # add right edge for current element before deleting 
                data[current[2]].add(records[current[2]][1])
                
                # split a db record by given list of edges 
                record_split.extend(split_records_helper(records, [current[2], list(data[current[2]])]))
                
                # delete this record from data to save memory
                data.pop(current[2])

    record_split.sort()
    return record_split


def split_records_helper(records, record):

    idx = int(record[0])

    # sort start and end points ... 
    record[1].sort()

    cc = records[idx][2]
    registry = records[idx][3]
    last_modified = records[idx][4]
    record_type = records[idx][5]
    description = records[idx][6]
       
    ret_value = list()
    for i in range(len(record[1])-1):

        start = record[1][i]
        end = record[1][i+1]
        
        new_record = [start, end, cc, registry, last_modified, record_type, description]

        ret_value.append(new_record)
        
    
    return ret_value


def run_parser():

    start_time = time.time()
    print("parsing started\n")

    del_files = [
        os.path.join(DEL_FILES_DIR, AFRINIC['del_fname']), 
        os.path.join(DEL_FILES_DIR, LACNIC['del_fname']),
        os.path.join(DEL_FILES_DIR, ARIN['del_fname']),
        os.path.join(DEL_FILES_DIR, APNIC['del_fname']), 
        os.path.join(DEL_FILES_DIR, RIPE['del_fname'])
    ]
    #merge_files(MERGED_DEL_FILE, del_files)          
     
    
    inet_files = [
        os.path.join(DEL_FILES_DIR, APNIC['inet_fname']), 
        os.path.join(DEL_FILES_DIR, RIPE['inet_fname']),
        os.path.join(DEL_FILES_DIR, APNIC['inet_fname_ipv6']),
        os.path.join(DEL_FILES_DIR, RIPE['inet_fname_ipv6'])
    ]
    #merge_files(MERGED_INET_FILE, inet_files)          

    #print("parsing del files ...")
    #parse_del_files()           

    #print("parsing inetnum files ...")
    ##parse_inet_files_single()
    #parse_inet_files_multicore()

    stripped_files = [
        os.path.join(STRIPPED_DEL_FILE), 
        os.path.join(STRIPPED_INET_FILE),
    ]
    merge_files(IP2COUNTRY_DB, stripped_files)


    #shutil.copyfile(IP2COUNTRY_DB, TRACE_FILE)


    records = remove_duplicates()

    [records, overlaps] = handle_overlaps()

    records.extend(overlaps)

  

    print(f"checking if there are stil any overlaps in final database ... -> {records_overlap(records)}")
    
    write_db(records, IP2COUNTRY_DB)

    #delete_temp_files()
    print("finished\n")

    end_time = time.time()
    print("total time needed was:", f'{end_time - start_time:.3f}', "s\n") 
    
    return 0


def restoreNetmasks(file = IP2COUNTRY_DB):
    pass




# Needed if for multiprocessing not to crash
if __name__ == "__main__":   

    #run_parser()

    #result = traceIP("2.59.10.0")

    #for r in result:
    #    print(r)
    
    #write_db(converttoNetwork(read_db()))
    
