# pixel_art_app.py

from turtle import Turtle, Screen
import cv2
from screenshot import ScreenShot # ScreenShot クラスの定義が必要

# グローバル変数は宣言だけにするか、main関数内で初期化する
dot = None
screen = None
# screenshot = None # 必要であれば同様に

# img, h, w は image_component から返されるので、グローバルで初期化は不要
# x, y, r, g, b は draw_pixel のループ内で定義される想定

def image_component():
    import cv2 # 関数内でimportするのは一般的ではないが、現状維持
    # sample.png が実行時に存在することを想定
    try:
        img = cv2.imread("sample.png", cv2.IMREAD_UNCHANGED)
        if img is None:
            raise FileNotFoundError("sample.png not found or could not be read by OpenCV.")
    except Exception as e:
        print(f"Error loading image: {e}")
        # テスト時にはモックされるので、実際のファイル読み込みエラーは発生しない想定
        # もしテスト以外でこの関数が呼ばれるなら、適切なエラーハンドリングが必要
        return None, 0, 0

    trans_img = img.transpose(1,0,2)[:,::-1]
    h,w,c = trans_img.shape
    print(f"height: {h}\nwidth: {w}\nchannel: {c}")
    # pos_rgb = trans_img[h-1,w-1] # この行は print でしか使われていない
    # print(pos_rgb)
    return trans_img, h, w

def settings(current_screen): # screen を引数で受け取るように変更
    current_screen.colormode(255)
    current_screen.setup(0.6,0.8)
    current_screen.screensize(1000,1000)
    current_screen.delay(0)
    current_screen.tracer(2000,0)
    current_screen.title("Pixelization App")

def draw_pixel(current_dot, x_pos, y_pos, r_val, g_val, b_val): # dot と描画情報を引数で受け取る
    current_dot.shape("circle")
    current_dot.speed(10)
    current_dot.penup()
    current_dot.setpos(x_pos-100, y_pos-100) # x,y は引数で渡されたものを使う
    current_dot.color((r_val, g_val, b_val), (r_val, g_val, b_val)) # r,g,b も引数
    current_dot.shapesize(0.2,0.2)
    current_dot.stamp()
    current_dot.penup()

def main():
    global dot, screen # グローバル変数を参照・代入することを明示

    # Turtle と Screen のインスタンスを main 関数内で生成
    dot = Turtle()
    screen = Screen()
    # screenshot = ScreenShot() # 必要であれば

    settings(screen) # screen インスタンスを渡す
    img_data, h_val, w_val = image_component()

    if img_data is None:
        print("Failed to load image data. Exiting.")
        return

    for x_coord in range(1,h_val+1,5):
        for y_coord in range(1,w_val+1,5):
            # position = [x_coord,y_coord] # 未使用
            pos_rgb_val = img_data[x_coord-1,y_coord-1]
            b_val_cv = pos_rgb_val[0]
            g_val_cv = pos_rgb_val[1]
            r_val_cv = pos_rgb_val[2]
            print(f"x:{x_coord}, y:{y_coord}, RGB:{r_val_cv,g_val_cv,b_val_cv}")
            draw_pixel(dot, x_coord, y_coord, r_val_cv, g_val_cv, b_val_cv) # dotと描画情報を渡す

    print(screen.canvheight)
    # screen.listen() # CI環境では不要
    screen.exitonclick()

# スクリプトとして直接実行された場合のみ main() を呼び出す
if __name__ == "__main__":
    main()
