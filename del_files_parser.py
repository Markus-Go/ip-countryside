from DBRangeEntry import DBRangeEntry
import re
import os

def parse_del_files(delName):
    
    dbRangeEntries = []

    del_files_dir = "del_files"
    os.chdir(del_files_dir)

    try:
        with open(delName) as fp:

            for line in fp:
                
                entry = create_dbRangeEntry(line)
                
                dbRangeEntries.append(entry)

    except IOError as e:
    
        print(e)

    os.chdir("../")

    return dbRangeEntries


def create_dbRangeEntry(strEntry):

    strEntry = strEntry.split("|")
    
    registry = strEntry[0]
    country = strEntry[1]
    
    ipFrom = re.sub('[^0-9]', '', strEntry[3])
    if(not ipFrom) :
        ipFrom = -1
    # python uses variable number of bits for integers -> no overflow
    ipFrom = int(ipFrom)

    ipTo = ipFrom + (int(strEntry[4]) - 1) 

    entry = DBRangeEntry(ipFrom, ipTo, country, registry)

    return entry