#!/bin/bash
WGET='/usr/bin/wget -q'
MD5SUM='/usr/bin/md5sum'
GUNZIP='/bin/gunzip'
RM='/bin/rm'

$RM -r delegated-afrinic-latest.md5
$WGET ftp://ftp.afrinic.net/pub/stats/afrinic/delegated-afrinic-latest.md5
if ! $MD5SUM --check delegated-afrinic-latest.md5 > /dev/null 2>&1; then
  $RM -f delegated-afrinic-latest
  $WGET ftp://ftp.afrinic.net/pub/stats/afrinic/delegated-afrinic-latest
fi

$RM -f delegated-lacnic-latest.md5
$WGET ftp://ftp.lacnic.net/pub/stats/lacnic/delegated-lacnic-latest.md5
if ! $MD5SUM --check delegated-lacnic-latest.md5 > /dev/null 2>&1; then
  $RM -f delegated-lacnic-latest
  $WGET ftp://ftp.lacnic.net/pub/stats/lacnic/delegated-lacnic-latest
fi

$RM -f delegated-arin-extended-latest.md5
$WGET ftp://ftp.arin.net/pub/stats/arin/delegated-arin-extended-latest.md5
sed -i 's/[0-9]*$/latest/g' delegated-arin-extended-latest.md5
if ! $MD5SUM --check delegated-arin-extended-latest.md5 > /dev/null 2>&1; then
  $RM -f delegated-arin-extended-latest
  $WGET ftp://ftp.arin.net/pub/stats/arin/delegated-arin-extended-latest
fi

$RM -f delegated-apnic-latest.md5
$WGET ftp://ftp.apnic.net/pub/stats/apnic/delegated-apnic-latest.md5
if ! $MD5SUM --check delegated-apnic-latest.md5 > /dev/null 2>&1; then
  $RM -f delegated-apnic-latest
  $RM -f apnic.db.inetnum*
  $WGET ftp://ftp.apnic.net/pub/stats/apnic/delegated-apnic-latest
ftp -n -v ftp.apnic.net <<END
  user anonymous -anonymous@anonymous.org
  binary
  passive
  get /apnic/whois/apnic.db.inetnum.gz apnic.db.inetnum.gz
  bye
END
  $GUNZIP apnic.db.inetnum
fi

$RM -f delegated-ripencc-latest.md5
$WGET ftp://ftp.ripe.net/ripe/stats/delegated-ripencc-latest.md5
if ! $MD5SUM --check delegated-ripencc-latest.md5 > /dev/null 2>&1; then
  $RM -f delegated-ripencc-latest
  $RM -f ripe.db.inetnum*
  $WGET ftp://ftp.ripe.net/ripe/stats/delegated-ripencc-latest
  $WGET ftp://ftp.ripe.net/ripe/dbase/split/ripe.db.inetnum.gz
  $GUNZIP ripe.db.inetnum
fi
