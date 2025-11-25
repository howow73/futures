Install:
  python3 -m venv .venv
  source .venv/bin/activate      # Windows: .venv\Scripts\activate
  pip install --upgrade pip
  pip install opencv-python pyautogui numpy pillow

macOS permissions:
  - Screen Recording & Accessibility for Terminal/VS Code

Run:
  python auto_trade_detector.py --template template.png --hotkey "ctrl+alt+1" --threshold 0.9 --cooldown 3 --interval 0.4
  # Optional region:
  python auto_trade_detector.py --template template.png --region "100,200,800,500"

Tips:
  - Use a small, unique template image from your app's event state.
  - Adjust --threshold based on console scores.
