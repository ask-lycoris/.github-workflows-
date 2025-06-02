from turtle import Turtle, Screen
import cv2
from screenshot import ScreenShot 

dot =Turtle()
screen = Screen()
screenshot = ScreenShot()

def image_component():
    import cv2
    img = cv2.imread("sample.png", cv2.IMREAD_UNCHANGED)   # specify the name of the file to be pixelization as the first argument.
    trans_img = img.transpose(1,0,2)[:,::-1]         # when importing a color image, for some reason it is turned sideways, so rotate it 90 degrees.
                                                     #=カラー画像読み込むとなぜか横向きになるので90度回転させる
    h,w,c = trans_img.shape
    print(f"height: {h}\nwidth: {w}\nchannel: {c}")
    pos_rgb = trans_img[h-1,w-1]      # extract the BGR of the specified coordinates.
    print(pos_rgb)
    return trans_img, h, w

def settings():
    screen.colormode(255)
    screen.setup(0.6,0.8)             # Determine the screen size to be displayed in the ratio of the height and width of the PC screen as 1,1 (pixels can also be specified).
                                      #=PCの画面の縦横を1,1(ピクセル指定も可)として比率で表示するスクリーンサイズ決定
    screen.screensize(1000,1000)      # specify the screen size that can be drawn.
    screen.delay(0)                   # to make it faster than speed.(10)
    screen.tracer(2000,0)             # to make it faster set up for batch processing every 100 at once.
    screen.title("Pixelization App")  # window title bar

def draw_pixel():
    dot.shape("circle")
    dot.speed(10)               # 0 = "fastest": no animation
    dot.penup()
    dot.setpos(x-100,y-100)     # start position from(0,0)
                                #=点描開始位置を(0,0)からずらす-->(x-400,y-300)
    dot.color((r,g,b),(r,g,b))
    dot.shapesize(0.2,0.2)      # customize stamp size(len magnification, wid magnification)
    dot.stamp()
    dot.penup()                 # after draw one line, pen will up at once then move again.


settings()
img, h, w = image_component()

for x in range(1,h+1,5):
    for y in range(1,w+1,5):
        position = [x,y]        # extraction of all coordinates
        pos_rgb = img[x-1,y-1]
        b = pos_rgb[0]          #OpenCV-> output order="BGR", turtle-> output order="RGB". Be careful.
        g = pos_rgb[1]
        r = pos_rgb[2]
        print(f"x:{x}, y:{y}, RGB:{r,g,b}")
        draw_pixel()

print(screen.canvheight)
#screen.listen()
screen.exitonclick()  
