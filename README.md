# SOUNDSHEEP ワールド配信データ

VRChat ワールドが毎月読みに行くテキストとポスター画像を置くリポジトリ。
ここを書き換えるとワールドに反映される。**ワールドの再ビルドは要らない。**

## 公開 URL

GitHub Pages を有効にすると、次の URL で配信される。

| 内容 | URL |
|---|---|
| テキスト | `https://wonderinglaika710-rgb.github.io/ss/live.json` |
| ポスター | `https://wonderinglaika710-rgb.github.io/ss/posters/001.png` 〜 `100.png` |
| 確認ページ | `https://wonderinglaika710-rgb.github.io/ss/` |

**この URL は Unity 側に焼き込まれている。変えてはいけない。**
リポジトリ名を変える、ファイルを別の場所へ移す、番号を振り直す、
拡張子を `.jpg` にする、いずれもワールドが読めなくなる。

### GitHub Pages の有効化（最初に一度だけ）

Settings → Pages → Build and deployment で
Source を `Deploy from a branch`、Branch を `main` / `(root)` にして Save。
数分で公開される。

## 毎月やること

1. `live.json` を開いて、鉛筆アイコンから3人分を書き換える
2. Commit する
3. 確認ページ（上の表の3行目）を開いて、検査がすべて緑になっているか見る

反映まで CDN のキャッシュで数分から十数分かかることがある。

### live.json の書き方

```json
{
  "updated": "2026-09-01",
  "acts": [
    {
      "poster": 1,
      "name": "演者名",
      "group": "グループ名",
      "groupId": "grp_00000000-0000-0000-0000-000000000000"
    }
  ]
}
```

- `poster` … `roster.json` の番号。この番号が `posters/001.png` に対応する
- `groupId` … VRChat のグループページ URL の `grp_` 以降をそのまま貼る。
  `https://vrchat.com/home/group/grp_xxxx…` の `grp_xxxx…` の部分。
  短縮コード（`EXAMPL.9920` の形式）は使えない
- 出演者が2人の月は、`acts` の要素を2つにする。ワールドが件数を見て枠を出し分ける

## ポスターを追加するとき

`roster.json` の末尾に続きの番号を足し、その番号で画像を作って `posters/` に置く。

```bash
python tools/prepare_poster.py "元の画像.png" 15
```

長辺 2048 を超えていれば自動で縮小され、`posters/015.png` として書き出される。

**番号は 100 までワールド側に用意してある。** 101 番以降を使うには
Unity 側で枠を増やしてワールドを再ビルドする必要がある。
また、一度振った番号は変更しない。過去の記録と食い違う。

## 壊さないための決まり

- **長辺 2048 ピクセル以下。** 超えるとその画像だけ VRChat で読み込みエラーになる
- **拡張子は `.png`。大文字小文字も区別される。** `.PNG` は別ファイル扱い
- **UTF-8（BOM なし）で保存する。** 演者名が化ける
- **演者名・グループ名に半角の `[ ] { }` を使わない。**
  Udon の JSON パーサがこれで誤パースするバグがある。全角の（）【】は問題ない
- **画像を差し替えるときは同じパスに上書きする。** 消してから上げ直しても URL は
  変わらないが、上書きのほうが履歴が追いやすい

## ファイル構成

```
.
├── .nojekyll                  Jekyll のビルドを止める
├── index.html                 確認ページ。JSON の壊れと画像の欠けを検査する
├── live.json                  ワールドが読む。毎月書き換えるのはこれだけ
├── roster.json                番号台帳。ワールドは読まない。人が見失わないための記録
├── posters/
│   ├── 001.png 〜             ポスター。番号が live.json の poster と対応する
└── tools/
    └── prepare_poster.py      画像を 2048 以下に整えて posters/ へ入れる
```
