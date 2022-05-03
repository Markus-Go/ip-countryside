from config import *;
from ip_countryside_db import *;
from ip_countryside_utilities import *;

# ==============================================================================
# Methods used for resolving conflicts/overlaps ... 

def merge_successive(records):
    # merge contiguous entries from the same source and country
    # [[1,2,'DE'], [3,4,'DE']] -> [1,4,'DE']
    i = 0
    end = len(records)
    while i < end - 1:
        temp_list = []
        # If current records end + 1 is start of next record and from same source (D,D or I,I) and is same country
        if records[i][1] + 1 == records[i+1][0] and records[i][2] == records[i + 1][2] and records[i][5] == records[i+1][5]:
            # loop to find records with same start but different end 
            while records[i][1] + 1 == records[i+1][0]:
                if  records[i][2] == records[i + 1][2] and records[i][5] == records[i+1][5]:
                    # delete entry and save the ip_to value of it
                    entry = records.pop(i+1)
                    temp_list.append(entry[1])
                # break if different country
                else: 
                    break
                # break if end of list was reached
                if i < end - 1:
                    break
            # find new end of the entry out of list
            newend = max(temp_list)
            records[i][1] = newend
            end = len(records)
        else:
            # increment counter value
            i += 1

    return records


def merge(records):
    # merge all overlapping entries
    # is only called when list of overlaps consists of only the same country  

    # if list is empty return
    if not records:
        return

    records.sort(key=lambda x: x[0])
 
    merged = []
    for record in records:
        # If merged is not empty or the last TO entry of merged is smaller than the FROM of the current one 
        # Add the current record to merged
        if not merged or merged[-1][1] < record[0]:
            merged.append(record)
        else:
        # Replace the TO entry of merged with the max value from the last TO of merged and the current TO
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
    # iterate through an overlap record to return if everything is same country
    country = record[0][2]
    
    for r in record:
    
        if r:

            if not country == r[2]:
        
                return False

    
    return True


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
            if current[1] == "R" and current[2] in data and current[2] in queue:
                
                # remove record index from queue
                queue.remove(current[2])

                # add right edge for current element before deleting 
                data[current[2]].add(records[current[2]][1])
                
                # split a db record by given list of edges 
                record_split = split_records_helper(records, [current[2], list(data[current[2]])])
                
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
    status = records[idx][6]
    description = ""

    if record_type == "I":
        description = records[idx][7]

    ret_value = list()
    for i in range(len(record[1])-1):

        start = record[1][i]
        end = record[1][i+1]
        
        new_record = [start, end, cc, registry, last_modified, record_type, status, description]

        ret_value.append(new_record)

    return ret_value


def remove_duplicates(records=[]):

    if not records:
        records = read_db()

    [duplicate_indicies, record] = get_duplicate_indicies(records)
    
    records = empty_entry_by_idx(records, duplicate_indicies)

    if record:

        records.append(record)

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

        duplicate_dict[key] = list(set(dict_L[key]).intersection(dict_R[key])) 

    record = []
    for key, value in duplicate_dict.items():
        
        group = [records[idx] for idx in value]
        record = remove_duplicates_helper(group)
            
        # join indexes of current duplicate sequence
        duplicate_indicies.extend(duplicate_dict[key])  

    return [duplicate_indicies, record]


def remove_duplicates_helper(group):
    
    data = {}

    # create dictionary with I and D as keys, 
    # each key have records with the corresponding source
    data =  group_records_by_type(group)
    inet_group = data["I"]
    del_group = data["D"]

    # remove delegation if we have inetnum records
    country_categorized = False # a flag for indicating if inet_group or del_group
                        # were categorized by country
    if inet_group and del_group:

        country_categorized = True

        inet_group = group_records_by_country(inet_group)
        del_group = group_records_by_country(del_group)
        
        # if inetnum have only one record with "EU" as country 
        # remove this
        if "EU" in inet_group and len(inet_group) == 1 and not "EU" in del_group:
           inet_group = []

        # otherwise there is either no inetnum record with "EU" there are 
        # other inetnum records with more specific information
        # -> For both cases we remove the delegation ...  
        else:
            del_group = []
        
    if inet_group:
        data = inet_group

    if del_group:
        data = del_group

    if not country_categorized:
        data = group_records_by_country(data)
        country_categorized = True

    # if we have only one country then lets take record with newest date
    if len(data) == 1:

        if country_categorized:
            data = data[list(data.keys())[0]]
        
        data = sorted(data, key=lambda x: -(int(x[4])))

        record = data[0]

        return record

    # if we still have multiple countries we need to handle
    else:
        
        # if there is "EU" country -> delete this category key
        if "EU" in data:
            data.pop("EU")

        # make a flat list
        data = [record for cc_list in data.values()
                    for record in cc_list]
        
        record = filter_records_by_status(data)

        return record


