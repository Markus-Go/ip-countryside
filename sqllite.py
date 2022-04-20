import sqlite3
import csv


# WRITE DB but need a ip2country.csv file
connection = sqlite3.connect("sql.db")
cursor = connection.cursor()
#ip_from|ip_to|country|ria|date|file|description
query = """
CREATE TABLE IF NOT EXISTS ip2country (
ip_from int,
ip_to int,
country varchar(3),
ria varchar(10),
date varchar(20),
file varchar(20),
description varchar(255)
);"""

cursor.execute(query)

query = """
INSERT INTO ip2country (ip_from, ip_to, country, ria, date, file, description)
VALUES (:ip_from, :ip_to, :country, :ria, :date, :file, :description)
"""

with open("ip2country.csv", encoding='utf-8', errors='ignore') as csvfile:
    csv_reader_object = csv.reader(csvfile, delimiter='|')

    with sqlite3.connect("sql.db") as connection:
        cursor = connection.cursor()
        cursor.executemany(query, csv_reader_object)


# READ DB
#connection = sqlite3.connect("sql.db")
#cursor = connection.cursor()
#cursor.execute("SELECT * FROM ip2country where ip_from <= 1547843363 and ip_to >= 1547843363")
#result = cursor.fetchall()
#print(result)
#connection.close()