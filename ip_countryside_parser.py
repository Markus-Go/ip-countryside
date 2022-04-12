import re
import os
import shutil
import fileinput
import ipaddress
import time
from datetime import datetime
#import locationtagger
import multiprocessing as mp

from config import *;
from ip_countryside_db import *;
from ip_countryside_utilities import *;

# Release 0.9.0 coming soon ... 

# @TODO handle_ranges_overlapp() have now a structure to modify the data                    # Aufwand 5
# base records. (The PDF can be helpful)           
# Info: we need to know which entries should be removed. 

# @TODO Bugfix in parse_inet_group() -> see todo there ...                                  # Auufwand 5 

# @TODO comment and write description for each method & clean code                          # Aufwand 5 

# @TODO later add parameters for the command line interpreter (cli)                         # Aufwand 5

# @TODO Flussdiagramm vom Parser erstellen                                                  # Aufwand 5

# @TODO MAX MindDB API importieren zum testen und anschauen benutzen                        # Aufwand 8
# wie sie die Objekte einer Datenbank aufbauen ....

# @TODO Speed up parsing process of inetnum files                                           # Aufwand 13/20
# Parsing should be done by multiple threads

# @TODO add city information (when available) to the method parse_inet parse_inet_group     # Aufwand 21


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
        if (line.startswith(group_by) or data) and not line.startswith("\n"):
            
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
        #print(*lines, '\n----------------------------------------\n')
        for group in get_inet_group(lines, "inetnum"):
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
                        "EARLY REGISTRATION ADDRESSES"                   in value.strip().upper()):
                        return []
                    
                # if a country line has comment, remove the comment
                if key == "country":
                    record[key] = value.split("#")[0]

                if key == "source" and value == "ripencc":
                    record[key] = "RIPE"
            
                if key == "last-modified":
                    record[key] = value

    # extract the ranges out of record
    range = record['inetnum'].split("-")
    
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


    range_start   = int(ipaddress.ip_address(range[0]))
    range_end     = int(ipaddress.ip_address(range[1]))
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


def handle_overlaps():

    # get db records
    records = read_db()

    # get all records which overlap and their corresponding indicies
    [overlaps, indicies] = extract_overlaps(records)

    # @TODO -> (delete); temporary (only for debugging) write overlap sequences into a file 
    with open(os.path.join(DEL_FILES_DIR, "overlaping"), "w", encoding='utf-8', errors='ignore') as f:
    
        for overlap_seq in overlaps:
            f.write("[\n")
            for record in overlap_seq:
                f.write(str(record))
                f.write("\n")

            f.write("]\n")

    # need to remove overlapps from the db
    delete_by_idx_from_list(records, indicies)

    # write back the clean list into db file
    write_db(records)

    # @TODO 
    # see method resolve_overlaps()
    resolve_overlaps(overlaps)

    # @TODO
    # write the clean version of records into the 
    # data base file again ...


