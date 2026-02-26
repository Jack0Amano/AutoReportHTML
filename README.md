# ResultGUI — 結果表示HTML

Python で処理した結果画像・グラフ・エラー画像を、1枚の HTML レポートにまとめて表示・印刷するためのツールです。

---

## 概要

- **テンプレート**（`template.html`）に、タイトル・結果画像・結果グラフ・評価値・メッセージ・エラー一覧を埋め込んで **出力用 HTML** を生成します。
- 画像は **result_images** フォルダに保存し、HTML から相対パスで参照します。
- レイアウトはテーブル形式で、**印刷しやすい**デザインです（PC 表示・印刷対応、レスポンシブは未対応）。

---

## 主な機能

| 項目 | 説明 |
|------|------|
| 結果画像（result_1） | 処理結果の画像を表示 |
| 結果グラフ（result_2） | グラフ画像（例: matplotlib のヒストグラム）を表示。結果画像と横並び |
| 評価値 | 数値やテキストを表示 |
| メッセージ | 任意のメッセージを表示 |
| エラー一覧 | 処理前（Error_Origin）と処理後（Error_Result）の画像をセットで表示。複数セット対応 |

---

## プロジェクト構成

```
ResultGUI/
├── README.md           # このファイル
├── requirements.txt    # Python 依存関係
├── template.html       # HTML テンプレート（プレースホルダを置換して使用）
├── report.py           # レポート生成モジュール（他プロジェクトに埋め込み用）
├── test_report.py      # テスト用スクリプト（ダミーデータ作成 + report 呼び出し）
├── result_images/      # 出力画像を保存するフォルダ（スクリプト実行時に生成）
├── output.html         # 生成されたレポート（test_report.py 実行後に生成）
└── image/              # テスト用画像を置くフォルダ（任意）
```

- **report.py** … レポート生成のみ。パスはすべて引数で受け取るため、他プロジェクトにコピーしてそのまま利用可能。ダミー生成は含まない。
- **test_report.py** … ダミー画像・偽ヒストグラムの作成と `report.generate_report` の呼び出しのみ。

---

## 必要環境

- Python 3.10 以上（型ヒントで `Path | None` を使用）
- 依存パッケージ: `opencv-python`, `matplotlib`

---

## セットアップ

```bash
# リポジトリをクローンまたはダウンロード後、プロジェクトフォルダで実行
pip install -r requirements.txt
```

---

## 使い方

### テスト実行（すぐに動作確認）

```bash
python test_report.py
```

- テンプレートを読み込み、**結果グラフは matplotlib で偽のヒストグラム**を生成します。
- 結果画像・エラー画像は **image** フォルダがあればそこから読み込み、なければダミー画像を生成します。
- 出力: **output.html** と **result_images/** 内の画像。完了後に既定ブラウザで `output.html` が開きます。

### 他プロジェクトに埋め込む場合

**report.py** をコピーし、`template.html` と一緒に配置して利用します。テンプレート・出力先はすべて引数で指定するため、スクリプトの場所に依存しません。

```python
from pathlib import Path
from report import generate_report, ensure_result_images_dir

template_path = Path("path/to/template.html")
output_html_path = Path("path/to/output.html")
result_images_dir = Path("path/to/result_images")

ensure_result_images_dir(result_images_dir)
# result_1.png / result_2.png を result_images_dir に用意するか、パスを渡す

generate_report(
    title="レポートタイトル",
    evaluation="0.85",
    message="処理が完了しました",
    result_1_path=Path("path/to/result_1.png"),
    result_2_path=Path("path/to/result_2.png"),  # 不要なら None
    error_pairs=[(Path("origin_0.png"), Path("result_0.png")), ...],
    output_html_path=output_html_path,
    template_path=template_path,
    result_images_dir=result_images_dir,
    open_browser=False,
)
```

- **テンプレート**  
  `template.html` のプレースホルダ: `{{TITLE}}`, `{{EVALUATION}}`, `{{MESSAGE}}`, `{{ERROR_ROWS}}` を `generate_report` が置換します。
- **画像**  
  `result_1_path` / `result_2_path` で指定した画像は `result_images_dir` にコピーされます。エラー画像は `error_pairs` の各パスから読み、同様に `result_images_dir` に保存されます。読み込みに失敗した場合は `ValueError` になります。
- **エラー画像をメモリから渡したい場合**  
  `generate_report(..., image_loader=my_loader)` で、`(origin_path, result_path) -> (origin_ndarray, result_ndarray)` の形の関数を渡せば、ファイルがなくてもメモリ上の画像でレポートを生成できます。例は `test_report.py` の `dummy_image_loader` を参照。

---

## テストデータ（test_report.py）

`run_test_data_1()` では次の条件でレポートを生成します。

- **タイトル**: 出力結果  
- **評価値**: 0.75  
- **メッセージ**: エラー画像が5ファイル検出されました  
- **結果画像**: `image/result_1.png`（なければダミー）  
- **結果グラフ**: matplotlib で生成したヒストグラム（`result_images/result_2.png`）  
- **エラー**: 5 セット（`image/error_origin_0.png` と `image/error_result_0.png` など。無ければダミー）

---

## ライセンス

**フリー（MIT License）**  
改変・再配布・商用利用ともに自由です。作者へのクレジット表記は任意です。

```text
MIT License

Copyright SAKI ITO(c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
