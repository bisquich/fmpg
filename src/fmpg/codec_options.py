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


# Most of these were taken directly from handbrake, ffmpeg, and Google.
# Except: libx265 crf 24 (between handbrake's and ffpmeg's numbers), libaom cpu-used 6 / row-mt, VP9 cpu-used 2, VP8 20M ceiling,
# dnxhr_hq, and the ffv1 flags.

# Lower is usually better for -crf / -q:v, except libtheora -q:v for some reason.
# Dictionary is used here instead of flat array to make it easy to override later.
VIDEO_OPTS = {
    # Modern codecs
    "libx264": {"-crf": "20", "-preset": "medium"},
    "libx265": {"-crf": "24", "-preset": "medium"},
    "libsvtav1": {"-crf": "30", "-preset": "8"},      # preset is numeric, 0-13
    "libaom-av1": {"-crf": "30", "-b:v": "0", "-cpu-used": "6", "-row-mt": "1"},
    "libvpx-vp9": {"-crf": "31", "-b:v": "0", "-deadline": "good", "-cpu-used": "2", "-row-mt": "1"},
    "libvpx": {"-crf": "10", "-b:v": "20M", "-deadline": "good", "-cpu-used": "2"},  # -b:v is a ceiling only

    # Legacy codecs
    "mpeg4": {"-q:v": "3"},
    "mpeg2video": {"-q:v": "3"},
    "mpeg1video": {"-q:v": "3"},
    "h263": {"-q:v": "3"},
    "flv": {"-q:v": "3"},
    "msmpeg4v2": {"-q:v": "3"},
    "msmpeg4": {"-q:v": "3"},
    "wmv1": {"-q:v": "3"},
    "wmv2": {"-q:v": "3"},
    "mjpeg": {"-q:v": "3"},
    "libtheora": {"-q:v": "7"},

    # Intermediate / lossless
    "prores_ks": {"-profile:v": "3"},
    "dnxhd": {"-profile:v": "dnxhr_hq"},
    "ffv1": {"-level": "3", "-slicecrc": "1"},
    "huffyuv": {},
    "rawvideo": {},
    "gif": {},
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


# Most of these were taken from xiph, audacity, handbrake, ffmpeg, and Google.
AUDIO_OPTS = {
    # Lossy, bitrate-controlled
    "aac": {"-b:a": "320k"},
    "libopus": {"-b:a": "128k"},
    "ac3": {"-b:a": "448k"},
    "eac3": {"-b:a": "448k"},
    "mp2": {"-b:a": "320k"},
    "wmav1": {"-b:a": "192k"},
    "wmav2": {"-b:a": "192k"},

    # Lossy, quality-controlled (VBR)
    "libmp3lame": {"-q:a": "2"},      # LAME V2, ~190 kbps; 0-9, lower = better
    "libvorbis": {"-q:a": "5"},      # -1 to 10, higher = better

    # Lossless / uncompressed
    "flac": {"-compression_level": "6"},  # Middle ground of 0-12. This affects the size but never quality
    "alac": {},
    "pcm_s16le": {},
    "pcm_s24le": {},
}

# Which flag counts as "quality" (what --vquality / --aquality override).
# The first one an encoder has wins. Encoders with none (lossless) can't
VIDEO_QUALITY_FLAGS = ("-crf", "-q:v", "-profile:v")
AUDIO_QUALITY_FLAGS = ("-b:a", "-q:a")
