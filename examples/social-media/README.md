# Social media examples

- [Demonstration video](demo.mp4): a 45-second video showing the pet in use on the desktop, all nine animations and sixteen look directions, with Chinese captions and piano music.
- [Edited screen recording](screen-recording-edited.mp4): the 6.4-second opening clip, trimmed and framed in portrait format, without music.
- [Cover image](cover.png): artwork for sharing the pet.

Both videos use H.264 at 1080 × 1920 and 30 fps. The demo also includes stereo AAC audio and a guide to triggering the animations, which you can pause to read. The guide reflects how the app behaved in September 2026; controls may differ in later versions.

## Generate the video

You will need Python 3 with `Pillow` and `numpy`, FFmpeg with the `libx264` and `aac` encoders on your `PATH`, and a Chinese font. On macOS, the renderer looks for PingFang SC in the system font collection (face index 3).

Run this command from the repository root:

```sh
python3 examples/social-media/scripts/render_demo.py
```

This rebuilds and replaces `demo.mp4` using the repository’s pet sprites and the two recordings in this directory. It leaves the opening clip and cover unchanged and needs no network connection.

Options:

- `--output /tmp/demo.mp4`: save the video elsewhere.
- `--preview`: save a `.jpg` contact sheet instead of the full video. Requires FFmpeg.
- `--work-dir /tmp/iu-demo-build`: keep intermediate files, the contact sheet and chapter metadata. These are deleted after rendering unless you specify a work directory.
- `--font /path/to/font.ttf --font-index 0`: choose a font and face index for the generated scenes. This does not change the text in the opening clip. You can also set the font path with `DEMO_FONT`.

## Recordings

The [edited screen recording](screen-recording-edited.mp4) was captured with CleanShot on 30 October 2026. It has already been trimmed and framed for this video, so you do not need the original recording to rebuild the demo.

The [piano recording](gymnopedie-no-1.mp3) is Kevin MacLeod’s recording of Erik Satie’s “Gymnopedie No. 1”, downloaded from the [official source](https://incompetech.com/music/royalty-free/mp3-royaltyfree/Gymnopedie%20No%201.mp3). It is available under the [CC BY 4.0 licence](https://creativecommons.org/licenses/by/4.0/). The demo uses the passage from 00:08 to 00:53, with the volume lowered and a fade at each end.

## Music credit

When sharing the video, include this attribution in the post caption or accompanying credits:

> Music: “Gymnopedie No. 1” by Kevin MacLeod (incompetech.com), composed by Erik Satie. Licensed under CC BY 4.0: https://creativecommons.org/licenses/by/4.0/. Excerpt 00:08–00:53; level adjusted and fades added. Source: https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1100787