def filter_records_by_status(records):

    # group records by status 
    data = group_records_by_status(records)

    # simply list all cases first have most priority
    if "ASSIGNED NON-PORTABLE" in data:         
        data = data["ASSIGNED NON-PORTABLE"]

    elif "ASSIGNED PI" in data:                 # ASSIGNED PI vs ALLOCATED PORTABLE
        data = data["ASSIGNED PI"]

    elif "ASSIGNED" in data: 
        data = data["ASSIGNED"]

    elif "ASSIGNED PORTABLE" in data:           # ASSIGNED PORTABLE vs ALLOCATED PORTABLE
        data = data["ASSIGNED PORTABLE"] 

    elif "ASSIGNED PA" in data:                 # ASSIGNED PA vs ALLOCATED PA vs LIR-PARTITIONED
        data = data["ASSIGNED PA"] 

    elif "ALLOCATED NON-PORTABLE" in data:      # ASSIGNED PA vs ALLOCATED NON-PORTABLE PA vs ALLOCATED PORTABLE
        data = data["ALLOCATED NON-PORTABLE"] 

    elif "SUB-ALLOCATED PA" in data:            # ASSIGNED PA vs ALLOCATED NON-PORTABLE PA vs ALLOCATED PORTABLE
        data = data["SUB-ALLOCATED PA"]

    elif "ALLOCATED-BY-LIR" in data:
        data = data["ALLOCATED-BY-LIR"]

    elif "ALLOCATED" in data:                   # delegation files ..
        data = data["ALLOCATED"]

    elif "LIR-PARTITIONED PA" in data:          # No duplicates at this point 
        data = data["LIR-PARTITIONED PA"]
    
    elif "AGGREGATED-BY-LIR" in data:
        data = data["AGGREGATED-BY-LIR"]
    
    elif "ALLOCATED PORTABLE" in data:          # ALLOCATED PORTABLE vs  ?? (loses always)
        data = data["ALLOCATED PORTABLE"] 
    
    elif "ALLOCATED-BY-RIR" in data:  
        data = data["ALLOCATED-BY-RIR"]
    
    elif "ALLOCATED PA" in data:                # ALLOCATED PORTABLE vs  ?? (loses always)
        data = data["ALLOCATED PA"]             
    
    elif "LEGACY" in data:                      # LEGACY vs LEGACY vs ALLOCATED PORTABLE
        data = data["LEGACY"]
    
    elif "ASSIGNED ANYCAST" in data:            
        data = data["ASSIGNED ANYCAST"]
    
    elif "UNSPECIFIED" in data:                 # NO CASES
        data = data["UNSPECIFIED"]              
    
    elif "ALLOCATED UNSPECIFIED" in data:       # NO CASES
        data = data["ALLOCATED UNSPECIFIED"]
    
    else:
        print("Unvalid Data detected in filter_by_status() !")

    # get record with newest record if exists, othwise the first one 
    record = sorted(data, key=lambda x: -(int(x[4])))[0]
        
    return record
        

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


def group_records_by_status(records):

    data = {}

    # categorize data based on status
    for record in records:

        # add record if status not in dict already 
        if not record[6] in data:    
            
            # add status category 
            data[record[6]] = [record]

        # otherwise just append the record to the correspnding category
        else:

            data[record[6]].append(record)

    return data


def  group_records_by_type(records):

    data = {}
    inet_group = []
    del_group = []
    
    # categorize records by resource
    for record in records:

        if record[5] == "I":
            inet_group.append(record)

        elif record[5] == "D":
            del_group.append(record)
        
        else: 
            print("There may be records which doesn't have any registry assigned. Please check the data!")
    
    data["I"] = inet_group
    data["D"] = del_group

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
    