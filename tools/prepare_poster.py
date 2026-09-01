# -*- coding: utf-8 -*-
"""ポスター画像を配信用に変換して posters/NNN.png へ置く。

使い方:
    python tools/prepare_poster.py <画像ファイル> <番号>

例:
    python tools/prepare_poster.py "C:/Users/shota miyazawa/Desktop/20260818_ss/poster/yuu.png" 1

出力は必ず 1365x2048（縦/横 = 1.50）に揃える。額縁の開口と同じ比率である。
元画像は切らずに、この枠へ収まる最大の大きさで中央に置き、余った部分は
台紙と同じ色で埋める。

ワールド側でポスター面の形を変えないための処置である。面の形が変わらなければ
Lightmap Static のまま焼けるので、焼いた光がそのまま正しく乗る。余白部分にも
台紙と同じライトマップが乗るため、境界は見えない。

番号は roster.json の台帳と対応させる。一度振った番号は変更しないこと。
Unity 側の VRCUrl はこの番号でワールドに焼き込まれているため、
番号を振り直すとワールドの再ビルドが必要になる。
"""

import os
import sys

from PIL import Image

# 額縁の開口と同じ比率（高さ / 幅）。出力はこの比率に必ず揃える。
# 解像度そのものは画像ごとに違ってよい。ポスター面の UV は 0〜1 なので、
# 比率さえ合っていれば正しい大きさで表示される。
CANVAS_RATIO = 1.50

# VRChat の Image Loading の上限。これを超えると読み込みエラーになる。
MAX_W = 1365
MAX_H = 2048

# 余白の色。Unity 側 MAT_Gallery_OffWhite_DomeTuned の _Color を sRGB8 にしたもの。
# ここを変えるときは Unity 側の台紙色も必ず合わせること。
MAT_COLOR = (239, 236, 229)

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

        # P（パレット）モードのまま縮小すると色が壊れるので RGB を経由する。
        work = im.convert("RGB")

        # 元画像をちょうど包む 1.50 の枠を求める。拡大はしない。
        # 拡大しても元にない解像度が増えるだけで、ぼけて容量も増える。
        canvas_w = max(width, -(-height * 2 // 3))   # ceil(height / 1.5)
        canvas_h = round(canvas_w * CANVAS_RATIO)

        # 上限を超える場合だけ、枠と画像を同じ倍率で縮める。
        if canvas_w > MAX_W or canvas_h > MAX_H:
            shrink = min(MAX_W / canvas_w, MAX_H / canvas_h)
            canvas_w = int(canvas_w * shrink)
            canvas_h = round(canvas_w * CANVAS_RATIO)
            new_size = (max(1, round(width * shrink)), max(1, round(height * shrink)))
        else:
            new_size = (width, height)

        # 端数で枠から 1px はみ出すことがあるので、収まるまで詰める。
        fit = min(1.0, canvas_w / new_size[0], canvas_h / new_size[1])
        if fit < 1.0:
            new_size = (max(1, int(new_size[0] * fit)), max(1, int(new_size[1] * fit)))
        if new_size != (width, height):
            work = work.resize(new_size, Image.LANCZOS)

        canvas = Image.new("RGB", (canvas_w, canvas_h), MAT_COLOR)
        left = (canvas_w - new_size[0]) // 2
        top = (canvas_h - new_size[1]) // 2
        canvas.paste(work, (left, top))
        canvas.save(dst_path, "PNG", optimize=True)

    if left > 0:
        margin = "左右に台紙 %dpx ずつ" % left
    elif top > 0:
        margin = "上下に台紙 %dpx ずつ" % top
    else:
        margin = "余白なし"
    src_mb = os.path.getsize(src_path) / 1024 / 1024
    dst_mb = os.path.getsize(dst_path) / 1024 / 1024
    print(
        "%03d.png  %dx%d -> 画像%dx%d / 枠%dx%d(%.3f)  %s  %.1fMB -> %.1fMB"
        % (slot, width, height, new_size[0], new_size[1],
           canvas_w, canvas_h, canvas_h / canvas_w, margin, src_mb, dst_mb)
    )
    return dst_path


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        raise SystemExit(1)
    prepare(sys.argv[1], int(sys.argv[2]))


if __name__ == "__main__":
    main()
