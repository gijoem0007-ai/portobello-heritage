import sys
from PIL import Image

def crop(screenshot_path, vw, x, y, w, h, out_path):
    im = Image.open(screenshot_path)
    sw, sh = im.size
    scale = sw / vw
    box = (round(x*scale), round(y*scale), round((x+w)*scale), round((y+h)*scale))
    c = im.crop(box)
    c.save(out_path)
    print(out_path, box, c.size)

if __name__ == '__main__':
    # args: screenshot_path vw x y w h out_path
    crop(sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5]), float(sys.argv[6]), sys.argv[7])
