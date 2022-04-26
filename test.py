import os
import pandas as pd
import dask.dataframe as dd
from  config import *


def resolve_overlaps_2(records=[]):
    
    if not records:
        records = read_db(os.path.join(DEL_FILES_DIR, "overlaping"))

 
    start = {}
    end = {}
    endpoints = sorted(list(set([r[0] for r in records] + [r[1] for r in records])))
    elems = []

    for e in endpoints:
        start[e] = set()
        end[e] = set()
    
    for i in range(len(records)):
        start[records[i][0]].add(i)
        end[records[i][1]].add(i)

    
    print("geting overlaped intervals")
    
    elems_start = [list(x) for x in start.values()]
    elems_end = [list(x) for x in end.values()]
    data = list(zip(endpoints[:-1], endpoints[1:], elems_start , elems_end))

    df = pd.DataFrame(data=data, columns=['ip_from', 'ip_to', 'start_elems', 'end_elems'])
    df = dd.from_pandas(df, npartitions=4)
    df['elems'] = df.start_elems.where(df.start_elems > df.end_elems, df.end_elems)


    current_ranges = set()
    zipped = zip(endpoints[:-1], endpoints[1:])
    for e1, e2 in zipped:

        current_ranges.difference_update(end[e1])
        current_ranges.update(start[e1]) 
        
    print("sotring results into csv file")

    print(df.compute())
    df.to_csv(os.path.join(DEL_FILES_DIR, "overlaping_df2.csv"), index=False)


# filename = os.path.join(DEL_FILES_DIR, 'overlaping')
# col_names = ["ip_from", "ip_to", "cc", "registry", "last-modified", "record_type", "description"]

# df = dd.read_csv(filename, delimiter="|",  names=col_names,  converters={'ip_from':int, 'ip_to':int}, blocksize=25e6)  # 25MB chunks  


# print(df.head(5))


