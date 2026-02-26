"""
結果表示HTMLレポート生成モジュール

他プロジェクトに埋め込み可能。テンプレート・出力先はすべて引数で指定する。
ダミーデータ生成は含まない。
"""
import webbrowser
from pathlib import Path
from typing import Callable

import cv2
import numpy as np


def ensure_result_images_dir(result_images_dir: Path) -> None:
    """出力用画像を保存するディレクトリを作成する。

    Args:
        result_images_dir: 作成するディレクトリのパス。親ディレクトリも必要なら作成する。
    """
    result_images_dir.mkdir(parents=True, exist_ok=True)


def load_image(path: Path) -> np.ndarray | None:
    """cv2 で画像を読み込む。

    Args:
        path: 画像ファイルのパス。

    Returns:
        読み込み成功時は BGR の ndarray、失敗時またはファイルが存在しない場合は None。
    """
    if not path.exists():
        return None
    img = cv2.imread(str(path))
    return img


def save_image(img: np.ndarray, save_path: Path) -> None:
    """画像を PNG で指定パスに保存する。

    Args:
        img: BGR 形式の画像（cv2 で読み込んだ ndarray）。
        save_path: 保存先ファイルパス。
    """
    cv2.imwrite(str(save_path), img)


def build_error_rows_html(
    error_pairs: list[tuple[Path, Path]],
    result_images_dir: Path,
    *,
    image_loader: Callable[[tuple[Path, Path]], tuple[np.ndarray, np.ndarray]] | None = None,
) -> str:
    """エラー画像のペアからテーブル行の HTML を生成し、画像を result_images_dir に保存する。

    Args:
        error_pairs: (Error_Origin 画像パス, Error_Result 画像パス) のリスト。
        result_images_dir: 画像の保存先ディレクトリ。ファイル名は error_origin_0.png 等になる。
        image_loader: 省略時は load_image で読み込む。(origin_path, result_path) を受け取り
            (origin_img, result_img) を返す callable を渡すと、ファイルがなくてもメモリ上の画像で生成可能。
            読み込み失敗時は ValueError を送出すること。

    Returns:
        テンプレートの {{ERROR_ROWS}} に埋め込む HTML 文字列（<tr> 行の連結、または「なし」の1行）。
    """
    def default_loader(pair: tuple[Path, Path]) -> tuple[np.ndarray, np.ndarray]:
        o = load_image(pair[0])
        r = load_image(pair[1])
        if o is None:
            raise ValueError(f"画像を読み込めません: {pair[0]}")
        if r is None:
            raise ValueError(f"画像を読み込めません: {pair[1]}")
        return (o, r)

    loader = image_loader or default_loader
    prefix = result_images_dir.name
    rows = []
    for i, (origin_path, result_path) in enumerate(error_pairs):
        origin_save = result_images_dir / f"error_origin_{i}.png"
        result_save = result_images_dir / f"error_result_{i}.png"
        origin_img, result_img = loader((origin_path, result_path))
        save_image(origin_img, origin_save)
        save_image(result_img, result_save)
        rel_origin = f"{prefix}/{origin_save.name}"
        rel_result = f"{prefix}/{result_save.name}"
        rows.append(
            f"        <tr>\n"
            f"          <td><img src=\"{rel_origin}\" alt=\"Error_Origin_{i}\"></td>\n"
            f"          <td><img src=\"{rel_result}\" alt=\"Error_Result_{i}\"></td>\n"
            f"        </tr>"
        )
    return "\n".join(rows) if rows else "        <tr><td colspan=\"2\">なし</td></tr>"


def generate_report(
    title: str,
    evaluation: str,
    message: str,
    result_1_path: Path,
    result_2_path: Path | None,
    error_pairs: list[tuple[Path, Path]],
    output_html_path: Path,
    template_path: Path,
    result_images_dir: Path,
    *,
    open_browser: bool = True,
    image_loader: Callable[[tuple[Path, Path]], tuple[np.ndarray, np.ndarray]] | None = None,
) -> None:
    """テンプレートを読み込み、画像を保存してプレースホルダを置換し、レポート用 HTML を出力する。

    他プロジェクトに埋め込む場合は、template_path / output_html_path / result_images_dir
    を任意のパスで指定する。output_html_path と result_images_dir は同じ親ディレクトリに置くことを推奨。

    Args:
        title: レポートのタイトル（{{TITLE}} に埋め込まれる）。
        evaluation: 評価値のテキスト（{{EVALUATION}}）。
        message: メッセージ文（{{MESSAGE}}）。
        result_1_path: 結果画像のファイルパス。result_images_dir に result_1.png としてコピーされる。
        result_2_path: 結果グラフのファイルパス。None の場合は保存をスキップ（事前に result_2.png を置いている想定）。
        error_pairs: (Error_Origin 画像パス, Error_Result 画像パス) のリスト。
        output_html_path: 出力する HTML ファイルのパス。
        template_path: テンプレート HTML のパス。
        result_images_dir: 画像を保存するディレクトリ（HTML 内では result_images/xxx として参照される）。
        open_browser: True の場合、出力後に既定ブラウザで HTML を開く。
        image_loader: エラー画像用のカスタムローダー。未指定時は load_image でファイルから読み込む。

    Raises:
        ValueError: result_1_path または result_2_path（None でない場合）の画像を読み込めないとき。
    """
    ensure_result_images_dir(result_images_dir)

    result_1_img = load_image(result_1_path)
    if result_1_img is None:
        raise ValueError(f"結果画像を読み込めません: {result_1_path}")
    save_image(result_1_img, result_images_dir / "result_1.png")

    if result_2_path is not None:
        result_2_img = load_image(result_2_path)
        if result_2_img is None:
            raise ValueError(f"結果グラフを読み込めません: {result_2_path}")
        save_image(result_2_img, result_images_dir / "result_2.png")

    error_rows_html = build_error_rows_html(
        error_pairs, result_images_dir, image_loader=image_loader
    )

    template_text = template_path.read_text(encoding="utf-8")
    html = (
        template_text
        .replace("{{TITLE}}", title)
        .replace("{{EVALUATION}}", evaluation)
        .replace("{{MESSAGE}}", message)
        .replace("{{ERROR_ROWS}}", error_rows_html)
    )

    output_html_path.write_text(html, encoding="utf-8")
    print(f"出力: {output_html_path}")

    if open_browser:
        webbrowser.open(f"file://{output_html_path.resolve().as_posix()}")
