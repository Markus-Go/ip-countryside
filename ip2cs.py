#!/usr/bin/env python3

import sys

try:
    import click
except ModuleNotFoundError:
    print("module 'click' is not installed")
    sys.exit()

from ip_countryside_downloader import *
from ip_countryside_utilities import *
from ip_countryside_parser import *
from ip_countryside_db import *

@click.group()
def cli():
    """ip-countryside manager"""
    pass

@cli.command(name='update', help='Update database and write output')
@click.option('--force', '-f', is_flag=True, help="Forcing update.")
@click.option('--multicore', '-m', is_flag=True, help='Enabeling multicore parsing')
@click.option('--output', '-o', multiple=True, help="Format option for update. " + str(FORMATS).replace("'",""))
#@click.option('--split', '-s', is_flag=True, help="Seperating IPv4 and IPv6.")
def update(force, multicore, output):
    click.echo("Updating ... Download is ", nl=False)
    if force is not True:
        click.echo('not ', nl=False)
    click.echo('forced. Multicore is ', nl=False)
    if multicore is True:
        click.echo('enabled.')
    else:
        click.echo('disabled.')
    click.echo('Output options: ', nl=False)
    if len(output) == 0:
        click.echo('default (CSV)')
    else:
        for o in output:
            if o not in FORMATS:
                click.echo("Incorrect output format: " + o)
                return
        click.echo(' '.join(output))
    click.echo('----------------------------------------------------------\n')
    doUpdate(force, multicore, output)
    sys.exit()

@cli.command(name='trace', help='Trace an IP for debugging reasons')
@click.argument('IP')
def trace(ip):
    if(checkIp(ip)):
        click.echo('Tracing ' + ip + "...")
        result =  traceIP(ip)
        for entry in result:
            click.echo(entry)
    else:
        pass

@cli.command(name='query', help='Query an IP v4 or v6 address')
@click.option('--all', '-a', is_flag=True, help="Display all information")
@click.argument('IP')
def query(ip, all):
    if(checkIp(ip)):
        click.echo('querying ' + ip)
        result = get_record_by_ip(ip)
        if not result: click.echo('IP not found')
        else:
            (ip_from, ip_to, cc, status) = result
            if all or cc == 'ZZ':
                click.echo(' '.join(map(str, [ip_from, ip_to, cc, COUNTRY_DICTIONARY[cc], status])))
            else:
                click.echo(' '.join((cc, COUNTRY_DICTIONARY[cc])))
    else:
        pass

@cli.command(name='convert', help='Write a new output format, requires that "update" was run before!')
@click.option('--output', '-o', multiple=True, help="Format option for output. " + str(FORMATS).replace("'",""))
#@click.option('--split', '-s', is_flag=True, help="Seperating IPv4 and IPv6.")
def convert(output):
    click.echo('Output options: ', nl=False)
    if len(output) == 0 or (len(output) == 1 and 'csv' in output):
        click.echo('Nothing to do.')
        return
    else:
        for o in output:
            if o not in FORMATS:
                click.echo("Incorrect output format: " + o)
                return
        click.echo(' '.join(output))
    writeOutputFormat(output)
    sys.exit()


def checkIp(ip):
    try:
        ip = ipaddress.ip_address(ip)
        click.echo('%s is a correct IP%s address.' % (ip, ip.version))
        return True
    except ValueError:
        click.echo('IP address is invalid: %s' % sys.argv[2])
        return False
    except:
        click.echo('Usage : %s  ip' % sys.argv[0])
        return False

def doUpdate(force, multicore, output):
    if(force):
        click.echo("Forcing Update.")
        download_del_files(True)
    else:
        click.echo("Checking if files are up-to-date for update.")
        download_del_files()
    click.echo('Parsing database...')
    run_parser(multicore)
    click.echo('CSV created!')
    writeOutputFormat(output)

def writeOutputFormat(output):
    for entry in output:
        entry = str(entry).lower()
        if entry == 'mmdb':
            click.echo('Creating mmdb output...')
            extract_as_mmdb_fast()
        elif entry == 'json':
            click.echo('Creating json output...')
            extract_as_json()
        elif entry == 'yaml':
            click.echo('Creating yaml output...')
            extract_as_yaml()
        elif entry == 'mysql':
            click.echo('Creating MySQL script...')
            extract_as_mysql()
        elif entry == 'sqlite':
            click.echo('Creating sqlite database...')
            extract_as_sqlite()

if __name__ == "__main__":
    cli()