def extract_overlaps(records):
    """
    Search for all overlaps in a list of RIA records and returns list 
    (overlaps) of lists (overlap_seq) of these overlaps. The Algorithm 
    has a complexity of O(n log(n)) known as Sweep-Line Algorithm.
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
        List of lists. Represents all found overlaps
        Each entry of overlap_seq have the following format: 
            [ 
              ...
              [ip_from, ip_to, cc, ....]
              ...
            ]
        
        indicies: list
            contains indicies of overlapped records

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
        P.append([records[i][0], "L", i, records[i]])
        P.append([records[i][1], "R", i, records[i]])

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
    
    overlaps.sort(key=lambda seq: len(seq))

    print(f"overlaps found {overlaps_nr}\n")

    return [overlaps, overlap_indicies]


def resolve_overlaps(overlaps):

    overlaps_tmp = [] 
    
    # need to solve overlaps for each overalp sequence .... 
    # as long as ther are overlaps in the sequence ->  complexity O(n²)
    for overlap_seq in overlaps:

        #while(records_overlaps(overlap_seq)):

            overlap_seq = [resolve_overlaps_helper(overlap_seq)]

            overlaps_tmp.extend(overlap_seq)    


    # @TODO -> (delete); temporary (only for debugging) write overlap sequences after removing overlapps 
    with open(os.path.join(DEL_FILES_DIR, "overlaping_left"), "w", encoding='utf-8', errors='ignore') as left, open(os.path.join(DEL_FILES_DIR, "overlaping_solved"), "w", encoding='utf-8', errors='ignore') as solved:
        
        nr_overlaps = 0
        for overlap_seq in overlaps_tmp:
            
            if(records_overlaps(overlap_seq)):

                left.write("[\n")
                
                for record in overlap_seq:
                    nr_overlaps = nr_overlaps + 1 
                    left.write(str(record))
                    left.write("\n")

                left.write("]\n")
            
            else:

                solved.write("[\n")
                
                for record in overlap_seq:
                    solved.write(str(record))
                    solved.write("\n")

                solved.write("]\n")
            
        print(f"overlaps left {nr_overlaps}")
        

def resolve_overlaps_helper(overlap_seq):
    
    records = []

    for i in range(len(overlap_seq)-1):

        # case 1 start and end same
        if (overlap_seq[i][0] == overlap_seq[i+1][0] and
           overlap_seq[i][1] == overlap_seq[i+1][1]):
               
            # check for inetnum
            if(overlap_seq[i][5] == 'I'):       
                records.append(overlap_seq[i])

            else :
                records.append(overlap_seq[i+1])

        # case 2 start same, second end is greater
        elif (overlap_seq[i][0] == overlap_seq[i+1][0] and
             overlap_seq[i][1] < overlap_seq[i+1][1]):

            # check for same country
            if overlap_seq[i][2] == overlap_seq[i+1][2]:

                # check for inetnum
                if(overlap_seq[i][5] == 'I'):       
                    records.append(overlap_seq[i])

                else :
                    records.append(overlap_seq[i+1])

            else:

                # set start from secont to end of first
                overlap_seq[i+1][0] = overlap_seq[i][1] + 1

                records.append(overlap_seq[i])
                records.append(overlap_seq[i+1])

        # case 3 second start is greater, second end is greater
        elif (overlap_seq[i][0] < overlap_seq[i+1][0] and
             overlap_seq[i][1] < overlap_seq[i+1][1]):

             # check for same country
            if overlap_seq[i][2] == overlap_seq[i+1][2]:

                if overlap_seq[i][6] == overlap_seq[i+1][6]:

                    overlap_seq[i][1] = overlap_seq[i+1][1]

                    records.append(overlap_seq[i])

                # check for inetnum
                elif(overlap_seq[i+1][5] == 'I'):

                    overlap_seq[i][1] = overlap_seq[i+1][0] - 1

                    records.append(overlap_seq[i])
                    records.append(overlap_seq[i+1])

                else :

                    overlap_seq[i+1][0] = overlap_seq[i][1] + 1

                    records.append(overlap_seq[i])
                    records.append(overlap_seq[i+1])

            else:

                if(overlap_seq[i][5] == 'I'):

                    overlap_seq[i+1][0] = overlap_seq[i][1] + 1

                    records.append(overlap_seq[i])
                    records.append(overlap_seq[i+1])

                else: 

                    overlap_seq[i][1] = overlap_seq[i+1][0] - 1

                    records.append(overlap_seq[i])
                    records.append(overlap_seq[i+1])
            

        # case 4 second start is greater, second end is smaler
        elif (overlap_seq[i][0] < overlap_seq[i+1][0] and
             overlap_seq[i][1] > overlap_seq[i+1][1]):

            #check country same
            if overlap_seq[i][2] == overlap_seq[i+1][2]:

                if overlap_seq[i][6] == overlap_seq[i+1][6]:

                    records.append(overlap_seq[i])
                
                else:

                    temp = overlap_seq[i]
                    temp[0] = overlap_seq[i+1][1] + 1
                    temp[1] = overlap_seq[i][1]
                    overlap_seq[i][1] = overlap_seq[i+1][0] - 1

                    records.append(overlap_seq[i])
                    records.append(overlap_seq[i+1])
                    records.append(temp)

            else:
                print("NO CASES")

        # case 5 second start is greater, end same
        elif (overlap_seq[i][0] < overlap_seq[i+1][0] and
             overlap_seq[i][1] == overlap_seq[i+1][1]):

            #check country same
            if overlap_seq[i][2] == overlap_seq[i+1][2]:

                if overlap_seq[i][6] == overlap_seq[i+1][6]:

                    records.append(overlap_seq[i])

            else:

                overlap_seq[i][1] = overlap_seq[i+1][0] - 1

                records.append(overlap_seq[i])
                records.append(overlap_seq[i+1])

        # case 6 start same, first end is greater
        elif (overlap_seq[i][0] == overlap_seq[i+1][0] and
             overlap_seq[i][1] > overlap_seq[i+1][1]):

            # check for same country
            if overlap_seq[i][2] == overlap_seq[i+1][2]:

                # check for inetnum
                if(overlap_seq[i+1][5] == 'I'):       
                    records.append(overlap_seq[i+1])

                else :
                    records.append(overlap_seq[i])

            else:

                # set start from secont to end of first
                overlap_seq[i][0] = overlap_seq[i+1][1] + 1

                records.append(overlap_seq[i])
                records.append(overlap_seq[i+1])

        # case 7 first start is greater, end same
        elif (overlap_seq[i][0] > overlap_seq[i+1][0] and
             overlap_seq[i][1] == overlap_seq[i+1][1]):

            #check country same
            if overlap_seq[i][2] == overlap_seq[i+1][2]:

                if overlap_seq[i][6] == overlap_seq[i+1][6]:

                    records.append(overlap_seq[i+1])

            else:

                overlap_seq[i+1][1] = overlap_seq[i][0] - 1

                records.append(overlap_seq[i])
                records.append(overlap_seq[i+1])

        # case 8 second start is smaler, second end is greater
        elif (overlap_seq[i][0] > overlap_seq[i+1][0] and
             overlap_seq[i][1] < overlap_seq[i+1][1]):

            #check country same
            if overlap_seq[i][2] == overlap_seq[i+1][2]:

                if overlap_seq[i][6] == overlap_seq[i+1][6]:

                    records.append(overlap_seq[i+1])
                
                else:

                    temp = overlap_seq[i+1]
                    temp[0] = overlap_seq[i][1] + 1
                    temp[1] = overlap_seq[i+1][1]
                    overlap_seq[i+1][1] = overlap_seq[i][0] - 1

                    records.append(overlap_seq[i])
                    records.append(overlap_seq[i+1])
                    records.append(temp)

            else:
                print("NO CASES")
        
        # case 9 first start is greater, first end is greater
        elif (overlap_seq[i][0] > overlap_seq[i+1][0] and
             overlap_seq[i][1] > overlap_seq[i+1][1]):

             # check for same country
            if overlap_seq[i][2] == overlap_seq[i+1][2]:

                if overlap_seq[i][6] == overlap_seq[i+1][6]:

                    overlap_seq[i+1][1] = overlap_seq[i][1]

                    records.append(overlap_seq[i+1])

                # check for inetnum
                elif(overlap_seq[i][5] == 'I'):

                    overlap_seq[i+1][1] = overlap_seq[i][0] - 1

                    records.append(overlap_seq[i])
                    records.append(overlap_seq[i+1])

                else :

                    overlap_seq[i][0] = overlap_seq[i+1][1] + 1

                    records.append(overlap_seq[i])
                    records.append(overlap_seq[i+1])

            else:

                if(overlap_seq[i+1][5] == 'I'):

                    overlap_seq[i][0] = overlap_seq[i+1][1] + 1

                    records.append(overlap_seq[i])
                    records.append(overlap_seq[i+1])

                else: 

                    overlap_seq[i+1][1] = overlap_seq[i][0] - 1

                    records.append(overlap_seq[i])
                    records.append(overlap_seq[i+1])

        else:
            # @TODO ...
            print("ELSE")
            records.append(overlap_seq[i])

    return records


def records_overlaps(records):
    """
    Checks if any two records overlaps in the given list of RIA records 
    Note that complexity  O(n log(n))

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


