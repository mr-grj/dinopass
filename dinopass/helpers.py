from rich.console import Console
from rich.table import Table


def pretty_print(title, data):
    console = Console()
    columns_to_display = ('name', 'password',)

    if not data:
        console.print('\nNo data available!\n', justify="center", style="bold red")
        return

    table = Table(title=f'[bold red][u]{title}[/u][/bold red]', show_lines=True)

    for column in columns_to_display:
        table.add_column(column.upper(), justify='center', style='magenta', no_wrap=True)

    for item in data:
        table.add_row(item['password_name'], item['password_value'])

    console.print(table)
