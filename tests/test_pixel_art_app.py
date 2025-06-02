import pytest
from unittest import mock
import numpy as np

# テスト対象のスクリプトをインポート
# このファイル (test_pixel_art_app.py) が tests/ ディレクトリにあり、
# pixel_art_app.py がプロジェクトルートにある場合、
# プロジェクトルートで pytest を実行すれば正しくインポートできます。
import pixel_art_app

# --- モックの設定 ---
@pytest.fixture
def mock_cv2_imread(monkeypatch):
    # ダミーの画像データ (高さ10, 幅15, 3チャンネル)
    # OpenCVのBGR順で [青, 緑, 赤]
    mock_image_data = np.zeros((10, 15, 3), dtype=np.uint8)
    # 例として右下のピクセルに色を設定 (BGR: 10, 20, 30)
    mock_image_data[9, 14] = [10, 20, 30]

    def _imread(filename, flags):
        if filename == "sample.png":
            return mock_image_data.copy() # 変更を防ぐためコピーを返す
        raise FileNotFoundError(f"Mock cv2.imread: File '{filename}' not found.")

    monkeypatch.setattr(pixel_art_app.cv2, "imread", _imread)
    # cv2.IMREAD_UNCHANGED も何らかの値にモックしておく（実際の値はテストに影響しない場合）
    monkeypatch.setattr(pixel_art_app.cv2, "IMREAD_UNCHANGED", "mock_flag_unchanged")
    return _imread

@pytest.fixture
def mock_turtle_screen(monkeypatch):
    # pixel_art_app内で Screen() が呼び出されるため、クラス自体をモックする
    mock_screen_instance = mock.Mock(spec=pixel_art_app.Screen) # インスタンスの振る舞いを定義
    Screen_class_mock = mock.Mock(return_value=mock_screen_instance) # クラス呼び出しでモックインスタンスを返す
    monkeypatch.setattr(pixel_art_app, "Screen", Screen_class_mock)

    # グローバル変数 'screen' もモックインスタンスで置き換える
    # (pixel_art_app.py の screen = Screen() の結果がこれになる)
    monkeypatch.setattr(pixel_art_app, "screen", mock_screen_instance)
    return mock_screen_instance

@pytest.fixture
def mock_turtle_dot(monkeypatch):
    mock_dot_instance = mock.Mock(spec=pixel_art_app.Turtle)
    Turtle_class_mock = mock.Mock(return_value=mock_dot_instance)
    monkeypatch.setattr(pixel_art_app, "Turtle", Turtle_class_mock)

    # グローバル変数 'dot' もモックインスタンスで置き換える
    monkeypatch.setattr(pixel_art_app, "dot", mock_dot_instance)
    return mock_dot_instance

