import subprocess
from pathlib import Path

import click

# Reference: https://ffmpeg.org/ffmpeg-codecs.html
VIDEO_ENCODERS = {
    "h264": "libx264",
    "hevc": "libx265",
    "vp8": "libvpx",
    "vp9": "libvpx-vp9",
    "av1": "libsvtav1",  # alternatives: libaom-av1, librav1e
    "mpeg4": "mpeg4",
    "mpeg2video": "mpeg2video",
    "mpeg1video": "mpeg1video",
    "theora": "libtheora",
    "h263": "h263",
    "flv1": "flv",
    "msmpeg4v2": "msmpeg4v2",
    "msmpeg4v3": "msmpeg4",
    "wmv1": "wmv1",
    "wmv2": "wmv2",
    "mjpeg": "mjpeg",
    "prores": "prores_ks",
    "dnxhd": "dnxhd",
    "ffv1": "ffv1",
    "huffyuv": "huffyuv",
    "gif": "gif",
    "rawvideo": "rawvideo",
}

AUDIO_ENCODERS = {
    "aac": "aac",
    "mp3": "libmp3lame",
    "mp2": "mp2",
    "opus": "libopus",
    "vorbis": "libvorbis",
    "flac": "flac",
    "alac": "alac",
    "ac3": "ac3",
    "eac3": "eac3",
    "wmav1": "wmav1",
    "wmav2": "wmav2",
    "pcm_s16le": "pcm_s16le",
    "pcm_s24le": "pcm_s24le",
}

# References:
#   - https://trac.ffmpeg.org/wiki/Encode/H.264  (CRF scale, 17-18 "visually lossless")
#   - https://trac.ffmpeg.org/wiki/Encode/H.265  (x265 default CRF 28 ~ x264 CRF 23)

# CRF is a quality target: lower means better quality and bigger file.
# The scale is not shared between encoders, so that's why each one gets its own value.
CRF = {
    "libx264": "18",  # 17-18 is "visually lossless or nearly so"
    "libx265": "23",  # x264's 18 shifted by the +5 gap between the defaults (23 -> 28).
}

ABITRATE = {
    "aac": "192k",
    "libmp3lame": "192k",
    "libopus": "128k",
    "libvorbis": "192k",
}


def to_seconds(timer: str) -> str:
    parts = timer.split(":")
    if len(parts) > 3:
        raise ValueError(f"too many parts ({len(parts)}), max is hh:mm:ss: {timer!r}")

    total = 0
    for part in parts:
        total = total * 60 + int(part)
    return str(total)


def source_codec(filename: str, stream: str) -> str:
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


def source_video_codec(filename: str) -> str:
    return source_codec(filename, "v:0")


def source_audio_codec(filename: str) -> str:
    return source_codec(filename, "a:0")


def get_video_encoder(video_codec: str) -> str:
    return VIDEO_ENCODERS.get(video_codec, "libx264")


def get_audio_encoder(audio_codec: str) -> str:
    return AUDIO_ENCODERS.get(audio_codec, "aac")


def vcodec_args(filename, vcodec) -> list:
    video_encoder = vcodec or get_video_encoder(source_video_codec(filename))
    arg = ["-c:v", video_encoder]

    if video_encoder in CRF:
        arg += ["-preset", "fast", "-crf", CRF[video_encoder]]

    return arg


def acodec_args(filename: str, acodec: str | None = None) -> list[str]:
    if acodec == "copy":
        return ["-c:a", "copy"]

    if acodec:
        encoder = AUDIO_ENCODERS.get(acodec, acodec)
    else:
        source = source_audio_codec(filename)
        if not source:
            return []  # No audio stream
        encoder = get_audio_encoder(source)

    args = ["-c:a", encoder]
    if encoder in ABITRATE:
        args += ["-b:a", ABITRATE[encoder]]
    return args


def ctime_ns(path: Path):
    """Returns the file in path's creation time in nanoseconds."""
    try:
        return path.stat().st_ctime_ns
    except FileNotFoundError:
        return None


def run_cmd(cmd, output: Path):
    out = Path(output)
    before = ctime_ns(out)

    subprocess.run(cmd, check=True)

    # Check if the file is actually created before returning
    # the output file name
    after = ctime_ns(out)
    if after is None or (before is not None and after <= before):
        raise click.ClickException(
            f"ffmpeg exited cleanly but {output} wasn't written."
        )
    if out.stat().st_size == 0:
        raise click.ClickException(f"{output} is empty.")

    click.echo(output)
