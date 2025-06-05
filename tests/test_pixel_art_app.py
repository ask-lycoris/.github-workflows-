# test_pixel_art_app.py
import pytest
from unittest import mock
import numpy as np

# テスト対象のスクリプトをインポート
import pixel_art_app

# --- モックの設定 ---
@pytest.fixture
def mock_cv2_imread(monkeypatch):
    mock_image_data = np.zeros((10, 15, 3), dtype=np.uint8)
    mock_image_data[9, 14] = [10, 20, 30] # BGR

    # _imread が複数回呼ばれる可能性や、状態を持つ場合を考慮し、
    # 簡単な mock オブジェクトでラップする
    _imread_mock = mock.Mock(return_value=mock_image_data.copy())

    def side_effect_imread(filename, flags):
        if filename == "sample.png":
            return _imread_mock(filename, flags) # _imread_mock を呼び出す
        raise FileNotFoundError(f"Mock cv2.imread: File '{filename}' not found.")

    monkeypatch.setattr(pixel_art_app.cv2, "imread", side_effect_imread)
    monkeypatch.setattr(pixel_art_app.cv2, "IMREAD_UNCHANGED", "mock_flag_unchanged")
    return _imread_mock # 呼び出しチェック用に _imread_mock を返す

@pytest.fixture
def mock_turtle_screen_setup(monkeypatch):
    """
    pixel_art_app.Screen クラスと、pixel_art_app.screen グローバル変数をモックします。
    pixel_art_app.main() が呼び出されたときにインスタンスが生成・使用されることを想定。
    """
    mock_screen_instance = mock.Mock(spec=pixel_art_app.Screen)
    Screen_class_mock = mock.Mock(return_value=mock_screen_instance)
    monkeypatch.setattr(pixel_art_app, "Screen", Screen_class_mock)

    # pixel_art_app.main() 内で screen が代入されるので、
    # ここで pixel_art_app.screen を直接モックする必要はない。
    # main() 実行後に pixel_art_app.screen が mock_screen_instance になっていることを確認できる。
    return mock_screen_instance, Screen_class_mock

@pytest.fixture
def mock_turtle_dot_setup(monkeypatch):
    """
    pixel_art_app.Turtle クラスと、pixel_art_app.dot グローバル変数をモックします。
    """
    mock_dot_instance = mock.Mock(spec=pixel_art_app.Turtle)
    Turtle_class_mock = mock.Mock(return_value=mock_dot_instance)
    monkeypatch.setattr(pixel_art_app, "Turtle", Turtle_class_mock)
    return mock_dot_instance, Turtle_class_mock


# --- テスト関数 ---
def test_image_component(mock_cv2_imread): # mock_cv2_imread は呼び出し確認用モック
    """image_component 関数のテスト"""
    trans_img, h, w = pixel_art_app.image_component()

    # cv2.imread が "sample.png" で呼び出されたか確認
    # mock_cv2_imread は cv2.imread の実体ではなく、その return_value を返す内部モック
    # なので、pixel_art_app.cv2.imread.assert_called_once_with(...) のようにする
    pixel_art_app.cv2.imread.assert_called_once_with("sample.png", "mock_flag_unchanged")

    assert h == 15
    assert w == 10
    assert trans_img.shape == (15, 10, 3)

    original_pixel_bgr = np.array([10, 20, 30])
    transposed_for_check = mock_cv2_imread.return_value.transpose(1,0,2) # _imread_mock.return_value を使う
    assert np.array_equal(transposed_for_check[14,9], original_pixel_bgr)
    assert np.array_equal(trans_img[14,0], original_pixel_bgr)


def test_settings(mock_turtle_screen_setup):
    """settings 関数のテスト"""
    mock_screen_instance, _ = mock_turtle_screen_setup # インスタンスを取得

    # settings 関数は screen インスタンスを引数に取るように変更された
    pixel_art_app.settings(mock_screen_instance)

    mock_screen_instance.colormode.assert_called_once_with(255)
    mock_screen_instance.setup.assert_called_once_with(0.6, 0.8)
    mock_screen_instance.screensize.assert_called_once_with(1000, 1000)
    mock_screen_instance.delay.assert_called_once_with(0)
    mock_screen_instance.tracer.assert_called_once_with(2000, 0)
    mock_screen_instance.title.assert_called_once_with("Pixelization App")


def test_draw_pixel(mock_turtle_dot_setup):
    """draw_pixel 関数のテスト"""
    mock_dot_instance, _ = mock_turtle_dot_setup # インスタンスを取得

    # draw_pixel は dot インスタンスと描画情報を引数に取るように変更された
    x_test, y_test = 10, 20
    r_test, g_test, b_test = 255, 128, 0
    pixel_art_app.draw_pixel(mock_dot_instance, x_test, y_test, r_test, g_test, b_test)

    mock_dot_instance.shape.assert_called_once_with("circle")
    mock_dot_instance.speed.assert_called_once_with(10)
    assert mock_dot_instance.penup.call_count >= 2 # 変更なし
    mock_dot_instance.setpos.assert_called_once_with(x_test - 100, y_test - 100)
    mock_dot_instance.color.assert_called_once_with((r_test, g_test, b_test), (r_test, g_test, b_test))
    mock_dot_instance.shapesize.assert_called_once_with(0.2, 0.2)
    mock_dot_instance.stamp.assert_called_once()

# (オプション) main 関数の結合テスト（モックを使ってGUIエラーを回避）
# このテストは、main関数内のロジックフローや各コンポーネントの呼び出しを検証します。
@mock.patch('pixel_art_app.cv2.imread') # image_component 内の imread
def test_main_function_flow(mock_cv2_imread_main, mock_turtle_screen_setup, mock_turtle_dot_setup):
    """main 関数のフローをテスト（GUIなしで実行できるか）"""
    # モックの設定
    mock_screen_instance, Screen_class_mock_main = mock_turtle_screen_setup
    mock_dot_instance, Turtle_class_mock_main = mock_turtle_dot_setup

    # cv2.imread の戻り値を設定 (main 関数内の image_component 呼び出し用)
    mock_image_data = np.zeros((5, 5, 3), dtype=np.uint8) # テスト用に小さい画像
    mock_image_data[0,0] = [1,2,3] # BGR
    mock_cv2_imread_main.return_value = mock_image_data

    # main 関数を実行
    # main 関数内で screen.exitonclick() が呼ばれるが、
    # screen は mock_screen_instance なので、実際のGUI処理は行われない
    pixel_art_app.main()

    # Screen と Turtle がインスタンス化されたか確認
    Screen_class_mock_main.assert_called_once()
    Turtle_class_mock_main.assert_called_once()

    # settings が呼び出されたか (screen のメソッド呼び出しで代用)
    mock_screen_instance.title.assert_called_with("Pixelization App")

    # image_component (cv2.imread) が呼び出されたか
    mock_cv2_imread_main.assert_called_once_with("sample.png", pixel_art_app.cv2.IMREAD_UNCHANGED)

    # draw_pixel が呼び出されたか (dot のメソッド呼び出しで代用)
    # ループ回数に応じて複数回呼ばれる
    assert mock_dot_instance.stamp.call_count > 0

    # exitonclick が呼び出されたか
    mock_screen_instance.exitonclick.assert_called_once()