def merge_stripped_files():
    
    try: 
        
        # merges the stripped files into a one file (final database)
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


def sort_file(file=IP2COUNTRY_DB):

    records = []

    # get records from final db
    records = read_db(file)

    # sort this list
    records.sort()

    # write sorted list back into final db
    write_db(records)


def delete_temp_files():
    os.remove(MERGED_DEL_FILE)
    os.remove(STRIPPED_DEL_FILE)
    os.remove(MERGED_INET_FILE)
    os.remove(STRIPPED_INET_FILE)


## ==============================================================================
## Parser Entry Method 


def run_parser():

    start_time = time.time()
    print("parsing started\n")

    print("parsing del files ...")
    merge_del_files()          
    parse_del_files()           

    print("parsing inetnum files ...")
    merge_inet_files()
    #parse_inet_files_single()
    parse_inet_files_multicore()
    
    merge_stripped_files()
    
    print("resolving overlaps ...")
    handle_overlaps()

    # delete_temp_files()
    print("finished\n")

    end_time = time.time()
    print("total time needed was:", f'{end_time - start_time:.3f}', "s\n") 
    
    return 0


def merge_following(records):

    # if list is empty return
    if not records:
        return 

    P = [] 

    for i in range(len(records)):
        P.append([records[i][0], "L", i, i])
        P.append([records[i][1], "R", i,i])

    P.sort()

    i = 0 
    while i < len(P)-1:

        # Check if R is followed by L
        if (P[i][1] == 'R' and P[i+1][1] == 'L'):
            # Check if distance is 1  
            if P[i][0] + 1 == P[i+1][0]:

                P[i] = [P[i+2][0],'R', P[i][2], P[i+1][2]]
                index = P[i+1][2]
                j = i + 1
                P.pop(j)
                while P[j][2] != index:
                    j += 1
                P.pop(j)
            else: 
                i+= 1
        else: 
            i += 1
    
    merged_record = []
    index_list = []
    for i in range(len(P)-1):
        curr_index = P[i][2]
        if curr_index not in index_list:
            index_list.append(curr_index)
            j = i + 1
            while curr_index != P[j][2]:
                j += 1
            if P[j][3] == P[j][2]:
                merged_record.append([P[i][0], P[j][0], records[curr_index][2], records[curr_index][3], records[curr_index][4],
                                      records[curr_index][5], records[curr_index][6]])
            else:
                merged_record.append([P[i][0], P[j][0], records[curr_index][2], records[curr_index][3], records[curr_index][4],
                                      records[curr_index][5], ""])

    return merged_record


    
