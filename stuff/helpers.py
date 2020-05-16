from rich.console import Console
from rich.table import Table


from argparse import ArgumentParser


def pp(title, data):
    title = f'[bold red][u]{title}[/u][/bold red]'
    table = Table(title=title, show_lines=True)

    console = Console()

    table.add_column("GROUP", justify="center", style="cyan", no_wrap=True)
    table.add_column("NAME", justify="center", style="magenta", no_wrap=True)
    table.add_column("PASSWORD", justify="center", style="bold green", no_wrap=True)

    for item in data:
        table.add_row(item['group'], item['name'], item['password'])

    console.print(table)


def command_line_parser():
    parser = ArgumentParser(
        description='Simple CLI Password manager for personal use',
        epilog='All the arguments are mutually exclusive'
    )
    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument(
        '-a', '--all',
        action='store_true',
        help='List all credentials'
    )
    group.add_argument(
        '-p', '--purge',
        action='store_true',
        help='Purge all credentials'
    )

    group.add_argument(
        '-c', '--create',
        nargs=3,
        metavar=('<name>', '<group>', '<password>'),
        help='Create a new credential with a specific name, in a specific group, with a specific password',
    )
    group.add_argument(
        '-g', '--get',
        nargs=2,
        metavar=('<field>', '<value>'),
        help='Get a specific credential by name/group value'
    )
    group.add_argument(
        '-u', '--update',
        nargs=4,
        metavar=('<field>', '<value>', '<field_to_update>', '<new_value>'),
        help='Update a credential field matching a specific condition with a new value'
    )
    group.add_argument(
        '-d', '--delete',
        nargs=2,
        metavar=('<field>', '<value>'),
        help='Delete a specific credential by name/group value'
    )

    return parser
