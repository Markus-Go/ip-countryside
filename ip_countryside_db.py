import sys
from ipaddress import *
import json
import math
import sqlite3
import csv
import random
from config import *
import time
from operator import itemgetter
from ip2country_merege_sort import large_sort

try:
    from netaddr import IPSet, IPNetwork
except ModuleNotFoundError:
    print("module 'netaddr' is not installed")
    sys.exit()
try:
    from mmdb_writer import MMDBWriter
except ModuleNotFoundError:
    print(
        "module 'mmdb_writer' is not installed, please install executing 'pip3 install -U git+https://github.com/Markus-Go/MaxMind-DB-Writer-python'.")
    sys.exit()
try:
    import maxminddb
except ModuleNotFoundError:
    print("module 'maxminddb' is not installed")
    sys.exit()
try:
    import yaml
except ModuleNotFoundError:
    print("module 'yaml' is not installed")
    sys.exit()


# record index:    0       1   2    3           4            5          6       7
# record format: ip_from|ip_to|cc|registry|last-modified|record_type|status|description

def get_db_files():
    """"
        return all databases which exists in DB_DIR
    """
    db_files = [
        IP2COUNTRY_DB,
        IP2COUNTRY_DB_IPV4,
        IP2COUNTRY_DB_IPV6,
        IP2COUNTRY_DB_JSON,
        IP2COUNTRY_DB_YAML,
        IP2COUNTRY_DB_MYSQL,
        IP2COUNTRY_DB_SQLITE,
        IP2COUNTRY_MM,
        IP2COUNTRY_DB_MMDB_V4,
        IP2COUNTRY_DB_MMDB_V6,
    ]
    data = []
    for file in db_files:
        if os.path.exists(file):
            data.append(os.path.basename(file))
    return data


def read_db(file=IP2COUNTRY_DB):
    records = []
    try:
        # save all records into a list
        with open(file, "r", encoding='utf-8', errors='ignore') as f:
            for line in f:
                if not line in ['\n', '\r\n']:
                    record = read_db_record(line)
                    if record:
                        records.append(record)
    except IOError as e:
        print(e)
    return records

def write_db(records, file=IP2COUNTRY_DB):
    if not records:
        return
    try:
        with open(file, "w", encoding='utf-8', errors='ignore') as f:
            for record in records:
                if record:
                    line = "|".join(map(str, record))
                    line = line + '\n'
                    f.write(line)
    except IOError as e:
        print(e)
    return records

def read_db_record(line):
    if line.startswith("\n"):
        return []
    line = line.split("|")
    if (len(line) >= 3):
        ip_from = int(line[0])
        ip_to = int(line[1])
        country = line[2].upper()
        registry = line[3].upper()
        last_modified = line[4]
        record_type = line[5]
        status = line[6].rstrip("\n")
        descr = ""

        if record_type == "I" and len(line) > 6:
            descr = line[7].rstrip("\n")
        return [ip_from, ip_to, country, registry, last_modified, record_type, status, descr]
    return []


def sort_db(file=IP2COUNTRY_DB):
    with (open(file, "r", encoding='utf-8', errors='ignore')) as input, open(os.path.join(DB_DIR, "ip2country_temp.db"),
                                                                             "w", encoding='utf-8',
                                                                             errors='ignore') as output:
        large_sort(input, output, lambda line: read_db_record(line)[0], False, limit_chars=1024 * 1024 * 64)
    os.remove(IP2COUNTRY_DB)
    os.rename(os.path.join(DB_DIR, "ip2country_temp.db"), IP2COUNTRY_DB)

def sort_db_2(file=IP2COUNTRY_DB):
    records = []
    # get records from final db
    records = read_db(file)
    # sort this list
    records.sort()
    # write sorted list back into final db
    write_db(records, file)

def split_db(file=IP2COUNTRY_DB):
    try:

        # save all records into a list
        with open(file, "r", encoding='utf-8', errors='ignore') as input, open(IP2COUNTRY_DB_IPV4, "w",
                                                                               encoding='utf-8',
                                                                               errors='ignore') as output4, open(
                IP2COUNTRY_DB_IPV6, "w", encoding='utf-8', errors='ignore') as output6:
            for line in input:
                record = read_db_record(line)
                if len(str(record[0])) < 11:
                    output4.write(line)
                else:
                    output6.write(line)
    except IOError as e:
        print(e)

