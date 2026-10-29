#!/usr/bin/env python3
"""Render the social-media demonstration with a procedurally generated soundtrack."""

import argparse
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageSequence

SCRIPT_DIR = Path(__file__).resolve().parent
ASSETS = SCRIPT_DIR.parent
ROOT = ASSETS.parents[1]


def main():
    """Render the demonstration or save a preview contact sheet."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ASSETS / "demo.mp4")
    parser.add_argument("--preview", action="store_true")
    parser.add_argument("--work-dir", type=Path)
    parser.add_argument(
        "--font", default=os.environ.get("DEMO_FONT") or os.environ.get("IU_DEMO_FONT")
    )
    parser.add_argument("--font-index", type=int, default=3)
    args = parser.parse_args()
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = (
        tempfile.TemporaryDirectory(prefix="pet-demo-")
        if args.work_dir is None
        else None
    )
    out = (args.work_dir or Path(temporary.name)).resolve()
    out.mkdir(parents=True, exist_ok=True)
    font = args.font
    if not font:
        candidates = list(
            Path("/System/Library/AssetsV2/com_apple_MobileAsset_Font8").glob(
                "*/AssetData/PingFang.ttc"
            )
        )
        if not candidates:
            parser.error(
                "Supply --font with a Chinese font file (and --font-index for its face)."
            )
        font = str(candidates[0])
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg and not args.preview:
        parser.error("ffmpeg must be installed and available on PATH")
    width, height = 1080, 1920
    ink = "#3e304b"
    muted = "#85718f"
    purple = "#9674b1"
    card = "#f7f6fb"
    fonts = {
        n: ImageFont.truetype(font, n, index=args.font_index)
        for n in [24, 28, 30, 32, 36, 42, 48, 64, 76, 86]
    }

    def text(im, xy, s, n=36, c=ink, anchor="mm"):
        ImageDraw.Draw(im).text(xy, s, font=fonts[n], fill=c, anchor=anchor)

    def base(chapter):
        im = Image.new("RGB", (width, height), "#eee8f3")
        d = ImageDraw.Draw(im)
        d.ellipse((-250, -210, 480, 520), fill="#e5d9ee")
        d.ellipse((850, 1400, 1310, 2020), fill="#e3d5eb")
        text(im, (100, 150), "IU BESIDE YOU", 32, purple, "lm")
        text(im, (980, 150), chapter, 28, muted, "rm")
        d.line((100, 207, 980, 207), fill="#d4c4df", width=2)
        text(im, (540, 1740), "知恩相伴 · 粉丝自制非官方 Codex 桌宠", 28, muted)
        return im

    serial = 0
    timeline = []
    samples = []
    manifest = []

    def save(im, duration):
        nonlocal serial
        p = out / f"frame-{serial:04d}.png"
        im.save(p)
        serial += 1
        return (p, duration)

    def add(seq, loops, title):
        start = sum(t for p, t in timeline)
        timeline.extend(seq * loops)
        manifest.append(
            {
                "title": title,
                "start": round(start, 3),
                "duration": round(sum(t for p, t in seq) * loops, 3),
            }
        )
        samples.append(seq[0][0])

    def paste_pet(im, pet, x=252, y=640):
        im.paste(
            pet.convert("RGB").resize((576, 624), Image.Resampling.LANCZOS), (x, y)
        )

    def panel(im):
        ImageDraw.Draw(im).rounded_rectangle((90, 570, 990, 1325), radius=60, fill=card)

    def gif_frames(name):
        gif = Image.open(ROOT / "examples" / name)
        return [
            (f.convert("RGB").copy(), f.info.get("duration", 100) / 1000)
            for f in ImageSequence.Iterator(gif)
        ]

    # This scene assembly section was truncated in the archived renderer.
    # Reconstructed from the reference video, recovered chapter timings and gallery assets.
    seq = []
    for pet, dur in gif_frames("waving.gif"):
        im = base("完整动作图鉴")
        text(im, (540, 340), "知恩女士，来陪你啦", 86)
        text(im, (540, 452), "九种动画 · 十六个视线方向", 36, muted)
        panel(im)
        paste_pet(im, pet)
        text(im, (540, 1450), "Uaena，今天也要元气满满呀", 42)
        text(im, (540, 1535), "IU Beside You  /  Codex pet", 30, muted)
        seq.append(save(im, dur))
    add(seq, 4, "开场")
    scenes = [
        ("idle.gif", "安静陪伴", "RESTING", "轻轻眨眼，静静呼吸", 3),
        ("running-right.gif", "向右走走", "MOVING RIGHT", "迈着小步向右走", 3),
        ("running-left.gif", "向左走走", "MOVING LEFT", "换个方向，继续陪你", 3),
        ("waving.gif", "向你挥手", "ATTENTION WAVE", "挥挥手，想让你注意到我", 5),
        ("jumping.gif", "开心跳跃", "JUMPING", "蹲下、跃起，再轻轻落地", 4),
        ("failed.gif", "有点失落", "DISAPPOINTED", "短暂失落后，慢慢恢复", 3),
        ("waiting.gif", "等你回应", "WAITING FOR YOU", "等着你的下一步指示", 4),
        ("running.gif", "认真思考", "THINKING", "任务进行中，专注忙碌", 4),
        ("review.gif", "看看结果", "REVIEWING", "带着思考，检查刚刚的成果", 4),
    ]
    for i, (name, title, en, caption, loops) in enumerate(scenes):
        seq = []
        for pet, dur in gif_frames(name):
            im = base(f"{i+1:02d} / 09")
            text(im, (540, 350), title, 86)
            text(im, (540, 454), en, 30, muted)
            panel(im)
            paste_pet(im, pet)
            text(im, (540, 1445), caption, 42)
            text(im, (540, 1530), "每个小动作，都是一点陪伴", 30, muted)
            d = ImageDraw.Draw(im)
            for j in range(9):
                d.rounded_rectangle(
                    (350 + j * 47, 1615, 380 + j * 47, 1621),
                    radius=3,
                    fill=purple if j == i else "#d4c4df",
                )
            seq.append(save(im, dur))
        add(seq, loops, title)
    seq = []
    for pet, dur in gif_frames("look-around.gif"):
        im = base("视线方向 / 01")
        text(im, (540, 350), "十六种小眼神", 86)
        text(im, (540, 455), "十六个方向 · 顺时针完整预览", 36, muted)
        panel(im)
        paste_pet(im, pet)
        text(im, (540, 1445), "十六个视线方向，一次看全", 42)
        text(im, (540, 1535), "此处为轮播演示；实际触发由应用控制", 30, muted)
        seq.append(save(im, dur))
    add(seq, 2, "十六方向顺时针轮播")
    seq = []
    for i in range(16):
        pet = Image.open(ROOT / "examples" / f"look-{i:02d}.png")
        im = base("视线方向 / 02")
        text(im, (540, 350), "每个方向，都有回应", 64)
        text(im, (540, 454), f"{i+1:02d} / 16  ·  {i*22.5:g}°", 36, muted)
        panel(im)
        paste_pet(im, pet)
        d = ImageDraw.Draw(im)
        for j in range(16):
            angle = j * math.pi / 8
            x = 540 + 342 * math.sin(angle)
            y = 950 - 342 * math.cos(angle)
            radius = 12 if j == i else 5
            d.ellipse(
                (x - radius, y - radius, x + radius, y + radius),
                fill=purple if j == i else "#d4c4df",
            )
        direction = (
            "正上方"
            if i == 0
            else (
                "右上方"
                if i < 4
                else (
                    "正右方"
                    if i == 4
                    else (
                        "右下方"
                        if i < 8
                        else (
                            "正下方"
                            if i == 8
                            else (
                                "左下方"
                                if i < 12
                                else "正左方" if i == 12 else "左上方"
                            )
                        )
                    )
                )
            )
        )
        text(im, (540, 1445), direction, 48)
        text(im, (540, 1535), "从正上方开始，顺时针逐一展示", 30, muted)
        seq.append(save(im, 0.6))
    add(seq, 1, "十六方向逐一展示")
    # Trigger summary based on the locally inspected app overlay implementation.
    im = base("互动小贴士")
    text(im, (540, 340), "小动作触发指南", 76)
    text(im, (540, 435), "互动小贴士 · 可暂停查看", 36, muted)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((85, 510, 995, 1495), radius=38, fill=card)
    text(im, (130, 564), "小动作", 32, purple, "lm")
    text(im, (410, 564), "什么时候会出现", 32, purple, "lm")
    d.line((125, 610, 955, 610), fill="#dfd3e7", width=2)
    rows = [
        ("安静陪伴", "没有活动提醒时"),
        ("左右走动", "按住桌宠，向左或向右拖动"),
        ("开心跳跃", "鼠标悬停在桌宠上"),
        ("向你挥手", "应用触发初次唤醒提醒时"),
        ("认真思考", "活动提醒显示任务进行中"),
        ("等你回应", "活动提醒显示需要输入时"),
        ("有点失落", "活动提醒显示失败或受阻时"),
        ("看看结果", "活动提醒显示任务完成时"),
        ("视线方向", "快捷聊天输入光标，或"),
    ]
    for i, (name, trigger) in enumerate(rows):
        y = 660 + i * 86
        text(im, (130, y), name, 32, ink, "lm")
        text(im, (410, y), trigger, 30, ink, "lm")
        if i < 8:
            d.line((125, y + 43, 955, y + 43), fill="#e9e1ee", width=1)
    text(im, (410, 1392), "Computer Use 的操作光标", 28, ink, "lm")
    text(im, (540, 1555), "普通鼠标移动不会让她轮播全部视线", 30, muted)
    text(im, (540, 1615), "按当前安装版本整理，实际表现以应用为准", 28, muted)
    add([save(im, 7)], 1, "动画触发指南")
    seq = []
    for pet, dur in gif_frames("waving.gif"):
        im = base("IU BESIDE YOU")
        text(im, (540, 350), "把陪伴留在桌面", 76)
        text(im, (540, 454), "九种动画 + 十六个视线方向", 36, muted)
        panel(im)
        paste_pet(im, pet)
        text(im, (540, 1445), "IU Beside You", 48)
        text(im, (540, 1535), "愿每一次忙碌，都有温柔相伴", 36, muted)
        seq.append(save(im, dur))
    add(seq, 4, "结尾")
    # PNG stills at a 100 Hz input timebase retain source durations; output sampled at 30fps.
    # FFmpeg resolves these generated filenames relative to the timeline file.
    # Keeping directory names out of the list also avoids concat path quoting issues.
    with (out / "timeline.txt").open("w", encoding="utf-8") as f:
        for p, dur in timeline:
            f.write(f"file '{p.name}'\noption framerate 100\nduration {dur:.3f}\n")
        f.write(f"file '{timeline[-1][0].name}'\noption framerate 100\n")
    (out / "manifest.json").write_text(
        json.dumps(
            {
                "width": width,
                "height": height,
                "fps": 30,
                "duration": 59.4,
                "source_timeline_duration": round(sum(t for _, t in timeline), 3),
                "chapters": manifest,
                "source": "examples/index.html and original example GIF/PNG assets",
                "audio": "Original instrumental soundtrack generated by compose_demo_music.py",
                "timing": "Recovered concat renderer, sampled at 30 fps and trimmed to the original 59.4-second export.",
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    preview = Image.new("RGB", (270 * 4, 480 * 4), "white")
    for i, p in enumerate(samples):
        im = Image.open(p)
        im.thumbnail((270, 480))
        preview.paste(im, ((i % 4) * 270, (i // 4) * 480))
    preview.save(out / "review.jpg")
    # Keep the existing social-media cover.
    print(json.dumps(manifest, ensure_ascii=False), flush=True)
    if args.preview:
        preview_output = output.with_suffix(".jpg")
        if preview_output != out / "review.jpg":
            shutil.copyfile(out / "review.jpg", preview_output)
        return
    subprocess.run(
        [
            ffmpeg,
            "-y",
            "-v",
            "warning",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(out / "timeline.txt"),
            "-t",
            "59.4",
            "-r",
            "30",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "18",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            str(out / "IU-Beside-You-完整动画展示.mp4"),
        ],
        check=True,
    )

    # Recover the original procedural score and mux it into the newly rendered video.
    subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "compose_demo_music.py"), str(out)],
        check=True,
    )
    subprocess.run(
        [
            ffmpeg,
            "-y",
            "-v",
            "error",
            "-i",
            str(out / "IU-Beside-You-完整动画展示.mp4"),
            "-i",
            str(out / "知恩相伴-original.wav"),
            "-map",
            "0:v:0",
            "-map",
            "1:a:0",
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-t",
            "59.4",
            "-movflags",
            "+faststart",
            str(output),
        ],
        check=True,
    )
    metadata = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
    metadata["audio_provenance"] = json.loads(
        (out / "music-provenance.json").read_text(encoding="utf-8")
    )
    (out / "manifest.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Rendered {output}")


if __name__ == "__main__":
    main()
