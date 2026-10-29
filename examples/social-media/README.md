# Social media examples

- [Demonstration video](demo.mp4): 1080 × 1920, 30 fps, 59.4 seconds, with Chinese captions and an original instrumental soundtrack. It includes all nine animations, sixteen look directions and a seven-second trigger guide that viewers can pause to read.
- [Cover image](cover.png): artwork for sharing the pet on social media.

The video uses H.264 video and stereo AAC audio in an MP4 container. Its trigger guide reflects the September 2026 app behaviour; controls may differ in later versions.

## Generate the video

You will need Python 3 with `Pillow` and `numpy`, FFmpeg with the `libx264` and `aac` encoders on your `PATH`, and a Chinese font. The default is PingFang SC, collection face 3, on macOS.

From the repository root, run:

```sh
python3 examples/social-media/scripts/render_demo.py
```

This replaces `demo.mp4` in this directory. The renderer builds the scenes from the repository’s animation assets, then synthesises and adds the soundtrack. The cover image is maintained separately.

To save another copy:

```sh
python3 examples/social-media/scripts/render_demo.py --output /tmp/demo.mp4
```

Both rendering and preview generation support these options:

- `--preview`: write a contact sheet with a `.jpg` extension instead of rendering a video.
- `--work-dir /tmp/demo-build`: retain intermediate files in the chosen directory.
- `--font /path/to/font.ttf --font-index 0`: use another font and face index. You can also set the font path with `DEMO_FONT`.

By default, intermediate frames, audio and metadata are created in a temporary directory and removed when the renderer exits. Retained builds include `review.jpg` and `manifest.json`; full video builds also include the generated audio and music provenance. No metadata sidecar is written beside the final video.

## Soundtrack

The renderer runs [`scripts/compose_demo_music.py`](scripts/compose_demo_music.py) to generate a stereo WAV, encodes it as AAC and includes it in the finished MP4. No separate audio file is needed in the repository.

The score uses synthesised sounds, with no artist recordings or external samples.

To generate the soundtrack separately:

```sh
python3 examples/social-media/scripts/compose_demo_music.py /tmp/demo-score
```

This writes a WAV file and music provenance information to the chosen directory. Full video builds also include that provenance in their temporary chapter manifest.