def extract_as_json(file=IP2COUNTRY_DB):
    data = {}
    records = read_db(file)
    try:
        with open(IP2COUNTRY_DB_JSON, 'w', encoding='utf-8', errors='ignore') as f:
            f.write("[\n")
            for record in records:
                data = {
                    'ip_from': record[0],
                    'ip_to': record[1],
                    'cc': record[2],
                }
                f.write(json.dumps(data, indent=4))
                f.write(",\n")
            f.write("]")
    except IOError as e:
        print(e)
    return 0


def extract_as_yaml(file=IP2COUNTRY_DB):
    data = {}
    records = read_db(file)
    try:
        with open(IP2COUNTRY_DB_YAML, 'w', encoding='utf-8', errors='ignore') as f:
            f.write("---\n")
            for record in records:
                f.write("- ip_from: ")
                f.write(str(record[0]))
                f.write("\n  ip_to: ")
                f.write(str(record[1]))
                f.write("\n  cc: ")
                f.write(record[2])
                f.write("\n")
    except IOError as e:
        print(e)
    return 0


def extract_as_sqlite(file=IP2COUNTRY_DB):
    if os.path.exists(IP2COUNTRY_DB_SQLITE):
        os.remove(IP2COUNTRY_DB_SQLITE)
    connection = sqlite3.connect(IP2COUNTRY_DB_SQLITE)
    cursor = connection.cursor()

    # ip_from|ip_to|country|ria|date|file|description
    query = """
    CREATE TABLE ip2country (
    ip_from BLOB,
    ip_to BLOB,
    cc CHAR,
    status CHAR, 
    PRIMARY KEY (ip_from, ip_to)
    );    
    """
    cursor.execute(query)
    connection.commit()

    # IP2COUNTRY_DB
    with open(IP2COUNTRY_DB, 'r', encoding='utf-8', errors='ignore') as db:
        database = []
        for row in db:
            record = read_db_record(row)
            ip_from_binary = bin(record[0])[2:].zfill(128)
            ip_to_binary = bin(record[1])[2:].zfill(128)
            cc = record[2]
            status = record[6]
            entry = (ip_from_binary, ip_to_binary, cc, status)
            database.append(entry)
        query = "INSERT INTO ip2country VALUES (?,?,?,?);"
        cursor.executemany(query, database)
        connection.commit()

        query = "CREATE INDEX ix_ip_range on ip2country (ip_from, ip_to);"
        cursor.execute(query)
        connection.commit()

        connection.close()
        # To query transform ip into integer and integer to a fixed 128 bit value


