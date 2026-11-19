from pathlib import Path

import click

from fmpg import decorators, utils


# TODO: Put acodec, vcodec, exception_handler, and one_of_two in decorators
@click.command()
@click.argument("filename", type=click.Path(exists=True, dir_okay=False))
@click.option("start", "--from", "-f", required=True, help="Start time.")
@click.option("--to", "-t", help="End time.")
@click.option("--duration", "-d", help="Duration.")
@click.option("--output", "-o", help="Output file name.")
@click.option("--vcodec", help="Video encoder, e.g. libx264. Default: match the input's codec.")
@click.option("--acodec", help="Audio encoder, e.g. aac. Default: match the input's codec.")
@click.option("--fast", is_flag=True, help="Use stream copy instead of re-encoding.")
@decorators.exception_handler
@decorators.with_dry_run
def trim(filename, start, to, duration, output, vcodec, acodec, fast):
    if (to is None) == (duration is None):
        raise click.UsageError("Provide exactly one of --to or --duration.")
    if fast and (vcodec or acodec):
        raise click.UsageError("--vcodec and --acodec can't be used with --fast.")

    # Bases
    cmd = ["ffmpeg", "-ss", start]
    cmd += ["-to", to] if to else ["-t", duration]
    cmd += ["-i", filename]

    # Output options
    if fast:
        cmd += ["-c", "copy"]
    else:
        cmd += utils.vcodec_args(filename, vcodec)
        cmd += utils.acodec_args(acodec)

    if output is None:
        p = Path(filename)
        output = str(p.with_name(f"{p.stem}.trimmed{p.suffix}"))

    cmd.append(output)

    return cmd
