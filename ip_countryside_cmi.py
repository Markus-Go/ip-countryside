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
@click.option('--split', '-s', is_flag=True, help="Seperating IPv4 and IPv6.")
def update(force, multicore, output, split):
    click.echo('Is Force = ' + str(force))
    click.echo('\nIs multicore = ' + str(multicore))
    click.echo('\nSplit IP = ' + str(split))
    click.echo('\nOutput options:')
    click.echo('\n'.join(output))
    CallUpdate(force)

@cli.command(name='trace', help='tracing IP')
@click.argument('IP')
def trace(ip):
    if(checkIp(ip)):
        click.echo('tracing ' + ip)
        result = CallTrace(ip)
        click.echo(result)
    else:
        pass

@cli.command(name='query', help='querying IP')
@click.argument('IP')
def query(ip):
    if(checkIp(ip)):
        click.echo('querying ' + ip)
        result = CallParse(ip)
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