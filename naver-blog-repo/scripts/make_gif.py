"""동영상 → 블로그용 GIF.
사용법: python3 make_gif.py <영상파일> <출력.gif> [시작초] [길이초]
- 기본: 영상의 가장 움직임 많은 구간을 직접 고르지 않고, 지정 구간(기본 0초부터 4초)을 변환
- 가로 720px, 초당 12프레임, 128색. 결과가 8MB를 넘으면 가로 540px로 다시 만든다.
"""
import subprocess, sys
from pathlib import Path

src, out = sys.argv[1], Path(sys.argv[2])
start = sys.argv[3] if len(sys.argv) > 3 else "0"
dur = sys.argv[4] if len(sys.argv) > 4 else "4"


def run(width):
    vf = (f"fps=12,scale={width}:-1:flags=lanczos,split[a][b];"
          "[a]palettegen=max_colors=128:stats_mode=diff[p];[b][p]paletteuse=dither=bayer:bayer_scale=4")
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", start, "-t", dur,
                    "-i", src, "-vf", vf, str(out)], check=True)
    return out.stat().st_size


size = run(720)
if size > 8 * 1024 * 1024:
    size = run(540)
print(f"{out} {size / 1024 / 1024:.1f}MB")
