#Comand line interpreter
from ip_countryside_utilities import get_record_by_ip
import click

@click.group()
def cli():
    """ip-countryside manager"""
    pass

@cli.command(name='update', help='update database')
@click.option('--force', '-f', is_flag=True, help="Forcing update.")
def update(force):
    if force:
        click.echo('forcing update')
    else:
        click.echo('updating if old enough')

@cli.command(name='parse', help='parsing IP')
@click.argument('IP')
def parse(ip):
    click.echo('Parsing ' + ip)

if __name__ == "__main__":
    cli()