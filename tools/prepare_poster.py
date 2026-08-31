# -*- coding: utf-8 -*-
"""ポスター画像を配信用に変換して posters/NNN.png へ置く。

使い方:
    python tools/prepare_poster.py <画像ファイル> <番号>

例:
    python tools/prepare_poster.py "C:/Users/shota miyazawa/Desktop/20260818_ss/poster/yuu.png" 1

VRChat の Image Loading は長辺 2048 ピクセルを超える画像を読み込めない。
超えるものは縮小する。PNG は可逆圧縮なので、縮小が要らない画像も
再圧縮して配信量を減らす（画質は落ちない）。

番号は roster.json の台帳と対応させる。一度振った番号は変更しないこと。
Unity 側の VRCUrl はこの番号でワールドに焼き込まれているため、
番号を振り直すとワールドの再ビルドが必要になる。
"""

import os
import sys

from PIL import Image

# VRChat Image Loading の上限。これを超えると読み込みエラーになる。
MAX_EDGE = 2048

# 割り当て済みの番号の上限。Unity 側に用意した VRCUrl の枠数と一致させる。
MAX_SLOT = 100

HERE = os.path.dirname(os.path.abspath(__file__))
POSTERS_DIR = os.path.join(os.path.dirname(HERE), "posters")


def prepare(src_path, slot):
    """1 枚を posters/NNN.png へ変換配置する。"""
    if not os.path.isfile(src_path):
        raise SystemExit("画像が見つからない: %s" % src_path)
    if not 1 <= slot <= MAX_SLOT:
        raise SystemExit("番号は 1〜%d の範囲で指定する: %d" % (MAX_SLOT, slot))

    os.makedirs(POSTERS_DIR, exist_ok=True)
    dst_path = os.path.join(POSTERS_DIR, "%03d.png" % slot)

    with Image.open(src_path) as im:
        width, height = im.size
        long_edge = max(width, height)

        # P（パレット）モードのまま縮小すると色が壊れるので RGBA を経由する。
        work = im.convert("RGBA")

        if long_edge > MAX_EDGE:
            scale = MAX_EDGE / long_edge
            new_size = (round(width * scale), round(height * scale))
            work = work.resize(new_size, Image.LANCZOS)
            action = "縮小"
        else:
            new_size = (width, height)
            action = "そのまま"

        # 透過が使われていなければ RGB に落としてファイルを軽くする。
        if work.getchannel("A").getextrema() == (255, 255):
            work = work.convert("RGB")

        work.save(dst_path, "PNG", optimize=True)

    src_mb = os.path.getsize(src_path) / 1024 / 1024
    dst_mb = os.path.getsize(dst_path) / 1024 / 1024
    print(
        "%03d.png  %s  %dx%d -> %dx%d  %.1fMB -> %.1fMB"
        % (slot, action, width, height, new_size[0], new_size[1], src_mb, dst_mb)
    )
    return dst_path


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        raise SystemExit(1)
    prepare(sys.argv[1], int(sys.argv[2]))


if __name__ == "__main__":
    main()
