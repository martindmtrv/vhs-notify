import tkinter as tk
from PIL import Image, ImageTk, ImageGrab


def screenshot():
  # sample images
  # return Image.open("./images/blue_end.png")
  # return Image.open("./images/static.png")
  # return Image.open("./images/normal.png")

  # actual screenshot
  return ImageGrab.grab()

topx, topy, botx, boty = 0, 0, 0, 0
rect_id = None

def get_mouse_posn(event):
    global topy, topx

    topx, topy = event.x, event.y

def update_sel_rect(event):
    global rect_id
    global topy, topx, botx, boty

    botx, boty = event.x, event.y
    canvas.coords(rect_id, topx, topy, botx, boty)  # Update selection rect.


window = tk.Tk()
window.title("Select Area")
window.configure(background='grey')

ss = screenshot()

img = ImageTk.PhotoImage(ss)
canvas = tk.Canvas(window, width=img.width(), height=img.height(),
                  borderwidth=0, highlightthickness=0)
canvas.pack(expand=True)
canvas.img = img  # Keep reference in case this code is put into a function.
canvas.create_image(0, 0, image=img, anchor=tk.NW)

# Create selection rectangle (invisible since corner points are equal).
rect_id = canvas.create_rectangle(topx, topy, topx, topy,
                                  dash=(2,2), fill='', outline='white')

canvas.bind('<Button-1>', get_mouse_posn)
canvas.bind('<B1-Motion>', update_sel_rect)

window.mainloop()

# now we have the dimensions
print(topx, topy, botx, boty)


# --- start here --- 

import random
import time
import requests

"""
This function will select n random pixels from the center/upper line of the screen and return them
"""
def get_random_central_pixels(n: int) -> list:
  pixels = []
  for _ in range(n):
    x = random.randint(topx, botx)
    y = random.randint(topy, boty)

    pixels.append((x, y))

  return pixels

def is_blueish(p: tuple) -> bool:
  # approx check for blue
  return p[0] <= 10 and p[2] >= 135 and p[2] <= 145 and p[1] < 5

def is_static(p: tuple) -> bool:
  # approx check for static 
  return p[0] == p[1] and p[1] == p[2]

DELAY = 10
NOTIFICATIONS_BEFORE_END = 20
NOTIF_SERVER = "https://ntfy.chromart.dynv6.net/vhs"

# increase to lower FP, but also increase TN
NUM_PIXELS = 10

notified = 0
frames = 0

while True:
  print(f"Frame {frames+1}:")
  # take a screenshot
  ss = screenshot()

  pixels = get_random_central_pixels(5)

  isEndBlue = True

  # check if all pixels are blueish -> signalling end of tape
  for p in pixels:
    if not is_blueish(ss.getpixel(p)):
      isEndBlue = False
      break

  isStatic = True

  # check if all static
  for p in pixels:
    if not is_static(ss.getpixel(p)):
      isStatic = False
      break

  if isEndBlue:
    requests.post(NOTIF_SERVER, data="VHS Recording hit End Blue")
    print("notify end blue")
    notified += 1

  if isStatic:
    requests.post(NOTIF_SERVER, data="VHS Recording hit Static")
    print("notify isstatic")
    notified += 1

  
  if notified > NOTIFICATIONS_BEFORE_END:
    requests.post(NOTIF_SERVER, data="Reached limit of notifications, please restart Python app on PC and continue")
    print("reached limit of notifications, please restart app and continue")
    break

  time.sleep(DELAY)
  frames += 1