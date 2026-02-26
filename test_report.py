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

from report import generate_report, ensure_result_images_dir


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
    ax.set_xlabel("値")
    ax.set_ylabel("度数")
    ax.set_title("結果グラフ（ヒストグラム）")
    fig.tight_layout()
    fig.savefig(save_path, bbox_inches="tight")
    plt.close(fig)


def run_test_data_1() -> None:
    """
    テストデータ1:
    - 結果グラフ: matplotlib で偽ヒストグラムを生成
    - 結果画像・エラー画像: image フォルダがあれば使用、なければダミー
    """
    from report import load_image, save_image

    ensure_result_images_dir(RESULT_IMAGES_DIR)
    create_fake_histogram(RESULT_IMAGES_DIR / "result_2.png")

    result_1_path = IMAGE_DIR / "result_1.png"
    if load_image(result_1_path) is None:
        save_image(
            load_or_create_image(result_1_path, "result_1"),
            RESULT_IMAGES_DIR / "result_1.png",
        )
        result_1_path = RESULT_IMAGES_DIR / "result_1.png"

    error_pairs = [
        (IMAGE_DIR / "error_origin_0.png", IMAGE_DIR / "error_result_0.png"),
        (IMAGE_DIR / "error_origin_1.png", IMAGE_DIR / "error_result_1.png"),
        (IMAGE_DIR / "error_origin_2.png", IMAGE_DIR / "error_result_2.png"),
        (IMAGE_DIR / "error_origin_3.png", IMAGE_DIR / "error_result_3.png"),
        (IMAGE_DIR / "error_origin_4.png", IMAGE_DIR / "error_result_4.png"),
    ]

    def dummy_image_loader(pair: tuple[Path, Path]) -> tuple[np.ndarray, np.ndarray]:
        a, b = pair
        return (
            load_or_create_image(a, "Error_Origin"),
            load_or_create_image(b, "Error_Result"),
        )

    generate_report(
        title="出力結果",
        evaluation="0.75",
        message="エラー画像が5ファイル検出されました",
        result_1_path=result_1_path,
        result_2_path=None,
        error_pairs=error_pairs,
        output_html_path=OUTPUT_HTML,
        template_path=TEMPLATE_PATH,
        result_images_dir=RESULT_IMAGES_DIR,
        open_browser=True,
        image_loader=dummy_image_loader,
    )


if __name__ == "__main__":
    run_test_data_1()
