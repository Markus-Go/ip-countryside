import re
import os
import shutil
import fileinput
import ipaddress
import time
from datetime import datetime
import multiprocessing as mp
import math


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
                        "EARLY REGISTRATION ADDRESSES"                   in value.strip().upper() or
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


def remove_duplicates(records=[]):

    if not records:
        records = read_db()

    print(f"Nr. of records before duplicate deletion {len(records)}")

    duplicate_indicies = get_duplicate_indicies(records)

    print(f"Nr. of duplicates being removed {len(duplicate_indicies)}")
    
    records = empty_entry_by_idx(records, duplicate_indicies)

    write_db(records)

    print(f"Nr. of records after duplicate deletion {len(records)}")



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
        if (P[i][0] == P[i+1][0] and P[i][1] == P[i+1][1] == "L" and 
            P[i][2] == P[i+1][2] ):

            if not added:
                dict_L[P[i][3]] = [P[i][3]]
                added = True
                current = P[i][3]

            dict_L[current].append(P[i+1][3])

        # R: if both have same ip end and same country
        # correct keys in dict_R
        elif (P[i][0] == P[i+1][0] and P[i][1] == P[i+1][1] == "R" and
              P[i][2] == P[i+1][2] and P[i][3] in dict_L):

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
        duplicate_dict[key] = dict_L[key] 
        duplicate_dict[key].pop(-1)

        # join indexes of current duplicate sequence
        duplicate_indicies = duplicate_indicies + duplicate_dict[key]  

    return duplicate_indicies



def handle_overlaps():

    # get db records
    records = read_db()

    print(f"Nr. of records before overlaps deletion {len(records)}")

    # get all records which overlap and their corresponding indicies
    [overlaps, indicies] = extract_overlaps(records)
    
    resolve_overlaps_length_2(overlaps)

    print("Deleting overlaps from db ... ")

    records = empty_entry_by_idx(records, indicies)

    write_db(records)

    print(f"number of records after overlaps deletion {len(records)}")
 

    # @TODO -> (delete); temporary (only for debugging) write overlap sequences into a file 
    with open(os.path.join(DEL_FILES_DIR, "overlaping"), "w", encoding='utf-8', errors='ignore') as f:

        for overlap_seq in overlaps:
            
            f.write("[\n")

            for record in overlap_seq:
                f.write(str(record))
                f.write("\n")

            f.write("]\n")
    
    # @TODO
    # write the clean version of records into the 
    # data base file again ...
    # write back the clean list into db file


def extract_overlaps(records):
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
    
    # sort sublists
    overlaps.sort(key=lambda seq: len(seq))

    print(f"overlaps found {overlaps_nr}\n")

    return [overlaps, overlap_indicies]


def resolve_overlaps_length_2(records):

    # get overlaps with length of 2 only 
    overlaps = [overlap_seq for overlap_seq in records if len(overlap_seq) <= 2] 

    # handling two records with same country
    for overlap_seq in overlaps:
        
        # lets solve records with same country first
        if overlap_seq[0][2] == overlap_seq[1][2]:

            # merge these two intervals and save the result into the first record  
            overlap_seq[0][0] = min(overlap_seq[0][0], overlap_seq[1][0])
            overlap_seq[0][1] = max(overlap_seq[0][1], overlap_seq[1][1])

            # delete the second one
            del overlap_seq[1]

        # here resolve these records with different countries


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

    # @TODO why not len -1 ?
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
    write_db(records, file)


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
    
    # get  all duplicates (simply take one from inetnum if 
    # other is delegation otherwise the one with longer description)
    remove_duplicates()

   
    print("resolving overlaps ...")
    handle_overlaps()

    
    print("checking if final database file have any ouverlapps ...")
    print(records_overlaps(read_db()))

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

    min_value = P[0][0]
    max_value = P[len(P)-1][0]

    min_in = [P[0][2]]
    max_in = [P[len(P)-1][2]]

    notchanged = True
    i = 1
    while notchanged:
        if P[i][0] != min_value: 
            notchanged = False
            break
        else:
            min_in.append(P[i][2])
            i += 1

    notchanged = True
    i = len(P) - 2
    while notchanged:
        if P[i][0] != max_value: 
            notchanged = False
            break
        else:
            max_in.append(P[i][2])
            i -= 1

    for number in min_in:

        if number in max_in:
            index = number
            return [records[index][0], records[index][1], records[index][2], records[index][3], records[index][4], records[index][5], ""]


    return records
    

def getNetwork(ip_from, ip_to):
    hosts = ip_to + 1 - ip_from 
    res = math.log2(hosts)
    subnetmask = 32 - int(res)
  
    if not res.is_integer():
        print("No valid subnetmask", ip_from, " ", ip_to, "with subnetmask: ", res)
        return
    
        
    return str(ipaddress.ip_address(ip_from)) + "/" + str(subnetmask)

   
# Needed if for multiprocessing not to crash
if __name__ == "__main__":   
     run_parser()
        
    
     #merge_following(l)

     #result = merge_following(f)
    

     #for item in result:
     #    print(*item)

     #print(bigrange(o))

     #run_parser()

    # 3278210188   3278210207
    #2152576164   2152576175
    #3279724520   3279724543
    #1548710752   1548710847

     #db = read_db()

     #for record in db:
     #    getNetwork(record[0], record[1])

     #print(getNetwork(3278210188,3278210207))

     l = [[1296624896, 1296624960, 'BE', 'RIPE', '20200414', 'I', 'IPNEXIA SBC INTERCONNECT'],
        [1296624896, 1296625151, 'BE', 'RIPE', '20200414', 'I', ''],
        [1296624961, 1296625023, 'BE', 'RIPE', '20200414', 'I', ''],
        [1296625024, 1296625039, 'BE', 'RIPE', '20200414', 'I', ''],
        [1296625040, 1296625055, 'BE', 'RIPE', '20200414', 'I', 'IPNEXIA customer THERABEL'],
        [1296625056, 1296625063, 'BE', 'RIPE', '20200414', 'I', 'IPNEXIA customer KREDIET PARTNER'],
        [1296625064, 1296625071, 'BE', 'RIPE', '20200414', 'I', 'IPNEXIA customer POLBRUNO'],
        [1296625072, 1296625087, 'BE', 'RIPE', '20200414', 'I', 'IPNEXIA IPSEC SIP'],
        [1296625088, 1296625095, 'BE', 'RIPE', '20200414', 'I', 'IPNEXIA customer TREVI'],
        [1296625120, 1296625151, 'BE', 'RIPE', '20200414', 'I', 'IPNEXIA customer SILVERLINING']]

     #print(bigrange(l))

