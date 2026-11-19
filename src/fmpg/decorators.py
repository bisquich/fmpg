import functools
import shlex
import subprocess

import click


def exception_handler(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except subprocess.CalledProcessError as e:
            raise click.ClickException(f"{e.cmd[0]} failed with exit code {e.returncode}")
    return wrapper


def with_dry_run(f):
    @click.option("--dry-run", is_flag=True, help="Print the command instead of running it.")
    @functools.wraps(f)
    def wrapper(*args, dry_run, **kwargs):
        cmd = f(*args, **kwargs)
        if dry_run:
            click.echo(shlex.join(cmd))
        else:
            subprocess.run(cmd, check=True)
    return wrapper
