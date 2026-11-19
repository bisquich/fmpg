# fmpg

fmpg is ffmpeg simplified for everyday use, wraps common ffmpeg tasks in short commands with sensible defaults, without making it so much less configurable.

## Requirements

- Python 3.12+
- [ffmpeg](https://ffmpeg.org/download.html) (including `ffprobe`)
- [uv](https://docs.astral.sh/uv/) (recommended for development)

## Contributing

fmpg is in early development, so contributions are very welcome!

### Development setup

It is very recommended to install in editable mode so your changes take effect immediately:

```sh
uv tool install -e .
```

### Contribution ideas

- Add more commands, such as:
  - compress
  - togif
  - merge
  - extractaudio
  - your own idea!
- Make commands stackable
- Write or refine documentation
- Pick up a task from [todo.txt](src/todo.txt)

If you plan a larger change with bigger idea, open an issue first so we can talk it through.
