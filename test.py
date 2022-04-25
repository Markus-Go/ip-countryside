import os
import pandas as pd
import dask.dataframe as dd
from  config import *

filename = os.path.join(DEL_FILES_DIR, 'overlaping')
col_names = ["ip_from", "ip_to", "cc", "registry", "last-modified", "record_type", "description"]

df = dd.read_csv(filename, delimiter="|",  names=col_names,  converters={'ip_from':int, 'ip_to':int}, blocksize=25e6)  # 25MB chunks  


print(df.head(5))