import functools
import shlex
import subprocess

import click

from fmpg import utils


def exception_handler(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except subprocess.CalledProcessError as e:
            raise click.ClickException(
                f"{e.cmd[0]} failed with exit code {e.returncode}"
            )

    return wrapper


def with_dry_run_option(f):
    @click.option(
        "--dry-run", is_flag=True, help="Print the command instead of running it."
    )
    @functools.wraps(f)
    def wrapper(*args, dry_run, **kwargs):
        cmd, output = f(*args, **kwargs)
        if dry_run:
            click.echo(shlex.join(cmd))
        else:
            utils.run_cmd(cmd, output)

    return wrapper

GENERIC_OPTIONS = {
    "start": (
        ("start", "--from", "-f"),
        {"required": True, "help": "Start time."}
    ),
    "to": (
        ("--to", "-t"),
        {"help": "End time."}
    ),
    "duration": (
        ("-d", "--duration"),
        {"help": "Set duration of the output."}
    ),
    "input": (
        ("-i", "--input"),
        {"required": True, "type": click.Path(), "help": "Input file."},
    ),
    "output": (
        ("-o", "--output"),
        {"type": click.Path(), "help": "Output file."},
    ),
    "vcodec": (
        ("--vcodec",),
        {"help": "Video encoder, e.g. libx264. Default is the input's codec."},
    ),
    "acodec": (
        ("--acodec",),
        {"help": "Audio encoder, e.g. aac. Default is the input's codec."},
    ),
}


def add_generic_options(*names):
    def wrapper(f):
        # reversed to keep --help in the correct order
        for name in reversed(names):
            option = GENERIC_OPTIONS.get(name)
            if option is None:
                raise ValueError(f"Option {name} is not available in GENERIC_OPTIONS")
            flags, kwargs = option
            f = click.option(*flags, **kwargs)(f)
        return f

    return wrapper
