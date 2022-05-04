#Comand line interpreter

import click
import ipaddress
import sys

@click.group()
def cli():
    """ip-countryside manager"""
    pass

@cli.command(name='update', help='update database')
@click.option('--force', '-f', is_flag=True, help="Forcing update.")
@click.option('--output', '-o', multiple=True, help="Format option for update.")
@click.option('--split', '-s', is_flag=True, help="Seperating IPv4 and IPv6.")
def update(force, output, split):
    #if force:
    #    click.echo('forcing update\n' + 'output = ' + output + '\nSeperating IP = ' + ip)
    #else:
    #    click.echo('updating if old enough\n' + 'output = ' + join(output) + '\nSeperating IP = ' + ip)
    click.echo('Is Force = ' + str(force))
    click.echo('\nOutput options:')
    click.echo('\n'.join(output))
    click.echo('\nSplit IP = ' + str(split))

@cli.command(name='trace', help='tracing IP')
@click.argument('IP')
def trace(ip):
    if(checkIp(ip)):
        click.echo('tracing ' + ip)
    else:
        pass

@cli.command(name='query', help='querying IP')
@click.argument('IP')
def query(ip):
    if(checkIp(ip)):
        click.echo('querying ' + ip)
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