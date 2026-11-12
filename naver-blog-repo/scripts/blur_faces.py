"""사진·영상 속 얼굴 모자이크 (초상권 보호).

사용법:
  python3 blur_faces.py <입력 폴더 또는 파일> <출력 폴더>
  - 사진(jpg/png)과 영상(mp4/mov) 모두 처리
  - 출력 폴더에 모자이크된 파일 + check_*.jpg(검출 위치 표시)를 만든다
  - 얼굴이 하나도 없으면 원본을 그대로 복사

검출 방식 (놓치는 얼굴을 줄이려고 여러 번 겹쳐 찾음):
  1. YuNet 딥러닝 얼굴 검출 (전체 이미지)
  2. 같은 검출을 2x2로 나눈 조각에서 다시 실행 (멀리 있는 작은 얼굴용)
  3. Haar 옆모습 검출 (좌우 반전 포함)
  기준을 낮게 잡아, 얼굴이 아닌 곳을 가리는 쪽을 택한다 (놓치는 것보다 낫기 때문).
"""
import shutil, subprocess, sys
from pathlib import Path
import cv2
import numpy as np

MODEL = str(Path(__file__).resolve().parent.parent / "models" / "yunet.onnx")
SCORE = 0.75          # 이 점수 이상은 자동 모자이크 (실제 얼굴은 보통 0.85~0.95)
TILE_SCORE = 0.8      # 조각 검출 자동 모자이크 기준
REVIEW = 0.45         # 이 점수~자동 기준 사이는 '후보'로 모아 사람이 눈으로 확인
PAD = 0.35            # 얼굴 상자를 이만큼 넓혀서 가림 (머리카락·귀 포함)
BLOCK = 12            # 모자이크 칸 수 (얼굴 하나를 가로 몇 칸으로 뭉갤지)
IMG_EXT = {".jpg", ".jpeg", ".png"}
VID_EXT = {".mp4", ".mov", ".m4v"}

_det = None
REVIEW_LIST = []  # (파일명, [후보 상자]) — 사람이 확인할 목록
_profile = (cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_profileface.xml")
            if hasattr(cv2, "CascadeClassifier") and hasattr(cv2, "data") else None)  # OpenCV 5에는 없음


def plausible(f):
    """눈-코-입 배치가 사람 얼굴 같은지 확인 (음식 무늬 오검출 방지)."""
    x, y, w, h = f[:4]
    rex, rey, lex, ley, nx, ny, mrx, mry, mlx, mly = f[4:14]
    if not (0.5 < w / max(h, 1) < 1.6):
        return False
    eye_y, mouth_y = (rey + ley) / 2, (mry + mly) / 2
    eye_dist = abs(lex - rex)
    return eye_y < ny < mouth_y and eye_dist > 0.25 * w and (mouth_y - eye_y) > 0.25 * h


def yunet(img, score=SCORE, with_score=False):
    global _det
    h, w = img.shape[:2]
    if _det is None:
        _det = cv2.FaceDetectorYN.create(MODEL, "", (w, h), 0.3, 0.3, 5000)
    _det.setInputSize((w, h))
    _, faces = _det.detect(img)
    if faces is None:
        return []
    keep = [f for f in faces if f[14] >= score and plausible(f)]
    return [(tuple(map(int, f[:4])), float(f[14])) for f in keep] if with_score else [tuple(map(int, f[:4])) for f in keep]


