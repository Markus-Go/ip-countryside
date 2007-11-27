#!/bin/bash
rm -f delegated-afrinic-latest
rm -f delegated-lacnic-latest
rm -f delegated-arin-latest
rm -f delegated-apnic-latest
rm -f delegated-ripencc-latest
rm -f ripe.db.inetnum
rm -f apnic.db.inetnum
rm -f ripe.db.inetnum.gz
rm -f apnic.db.inetnum.gz
wget ftp://ftp.afrinic.net/pub/stats/afrinic/delegated-afrinic-latest
wget ftp://ftp.lacnic.net/pub/stats/lacnic/delegated-lacnic-latest
wget ftp://ftp.arin.net/pub/stats/arin/delegated-arin-latest
wget ftp://ftp.apnic.net/pub/stats/apnic/delegated-apnic-latest
wget ftp://ftp.ripe.net/ripe/stats/delegated-ripencc-latest
wget ftp://ftp.ripe.net/ripe/dbase/split/ripe.db.inetnum.gz
wget ftp://ftp.apnic.net/apnic/whois-data/APNIC/split/apnic.db.inetnum.gz
gunzip ripe.db.inetnum
gunzip apnic.db.inetnum