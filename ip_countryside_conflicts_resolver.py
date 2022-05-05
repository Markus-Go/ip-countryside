from config import *;
from ip_countryside_db import *;

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

    if record_type == "I":
        description = records[idx][7]
 
        
    for i in range(len(record[1])-1):

        start = record[1][i]
        end = record[1][i+1] 
        
        new_record = [start, end, cc, registry, last_modified, record_type, status, description]

        line = "|".join(map(str, new_record))
        line = line + '\n'
        f.write(line)


def save_conflicts():

    with open(IP2COUNTRY_DB, 'r', encoding='utf-8', errors='ignore') as f, open(INET_CONFLICTS, 'w', encoding='utf-8', errors='ignore') as output:

        # groups is a sequence of duplicate records    
        for group in get_dupplicate_group(f):

            inetnum_country_conflicts = save_conflicts_helper(group) 

            if inetnum_country_conflicts:
                
                output.write(">>>>>>>>>>>>>>>>>>>>>>>>>>>\n")

                for record in inetnum_country_conflicts:
                    
                    if record:

                        line = "|".join(map(str, record))
                        line = line + '\n'
                        output.write(line)

                output.write("<<<<<<<<<<<<<<<<<<<<<<<<<<<\n")


def save_conflicts_helper(group):

    # remove euql records
    data = {}

    # create dictionary with I and D as keys, 
    # each key have records with the corresponding source
    data =  group_records_by_type(group)
    inet_group = data["I"]
    del_group = data["D"]
    inet_group = group_records_by_country(inet_group)
    del_group = group_records_by_country(del_group)
        
    if inet_group and del_group:

        # if inetnum have only one record with "EU" as country 
        # process delegation and delete inetnum
        if "EU" in inet_group and len(inet_group) == 1 and not "EU" in del_group:
            inet_group = []
            
        # otherwise there is either no inetnum record with "EU" or there are 
        # other inetnum records with more specific countries
        # -> For both cases we remove the delegation ...  
        else:
            del_group = []

    if inet_group:
        data = inet_group

    if del_group:
        data = del_group

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

            if len(group) > 1:

                record = remove_duplicates_helper(group)
                # solve this duplicate and append it to records
            
            else:
                
                record = group[0]
                
            records.append(record)

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


def merge_successive():

    with open(IP2COUNTRY_DB, "r", encoding='utf-8', errors='ignore') as input, open(os.path.join(DB_DIR, "ip2country_temp.db"), "w", encoding='utf-8', errors='ignore') as output:

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
    os.rename(os.path.join(DB_DIR, "ip2country_temp.db"), IP2COUNTRY_DB)


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


def correct_edges():

    with open(IP2COUNTRY_DB, "r", encoding='utf-8', errors='ignore') as input, open(os.path.join(DB_DIR, "ip2country_temp.db"), "w", encoding='utf-8', errors='ignore') as output:

        temp = []

        for line in input:
            
            record = read_db_record(line)

            if not temp: 
                temp = record
                continue

            else:

                if temp[1] == record[0] and temp[2] != record[2]:
                    
                    temp[1] = temp[1] - 1

                    line = "|".join(map(str, temp))
                    line = line + '\n'
                    output.write(line)

                    temp = record
                
                else:

                    line = "|".join(map(str, temp))
                    line = line + '\n'
                    output.write(line)

                    temp = record
            
        line = "|".join(map(str, temp))
        line = line + '\n'
        output.write(line)
                    
    os.remove(IP2COUNTRY_DB)
    os.rename(os.path.join(DB_DIR, "ip2country_temp.db"), IP2COUNTRY_DB)


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
            print(records[P[i][2]])
            print(records[P[i+1][2]])
            return True
            
    return False