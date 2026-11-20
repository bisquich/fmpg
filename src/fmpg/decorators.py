import functools
import shlex

import click

from fmpg import utils


def ffmpeg_command(f):
    """Add --dry-run and run the (cmd, output) pair that f returns."""

    @click.option(
        "--dry-run", is_flag=True, help="Print the command instead of running it."
    )
    @functools.wraps(f)
    def wrapper(*args, dry_run, **kwargs):
        cmd, output = f(*args, **kwargs)
        if dry_run:
            click.echo(shlex.join(cmd))
        else:
            click.echo(utils.run_cmd(cmd, output))

    return wrapper


GENERIC_OPTIONS = {
    "start": (("start", "--from", "-f"), {"help": "Start time: SS, MM:SS, or HH:MM:SS."}),
    "to": (("--to", "-t"), {"help": "End time: SS, MM:SS, or HH:MM:SS."}),
    "duration": (("-d", "--duration"), {"help": "Output duration: SS, MM:SS, or HH:MM:SS."}),
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
        {"help": "Video encoder, e.g. libx264 or h264. Default is the input's codec and bitrate."},
    ),
    "vquality": (
        ("--vquality",),
        {"help": "Video quality in the encoder's own scale, e.g. 18 (CRF) for libx264."},
    ),
    "acodec": (
        ("--acodec",),
        {"help": "Audio encoder, e.g. aac or mp3. Default is the input's codec and bitrate."},
    ),
    "aquality": (
        ("--aquality",),
        {"help": "Audio quality in the encoder's own scale, e.g. 192k for aac, 2 for libmp3lame."},
    ),
}


def add_generic_options(*names):
    """Example usage as a decorator:
    ```@add_generic_operations("input", "start", "to", "duration", "output")"""
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
