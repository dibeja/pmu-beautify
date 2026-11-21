#!/usr/bin/env python3
"""Side-by-side before/after for approval: photo -> photo, video -> video (audio from BEFORE).

  python compare.py BEFORE AFTER OUT [--labels "ORIGINAL,RETOUCHED"] [--height 1280]

Both sides are scaled to the same height; a label bar sits on top of each.
Labels use OpenCV's built-in font: plain ASCII only (no accents).
"""
import argparse
import subprocess
from pathlib import Path

import cv2
import numpy as np

from retouch import PHOTO, probe, read_photo

BAR = 0.06  # label bar height, fraction of image height


def label(f, text):
    h, w = f.shape[:2]
    bar = max(28, int(h * BAR))
    out = np.full((h + bar, w, 3), 255, np.uint8)
    out[bar:] = f
    scale = bar / 40
    th = max(1, int(scale * 2))
    (tw, tht), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_DUPLEX, scale, th)
    cv2.putText(out, text, ((w - tw) // 2, (bar + tht) // 2), cv2.FONT_HERSHEY_DUPLEX, scale, (30, 30, 30), th, cv2.LINE_AA)
    return out


def side(a, b, labels, gap):
    h = a.shape[0]
    b = cv2.resize(b, (round(b.shape[1] * h / b.shape[0]), h), interpolation=cv2.INTER_AREA)
    sep = np.full((h + max(28, int(h * BAR)), gap, 3), 255, np.uint8)
    return np.hstack([label(a, labels[0]), sep, label(b, labels[1])])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("before"); ap.add_argument("after"); ap.add_argument("out")
    ap.add_argument("--labels", default="ORIGINAL,RETOUCHED")
    ap.add_argument("--height", type=int, default=1280, help="output height of each side (video and photo)")
    a = ap.parse_args()
    labels = a.labels.split(",")

    if Path(a.before).suffix.lower() in PHOTO:
        x, y = read_photo(a.before), read_photo(a.after)
        hgt = min(a.height, x.shape[0])
        x = cv2.resize(x, (round(x.shape[1] * hgt / x.shape[0]), hgt), interpolation=cv2.INTER_AREA)
        cv2.imwrite(a.out, side(x, y, labels, max(8, hgt // 80)), [cv2.IMWRITE_JPEG_QUALITY, 92])
        print("wrote", a.out)
        return

    w, h, fps = probe(a.before)
    H = min(a.height, h) // 2 * 2
    W = round(w * H / h / 2) * 2
    gap = max(8, H // 80) // 2 * 2

    def dec(p):
        return subprocess.Popen(["ffmpeg", "-v", "error", "-i", p, "-vf", f"scale={W}:{H}", "-f", "rawvideo",
                                 "-pix_fmt", "bgr24", "-"], stdout=subprocess.PIPE)

    da, db = dec(a.before), dec(a.after)
    bar = max(28, int(H * BAR))
    ow, oh = 2 * W + gap, (H + bar) // 2 * 2
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{ow}x{oh}",
                            "-r", fps, "-i", "-", "-i", a.before, "-map", "0:v", "-map", "1:a?", "-shortest",
                            "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac",
                            "-movflags", "+faststart", a.out], stdin=subprocess.PIPE)
    n, size = 0, W * H * 3
    while True:
        ba, bb = da.stdout.read(size), db.stdout.read(size)
        if len(ba) < size or len(bb) < size:
            break
        fr = side(np.frombuffer(ba, np.uint8).reshape(H, W, 3), np.frombuffer(bb, np.uint8).reshape(H, W, 3), labels, gap)
        enc.stdin.write(np.ascontiguousarray(fr[:oh]).tobytes())
        n += 1
    enc.stdin.close(); enc.wait()
    da.kill(); db.kill()
    print(f"wrote {a.out}, {n} frames")


if __name__ == "__main__":
    main()
