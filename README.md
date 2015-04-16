ip-countryside
==============

This tool creates an ip-to-country database, which can be used in multiple 
applications for geolocating internet users based on  their IP address.

<b>If you only need the ip2country database itself (not the program creating 
it),  
you can <a 
href='http://madm.dfki.de/demo/ip-countryside/ip2country.zip'>download 
it here</a> (updated weekly).</b>

Detailed Information
--------------------

This tool creates an ip-to-country database, which can be used in multiple 
applications for geolocating internet users based on their IP address.
The database is built automatically out of the 5 Regional Internet Registrars (RIR)
databases: AFRINIC, APNIC, ARIN, LACNIC and RIPE. The resulting database is a plain
sorted text file in the format 

    "ip_from ip_to country_code" 
    
where IPs are 32 bit integers and the 2 letter country code is as defined in 
ISO 3166. This tool uses the delegation files of all RIRs and additionally for 
APNIC and RIPE it uses the detailed databases.

In contrast to other tools, our database is free, self-creatable and more accurate.

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
Copyright 2008-2015 Markus Goldstein

This is free software. Licensed under the [Apache License, Version 
2.0](LICENSE.txt).  
There is NO WARRANTY, to the extent permitted by law.

![http://madm.dfki.de/lib/tpl/dfki/images/logo.jpg](http://madm.dfki.de/lib/tpl/
dfki/images/logo.jpg)
