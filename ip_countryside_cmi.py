#Comand line interpreter

import click
import ipaddress
import sys

from Console_Selector import *

@click.group()
def cli():
    """ip-countryside manager"""
    pass

@cli.command(name='update', help='update database')
@click.option('--force', '-f', is_flag=True, help="Forcing update.")
@click.option('--multicore', '-m', is_flag=True, help='Enabeling multicore parsing')
@click.option('--output', '-o', multiple=True, help="Format option for update.")
#@click.option('--split', '-s', is_flag=True, help="Seperating IPv4 and IPv6.")
def update(force, multicore, output):
    click.echo('\n')
    click.echo('Is Force = ' + str(force))
    click.echo('\nIs multicore = ' + str(multicore))
    click.echo('\nOutput options:')
    click.echo('\n'.join(output))
    click.echo('\n----------------------------------------------------------\n')
    CallUpdate(force, multicore, output)

@cli.command(name='trace', help='tracing IP')
@click.argument('IP')
def trace(ip):
    if(checkIp(ip)):
        click.echo('tracing ' + ip)
        result = CallTrace(ip)
        for entry in result:
            click.echo(entry)
    else:
        pass

@cli.command(name='query', help='querying IP')
@click.option('--all', '-a', is_flag=True, help="Get all Information")
@click.argument('IP')
def query(ip, all):
    if(checkIp(ip)):
        click.echo('querying ' + ip)
        result = CallParse(ip, all)
        click.echo(result)
    else:
        pass

def checkIp(ip):
    try:
        ip = ipaddress.ip_address(ip)
        click.echo('%s is a correct IP%s address.' % (ip, ip.version))
        return True
    except ValueError:
        click.echo('address/netmask is invalid: %s' % sys.argv[1])
        return False
    except:
        click.echo('Usage : %s  ip' % sys.argv[0])
        return False


if __name__ == "__main__":
    cli()