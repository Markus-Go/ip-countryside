import os
import pandas as pd
import dask.dataframe as dd
from  config import *

import numpy as np
from ip_countryside_db import read_db, write_db

from ip_countryside_utilities import empty_entry_by_idx

# filename = os.path.join(DEL_FILES_DIR, 'overlaping')
t = [
    [1, 2, 'A', 'APNIC', '20091023', 'I', 'Doors and Doors Systems (India) Pvt Ltd'],
    [3, 4, 'A', 'APNIC', '20091023', 'I', 'Doors and Doors Systems (India) Pvt Ltd'],
    [3, 6, 'A', 'APNIC', '20091023', 'I', 'Doors and Doors Systems (India) Pvt Ltd'],
    [7, 8, 'B', 'APNIC', '2', 'I', 'Doors and Doors Systems (India) Pvt Ltd'],
    [9, 10, 'B', 'APNIC', '2', 'I', 'Doors and Doors Systems (India) Pvt Ltd'],
    #[10, 20, 'A', 'APNIC', '20091023', 'D', 'Doors and Doors Systems (India) Pvt Ltd'],
    [5, 6, 'A', 'APNIC', '20091023', 'I', 'Doors and Doors Systems (India) Pvt Ltd'],
    [7, 8, 'A', 'APNIC', '20091023', 'I', 'Doors and Doors Systems (India) Pvt Ltd'],
    [9, 18, 'A', 'APNIC', '20091023', 'I', 'Doors and Doors Systems (India) Pvt Ltd'],
    [10, 60, 'C', 'APNIC', '20091023s', 'I', 'Doors and Doors Systems (India) Pvt Ltd'],
    [61, 70, 'C', 'APNIC', '20091023s', 'I', 'Doors and Doors Systems (India) Pvt Ltd'],
    # [1, 60, 'C', 'APNIC', '20091023', 'I', 'Doors and Doors Systems (India) Pvt Ltd'],
    # [60, 70, 'D', 'APNIC', '2', 'I', 'Doors and Doors Systems (India) Pvt Ltd'],
    # [60, 100, 'D', 'APNIC', '2', 'I', 'Doors and Doors Systems (India) Pvt Ltd'],
    # [101, 200, 'D', 'APNIC', '2', 'I', 'Doors and Doors Systems (India) Pvt Ltd'],
    # [201, 300, 'D', 'APNIC', '2', 'I', 'Doors and Doors Systems (India) Pvt Ltd'],
    # [301, 400, 'D', 'APNIC', '2', 'I', 'Doors and Doors Systems (India) Pvt Ltd'],
]

t = read_db(os.path.join(DEL_FILES_DIR, "overlaping"))

records_clean = []
indicies = set()


def merge_successive(cc_group):

    cc_group = cc_group.apply(lambda record: merge_helper(cc_group, record), axis=1)
    #print(cc_group)
    


def merge_helper(cc_group, record=[]):

    next_record = cc_group.loc[((cc_group['ip_from'] == record.ip_to + 1) & (cc_group['status'] != "V"))].values
    
    if len(next_record) > 0:
        
        next_record = next_record[0]

        next_idx = next_record[8]
        
        indicies.add(next_idx)

        df.at[next_idx, 'status'] = "V"

        record[1] = next_record[1]

        return merge_helper(cc_group, record)
    
    if len(next_record) == 0:

        records_clean.append(list(record[:-2]))

        return record

col_names = ["ip_from", "ip_to", "cc", "registry", "last-modified", "record_type", "description"]
df = pd.DataFrame(data=t, columns=col_names)
df['status'] = np.nan
df['index'] = df.index

df = df.groupby("cc").apply(lambda cc_group: merge_successive(cc_group))

# for group in df:

#     for key, item in group:

#       print(key) 
#       print(item)


# print(indicies)

records_clean = empty_entry_by_idx(records_clean, indicies)
#print(records_clean)


write_db(records_clean, os.path.join(DEL_FILES_DIR, "overlaping_df3.csv"))


