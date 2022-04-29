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
# Inetnum Pars

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
            if line.startswith("descr") or line.startswith("status"):
                
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
    
        #print(*lines, '\n----------------------------------------\n')
    
        for group in get_inet_group(lines, ["inetnum", "inet6num"]):
            line = parse_inet_group(group)
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
    registry      = record['source'].split("#")[0].upper()
    last_modified = ""
    descr         = "" 
    status        = record['status'] 
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
# Methods used for resolving conflicts/overlaps ... 

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


    with open(IP2COUNTRY_DB, "w", encoding='utf-8', errors='ignore') as f:

        for i in range(len(P)):
            
            current = P[i]

            # if current index is not in dictionary
            # then this is a new record to be processed
            if not current[2] in data: 

                # save index of the record 
                data[current[2]] = set()
                data[current[2]].add(current[0])

                # if loop at first record save its index to the queue 
                # and jump to next item in P 
                if i == 0:
                    queue.add(current[2])
                    continue
            
                else:
                    
                    # save edge of current for all records in queue 
                    # -> for each record with it's index within the queue
                    # -> save edge of overlaping (current[0]) -> to split
                    # the record at this point later
                    # worst case -> queue = [1,2,3,4,5,6,7,8,9, ...]
                    # meaning records are nested successively (wount be the case)
                    for idx in queue:

                        data[idx].add(current[0])

                    queue.add(current[2])

            # if current index is in dictionary
            # then we arrived the right edge of a record
            else:

                # save edge of current for all records in queue 
                # -> for each record with it's index within the queue
                # -> save edge of overlaping (current[0]) -> to split
                # the record at this point later
                for idx in queue:

                    data[idx].add(current[0])

                # if we arrived at the right edge of current then 
                # we processed all overlaps with 'current' 
                if current[1] == "R" and current[2] in data and current[2] in queue :
                    
                    # remove record index from queue
                    queue.remove(current[2])

                    # add right edge for current element before deleting 
                    data[current[2]].add(records[current[2]][1])
                    
                    # split a db record by given list of edges 
                    split_records_helper(records, [current[2], list(data[current[2]])], f)
                    
                    # delete this record from data to save memory
                    data.pop(current[2])
      

def split_records_helper(records, record, f):

    idx = int(record[0])

    # sort start and end points ... 
    record[1].sort()

    cc = records[idx][2]
    registry = records[idx][3]
    last_modified = records[idx][4]
    record_type = records[idx][5]
    status = records[idx][6]
    description = ""

    if len(record)-1 > 6:
        description = records[idx][7]
        
    for i in range(len(record[1])-1):

        start = record[1][i]
        end = record[1][i+1]
        
        new_record = [start, end, cc, registry, last_modified, record_type, status, description]

        line = "|".join(map(str, new_record))
        line = line + '\n'
        f.write(line)


def save_inetnum_conflicts():

    with open(IP2COUNTRY_DB, 'r', encoding='utf-8', errors='ignore') as f, open(INET_CONFLICTS, 'w', encoding='utf-8', errors='ignore') as output:

        # groups is a sequence of duplicate records    
        for group in get_dupplicate_group(f):

            inetnum_country_conflicts = save_inetnum_conflicts_helper(group) 

            if inetnum_country_conflicts:
                
                output.write(">>>>>>>>>>>>>>>>>>>>>>>>>>>\n")

                for record in inetnum_country_conflicts:
                    
                    if record:

                        line = "|".join(map(str, record))
                        line = line + '\n'
                        output.write(line)

                output.write("<<<<<<<<<<<<<<<<<<<<<<<<<<<\n")


def save_inetnum_conflicts_helper(group):

    # remove euql records
    data = {}
    record = []

    inet_group = []
    del_group = []

    for record in group:

        if record[5] == "I":
            inet_group.append(record)
        elif record[5] == "D":
            del_group.append(record)
        else: 
            print("There may be records which doesn't have any registry assigned. Please check the data!")

    # remove delegation if we have inetnum records
    if inet_group and del_group:
        del_group = []

    if inet_group:
        data = group_records_by_country(inet_group)

    if del_group:
        data = group_records_by_country(del_group)

    # remove EU records if thery are not the only countries we have
    if "EU" in data.keys() and len(data) > 1:
        data.pop("EU")

    # if we only have conflicts in countries
    if len(data) > 1:

        countries = list(data.keys())
        result = []

        if len(countries) > 1:

            for country in countries:
                result.extend(data[country])

            return result

    return []


def remove_duplicates():

    with open(IP2COUNTRY_DB, 'r', encoding='utf-8', errors='ignore') as f:

        # non overlaped records list
        records = []

        # groups is a sequence of duplicate records    
        for group in get_dupplicate_group(f):

            # solve this duplicate and append it to records
            records.append(remove_duplicates_helper(group))
            
    write_db(records)