def bigrange(records):

    # if list is empty return
    if not records:
        return 

    P = [] 

    for i in range(len(records)):
        P.append([records[i][0], "L", i])
        P.append([records[i][1], "R", i])

    P.sort()



    if P[0][2] == P[len(P)-1][2]:
        index = P[0][2]
        return [P[0][0], P[len(P)-1][0], records[index][2], records[index][3], records[index][4], records[index][5], ""]
    else:
        return records
        

    



    


# Needed if for multiprocessing not to crash
if __name__ == "__main__":   
     #run_parser()
        
     l = [
            [771751936, 771817471, 'RU', 'RIPE', '20100810', 'D', ''],
            [771751936, 771817471, 'RU', 'RIPE', '20100810', 'D', ''],
            [771751936, 771760127, 'RU', 'RIPE', '20110119', 'I', 'CJSC "ER-Telecom" Company" Samara Samara, Russia PPPoE individual customers network'],
            [771760128, 771762175, 'RU', 'RIPE', '20110119', 'I', 'CJSC "ER-Telecom" Company" Samara Samara, Russia PPPoE individual customers network'],
            [771762176, 771764223, 'RU', 'RIPE', '20110119', 'I', 'CJSC "ER-Telecom" Company" Samara Samara, Russia PPPoE individual customers network'],
            [771764224, 771768319, 'RU', 'RIPE', '20110119', 'I', 'CJSC "Company "ER-Telecom" Samara Samara, Russia PPPoE individual customers network'],
            [771768320, 771784703, 'RU', 'RIPE', '20110119', 'I', 'CJSC "ER-Telecom" Company" Samara Samara, Russia PPPoE individual customers network'],
            [771784704, 771786751, 'RU', 'RIPE', '20110119', 'I', 'CJSC "ER-Telecom" Company" Samara Samara, Russia PPPoE individual customers network'],
            [771786752, 771788799, 'RU', 'RIPE', '20110119', 'I', 'CJSC "ER-Telecom" Company" Samara Samara, Russia PPPoE individual customers network'],
            [771788800, 771790847, 'RU', 'RIPE', '20110119', 'I', 'CJSC "ER-Telecom" Company" Samara Samara, Russia PPPoE individual customers network'],
            [771790848, 771792895, 'RU', 'RIPE', '20110119', 'I', 'CJSC "ER-Telecom" Company" Samara Samara, Russia PPPoE individual customers network'],
            [771792896, 771794943, 'RU', 'RIPE', '20110119', 'I', 'CJSC "ER-Telecom" Company" Samara Samara, Russia PPPoE individual customers network'],
            [771794944, 771796991, 'RU', 'RIPE', '20110119', 'I', 'CJSC "ER-Telecom" Company" Samara Samara, Russia PPPoE individual customers network'],
            [771796992, 771799039, 'RU', 'RIPE', '20110119', 'I', 'CJSC "ER-Telecom" Company" Samara Samara, Russia PPPoE individual customers network'],
            [771799040, 771801087, 'RU', 'RIPE', '20110119', 'I', 'CJSC "ER-Telecom" Company" Samara Samara, Russia PPPoE individual customers network'],
            [771801088, 771803135, 'RU', 'RIPE', '20110119', 'I', 'CJSC "ER-Telecom" Company" Samara Samara, Russia PPPoE individual customers network'],
            [771803136, 771805183, 'RU', 'RIPE', '20110119', 'I', 'CJSC "ER-Telecom" Company" Samara Samara, Russia PPPoE individual customers network'],
            [771805184, 771807231, 'RU', 'RIPE', '20110119', 'I', 'CJSC "ER-Telecom Holding" Samara branch Samara, Russia PPPoE individual customers network'],
            [771807232, 771809279, 'RU', 'RIPE', '20110119', 'I', 'CJSC "ER-Telecom Holding" Samara branch Samara, Russia PPPoE individual customers network'],
            [771809280, 771811327, 'RU', 'RIPE', '20110119', 'I', 'CJSC "ER-Telecom Holding" Samara branch Samara, Russia PPPoE individual customers network'],
            [771811328, 771813375, 'RU', 'RIPE', '20110119', 'I', 'CJSC "ER-Telecom Holding" Samara branch Samara, Russia PPPoE individual customers network'],
            [771813376, 771815423, 'RU', 'RIPE', '20110119', 'I', 'CJSC "ER-Telecom Holding" Samara branch Samara, Russia PPPoE individual customers network'],
            [771815424, 771817471, 'RU', 'RIPE', '20110119', 'I', 'CJSC "ER-Telecom Holding" Samara branch Samara, Russia PPPoE individual customers network'],

            [771817480, 771817490, 'RU', 'RIPE', '20110119', 'I', 'CJSC "ER-Telecom Holding" Samara branch Samara, Russia PPPoE individual customers network'],
            [771817491, 771817494, 'RU', 'RIPE', '20110119', 'I', 'CJSC "ER-Telecom Holding" Samara branch Samara, Russia PPPoE individual customers network']]
     
     f = [
          [2002610792, 2002610799, 'PH', 'APNIC', '20210115', 'I', '2-4412228_RICHWELL PHILS This space has been assigned as STATIC'],
        [2002610800, 2002610807, 'PH', 'APNIC', '20210115', 'I', '18-4085229_MEDIAPOOL INC This space has been assigned as STATIC'],
        [2002610808, 2002610850, 'PH', 'APNIC', '20210115', 'I', '2-4412228_RICHWELL PHILS This space has been assigned as STATIC'],
        [2002610851, 2002610900, 'PH', 'APNIC', '20210115', 'I', '2-4412228_RICHWELL PHILS This space has been assigned as STATIC'],
        [2002610901, 2002610930, 'PH', 'APNIC', '20210115', 'I', '2-4412228_RICHWELL PHILS This space has been assigned as STATIC'],
        [2002610931, 2002610950, 'PH', 'APNIC', '20210115', 'I', '2-4412228_RICHWELL PHILS This space has been assigned as STATIC'],
        [2002610951, 2002610980, 'PH', 'APNIC', '20210115', 'I', '2-4412228_RICHWELL PHILS This space has been assigned as STATIC'],
        
        ]

     c = [[1509679104, 1509683199, 'ES', 'RIPE', '20210413', 'I', ''],
        [1509679376, 1509679359, 'ES', 'RIPE', '20060920', 'D', ''],
        [1509679360, 1509679407, 'ES', 'RIPE', '20170206', 'I', 'Shared Firewall Service'],
        [1509679376, 1509679359, 'ES', 'RIPE', '20060920', 'D', ''],
        [1509679360, 1509679407, 'ES', 'RIPE', '20170206', 'I', 'Shared Firewall Service'],
        [1509679392, 1509679415, 'ES', 'RIPE', '20170207', 'I', 'Shared Firewall Service'],
        [1509679408, 1509679423, 'ES', 'RIPE', '20170207', 'I', 'Shared Firewall Service'],
        [1509679416, 1509679439, 'ES', 'RIPE', '20170207', 'I', 'Shared Firewall Service'],
        [1509679424, 1509679447, 'ES', 'RIPE', '20170207', 'I', 'Shared Firewall Service'],
        [1509679440, 1509679455, 'ES', 'RIPE', '20170207', 'I', 'Shared Firewall Service'],
        [1509679448, 1509679463, 'ES', 'RIPE', '20170207', 'I', 'Shared Firewall Service'],
        [1509679456, 1509679471, 'ES', 'RIPE', '20170207', 'I', 'Shared Firewall Service'],
        [1509679464, 1509679479, 'ES', 'RIPE', '20170206', 'I', 'Shared Firewall Service'],
        [1509679472, 1509679487, 'ES', 'RIPE', '20170207', 'I', 'Shared Firewall Service'],
        [1509679480, 1509679495, 'ES', 'RIPE', '20170207', 'I', 'Shared Firewall Service'],
        [1509679488, 1509679511, 'ES', 'RIPE', '20170207', 'I', 'Shared Firewall Service'],
        [1509679504, 1509679519, 'ES', 'RIPE', '20170207', 'I', 'Shared Firewall Service'],
        [1509679512, 1509679523, 'ES', 'RIPE', '20170207', 'I', 'Shared Firewall Service'],
        [1509679520, 1509679535, 'ES', 'RIPE', '20170207', 'I', 'Shared Firewall Service'],
        [1509679528, 1509679975, 'ES', 'RIPE', '20170207', 'I', 'Shared Firewall Service'],
        [1509679968, 1509679983, 'ES', 'RIPE', '20170207', 'I', 'Shared Firewall Service'],
        [1509679976, 1509679991, 'ES', 'RIPE', '20170207', 'I', 'Shared Firewall Service'],
        [1509679984, 1509680063, 'ES', 'RIPE', '20170207', 'I', 'Shared Firewall Service'],
        [1509680056, 1509680383, 'ES', 'RIPE', '20170207', 'I', 'Shared Firewall Service'],
        [1509680384, 1509680511, 'ES', 'RIPE', '20170207', 'I', 'Cloud Service'],
        [1509680384, 1509680511, 'ES', 'RIPE', '20170207', 'I', 'Cloud Service'],
        [1509680448, 1509680575, 'ES', 'RIPE', '20170207', 'I', 'Cloud Service'],
        [1509680512, 1509680591, 'ES', 'RIPE', '20170207', 'I', 'Cloud Service'],
        [1509680576, 1509680607, 'ES', 'RIPE', '20170207', 'I', 'Cloud Service'],
        [1509680592, 1509680639, 'ES', 'RIPE', '20170207', 'I', 'Cloud Service'],
        [1509680608, 1509681151, 'ES', 'RIPE', '20170207', 'I', 'Cloud Service'],
        [1509681152, 1509681191, 'ES', 'RIPE', '20170207', 'I', 'VAESA DEALERS POOL'],
        [1509681152, 1509681191, 'ES', 'RIPE', '20170207', 'I', 'VAESA DEALERS POOL'],
        [1509681184, 1509681407, 'ES', 'RIPE', '20170207', 'I', 'VAESA DEALERS POOL'],
        [1509681408, 1509681503, 'ES', 'RIPE', '20170207', 'I', 'Shared Firewall Service'],
        [1509681408, 1509681503, 'ES', 'RIPE', '20170207', 'I', 'Shared Firewall Service'],
        [1509681472, 1509681535, 'ES', 'RIPE', '20170207', 'I', 'Shared Firewall Service'],
        [1509681504, 1509681599, 'ES', 'RIPE', '20170207', 'I', 'Shared Firewall Service'],
        [1509681536, 1509681663, 'ES', 'RIPE', '20170207', 'I', 'Shared Firewall Service'],
        [1509681600, 1509681791, 'ES', 'RIPE', '20170207', 'I', 'Shared Firewall Service'],
        [1509681664, 1509681919, 'ES', 'RIPE', '20170207', 'I', 'Shared Firewall Service'],
        [1509681792, 1509681919, 'ES', 'RIPE', '20170207', 'I', 'Shared Firewall Service'],
        [1509681920, 1509682687, 'ES', 'RIPE', '20170207', 'I', 'Cloud Service'],
        [1509681920, 1509682687, 'ES', 'RIPE', '20170207', 'I', 'Cloud Service'],
        [1509682688, 1509682751, 'ES', 'RIPE', '20170207', 'I', 'Backbone'],
        [1509682688, 1509682751, 'ES', 'RIPE', '20170207', 'I', 'Backbone'],
        [1509682720, 1509682759, 'ES', 'RIPE', '20170207', 'I', 'Backbone']]

     o = [[1509679104, 1509683199, 'ES', 'RIPE', '20210413', 'I', 'Hallo'],
        [1509679359,   1509679376, 'ES', 'RIPE', '20060920', 'D', 'Hdasdasdasd'],
        [1509679360, 1509679407, 'ES', 'RIPE', '20170206', 'I', 'Shared Firewall Service'],
        [1509679376, 1509679359, 'ES', 'RIPE', '20060920', 'D', 'adssssssssssxxxx'],
        [1509679360, 1509679407, 'ES', 'RIPE', '20170206', 'I', 'Shared Firewall Service'],
        [1509679392, 1509679415, 'ES', 'RIPE', '20170207', 'I', 'Shared Firewall Service']]
            
     #merge_following(l)

     #result = merge_following(f)
    

     #for item in result:
     #    print(*item)

     #print(bigrange(o))
    
        

 


