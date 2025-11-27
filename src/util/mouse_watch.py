import time, pyautogui

print("Move the mouse. Press Ctrl+C to stop.")
try:
    while True:
        x, y = pyautogui.position()
        print(f"X={x} Y={y}", end="\r", flush=True)
        time.sleep(0.05)
except KeyboardInterrupt: 
    print("\nStopped.")
