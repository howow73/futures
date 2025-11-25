
"""
test.py
- Helper to test grab_region.py by invoking it with a region.
- Usage:
    python test.py --region "x,y,w,h" --out template_test.png
  If --region is omitted, it will interactively prompt you.
"""
import argparse
import subprocess
import sys
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--region", type=str, default=None, help='"x,y,w,h" (e.g., "100,200,300,150")')
    parser.add_argument("--out", type=str, default="template_test.png", help="Output image path")
    args = parser.parse_args()

    # Ask interactively if not provided
    region = args.region
    if not region:
        print("[test.py] --region not provided.")
        print("  Tip: Run 'python mouse_watch.py' in another terminal to see live X,Y.")
        region = input('Enter region as "x,y,w,h": ').strip()

    # Basic validation
    try:
        x, y, w, h = (int(v) for v in region.split(","))
        if w <= 0 or h <= 0:
            raise ValueError("w,h must be positive")
    except Exception as e:
        print("[test.py] Invalid --region format. Expected x,y,w,h (ints). Error:", e)
        sys.exit(2)

    # Determine path to grab_region.py (same folder as this script)
    here = Path(__file__).resolve().parent
    grab = here / "grab_region.py"
    if not grab.exists():
        print(f"[test.py] ERROR: {grab} not found. Make sure you're running inside the auto_trade_detector folder.")
        sys.exit(1)

    cmd = [sys.executable, str(grab), "--region", f"{x},{y},{w},{h}", "--out", args.out]
    print("[test.py] Running:", " ".join(cmd))
    try:
        res = subprocess.run(cmd, check=True, capture_output=True, text=True)
        if res.stdout:
            print(res.stdout.strip())
        if res.stderr:
            print(res.stderr.strip())
        print(f"[test.py] ✅ Done. Saved: {args.out}")
    except subprocess.CalledProcessError as e:
        print("[test.py] grab_region.py failed with exit code", e.returncode)
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        sys.exit(e.returncode)

if __name__ == "__main__":
    main()
