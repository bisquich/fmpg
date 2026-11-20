import json
import subprocess
from pathlib import Path

import click

from fmpg import codec_options


def source_codec(filename: str, stream: str) -> str:
    """Run ffprobe to get a video or audio codec."""
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            stream,
            "-show_entries",
            "stream=codec_name",
            "-of",
            "csv=p=0",
            filename,
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def source_bitrate(filename: str, stream: str) -> int | None:
    """Bits/s of a stream. Return None if the file doesn't report one."""
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", stream,
         "-show_entries", "stream=bit_rate:stream_tags", "-of", "json", filename],
        capture_output=True, text=True, check=True,
    ).stdout
    info = (json.loads(out).get("streams") or [{}])[0]
    candidates = [info.get("bit_rate")]
    candidates += [v for k, v in info.get("tags", {}).items() if k.upper().startswith("BPS")]
    return next((int(v) for v in candidates if v and str(v).isdigit()), None)


def _quality_flag(opts: dict[str, str], flags: tuple[str, ...]) -> str | None:
    """Return the flag in opts that controls quality, or None (e.g. lossless)."""
    return next((flag for flag in flags if flag in opts), None)


def get_audio_encoder(audio_codec: str) -> str:
    """Get audio encoder of a audio codec. Default is aac."""
    return codec_options.AUDIO_ENCODERS.get(audio_codec, "aac")


def get_video_encoder(video_codec: str) -> str:
    """Get video encoder of a video codec. Default is libx264."""
    return codec_options.VIDEO_ENCODERS.get(video_codec, "libx264")


def vcodec_args(
    filename: str, vcodec: str | None = None, quality: str | None = None
) -> list[str]:
    """Build ffmpeg video codec arguments.

    No vcodec: the source's codec at the source's bitrate (falls back to the
    VIDEO_OPTS default if the file doesn't report one).
    With vcodec: that encoder's VIDEO_OPTS defaults.
    quality, if given, replaces the encoder's quality value in either case."""
    if vcodec:
        encoder = codec_options.VIDEO_ENCODERS.get(vcodec, vcodec)
    else:
        encoder = get_video_encoder(source_codec(filename, "v:0"))

    opts = dict(codec_options.VIDEO_OPTS.get(encoder, {}))
    flag = _quality_flag(opts, codec_options.VIDEO_QUALITY_FLAGS)

    if quality:
        if flag is None:
            raise click.UsageError(f"{encoder} has no quality setting to override.")
        opts[flag] = quality
    elif not vcodec and flag in ("-crf", "-q:v") and (bitrate := source_bitrate(filename, "v:0")):
        del opts[flag]
        opts["-b:v"] = str(bitrate)

    args = ["-c:v", encoder]
    for opt, value in opts.items():
        args += [opt, value]
    return args


def acodec_args(
    filename: str, acodec: str | None = None, quality: str | None = None
) -> list[str]:
    """Build ffmpeg audio codec arguments.

    No acodec: the source's codec at the source's bitrate (falls back to the
    AUDIO_OPTS default if the file doesn't report one).
    With acodec: that encoder's AUDIO_OPTS defaults.
    quality, if given, replaces the encoder's quality value in either case."""
    if acodec:
        encoder = codec_options.AUDIO_ENCODERS.get(acodec, acodec)
    else:
        encoder = get_audio_encoder(source_codec(filename, "a:0"))

    opts = dict(codec_options.AUDIO_OPTS.get(encoder, {}))
    flag = _quality_flag(opts, codec_options.AUDIO_QUALITY_FLAGS)

    if quality:
        if flag is None:
            raise click.UsageError(f"{encoder} has no quality setting to override.")
        opts[flag] = quality
    elif not acodec and flag and (bitrate := source_bitrate(filename, "a:0")):
        del opts[flag]               # bitrate replaces VBR quality (-q:a) too
        opts["-b:a"] = str(bitrate)

    args = ["-c:a", encoder]
    for opt, value in opts.items():
        args += [opt, value]
    return args


def ctime_ns(path: Path):
    """Return a file's creation time in nanoseconds."""
    try:
        return path.stat().st_ctime_ns
    except FileNotFoundError:
        return None


def run_cmd(cmd: list[str], output: Path) -> Path:
    """Run cmd and check that output was written.

    Return output. Raise ClickException if the command fails or the
    file is missing or empty.
    """
    output = Path(output)
    before = ctime_ns(output)

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        raise click.ClickException(
            f"{e.cmd[0]} failed with exit code {e.returncode}"
        ) from e

    after = ctime_ns(output)
    if after is None or (before is not None and after <= before):
        raise click.ClickException(
            f"{cmd[0]} exited cleanly but {output} wasn't written."
        )
    if output.stat().st_size == 0:
        raise click.ClickException(f"{output} is empty.")

    return output
