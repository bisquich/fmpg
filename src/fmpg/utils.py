import subprocess

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


def to_seconds(timer: str) -> str:
    parts = timer.split(":")
    if len(parts) > 3:
        raise ValueError(f"too many parts ({len(parts)}), max is hh:mm:ss: {timer!r}")

    total = 0
    for part in parts:
        total = total * 60 + int(part)
    return str(total)


def source_video_codec(filename: str) -> str:
    codec = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
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
    return codec.stdout.strip()


def get_video_encoder(video_codec: str) -> str:
    return VIDEO_ENCODERS.get(video_codec, "libx264")

def source_audio_codec(filename: str) -> str:
    codec = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "a:0",
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
    return codec.stdout.strip()

def get_audio_encoder(audio_codec: str) -> str:
    return AUDIO_ENCODERS.get(audio_codec, "aac")