def detect(img):
    h, w = img.shape[:2]
    scale = min(1.0, 1600 / max(h, w))
    small = cv2.resize(img, (int(w * scale), int(h * scale))) if scale < 1 else img
    boxes = [tuple(int(v / scale) for v in b) for b in yunet(small)]
    # 2x2 조각 (작은 얼굴)
    th, tw = h // 2, w // 2
    for ty in (0, th // 2, th):
        for tx in (0, tw // 2, tw):
            tile = img[ty:ty + th, tx:tx + tw]
            s2 = min(1.0, 1200 / max(tile.shape[:2]))
            t2 = cv2.resize(tile, (int(tile.shape[1] * s2), int(tile.shape[0] * s2))) if s2 < 1 else tile
            for x, y, bw, bh in yunet(t2, TILE_SCORE):
                boxes.append((int(x / s2) + tx, int(y / s2) + ty, int(bw / s2), int(bh / s2)))
    # 옆모습
    gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
    for flip in ((False, True) if _profile is not None else ()):
        g = cv2.flip(gray, 1) if flip else gray
        for x, y, bw, bh in _profile.detectMultiScale(g, 1.1, 6, minSize=(24, 24)):
            if flip:
                x = g.shape[1] - x - bw
            boxes.append(tuple(int(v / scale) for v in (x, y, bw, bh)))
    return merge(boxes)


def candidates(img):
    """자동 기준엔 못 미치지만 얼굴일 수도 있는 후보 (전체 + 조각)."""
    h, w = img.shape[:2]
    out = []
    for sc_max in (1600, 1200, 900):
        sc = min(1.0, sc_max / max(h, w))
        small = cv2.resize(img, (int(w * sc), int(h * sc)))
        for b, sco in yunet(small, REVIEW, True):
            if sco < SCORE:
                out.append(tuple(int(v / sc) for v in b))
    return merge(out)


def merge(boxes):
    out = []
    for b in sorted(boxes, key=lambda b: -b[2] * b[3]):
        x, y, w, h = b
        if any(x < ox + ow and ox < x + w and y < oy + oh and oy < y + h for ox, oy, ow, oh in out):
            continue
        out.append(b)
    return out


def mosaic(img, boxes):
    h, w = img.shape[:2]
    for x, y, bw, bh in boxes:
        px, py = int(bw * PAD), int(bh * PAD)
        x0, y0 = max(0, x - px), max(0, y - py)
        x1, y1 = min(w, x + bw + px), min(h, y + bh + py)
        roi = img[y0:y1, x0:x1]
        if roi.size == 0:
            continue
        n = max(1, BLOCK)
        k = max(1, roi.shape[1] // n)
        tiny = cv2.resize(roi, (max(1, roi.shape[1] // k), max(1, roi.shape[0] // k)), interpolation=cv2.INTER_LINEAR)
        img[y0:y1, x0:x1] = cv2.resize(tiny, (roi.shape[1], roi.shape[0]), interpolation=cv2.INTER_NEAREST)
    return img


def check_image(img, boxes, path):
    c = img.copy()
    for x, y, bw, bh in boxes:
        cv2.rectangle(c, (x, y), (x + bw, y + bh), (0, 0, 255), max(3, img.shape[1] // 300))
    s = 900 / max(c.shape[:2])
    cv2.imwrite(str(path), cv2.resize(c, (int(c.shape[1] * s), int(c.shape[0] * s))))


def do_image(src, out):
    img = cv2.imread(str(src))
    boxes = detect(img)
    cands = [c for c in candidates(img) if not any(c[0] < x + w and x < c[0] + c[2] and c[1] < y + h and y < c[1] + c[3] for x, y, w, h in boxes)]
    if cands:
        REVIEW_LIST.append((src.name, cands))
        tiles = []
        for x, y, bw, bh in cands:
            pad = int(max(bw, bh) * 0.6)
            crop = img[max(0, y - pad):y + bh + pad, max(0, x - pad):x + bw + pad]
            tiles.append(cv2.resize(crop, (220, 220)))
        cv2.imwrite(str(out / f"review_{src.stem}.jpg"), np.hstack(tiles))
    dst = out / src.name
    if boxes:
        check_image(img, boxes, out / f"check_{src.stem}.jpg")
        cv2.imwrite(str(dst), mosaic(img, boxes), [cv2.IMWRITE_JPEG_QUALITY, 92])
    else:
        shutil.copy2(src, dst)
    return len(boxes)


def do_video(src, out):
    cap = cv2.VideoCapture(str(src))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    w, h = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    tmp = out / f"_{src.stem}.mp4"
    ff = subprocess.Popen(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24",
                           "-s", f"{w}x{h}", "-r", str(fps), "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p",
                           "-crf", "20", str(tmp)], stdin=subprocess.PIPE)
    prev, max_faces, i = [], 0, 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        boxes = detect(frame) if i % 2 == 0 else prev   # 2프레임마다 검출
        # 직전 프레임 얼굴도 같이 가림 (검출이 한 프레임 놓쳐도 노출되지 않게)
        cover = merge(boxes + prev)
        if cover and max_faces == 0:
            check_image(frame, cover, out / f"check_{src.stem}.jpg")
        max_faces = max(max_faces, len(boxes))
        ff.stdin.write(mosaic(frame, cover).tobytes())
        prev, i = boxes, i + 1
    cap.release(); ff.stdin.close(); ff.wait()
    # 원본 소리 붙이기 (소리 없으면 영상만)
    dst = out / f"{src.stem}.mp4"
    r = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(tmp), "-i", str(src),
                        "-map", "0:v", "-map", "1:a?", "-c:v", "copy", "-c:a", "aac", str(dst)])
    if r.returncode != 0:
        tmp.replace(dst)
    tmp.unlink(missing_ok=True)
    return max_faces


def apply_review(out, decisions):
    """decisions: {"파일명": [후보 번호(0부터), ...]} — 얼굴로 판정된 후보만 추가 모자이크."""
    import json
    rv = dict((n, c) for n, c in json.loads((out / "review.json").read_text()))
    for name, idxs in decisions.items():
        img = cv2.imread(str(out / name))
        cv2.imwrite(str(out / name), mosaic(img, [rv[name][i] for i in idxs]), [cv2.IMWRITE_JPEG_QUALITY, 92])
        print(f"{name}: 후보 {idxs} 추가 모자이크")


if __name__ == "__main__":
    if sys.argv[1] == "apply_review":
        import json
        apply_review(Path(sys.argv[2]), json.loads(sys.argv[3])); sys.exit()
    src, out = Path(sys.argv[1]), Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    files = [src] if src.is_file() else sorted(p for p in src.iterdir() if p.suffix.lower() in IMG_EXT | VID_EXT)
    for f in files:
        n = do_video(f, out) if f.suffix.lower() in VID_EXT else do_image(f, out)
        print(f"{f.name}: 얼굴 {n}개{' → 모자이크' if n else ''}")
    if REVIEW_LIST:
        import json
        (out / "review.json").write_text(json.dumps(REVIEW_LIST))
        print("\n눈으로 확인할 후보:", ", ".join(f"{n} {len(c)}개" for n, c in REVIEW_LIST), "→ review_*.jpg 확인 후 apply_review로 반영")