def extract_as_mmdb_fast(file=IP2COUNTRY_DB):
    data = {}
    filteredlist = []
    countryips4 = []
    countryips6 = []
    with open(file, 'r', encoding='utf-8', errors='ignore') as database:
        for record in database:
            record = record.split('|')
            entry = record[2].strip('\n')
            filteredlist.append(entry)
        sortedlist = sorted(list(dict.fromkeys(filteredlist)))

        writerv4 = MMDBWriter(ip_version=4)
        writerv6 = MMDBWriter(ip_version=6)
        i = 0
        j = 0
        database.close()

        print(sortedlist)
        for row in sortedlist:
            with open(file, 'r', encoding='utf-8', errors='ignore') as database:
                print(row + "")
                for record in database:
                    record = record.split('|')
                    if row == record[2]:
                        split_ips = converttoNetwork(record)
                        for network in split_ips:
                            i += 1
                            ipversion = ip_interface(network).ip.version
                            if ipversion == 4:
                                # countryips4.append(IPNetwork(network))
                                writerv4.insert_network(IPSet([network]),
                                                        {'CountryCode': '{0}'.format(row)})
                                # writerv4.to_db_file(IP2COUNTRY_DB_MMDB_V4)
                            else:
                                # countryips6.append(network)
                                writerv6.insert_network(IPSet([network]),
                                                        {'CountryCode': '{0}'.format(row)})
                                # writerv6.to_db_file(IP2COUNTRY_DB_MMDB_V6)

                            j += 1
                            if j > 1000000:
                                writerv4.to_db_file(IP2COUNTRY_DB_MMDB_V4)
                                writerv6.to_db_file(IP2COUNTRY_DB_MMDB_V6)
                                print(
                                    "Wrote 1.000.000 IP ranges, for a total of %s written entries, estimated progress is %s%%" % (
                                    i, ((i / 27000000) * 100)))
                                j = 0
            # countryips4.sort()
            # countryips6.sort()

            # blockPrint()
            # for ip4 in countryips4:

            #    writerv4.insert_network(IPSet([ip4]), {'CountryCode': '{0}'.format(row)})
            #    #writerv4.to_db_file(IP2COUNTRY_DB_MMDB_V4)

            # for ip6 in countryips6:
            #    writerv6.insert_network(IPSet([ip6]),{'CountryCode': '{0}'.format(row)})
            #    #writerv6.to_db_file(IP2COUNTRY_DB_MMDB_V6)

            print("\nNr. of ips written %s, progress is %s%%" % (i, (i / 27000000) * 100))

        writerv4.to_db_file(IP2COUNTRY_DB_MMDB_V4)
        writerv6.to_db_file(IP2COUNTRY_DB_MMDB_V6)


def converttoNetwork(record):
    ip_from = int(record[0])
    ip_to = int(record[1])

    ip_from = ip_address(ip_from)
    ip_to = ip_address(ip_to)

    ranges = [ipaddr for ipaddr in summarize_address_range(ip_from, ip_to)]

    return_list = []
    for range in ranges:
        line = "|".join(map(str, [range]))
        return_list.append(line)
    return return_list

def read_mmdb(ipaddress):
    if ip_interface(ipaddress).ip.version == 4:
        m = maxminddb.open_database(IP2COUNTRY_DB_MMDB_V4)
    else:
        m = maxminddb.open_database(IP2COUNTRY_DB_MMDB_V6)
    return m.get(ipaddress)


def extract_as_mysql(file=IP2COUNTRY_DB):
    # query with: Select country from ip2country where inet6_aton('41.31.255.254') >= inet6_aton(ip_to) and inet6_aton('41.31.255.254') <= inet6_aton(ip_to)
    with open(IP2COUNTRY_DB_MYSQL, 'w', encoding='utf-8', errors='ignore') as f, open(IP2COUNTRY_DB, 'r',
                                                                                      encoding='utf-8',
                                                                                      errors='ignore') as db:
        f.write(
            "CREATE TABLE ip2country (ip_from BINARY(16), ip_to BINARY(16),cc CHAR(2), PRIMARY KEY(ip_from, ip_to));\n")
        f.write("CREATE INDEX ip_range on ip2country (ip_from, ip_to);\n")
        f.write("INSERT INTO ip2country (ip_from, ip_to, cc)\n")
        f.write("VALUES\n")

        database = []
        for row in db:
            row = row.split('|')
            database.append(row)

        for row in database[:-1]:
            if int(row[0]) > 4294967296:
                line = "(INET6_ATON('%s'), INET6_ATON('%s'), '%s'),\n" % (
                str(ip_address(int(row[0]))), str(ip_address(int(row[1]))), row[2])
                f.write(line)
            else:
                line = "(INET_ATON('%s'), INET_ATON('%s'), '%s'),\n" % (
                str(ip_address(int(row[0]))), str(ip_address(int(row[1]))), row[2])
                f.write(line)
        else:
            if int(row[0]) > 4294967296:
                line = "(INET6_ATON('%s'), INET6_ATON('%s'), '%s');" % (
                str(ip_address(int(row[0]))), str(ip_address(int(row[1]))), row[2])
                f.write(line)
            else:
                line = "(INET_ATON('%s'), INET_ATON('%s'), '%s');" % (
                str(ip_address(int(row[0]))), str(ip_address(int(row[1]))), row[2])
