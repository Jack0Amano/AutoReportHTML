"""
結果表示HTMLレポート生成モジュール

他プロジェクトに埋め込み可能。テンプレート・出力先はすべて引数で指定する。
画像ファイルのコピーは行わず、渡されたパスをそのまま ``src`` 属性として利用する。
"""
import webbrowser
from pathlib import Path


def _to_html_src(path: Path) -> str:
    """パスを HTML の ``src`` 属性向けの文字列に変換する。

    Windows のバックスラッシュをスラッシュに置き換えるだけなので、
    相対パス・絶対パスのいずれにも利用できる。

    :param path: 変換対象のパス。
    :type path: pathlib.Path
    :returns: HTML で利用するパス文字列。
    :rtype: str
    """
    return str(path).replace("\\", "/")


def build_error_rows_html(error_pairs: list[tuple[Path, Path]]) -> str:
    """エラー画像のペアからテーブル行の HTML を生成する。

    画像ファイルはコピーせず、渡されたパスをそのまま ``src`` として使用する。

    :param error_pairs: (Error_Origin 画像パス, Error_Result 画像パス) のリスト。
    :type error_pairs: list[tuple[pathlib.Path, pathlib.Path]]
    :returns: テンプレートの ``{{ERROR_ROWS}}`` に埋め込む HTML 文字列。
              各行は ``<tr>`` 要素として連結される。
    :rtype: str
    """
    rows: list[str] = []
    for i, (origin_path, result_path) in enumerate(error_pairs):
        origin_src = _to_html_src(origin_path)
        result_src = _to_html_src(result_path)
        rows.append(
            f"        <tr>\n"
            f"          <td><img src=\"{origin_src}\" alt=\"Error_Origin_{i}\"></td>\n"
            f"          <td><img src=\"{result_src}\" alt=\"Error_Result_{i}\"></td>\n"
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
    *,
    open_browser: bool = True,
) -> None:
    """テンプレートを読み込み、プレースホルダを置換してレポート用 HTML を出力する。

    画像ファイルはコピーせず、引数として渡されたパスをそのまま ``src`` に埋め込む。
    そのため、呼び出し側でブラウザから参照可能なパス（テンプレートからの相対パスなど）を
    渡す必要がある。

    :param title: レポートのタイトル（``{{TITLE}}`` に埋め込まれる）。
    :type title: str
    :param evaluation: 評価値のテキスト（``{{EVALUATION}}``）。
    :type evaluation: str
    :param message: メッセージ文（``{{MESSAGE}}``）。
    :type message: str
    :param result_1_path: 結果画像のパス。``{{RESULT_1_SRC}}`` に埋め込まれる。
    :type result_1_path: pathlib.Path
    :param result_2_path: 結果グラフのパス。None の場合は ``{{RESULT_2_SRC}}`` を空文字で置換する。
    :type result_2_path: pathlib.Path | None
    :param error_pairs: (Error_Origin 画像パス, Error_Result 画像パス) のリスト。
    :type error_pairs: list[tuple[pathlib.Path, pathlib.Path]]
    :param output_html_path: 出力する HTML ファイルのパス。
    :type output_html_path: pathlib.Path
    :param template_path: テンプレート HTML のパス。
    :type template_path: pathlib.Path
    :param open_browser: True の場合、出力後に既定ブラウザで HTML を開く。
    :type open_browser: bool
    """
    template_text = template_path.read_text(encoding="utf-8")

    result_1_src = _to_html_src(result_1_path)
    result_2_src = _to_html_src(result_2_path) if result_2_path is not None else ""
    error_rows_html = build_error_rows_html(error_pairs)

    html = (
        template_text
        .replace("{{TITLE}}", title)
        .replace("{{EVALUATION}}", evaluation)
        .replace("{{MESSAGE}}", message)
        .replace("{{RESULT_1_SRC}}", result_1_src)
        .replace("{{RESULT_2_SRC}}", result_2_src)
        .replace("{{ERROR_ROWS}}", error_rows_html)
    )

    output_html_path.write_text(html, encoding="utf-8")
    print(f"出力: {output_html_path}")

    if open_browser:
        webbrowser.open(f"file://{output_html_path.resolve().as_posix()}")
