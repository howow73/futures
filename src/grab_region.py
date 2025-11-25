import argparse, pyautogui
from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument("--region", required=True, help='"x,y,w,h"')
ap.add_argument("--out", default="template.png")
args = ap.parse_args()

x,y,w,h = (int(v) for v in args.region.split(","))
img = pyautogui.screenshot(region=(x,y,w,h))
img.save(args.out)
print(f"Saved {args.out} from region ({x},{y},{w},{h})")