def get_dupplicate_group(file):

    # data is s duplicates sequence in the splitted db file 
    # note all duplicates will be successive (sorted db file)
    # for example a duplicate group may be like this:
    # 10|20|DE|RIPE|20161012|I|TELEX SRL
    # 10|20|AU|RIPE|20161012|I|TELEX SRL
    # 10|20|RB|RIPE|20161012|I|TELEX SRL
    data = []
    
    for line in file:

        record = read_db_record(line)

        # if data array is empty then append current record
        if len(data) == 0:

            data.append(record)
            continue
        
        # otherwise check if we're still reading duplicate group
        elif record[0] == data[0][0] and record[1] == data[0][1]:
            
            data.append(record)

        # keep track of current record, yield group and
        # proccess further
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


def remove_duplicates_helper(group):
    
    # remove euql records
    data = {}
    record = []

    inet_group = []
    del_group = []

    for record in group:

        if record[5] == "I":
            inet_group.append(record)
        elif record[5] == "D":
            del_group.append(record)
        else: 
            print("There may be records which doesn't have any registry assigned. Please check the data!")

    # remove delegation if we have inetnum records
    if inet_group and del_group:
        del_group = []

    if inet_group:
        data = group_records_by_country(inet_group)

    if del_group:
        data = group_records_by_country(del_group)

    # remove EU records if thery are not the only countries we have
    if "EU" in data.keys() and len(data) > 1:
        data.pop("EU")

    # if we only have one country left then lets take any record
    if len(data) == 1:

        records_list = data[list(data.keys())[0]]
        
        # @TODO 
        # we can take one with longer description
        # proiority is low at the mean time ... 
        return records_list[0]

    # if we still have multiple countries we need to handle
    else:

        pass


def group_records_by_country(records):

    data = {}

    # categorize data based on country
    for record in records:

        # add record if country not in dict already 
        if not record[2] in data:    
            
            # add country category 
            data[record[2]] = [record]

        # otherwise just append the record to the correspnding category
        else:

            data[record[2]].append(record)

    return data


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


def merge_files(output, input_files):

    try: 
        
        # merges the delegated files into a one file 
        with open(output, "wb") as f:
            
            for file in input_files:

                with open(file, "rb") as source:

                    shutil.copyfileobj(source, f)

                    f.write(os.linesep.encode())
    
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
            j = i
            if records[i][1] + 1 == records[j+1][0] and records[i][2] == records[i + 1][2]:
                while records[i][1] + 1 == records[j+1][0]:
                    if  records[i][2] == records[i + 1][2]:
                        entry = records.pop(j+1)
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


def run_parser(save_inet_conflicts=False):

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
    #parse_inet_files_single()
    #parse_inet_files_multicore()


    stripped_files = [
        os.path.join(STRIPPED_DEL_FILE), 
        os.path.join(STRIPPED_INET_FILE),
    ]
    merge_files(IP2COUNTRY_DB, stripped_files)

    split_records()

    # @TODO Error in Encoding 
    # csvsort(IP2COUNTRY_DB,  [0], delimiter="|", max_size=1000, has_header=False, quoting=csv.QUOTE_ALL, show_progress=True, encoding="utf-8") 
    # takes a lot of memory !!
    sort_file()

    if(save_inet_conflicts):
        save_inetnum_conflicts()

    remove_duplicates()

    #print(f"checking if there are stil any overlaps in final database ... -> {records_overlap()}")

    #delete_temp_files()
    print("finished\n")

    end_time = time.time()
    print("total time needed was:", f'{end_time - start_time:.3f}', "s\n") 
    
    return 0


# Needed if for multiprocessing not to crash
if __name__ == "__main__":   

    #run_parser()

     
    # @TODOs
    # 01. sort method optimieren
    # 02. grenzen (split_files())
    # 03. mergen
    # 04. remove_duplicates -> Wird nicht richtig gelöst 
    #       1|10|RU|RIPE|20161012|I|TELEX SRL
    #       1|10|DE|RIPE|20161012|D|TELEX SRL
   
    t = [
        
        [1,20,'DE','RIPE', '20161012', 'I', 'TELEX SRL'],
        [1,20,'RE','RIPE', '20161012', 'I', 'TELEX SRL'],
        [1,20,'EU','RIPE', '20161012', 'I', 'TELEX SRL'],
        [1,30,'AU','RIPE', '20161012', 'I', 'TELEX SRL'],
        [15,25,'NL','RIPE', '20161012', 'I', 'TELEX SRL'],
        [20,55,'BE','RIPE', '20161012', 'I', 'TELEX SRL'],
        [40,60,'SY','RIPE', '20161012', 'I', 'TELEX SRL'],
        [45,55,'AT','RIPE', '20161012', 'I', 'TELEX SRL'],
        [60,100,'TE','RIPE', '20161012', 'I', 'TELEX SRL'],
        [70,100,'TE','RIPE', '20161012', 'I', 'TELEX SRL'],
        [40,100,'TE','RIPE', '20161012', 'I', 'TELEX SRL'],

    ]

    # remove_duplicates()

    stripped_files = [
        os.path.join(STRIPPED_DEL_FILE), 
        os.path.join(STRIPPED_INET_FILE),
    ]
    merge_files(IP2COUNTRY_DB, stripped_files)

    split_records()
    sort_file()

    save_inetnum_conflicts()
