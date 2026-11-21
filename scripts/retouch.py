#!/usr/bin/env python3
"""Face-aware skin retouch for photos and talking-head video (a "beauty" pass, by script).

MediaPipe Face Landmarker finds the face every frame; the mask is the face oval
minus eyes, brows and lips, feathered. Inside it the mid-frequency band (lines,
blotches, under-eye texture) is pulled down while the finest band (pores, grain)
stays, so skin reads smoother without going plastic. Nothing outside the mask moves.

Never use it on the treated area of a client's result (brows, lips, eyeliner, areola):
retouching the work is misleading advertising. Use --guard 0.06 on anyone wearing PMU.

Light and colour are NOT done here.

  python retouch.py IN OUT [--ss 28 --t 8] [--amount 0.6] [--even 0.1] [--guard 0.06]
                    [--slim 0] [--teeth 0] [--ref SEC | --ref-image PHOTO] [--debug-mask]
  IN a photo (.jpg .png .heic .webp ...) -> OUT a photo (.jpg/.png); IN a video -> OUT .mp4

--amount  how much of the line/blotch band to remove (0..1). 0.6 = natural, no plastic look.
--even    flattens large-scale tone patches (redness, shine) toward local average.
          Above ~0.2 it takes the colour out of the cheeks.
--guard   widens the protected brow/eye/lip zones by this fraction of face width.
          0.06 keeps eyeliner and lip-liner PMU untouched (fine lines right there stay too).
--slim    narrows the jaw and lifts the chin (fraction, e.g. 0.03 = 3%), off by default.
          The nose is never touched. Warps whatever is near the jaw too (hair, collar): keep it small.
--teeth   takes yellow out of the teeth inside the inner lip line (0..1), off by default.
          0.5 reads natural; lips, tongue and gums are left alone.
--ref     (video) seconds into the span where the person to retouch is alone in frame:
          SFace learns that face and only it is retouched; other faces are left untouched.
--ref-image  same, from a photo where that person is alone (works for photo and video input).
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

os.environ.setdefault("GLOG_minloglevel", "2")  # mute MediaPipe/TFLite startup chatter
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")
import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks.python import BaseOptions, vision

HOME = Path(os.environ.get("PMU_BEAUTIFY_HOME", Path.home() / ".pmu-beautify"))
MODEL = HOME / "models/face_landmarker.task"
SFACE = HOME / "models/face_recognition_sface_2021dec.onnx"  # opencv_zoo, for --ref
PHOTO = {".jpg", ".jpeg", ".png", ".heic", ".heif", ".webp", ".tif", ".tiff", ".bmp"}
C = vision.FaceLandmarksConnections


def idx(conns):
    return sorted({i for c in conns for i in (c.start, c.end)})


OVAL = idx(C.FACE_LANDMARKS_FACE_OVAL)
HOLES = [idx(C.FACE_LANDMARKS_LEFT_EYE), idx(C.FACE_LANDMARKS_RIGHT_EYE),
         idx(C.FACE_LANDMARKS_LEFT_EYEBROW), idx(C.FACE_LANDMARKS_RIGHT_EYEBROW),
         idx(C.FACE_LANDMARKS_LIPS)]

ANCHOR = sorted(set(sum(HOLES[:4], [])) | set(idx(C.FACE_LANDMARKS_NOSE)))
INNER_LIP = [78, 95, 88, 178, 87, 14, 317, 402, 318, 324, 308,  # lower, left to right
             415, 310, 311, 312, 13, 82, 81, 80, 191]           # upper, right to left


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height,r_frame_rate:stream_side_data=rotation",
                          "-of", "json", path], capture_output=True, text=True, check=True).stdout
    s = json.loads(out)["streams"][0]
    w, h = s["width"], s["height"]
    rot = next((abs(int(d.get("rotation", 0))) for d in s.get("side_data_list", [])), 0)
    if rot in (90, 270):
        w, h = h, w
    return w, h, s["r_frame_rate"]


EYES = idx(C.FACE_LANDMARKS_LEFT_EYE), idx(C.FACE_LANDMARKS_RIGHT_EYE)


def embedding(rec, f, pts):
    """SFace identity vector. The 5 alignment points come from the MediaPipe landmarks,
    in YuNet order (image-left eye first), so no second detector is needed."""
    eyes = sorted((pts[e].mean(0) for e in EYES), key=lambda p: p[0])
    mouth = sorted((pts[61], pts[291]), key=lambda p: p[0])
    x0, y0 = pts[OVAL].min(0); x1, y1 = pts[OVAL].max(0)
    row = np.array([[x0, y0, x1 - x0, y1 - y0, *eyes[0], *eyes[1], *pts[1], *mouth[0], *mouth[1], 1]], np.float32)
    v = rec.feature(rec.alignCrop(f, row)).ravel()
    return v / np.linalg.norm(v)


def mask_for(pts, shape, face_w, guard=0.0):
    m = np.zeros(shape, np.uint8)
    cv2.fillConvexPoly(m, cv2.convexHull(pts[OVAL]), 255)
    m = cv2.erode(m, None, iterations=max(1, int(face_w * 0.015)))  # keep off hairline/jaw edge
    holes = np.zeros(shape, np.uint8)
    for hole in HOLES:
        cv2.fillConvexPoly(holes, cv2.convexHull(pts[hole]), 255)
    if guard > 0:  # widen brows/eyes/lips so PMU on the lash line (eyeliner) or lip border is never smoothed
        g = int(face_w * guard) | 1
        holes = cv2.dilate(holes, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (g, g)))
    m[holes > 0] = 0
    pad = int(face_w * 0.03)
    m = cv2.erode(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (pad, pad)))
    k = int(face_w * 0.06) | 1
    return cv2.GaussianBlur(m, (k, k), 0).astype(np.float32)[..., None] / 255


def retouch(f, m, face_w, amount, even):
    x = f.astype(np.float32)
    s = face_w / 500  # filter radii scale with face size
    fine = cv2.GaussianBlur(x, (0, 0), 0.7 * s)
    mid = cv2.GaussianBlur(x, (0, 0), 5 * s)
    low = cv2.GaussianBlur(x, (0, 0), 30 * s)
    band = fine - mid                      # lines, small blotches
    tone = mid - low                       # larger patches
    y = x - amount * band * m - even * tone * m
    return np.clip(y, 0, 255).astype(np.uint8)


def whiten_teeth(f, pts, face_w, teeth):
    """Inside the inner lip line only: bright, low-saturation pixels (teeth, not tongue or
    gums) lose part of their yellow and gain a little light."""
    m = np.zeros(f.shape[:2], np.uint8)
    cv2.fillPoly(m, [pts[INNER_LIP]], 255)
    pad = max(1, int(face_w * 0.012))
    m = cv2.erode(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (pad, pad)))  # stay off the lips
    if m.sum() < 255 * 50:
        return f                                        # mouth closed
    hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV).astype(np.float32)
    sat, val = hsv[..., 1], hsv[..., 2]
    w = np.clip((110 - sat) / 50, 0, 1) * np.clip((val - 90) / 50, 0, 1) * (m / 255)
    k = max(3, int(face_w * 0.02)) | 1
    w = cv2.GaussianBlur(w, (k, k), 0)
    lab = cv2.cvtColor(f, cv2.COLOR_BGR2LAB).astype(np.float32)
    lab[..., 2] -= teeth * w * np.maximum(lab[..., 2] - 128, 0) * 0.7  # yellow toward neutral
    lab[..., 0] += teeth * w * (255 - lab[..., 0]) * 0.12            # a touch of light
    return cv2.cvtColor(np.clip(lab, 0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR)


def slim_warp(f, pts, face_w, slim):
    """Pull lower-face oval points toward the face midline and the chin up, as a smooth
    backward warp (each output pixel samples from where the displaced face came from)."""
    top, chin, nose = pts[10], pts[152], pts[1]
    u = (chin - top) / np.linalg.norm(chin - top)       # midline direction, follows head tilt
    span = np.dot(chin - nose, u)
    ctrl, disp = [], []
    for i in OVAL:
        p = pts[i]
        t = np.dot(p - nose, u) / span                  # 0 at nose tip, 1 at chin
        if t < -0.3:
            continue                                    # cheekbones and above stay put
        wgt = np.clip((t + 0.3) / 0.5, 0, 1)
        mid = top + np.dot(p - top, u) * u
        d = slim * wgt * (mid - p) - slim * 0.8 * span * np.clip(t, 0, 1) ** 2 * u
        ctrl.append(p); disp.append(d)
    for i in ANCHOR:                                    # eyes, brows, nose: pinned at zero
        ctrl.append(pts[i]); disp.append(np.zeros(2, np.float32))
    ctrl, disp = np.array(ctrl), np.array(disp)
    h, w = f.shape[:2]
    q = 4                                               # field on a 1/4 grid, then upscaled
    ys, xs = np.mgrid[0:h:q, 0:w:q].astype(np.float32)
    r2 = 2 * (0.12 * face_w) ** 2
    wts = np.exp(-((xs[..., None] - ctrl[:, 0]) ** 2 + (ys[..., None] - ctrl[:, 1]) ** 2) / r2)
    tot = wts.sum(-1, keepdims=True)
    field = (wts[..., None] * disp).sum(2) / np.maximum(tot, 1e-6) * np.minimum(tot, 1)
    fx = cv2.resize(field[..., 0], (w, h)); fy = cv2.resize(field[..., 1], (w, h))
    gy, gx = np.mgrid[0:h, 0:w].astype(np.float32)
    return cv2.remap(f, gx - fx, gy - fy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


def read_photo(path):
    """cv2.imread applies EXIF rotation; HEIC (iPhone) goes through macOS sips, or pillow-heif elsewhere."""
    if Path(path).suffix.lower() in (".heic", ".heif") and sys.platform != "darwin":
        from PIL import Image, ImageOps
        from pillow_heif import register_heif_opener
        register_heif_opener()
        rgb = np.asarray(ImageOps.exif_transpose(Image.open(path)).convert("RGB"))
        return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    if Path(path).suffix.lower() in (".heic", ".heif"):
        with tempfile.TemporaryDirectory() as d:
            jpg = str(Path(d) / "in.jpg")
            subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "100", path, "--out", jpg],
                           capture_output=True, check=True)
            return read_photo(jpg)
    f = cv2.imread(path, cv2.IMREAD_COLOR)
    if f is None:
        raise SystemExit(f"cannot read photo {path}")
    return f


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src"); ap.add_argument("dst")
    ap.add_argument("--ss", type=float); ap.add_argument("--t", type=float)
    ap.add_argument("--amount", type=float, default=0.6)
    ap.add_argument("--even", type=float, default=0.1)
    ap.add_argument("--smooth", type=float, default=0.6, help="landmark EMA, 0 = none")
    ap.add_argument("--slim", type=float, default=0.0)
    ap.add_argument("--teeth", type=float, default=0.0)
    ap.add_argument("--ref", type=float, help="(video) seconds into the span where the person to retouch is alone")
    ap.add_argument("--ref-image", help="photo where the person to retouch is alone; only that face is retouched")
    ap.add_argument("--ref-sim", type=float, default=0.363, help="min SFace cosine still counted as the same person (0.363 = OpenCV's same-person cut)")
    ap.add_argument("--guard", type=float, default=0.0, help="widen the brow/eye/lip holes by this fraction of face width (0.06 keeps eyeliner and lip-liner PMU untouched)")
    ap.add_argument("--debug-mask", action="store_true")
    a = ap.parse_args()
    if not MODEL.exists():
        raise SystemExit(f"models missing in {HOME}: run scripts/setup.sh (macOS) or scripts/setup.ps1 (Windows) first")

    still = Path(a.src).suffix.lower() in PHOTO
    if still and Path(a.dst).suffix.lower() not in (".jpg", ".jpeg", ".png"):
        raise SystemExit("photo in -> photo out: give OUT a .jpg or .png name")
    if still and a.ref is not None:
        raise SystemExit("--ref is for video; for a photo use --ref-image PHOTO_OF_THAT_PERSON_ALONE")
    cut = (["-ss", str(a.ss)] if a.ss is not None else []) + (["-t", str(a.t)] if a.t else [])
    if still:  # photo: read and write pixels directly, no yuv roundtrip
        img = read_photo(a.src)
        h, w = img.shape[:2]
        fps = "1/1"
    else:
        w, h, fps = probe(a.src)
    use_ref = a.ref is not None or a.ref_image is not None
    ref = None
    if use_ref:  # before any encoder starts: a bad reference must not leave a broken OUT behind
        if a.ref_image:
            rf = read_photo(a.ref_image)
        else:
            rf = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", *cut, "-i", a.src, "-ss", str(a.ref),
                                               "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "bgr24", "-"],
                                              capture_output=True, check=True).stdout, np.uint8).reshape(h, w, 3)
        rh, rw = rf.shape[:2]
        with vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(
                base_options=BaseOptions(model_asset_path=str(MODEL)), num_faces=2)) as one:
            fl = one.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(rf, cv2.COLOR_BGR2RGB))).face_landmarks
        if len(fl) != 1:
            raise SystemExit(f"reference: need exactly one face there, found {len(fl)} (try another time/photo)")
        rec = cv2.FaceRecognizerSF.create(str(SFACE), "")
        ref = embedding(rec, rf, np.array([[q.x * rw, q.y * rh] for q in fl[0]], np.float32))
    if still:
        frames, enc = iter([img]), None
    else:
        dec = subprocess.Popen(["ffmpeg", "-v", "error", *cut, "-i", a.src, "-f", "rawvideo",
                                "-pix_fmt", "bgr24", "-"], stdout=subprocess.PIPE)
        frames = (np.frombuffer(b, np.uint8).reshape(h, w, 3)
                  for b in iter(lambda: dec.stdout.read(w * h * 3), b"") if len(b) == w * h * 3)
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24",
                                "-s", f"{w}x{h}", "-r", fps, "-i", "-", *cut, "-i", a.src,
                                "-map", "0:v", "-map", "1:a?", "-c:v", "libx264", "-crf", "15",
                                "-preset", "slow", "-pix_fmt", "yuv420p", "-c:a", "copy",
                                "-movflags", "+faststart", a.dst], stdin=subprocess.PIPE)
    lm = vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=str(MODEL)),
        running_mode=vision.RunningMode.VIDEO, num_faces=3 if use_ref else 1))
    num, den = map(int, fps.split("/"))
    n, prev, raw, missed, others = 0, None, None, 0, 0
    for f in frames:
        r = lm.detect_for_video(mp.Image(image_format=mp.ImageFormat.SRGB,
                                         data=cv2.cvtColor(f, cv2.COLOR_BGR2RGB)),
                                int(n * 1000 * den / num))
        faces = [np.array([[q.x * w, q.y * h] for q in fl], np.float32) for fl in r.face_landmarks]
        if ref is not None and faces:
            sim = [float(embedding(rec, f, p) @ ref) for p in faces]
            hit = max(sim) >= a.ref_sim
            others += len(faces) - hit
            faces = [faces[int(np.argmax(sim))]] if hit else []
            if not faces:
                prev = None  # only someone else in frame: retouch nothing, never a stale mask on them
        if faces:
            raw = faces[0]
            prev = raw if prev is None else a.smooth * prev + (1 - a.smooth) * raw
        else:
            missed += 1  # shortcut: keeps last mask on a lost face; fine for brief misses, not cuts
        out = f
        if prev is not None:
            pts = prev.astype(np.int32)
            face_w = float(np.ptp(pts[OVAL, 0]))
            m = mask_for(pts, (h, w), face_w, a.guard)
            out = (m * 255).astype(np.uint8).repeat(3, 2) if a.debug_mask else retouch(f, m, face_w, a.amount, a.even)
            if a.teeth and not a.debug_mask:  # unsmoothed points: the mouth moves too fast for the EMA
                out = whiten_teeth(out, raw.astype(np.int32), face_w, a.teeth)
            if a.slim and not a.debug_mask:
                out = slim_warp(out, prev, face_w, a.slim)
        if still:
            cv2.imwrite(a.dst, out, [cv2.IMWRITE_JPEG_QUALITY, 95])
        else:
            enc.stdin.write(np.ascontiguousarray(out).tobytes())
        n += 1
    if enc:
        enc.stdin.close(); enc.wait()
        dec.wait()
    print(f"{n} frames, face missed in {missed}" + (f", other faces left alone: {others}" if ref is not None else ""))


if __name__ == "__main__":
    main()
