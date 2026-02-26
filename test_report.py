"""
結果表示HTMLのテストスクリプト（ダミーデータでレポート生成）

レポート生成機能は report モジュールにあり、本ファイルは
ダミー画像・偽ヒストグラムの作成と report.generate_report の呼び出しのみ行う。
"""
from pathlib import Path

import cv2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from report import generate_report


# このスクリプトのディレクトリ
SCRIPT_DIR = Path(__file__).resolve().parent
TEMPLATE_PATH = SCRIPT_DIR / "template.html"
OUTPUT_HTML = SCRIPT_DIR / "output.html"
RESULT_IMAGES_DIR = SCRIPT_DIR / "result_images"
IMAGE_DIR = SCRIPT_DIR / "image"


def load_or_create_image(path: Path, fallback_name: str) -> np.ndarray:
    """
    画像を cv2 で読み込む。存在しない場合はテスト用のダミー画像を生成する。
    （report モジュールには含めず、テスト・ダミー用のみ）
    """
    if path.exists():
        img = cv2.imread(str(path))
        if img is not None:
            return img
    h, w = 200, 300
    img = np.full((h, w, 3), 220, dtype=np.uint8)
    cv2.rectangle(img, (10, 10), (w - 10, h - 10), (180, 180, 180), 2)
    cv2.putText(
        img, fallback_name, (20, 100),
        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 100), 2,
    )
    return img


def create_fake_histogram(save_path: Path) -> None:
    """matplotlib で偽のヒストグラムを作成し、指定パスに保存する。"""
    np.random.seed(42)
    data = np.random.normal(100, 15, 200)
    fig, ax = plt.subplots(figsize=(5, 3.5), dpi=120)
    ax.hist(data, bins=25, color="steelblue", edgecolor="white", linewidth=0.5)
    ax.set_title("ResultGraph")
    fig.tight_layout()
    fig.savefig(save_path)
    plt.close(fig)


def run_test_data_1() -> None:
    """
    テストデータ1:
    - 結果グラフ: matplotlib で偽ヒストグラムを生成
    - 結果画像・エラー画像: image フォルダがあれば使用、なければダミー
    """
    RESULT_IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    # 結果グラフ（ヒストグラム）は result_images に生成
    result_2_path = RESULT_IMAGES_DIR / "result_2.png"
    create_fake_histogram(result_2_path)

    # 結果画像 result_1 は image があればそれを使い、なければ result_images にダミーを生成
    result_1_candidate = IMAGE_DIR / "result_1.png"
    if result_1_candidate.exists():
        result_1_path = result_1_candidate
    else:
        result_1_path = RESULT_IMAGES_DIR / "result_1.png"
        cv2.imwrite(str(result_1_path), load_or_create_image(result_1_path, "result_1"))

    # エラー画像は image があればそれを参照し、なければ result_images にダミーを生成
    error_pairs: list[tuple[Path, Path]] = []
    for i in range(5):
        origin_src = IMAGE_DIR / f"error_origin_{i}.png"
        result_src = IMAGE_DIR / f"error_result_{i}.png"
        if not origin_src.exists():
            origin_src = RESULT_IMAGES_DIR / f"error_origin_{i}.png"
            cv2.imwrite(str(origin_src), load_or_create_image(origin_src, f"Error_Origin_{i}"))
        if not result_src.exists():
            result_src = RESULT_IMAGES_DIR / f"error_result_{i}.png"
            cv2.imwrite(str(result_src), load_or_create_image(result_src, f"Error_Result_{i}"))
        error_pairs.append((origin_src, result_src))

    generate_report(
        title="出力結果",
        evaluation="0.75",
        message="エラー画像が5ファイル検出されました",
        result_1_path=result_1_path,
        result_2_path=result_2_path,
        error_pairs=error_pairs,
        output_html_path=OUTPUT_HTML,
        template_path=TEMPLATE_PATH,
        open_browser=True,
    )


if __name__ == "__main__":
    run_test_data_1()
