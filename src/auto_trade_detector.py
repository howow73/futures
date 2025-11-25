from PyQt6.QtCore import Qt, QTimer, QDateTime, QObject, pyqtSignal
# Note: PyQt6 is not required for detection; present due to earlier context.
# Core deps: opencv-python, pyautogui, numpy, pillow

import argparse, time
from typing import Optional, Tuple, List
import numpy as np, pyautogui
from PIL import Image
import cv2

pyautogui.FAILSAFE = True

def parse_region(s: Optional[str]):
    return None if not s else tuple(int(p.strip()) for p in s.split(","))

def parse_hotkey(s: str):
    return [t.strip() for t in s.split("+") if t.strip()]

def grab_screen(region):
    shot = pyautogui.screenshot(region=region) if region else pyautogui.screenshot()
    import numpy as _np, cv2 as _cv2
    return _cv2.cvtColor(_np.array(shot), _cv2.COLOR_RGB2BGR)

def load_template(path: str):
    img = Image.open(path).convert("RGB")
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

def multi_scale_match(screen, template, scales, threshold):
    h_t, w_t = template.shape[:2]
    best_val, best_loc, best_wh, best_scale = -1.0, None, None, None
    for s in scales:
        tw, th = int(w_t*s), int(h_t*s)
        if tw < 8 or th < 8: continue
        tpl = cv2.resize(template, (tw, th), interpolation=cv2.INTER_AREA if s<1.0 else cv2.INTER_CUBIC)
        res = cv2.matchTemplate(screen, tpl, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        if max_val > best_val:
            best_val, best_loc, best_wh, best_scale = max_val, max_loc, (tw, th), s
    if best_val >= threshold:
        x, y = best_loc; w, h = best_wh
        return True, (x, y, w, h), best_val, best_scale
    return False, None, best_val, best_scale

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--template", required=True)
    ap.add_argument("--threshold", type=float, default=0.87)
    ap.add_argument("--cooldown", type=float, default=3.0)
    ap.add_argument("--hotkey", type=str, default="ctrl+alt+1")
    ap.add_argument("--region", type=str, default=None)
    ap.add_argument("--interval", type=float, default=0.4)
    ap.add_argument("--scales", type=str, default="1.0,0.9,1.1")
    ap.add_argument("--once", action="store_true")
    args = ap.parse_args()

    region = parse_region(args.region)
    scales = [float(s.strip()) for s in args.scales.split(",") if s.strip()]
    template = load_template(args.template)
    combo = parse_hotkey(args.hotkey)

    print(f"[Detector] template={args.template}, threshold={args.threshold}, hotkey={combo}")
    if region: print(f"[Detector] region={region}")
    print(f"[Detector] scales={scales}, interval={args.interval}s, cooldown={args.cooldown}s, once={args.once}")
    last_trigger = 0.0

    try:
        while True:
            img = grab_screen(region)
            ok, rect, score, scale = multi_scale_match(img, template, scales, args.threshold)
            now = time.time()
            if ok and (now - last_trigger) >= args.cooldown:
                print(f"[HIT] score={score:.3f} scale={scale} rect={rect} → hotkey {combo}")
                try:
                    pyautogui.hotkey(*combo)
                except Exception as e:
                    print("[ERROR] failed to send hotkey:", e)
                last_trigger = now
                if args.once: break
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("Stopped by user (Ctrl+C).")

if __name__ == "__main__":
    main()
