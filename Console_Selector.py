#from . import ip_countryside_downloader as dwn
import click

from ip_countryside_downloader import *
from ip_countryside_utilities import *
from ip_countryside_parser import *
from ip_countryside_db import *


def CallUpdate(force, multicore, output):
    if(force):
        click.echo("Forcing Update!")
        #download_del_files(True)
    else:
        click.echo("Check if files are old enough for update.")
        #download_del_files()
    click.echo('parsing database')
    #run_parser(multicore)
    click.echo('csv created')
    evaluateOutput(output)


def CallParse(ip, getAll):
    return get_record_by_ip_cli(ip, getAll)



def CallTrace(ip):
    return traceIP(ip)



def evaluateOutput(output):
    for entry in output:
        entry = str(entry).lower()
        if entry == 'mmdb':
            click.echo('creating mmdb')
            #extract_as_mmdb()
        elif entry == 'json':
            click.echo('creating json')
            #extract_as_json()
        elif entry == 'yaml':
            click.echo('creating yaml')
            #extract_as_yaml()
        elif entry == 'mysql':
            click.echo('creating mysql')
            #extract_as_mysql()
        elif entry == 'sqllite':
            click.echo('creating sqllite')
            #extract_as_sqllite()
        else: 
            click.echo('format not valid (' + entry + ')')
            continue