ip-countryside 2.0
==============

This tool creates an ip-to-country database in multiple formats such as MAXMIND, SQLite, MySQL and CSV. <br> 
These databases can be used in multiple applications for geolocating internet users based on  their IP addresses. 

<b>If you only need the ip2country database itself (not the program creating 
it), you can download the different databases <a href=''> here</a> (updated weekly).</b>

A demo can be found on our webpage <a href='' target='_BLANK'>here</a>.

To acess the api (limited to 100 requests a day) visit our <a href='/api?'> webpage </a> under the URL /api?ip=1.2.3.4

Detailed Information
--------------------
The database is built automatically out of the 5 Regional Internet Registrars (RIR)
databases: AFRINIC, APNIC, ARIN, LACNIC and RIPE. The resulting database is a plain
sorted csv file in the format 

    ip_from|ip_to|cc|registry|last-modified|record_type|status|description
    
where IPs are 32 bit integers for IPv4 and 64 bit integers for IPv6. The 2 letter country code (cc) is as defined in 
ISO 3166. This tool uses the delegation files of all RIRs and additionally for 
APNIC and RIPE it uses the detailed databases (inetnum files / inet6num files).

In contrast to other tools, our database is free, self-creatable and more accurate.

How to use the different databases 
--------------------
The MaxMind format can be read in different programming languages for example in <a href="https://dev.maxmind.com/geoip/geolocate-an-ip/databases?lang=en"> C#, Java, Node, PHP, Python and Ruby. </a> 
<br>
The MySQL database is provided as executeable sql script. (115mb large)
Country code can be queried with for IPv4 and IPv6:
```sql
SELECT cc FROM ip2country WHERE INET_ATON('1.0.0.1') >= ip_from AND INET_ATON('1.0.0.1') <= ip_to
SELECT cc FROM ip2country where INET6_ATON('2607:c181::') >= ip_from AND INET6_ATON('2607:c181::') <= ip_to
```
The SQLite format can only be queried by converting an IP adress into an integer and then into a 128 bit value with fixed length. 
```python
from ipaddress import *
ip = ip_address(ip)
ip = bin(int(ip))[2:].zfill(128)
query = "SELECT cc FROM ip2country WHERE ip_from <= '%s' and ip_to >= '%s'" % (ip, ip)
```
MaxMind is easily the fastes database to query (0.045ms) for one IP. SQLite is the slowest (300ms) due to the inefficient comparison. 





Prerequisite
------------

The following files are required to build the database. The script 'getDBs.sh' 
can be used for downloading them:

1.  ripencc Delegation file  
   ftp://ftp.ripe.net/ripe/stats/delegated-ripencc-latest
2.  ripencc Database  
   ftp://ftp.ripe.net/ripe/dbase/split
3.  apnic Delegation file  
   ftp://ftp.apnic.net/pub/stats/apnic/delegated-apnic-latest
4.  apnic Database  
   ftp://ftp.apnic.net/apnic/whois-data/APNIC/split
5.  arin Delegation file  
   ftp://ftp.arin.net/pub/stats/arin/delegated-arin-latest
6.  lacnic Delegation file  
   ftp://ftp.lacnic.net/pub/stats/lacnic/delegated-lacnic-latest
7.  afrinic Delegation file  
   ftp://ftp.afrinic.net/pub/stats/afrinic/delegated-afrinic-latest

The config file should be modified to point to the actual location AND names of the
above mentioned files.

Installation
------------

1. Run the getDBs.sh script, this will download a fresh copy of the delegation 
 files and the databases
2. Check the 'config' file.
3. :~$ make
4. :~$ ./createDb to execute the program

How it works
------------

The program will start with parsing all the delegation files (ripencc, apnic, lacnic, arin, and 
afrinic). The parser will return the delegation files in the form of ipFrom, 
ipTo, country and
registry. The results of parsing the delegation files are stored in one file called "Testout". 
Now the list that contains all delegation files are sorted and checked to see if there are any 
overlaping entries. If the overlap is between ripe delegation file and other one then the part 
of the overlap is removed from the ripe entry (i.e. the entry in the ripe delegation file is 
changed to remove the overlap) otherwise if the overlap is between other two registries the 
first one is changed to remove the overlap. Then 3 delegation files (afrinic, lacnic, and arin)
are written to a file.

Ripe and apnic need more processing (this is due to inconsistencies in their DBs), the following
procedure is applied for both:
The program will iterate over the delegation file of (for example) ripe, it gets the first entry
of the delegation file (lets call that entry X). X contains a range of IPs with no country is 
assigned to. The country information will be taken from the ripe database. The program will check
the database entries if they overlap with entry X and assign the country of the smallest range
entries to X (i.e. if two entries in DB with different countries overlap over the same location 
in X the country of the smaller range will be assigned to X). Then we pick the next entry (X++;)
in the delegation file and so on.

The last step is to sort the file that contain the delegation files and output the result to file 
called "ip2country.db". 

Copyright/ License/ Credits
---------------------------

Copyright 2006-2007 Deutsches Forschungszentrum fuer Kuenstliche Intelligenz  
Copyright 2008-2020 Markus Goldstein

This is free software. Licensed under the [Apache License, Version 2.0](LICENSE.txt).  
There is NO WARRANTY, to the extent permitted by law.

![http://madm.dfki.de/lib/tpl/dfki/images/logo.jpg](http://madm.dfki.de/lib/tpl/dfki/images/logo.jpg)
