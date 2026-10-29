#!/usr/bin/env python3
"""Build the IU scrapbook demonstration from the edited recording and pet artwork."""

import argparse
from contextlib import ExitStack
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ASSETS = Path(__file__).resolve().parents[1]
ROOT = ASSETS.parents[1]
WIDTH, HEIGHT, FPS = 1080, 1920, 30
INTRO_DURATION = 6.4
MUSIC_START = 8
SCENES = [
    ("hello", 6.6, "把日常，变成一点小欢喜"),
    ("walk", 6.0, "跟着你，走走停停"),
    ("work", 7.0, "忙碌的时候，也有回应"),
    ("look", 8.0, "十六个方向，都有回应"),
    ("guide", 7.0, "把这些小互动，记下来"),
    ("end", 4.0, "知恩相伴"),
]
DURATION = INTRO_DURATION + sum(duration for _, duration, _ in SCENES)
INK, MUTED, PURPLE = "#493e48", "#766b75", "#9475a3"


def run(command):
    """Run an encoder command and propagate failures."""
    subprocess.run(command, check=True)


class Scrapbook:
    """Compose paper layouts with the original transparent pet artwork."""

    def __init__(self, font_path, font_index):
        self.fonts = {
            size: ImageFont.truetype(font_path, size, index=font_index)
            for size in (24, 26, 28, 30, 32, 36, 40, 44, 48, 56, 64, 72, 84, 100)
        }
        self.animations = json.loads(
            (ROOT / "examples/animations.json").read_text(encoding="utf-8")
        )
        with Image.open(ROOT / "spritesheet.webp") as source:
            self.atlas = source.convert("RGBA")
        self.sprites = {}
        noise = np.random.default_rng(29).integers(-3, 4, (HEIGHT, WIDTH, 1))
        paper = np.clip(np.array([249, 244, 234]) + noise, 0, 255).astype("uint8")
        self.paper = Image.fromarray(paper)
        self.layouts = {}

    def text(self, im, xy, value, size=36, colour=INK, anchor="mm"):
        ImageDraw.Draw(im).text(
            xy, value, font=self.fonts[size], fill=colour, anchor=anchor
        )

    def base(self, label, title, subtitle):
        im = self.paper.copy()
        d = ImageDraw.Draw(im)
        d.line((64, 154, 1016, 154), fill="#d6c9b8", width=2)
        self.text(im, (68, 110), "IU BESIDE YOU", 28, anchor="lm")
        self.text(im, (1012, 110), label, 26, MUTED, "rm")
        self.text(im, (76, 270), title, 64, anchor="lm")
        self.text(im, (78, 372), subtitle, 30, MUTED, "lm")
        d.line((76, 1760, 1004, 1760), fill="#d6c9b8", width=2)
        self.text(im, (76, 1810), "知恩相伴 · 非官方 Codex 桌宠", 26, MUTED, "lm")
        self.text(im, (1004, 1810), "一点陪伴", 26, PURPLE, "rm")
        return im

    def card(self, im, box, label, number):
        x, y, w, h = box
        d = ImageDraw.Draw(im)
        d.rectangle((x + 9, y + 12, x + w + 9, y + h + 12), fill="#ddd3c5")
        d.rectangle((x, y, x + w, y + h), fill="#fffdf9")
        d.polygon(
            [(x + 20, y - 12), (x + 150, y - 19), (x + 156, y + 17), (x + 24, y + 24)],
            fill="#dcd1e3",
        )
        self.text(im, (x + 30, y + 57), number, 24, PURPLE, "lm")
        self.text(im, (x + w / 2, y + h - 44), label, 32)

    def sprite(self, row, col, size):
        key = row, col, size
        if key not in self.sprites:
            self.sprites[key] = self.atlas.crop(
                (col * 192, row * 208, (col + 1) * 192, (row + 1) * 208)
            ).resize(size, Image.Resampling.LANCZOS)
        return self.sprites[key]

    def pose(self, row, time):
        durations = self.animations[row]["durations_ms"]
        elapsed = (time * 1000) % sum(durations)
        for col, duration in enumerate(durations):
            elapsed -= duration
            if elapsed < 0:
                return col
        return len(durations) - 1

    def pet(self, im, row, col, xy, size):
        sprite = self.sprite(row, col, size)
        im.paste(sprite, xy, sprite)

    def layout(self, scene):
        if scene in self.layouts:
            return self.layouts[scene].copy()
        if scene == "hello":
            im = self.base(
                "01 / 小欢喜", "把日常，变成小欢喜", "不赶时间，先和她打个招呼。"
            )
            self.card(im, (70, 500, 560, 900), "安静陪伴", "01")
            self.card(im, (670, 520, 330, 440), "向你挥手", "02")
            self.card(im, (670, 1010, 330, 440), "开心跳跃", "03")
            self.text(im, (90, 1570), "眨眨眼，挥挥手，再轻轻跳一下。", 36, anchor="lm")
        elif scene == "walk":
            im = self.base(
                "02 / 走走停停", "你去哪，她就去哪", "按住桌宠，向左或向右拖动。"
            )
            self.card(im, (80, 540, 920, 450), "向左走走", "04 / LEFT")
            self.card(im, (80, 1080, 920, 450), "向右走走", "05 / RIGHT")
            self.text(im, (540, 1650), "把陪伴，挪到喜欢的位置。", 36)
        elif scene == "work":
            im = self.base(
                "03 / 工作小表情",
                "忙碌的时候，也有回应",
                "四种状态，四个不同的小表情。",
            )
            for number, (label, x, y) in enumerate(
                [
                    ("认真思考", 80, 510),
                    ("等你回应", 565, 510),
                    ("有点失落", 80, 1080),
                    ("看看结果", 565, 1080),
                ],
                6,
            ):
                self.card(im, (x, y, 435, 505), label, f"{number:02d}")
        elif scene == "look":
            im = self.base(
                "04 / 小眼神",
                "十六个方向，都有回应",
                "顺时针逐一展示 · 实际视线由应用控制",
            )
            self.card(im, (190, 490, 700, 850), "", "16 LOOKS")
            self.text(im, (540, 1640), "每一个方向，都认真看向你。", 36)
        elif scene == "guide":
            im = self.base(
                "收藏 / 互动便签",
                "把这些小互动，记下来",
                "可暂停阅读 · 2026 年 9 月版本行为参考",
            )
            d = ImageDraw.Draw(im)
            d.rectangle((75, 490, 1005, 1640), fill="#fffdf9")
            rows = [
                ("悬停", "开心跳跃"),
                ("向左 / 右拖动", "左右走动"),
                ("初次唤醒提醒", "向你挥手"),
                ("任务进行中", "认真思考"),
                ("需要输入", "等你回应"),
                ("失败或受阻", "有点失落"),
                ("任务完成", "看看结果"),
                ("没有活动提醒", "安静陪伴"),
            ]
            for i, (trigger, reaction) in enumerate(rows):
                y = 565 + i * 108
                self.text(im, (110, y), trigger, 32, MUTED, "lm")
                self.text(im, (950, y), reaction, 36, INK, "rm")
                d.line((110, y + 48, 950, y + 48), fill="#e6ddd1", width=2)
            self.text(im, (110, 1460), "视线：快捷聊天输入光标，或", 30, anchor="lm")
            self.text(
                im,
                (110, 1510),
                "Computer Use 操作光标；不是普通鼠标。",
                30,
                anchor="lm",
            )
            self.text(im, (540, 1690), "实际表现以你安装的应用版本为准", 28, MUTED)
        else:
            im = self.base(
                "留一页 / 给你", "愿忙碌，也有温柔相伴", "IU Beside You · 知恩相伴"
            )
            self.text(im, (540, 1190), "九种动画 · 十六个视线方向", 36)
            self.text(im, (540, 1280), "把陪伴，留在每一个平凡日子里。", 28, PURPLE)
        self.layouts[scene] = im
        return im.copy()

    def frame(self, scene, time):
        im = self.layout(scene)
        if scene == "hello":
            for row, xy, size in [
                (0, (110, 650), (480, 520)),
                (3, (705, 615), (264, 286)),
                (4, (705, 1105), (264, 286)),
            ]:
                self.pet(im, row, self.pose(row, time), xy, size)
        elif scene == "walk":
            distance = int(440 * ((time / 3) % 1))
            self.pet(im, 2, self.pose(2, time), (620 - distance, 605), (288, 312))
            self.pet(im, 1, self.pose(1, time), (160 + distance, 1145), (288, 312))
        elif scene == "work":
            for row, xy in [
                (7, (140, 600)),
                (6, (625, 600)),
                (5, (140, 1170)),
                (8, (625, 1170)),
            ]:
                self.pet(im, row, self.pose(row, time), xy, (312, 338))
        elif scene == "look":
            index = min(int(time * 2), 15)
            self.pet(im, 9 + index // 8, index % 8, (252, 615), (576, 624))
            self.text(
                im, (540, 1295), f"{index+1:02d} / 16    ·    {index*22.5:g}°", 32
            )
            d = ImageDraw.Draw(im)
            for i in range(16):
                x, y = 220 + (i % 8) * 90, 1440 + (i // 8) * 75
                d.ellipse(
                    (x - 20, y - 20, x + 20, y + 20),
                    fill=PURPLE if i == index else "#ded4e4",
                )
                self.text(im, (x, y), str(i + 1), 24, "white" if i == index else MUTED)
        elif scene == "end":
            self.pet(im, 3, self.pose(3, time), (300, 570), (480, 520))
        return im


def encode_body(book, ffmpeg, out):
    command = [
        ffmpeg,
        "-y",
        "-v",
        "error",
        "-f",
        "rawvideo",
        "-pix_fmt",
        "rgb24",
        "-s",
        f"{WIDTH}x{HEIGHT}",
        "-r",
        str(FPS),
        "-i",
        "-",
        "-an",
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "18",
        "-pix_fmt",
        "yuv420p",
        "-video_track_timescale",
        "15360",
        str(out / "body.mp4"),
    ]
    with subprocess.Popen(command, stdin=subprocess.PIPE) as proc:
        try:
            for scene, duration, _ in SCENES:
                for n in range(round(duration * FPS)):
                    proc.stdin.write(book.frame(scene, n / FPS).tobytes())
        finally:
            proc.stdin.close()
        result = proc.wait()
        if result:
            raise subprocess.CalledProcessError(result, command)


def render(args, out, ffmpeg):
    book = Scrapbook(args.font, args.font_index)
    intro = out / "screen-recording-edited.mp4"
    source = ASSETS / "screen-recording-edited.mp4"
    if intro != source:
        shutil.copyfile(source, intro)
    run(
        [
            ffmpeg,
            "-y",
            "-v",
            "error",
            "-ss",
            "1",
            "-i",
            str(intro),
            "-frames:v",
            "1",
            str(out / "intro.png"),
        ]
    )
    with Image.open(out / "intro.png") as source:
        previews = [source.convert("RGB")]
    previews.extend(book.frame(scene, 1) for scene, _, _ in SCENES)
    sheet = Image.new("RGB", (270 * 4, 480 * 2), "#e7dfd2")
    for i, frame in enumerate(previews):
        sheet.paste(
            frame.resize((270, 480), Image.Resampling.LANCZOS),
            ((i % 4) * 270, (i // 4) * 480),
        )
    sheet.save(out / "review.jpg", quality=95)
    chapters = [{"title": "桌面实录", "start": 0, "duration": INTRO_DURATION}]
    at = INTRO_DURATION
    for _, duration, title in SCENES:
        chapters.append({"title": title, "start": round(at, 3), "duration": duration})
        at += duration
    (out / "manifest.json").write_text(
        json.dumps(
            {
                "width": WIDTH,
                "height": HEIGHT,
                "fps": FPS,
                "duration": DURATION,
                "chapters": chapters,
                "music": {
                    "title": "Gymnopedie No. 1",
                    "artist": "Kevin MacLeod",
                    "licence": "CC BY 4.0",
                    "start": MUSIC_START,
                    "duration": DURATION,
                },
                "recording": {
                    "source": "screen-recording-edited.mp4",
                    "duration": INTRO_DURATION,
                },
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    if args.preview:
        target = args.output.with_suffix(".jpg")
        if target != out / "review.jpg":
            shutil.copyfile(out / "review.jpg", target)
        return
    encode_body(book, ffmpeg, out)
    (out / "segments.txt").write_text(
        "file 'screen-recording-edited.mp4'\nfile 'body.mp4'\n", encoding="utf-8"
    )
    final = out / "final.mp4"
    run(
        [
            ffmpeg,
            "-y",
            "-v",
            "error",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(out / "segments.txt"),
            "-ss",
            str(MUSIC_START),
            "-i",
            str(ASSETS / "gymnopedie-no-1.mp3"),
            "-map",
            "0:v:0",
            "-map",
            "1:a:0",
            "-c:v",
            "copy",
            "-af",
            f"atrim=duration={DURATION},asetpts=PTS-STARTPTS,volume=0.75,afade=t=in:d=0.7,afade=t=out:st={DURATION-2.5}:d=2.5",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-t",
            str(DURATION),
            "-movflags",
            "+faststart",
            str(final),
        ]
    )
    if final != args.output:
        shutil.copyfile(final, args.output)
    print(f"Rendered {args.output} ({DURATION:g} seconds)")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ASSETS / "demo.mp4")
    parser.add_argument("--preview", action="store_true")
    parser.add_argument("--work-dir", type=Path)
    parser.add_argument(
        "--font", default=os.environ.get("DEMO_FONT") or os.environ.get("IU_DEMO_FONT")
    )
    parser.add_argument("--font-index", type=int, default=3)
    args = parser.parse_args()
    if not args.font:
        fonts = sorted(
            Path("/System/Library/AssetsV2/com_apple_MobileAsset_Font8").glob(
                "*/AssetData/PingFang.ttc"
            )
        )
        if not fonts:
            parser.error(
                "Supply --font with a Chinese font file and --font-index for its face."
            )
        args.font = str(fonts[0])
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        parser.error("ffmpeg must be installed and available on PATH")
    args.output = args.output.resolve()
    if not args.preview and args.output in {
        (ASSETS / "screen-recording-edited.mp4").resolve(),
        (ASSETS / "gymnopedie-no-1.mp3").resolve(),
    }:
        parser.error("--output must not overwrite a source recording")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with ExitStack() as stack:
        out = (
            args.work_dir.resolve()
            if args.work_dir
            else Path(
                stack.enter_context(tempfile.TemporaryDirectory(prefix="iu-demo-"))
            )
        )
        out.mkdir(parents=True, exist_ok=True)
        render(args, out, ffmpeg)


if __name__ == "__main__":
    main()
