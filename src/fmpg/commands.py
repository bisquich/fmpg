import subprocess
from pathlib import Path

import click

from fmpg import utils


# TODO: Put acodec, vcodec, exception handler, in decorators
@click.command()
@click.argument("filename", type=click.Path(exists=True, dir_okay=False))
@click.option("--from", "-f", "start", required=True, help="Start time.")
@click.option("--to", "-t", help="End time.")
@click.option("--duration", "-d", help="Duration.")
@click.option("--output", "-o", help="Output file name.")
@click.option(
    "--vcodec", help="Video encoder, e.g. libx264. Default: match the input's codec."
)
@click.option(
    "--acodec", help="Audio encoder, e.g. aac. Default: match the input's codec."
)
@click.option("--fast", is_flag=True, help="Use stream copy instead of re-encoding.")
def trim(
    filename: str,
    start: str,
    to: str | None,
    duration: str | None,
    output: str | None,
    vcodec: str | None,
    acodec: str | None,
    fast: bool,
):
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
        video_encoder = vcodec or utils.get_video_encoder(
            utils.source_video_codec(filename)
        )
        cmd += ["-c:v", video_encoder]

        # References:
        #   - https://trac.ffmpeg.org/wiki/Encode/H.264  (CRF scale, 17-18 "visually lossless")
        #   - https://trac.ffmpeg.org/wiki/Encode/H.265  (x265 default CRF 28 ~ x264 CRF 23)

        # CRF is a quality target: lower means better quality and bigger file.
        # The scale is not shared between encoders, so that's why each one gets its own value.
        CRF = {
            "libx264": "18",  # 17-18 is "visually lossless or nearly so"
            "libx265": "23",  # x264's 18 shifted by the +5 gap between the defaults (23 -> 28).
        }

        if video_encoder in CRF:
            cmd += ["-preset", "fast", "-crf", CRF[video_encoder]]

        audio_source = utils.source_audio_codec(filename)
        if acodec or audio_source:
            cmd += ["-c:a", acodec or utils.get_audio_encoder(audio_source)]

    if output is None:
        p = Path(filename)
        output = str(p.with_name(f"{p.stem}.trimmed{p.suffix}"))

    cmd.append(output)

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        raise click.ClickException(f"ffmpeg failed with exit code {e.returncode}")
