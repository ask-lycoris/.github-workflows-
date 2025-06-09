import unittest
from unittest.mock import patch, MagicMock
import numpy as np
import cv2  # <--- この行を追加しました

# テスト対象のスクリプトをインポート
import pixel_art_app

class TestPixelArtApp(unittest.TestCase):
    """
    pixel_art_app.py のためのテストスイート。
    各テストは関心事ごとに分離されています。
    """

    @patch('cv2.imread')
    def test_image_component_success(self, mock_imread):
        """image_component: 画像の読み込みが成功するケースをテスト"""
        # --- 準備 (Arrange) ---
        # cv2.imreadが返すダミーの画像データを作成
        # transpose後の (高さ, 幅, チャンネル) を想定
        height, width = 10, 20
        dummy_image = np.zeros((height, width, 3), dtype=np.uint8)
        mock_imread.return_value = dummy_image

        # --- 実行 (Act) ---
        trans_img, h, w = pixel_art_app.image_component()

        # --- 検証 (Assert) ---
        # 'cv2'をインポートしたので、この行は正しく動作します
        mock_imread.assert_called_once_with("sample.png", cv2.IMREAD_UNCHANGED)
        self.assertIsNotNone(trans_img)
        # image_component内でtransposeされるため、hとwが逆になる
        self.assertEqual(h, width) 
        self.assertEqual(w, height)

    @patch('cv2.imread')
    def test_image_component_failure(self, mock_imread):
        """image_component: 画像の読み込みが失敗するケースをテスト"""
        # --- 準備 (Arrange) ---
        mock_imread.return_value = None # 読み込み失敗を模倣

        # --- 実行 (Act) ---
        trans_img, h, w = pixel_art_app.image_component()

        # --- 検証 (Assert) ---
        self.assertIsNone(trans_img)
        self.assertEqual(h, 0)
        self.assertEqual(w, 0)

    def test_settings_calls_screen_methods(self):
        """settings: 渡されたscreenインスタンスのメソッドを正しく呼び出すかテスト"""
        # --- 準備 (Arrange) ---
        # Screenクラスの「インスタンス」を模倣したモックを手動で作成
        mock_screen_instance = MagicMock()

        # --- 実行 (Act) ---
        pixel_art_app.settings(mock_screen_instance)

        # --- 検証 (Assert) ---
        # 期待通りにメソッドが特定の引数で呼び出されたかを検証
        mock_screen_instance.colormode.assert_called_once_with(255)
        mock_screen_instance.setup.assert_called_once_with(0.6, 0.8)
        mock_screen_instance.screensize.assert_called_once_with(1000, 1000)
        mock_screen_instance.title.assert_called_once_with("Pixelization App")
        # tracerは2つの引数で呼ばれることを確認
        mock_screen_instance.tracer.assert_called_once_with(2000, 0)

    # main関数が依存するオブジェクトをすべてモック化
    @patch('pixel_art_app.image_component')
    @patch('pixel_art_app.Turtle')
    @patch('pixel_art_app.Screen')
    def test_main_function_flow(self, mock_screen_cls, mock_turtle_cls, mock_image_component):
        """main: 全体の処理フロー（各部品の連携）をテスト"""
        # --- 準備 (Arrange) ---
        
        # main関数内で image_component が呼ばれた際の戻り値を設定
        height, width = 5, 5
        dummy_image = np.zeros((height, width, 3), dtype=np.uint8)
        mock_image_component.return_value = (dummy_image, height, width)

        # main関数内で Screen() や Turtle() が呼び出されたときに返される
        # 「インスタンスのモック」を取得
        mock_screen_instance = mock_screen_cls.return_value
        mock_turtle_instance = mock_turtle_cls.return_value

        # --- 実行 (Act) ---
        pixel_art_app.main()

        # --- 検証 (Assert) ---
        
        # 1. 依存オブジェクトが正しく生成・呼び出しされたか
        mock_image_component.assert_called_once()
        mock_screen_cls.assert_called_once()
        mock_turtle_cls.assert_called_once()

        # 2. settings関数が呼ばれ、Screenインスタンスのメソッドが叩かれたか
        mock_screen_instance.title.assert_called_with("Pixelization App")

        # 3. ループ内でdraw_pixelが呼ばれ、Turtleインスタンスのメソッドが叩かれたか
        #    ループは(x=1,y=1), (x=1,y=5) などで回るため、stampは少なくとも1回は呼ばれる
        self.assertTrue(mock_turtle_instance.stamp.called)
        # 最初のstamp()呼び出しの前に、期待されるメソッドが呼ばれているか確認
        mock_turtle_instance.setpos.assert_any_call(1 - 100, 1 - 100)
        
        # 4. 最後にGUIを終了させる処理が呼ばれたか
        mock_screen_instance.exitonclick.assert_called_once()


# このファイルが直接実行された場合にテストを走らせる
if __name__ == '__main__':
    unittest.main()
