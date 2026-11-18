import click

from fmpg import commands


@click.group()
def main() -> None:
    pass

main.add_command(commands.trim)
