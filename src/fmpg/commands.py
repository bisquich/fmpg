from collections import namedtuple
from pathlib import Path

import click

from fmpg import decorators, utils

Command = namedtuple('Command', ['cmd', 'output'])


@click.command()
@decorators.add_generic_options("input", "start", "to", "duration", "output", "vcodec", "acodec")
@click.option("--fast", is_flag=True, help="Use stream copy instead of re-encoding.")
@decorators.exception_handler
@decorators.with_dry_run_option
def trim(input, start, to, duration, output, vcodec, acodec, fast) -> Command:
    if (to is None) == (duration is None):
        raise click.UsageError("Provide exactly one of --to or --duration.")
    if fast and (vcodec or acodec):
        raise click.UsageError("--vcodec and --acodec can't be used with --fast.")

    # Bases
    cmd = ["ffmpeg", "-ss", start]
    cmd += ["-to", to] if to else ["-t", duration]
    cmd += ["-i", input]

    # Output options
    if fast:
        cmd += ["-c", "copy"]
    else:
        cmd += utils.vcodec_args(input, vcodec)
        cmd += utils.acodec_args(input, acodec)

    if output is None:
        p = Path(input)
        output = str(p.with_name(f"{p.stem}.trimmed{p.suffix}"))

    cmd.append(output)

    return Command(cmd, output)
