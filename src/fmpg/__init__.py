import click

from fmpg import commands


@click.group()
@click.version_option("0.1.0", "-V", "--version")
def main() -> None:
    pass

main.add_command(commands.trim)
