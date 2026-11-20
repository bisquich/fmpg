from collections import namedtuple
from pathlib import Path

import click

from fmpg import decorators, utils

Command = namedtuple("Command", ["cmd", "output"])


@click.command()
@decorators.add_generic_options(
    "input", "start", "to", "duration", "output", "vcodec", "acodec"
)
@click.option("--fast", is_flag=True, help="Use stream copy instead of re-encoding.")
@decorators.ffmpeg_command
def trim(input, start, to, duration, output, vcodec, acodec, fast) -> Command:
    """\b
    Examples:
    # Cut from 4s to 10s
    fmpg trim -i video.mp4 -f 4 -t 10

    \b
    # Cut 82s (or 01:12 mins) starting at 00:44, with a custom output name
    fmpg trim -i video.mp4 --from 00:44 --duration 82 --output song_from_video.mp4

    \b
    # Print the ffmpeg command without running it
    fmpg trim -i video.mp4 -f 30 -t 120 --dry-run
    """
    if (to is None) == (duration is None):
        raise click.UsageError("Provide exactly one of --to or --duration.")
    if fast and (vcodec or acodec):
        raise click.UsageError("--vcodec and --acodec can't be used with --fast.")

    # Bases
    cmd = ["ffmpeg"]
    cmd += ["-ss", start] if start else []
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
