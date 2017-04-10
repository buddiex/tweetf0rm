import click

# @click.group()
# @click.option('--debug/--no-debug', default=False)
# @click.pass_context
# def cli(ctx, debug):
#     ctx.obj['DEBUG'] = debug

# @cli.command()
# @cli.argument
# @click.pass_context
# def sync(ctx):
#     """Command on cli1"""
#     click.echo('Debug is %s' % (ctx.obj['DEBUG'] and 'on' or 'off'))

# if __name__ == '__main__':
#     cli(obj={})



@click.group()
@click.argument('filename')
@click.argument('config')
@click.argument('src', nargs=-1)
@click.argument('dst', nargs=1)
@click.option('--check_proxies', is_flag=True) 
@click.pass_context
def cli(ctx, config, filename, check_proxies):
    ctx.obj['config'] = config

@cli.command()
@click.pass_context
def cmd1(ctx):
    """Command on cli1 --id asdfsf """
    print ("asdf" + ctx.obj['config'])

@cli.command()
def cmd2():
    """Command on cli21"""

@cli.command()
def cmd3():
    """Command on cli22"""    

# cli = click.CommandCollection(sources=[cli2])
if __name__ == '__main__':
    cli(obj={})