# --- テスト関数 ---
def test_image_component(mock_cv2_imread):
    """image_component 関数のテスト"""
    # 関数を実行
    trans_img, h, w = pixel_art_app.image_component()

    # cv2.imread が "sample.png" で呼び出されたか確認
    # mock_cv2_imread.assert_called_once_with("sample.png", "mock_flag_unchanged")
    # assert_any_call の方が柔軟な場合がある
    assert any(call == mock.call("sample.png", "mock_flag_unchanged") for call in mock_cv2_imread.call_args_list)


    # 元のモック画像は (高さ10, 幅15)
    # trans_img = img.transpose(1,0,2) なので、形状は (幅15, 高さ10, 3) になる
    # h,w,c = trans_img.shape なので、h=15, w=10
    assert h == 15  # transpose後の高さ
    assert w == 10  # transpose後の幅
    assert trans_img.shape == (15, 10, 3)

    # pixel_art_app.py内のロジック: pos_rgb = trans_img[h-1,w-1]
    # h=15, w=10 なので、trans_img[14,9] を参照する。
    # 元画像 img[9,14] = [10,20,30] (BGR)
    # transpose(1,0,2) すると、trans_img[14,9] = [10,20,30]
    # さらに [:,::-1] (左右反転) すると、trans_img[14,9] は変わらない (ピクセル単位なので)
    # いや、[:,::-1] は幅方向の反転。trans_img[14,0] が元の trans_img[14,9] になるはず。
    # しかし、コードでは `trans_img = img.transpose(1,0,2)[:,::-1]` となっているので、
    # `trans_img[h_trans-1, w_trans-1]` は `(img.transpose(1,0,2)[:,::-1])[h_trans-1, w_trans-1]`
    # `h_trans=15, w_trans=10`.
    # `trans_img[14, 9]` の値を確認
    # `img.transpose(1,0,2)` の段階では `[14,9]` は `[10,20,30]`
    # `[:,::-1]` を適用すると、`w`次元が反転。`trans_img[row, col]` の `col` が `W-1-col` になる。
    # `trans_img[14, 9]` は、反転前の `(img.transpose(1,0,2))[14, 10-1-9] = (img.transpose(1,0,2))[14,0]`
    # `(img.transpose(1,0,2))[14,0]` は元画像の `img[0,14]` に対応する。
    # モック画像 `mock_image_data[0,14]` は `[0,0,0]`
    # これは複雑なので、関数の最後の print(pos_rgb) に依存するのではなく、
    # 関数の主要な変換ロジック（transpose）が機能しているかを主に確認する。
    #
    # 関数の最後の pos_rgb 抽出ロジックを直接テストするなら:
    # expected_pixel_after_transpose_and_flip = mock_cv2_imread.return_value.transpose(1,0,2)[:,::-1][h-1, w-1]
    # pos_rgb_in_func = ... (これを取得する方法がないので、このテストは難しい)
    #
    # ここでは、transposeされた形状と、特定の変換後のピクセルが期待通りかを単純化して確認
    original_pixel_bgr = np.array([10, 20, 30]) # mock_image_data[9,14]
    # transpose(1,0,2) -> mock_image_data の (9,14) は trans_img の (14,9) に移動
    # [:,::-1] -> trans_img の (14,9) は、反転前の (14, 10-1-9) = (14,0) の値
    # よって、trans_img[14,9] は、元々の mock_image_data の (0,14) のピクセルのBGRになる。
    # mock_image_data[0,14] は [0,0,0]
    # これでは意図したテストにならない。

    # 再考：関数内の `pos_rgb = trans_img[h-1,w-1]` を直接検証するのは難しい。
    # 関数が `trans_img` を正しく生成していることを検証するに留める。
    # 元の `mock_image_data[9,14]` (BGR: 10,20,30) は、
    # `img.transpose(1,0,2)` によって `transposed_for_check[14,9]` に位置する。
    transposed_for_check = mock_cv2_imread.return_value.transpose(1,0,2)
    assert np.array_equal(transposed_for_check[14,9], original_pixel_bgr)

    # `[:,::-1]` の効果は、`trans_img` の幅全体に影響する。
    # `trans_img[14,0]` が `transposed_for_check[14,9]` の値を持つはず。
    assert np.array_equal(trans_img[14,0], original_pixel_bgr)


def test_settings(mock_turtle_screen):
    """settings 関数のテスト"""
    pixel_art_app.settings()

    mock_turtle_screen.colormode.assert_called_once_with(255)
    mock_turtle_screen.setup.assert_called_once_with(0.6, 0.8)
    mock_turtle_screen.screensize.assert_called_once_with(1000, 1000)
    mock_turtle_screen.delay.assert_called_once_with(0)
    mock_turtle_screen.tracer.assert_called_once_with(2000, 0)
    mock_turtle_screen.title.assert_called_once_with("Pixelization App")

def test_draw_pixel(mock_turtle_dot, monkeypatch):
    """draw_pixel 関数のテスト"""
    # グローバル変数をテスト用に設定
    monkeypatch.setattr(pixel_art_app, "x", 10) # draw_pixel 内で x-100 される
    monkeypatch.setattr(pixel_art_app, "y", 20) # draw_pixel 内で y-100 される
    monkeypatch.setattr(pixel_art_app, "r", 255)
    monkeypatch.setattr(pixel_art_app, "g", 128)
    monkeypatch.setattr(pixel_art_app, "b", 0)

    pixel_art_app.draw_pixel()

    mock_turtle_dot.shape.assert_called_once_with("circle")
    mock_turtle_dot.speed.assert_called_once_with(10)
    # penup は複数回呼ばれる可能性がある
    assert mock_turtle_dot.penup.call_count >= 2
    mock_turtle_dot.setpos.assert_called_once_with(10 - 100, 20 - 100)
    mock_turtle_dot.color.assert_called_once_with((255, 128, 0), (255, 128, 0))
    mock_turtle_dot.shapesize.assert_called_once_with(0.2, 0.2)
    mock_turtle_dot.stamp.assert_called_once()

# メインの for ループ部分のテストは、そのロジックを別の関数に切り出すなど
# リファクタリングを行うと、よりテストしやすくなります。
# 現状では、主要な関数が期待通りに呼び出されるかを上記のテストで確認しています。
