from rich.console import Console
from rich.table import Table


def pp(title, data):
    title = f'[bold red][u]{title}[/u][/bold red]'
    table = Table(title=title, show_lines=True)

    console = Console()

    table.add_column("NAME", justify="center", style="magenta", no_wrap=True)
    table.add_column("PASSWORD", justify="center", style="bold green", no_wrap=True)

    for item in data:
        table.add_row(item['name'], item['value'])

    console.print(table)
