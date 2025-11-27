import time
import cv2
import numpy as np
import pyautogui
import mss # 고속 캡처 라이브러리
from PyQt6.QtCore import QThread, pyqtSignal

# 윈도우 활성화를 위한 API
import win32gui, win32con

class ImageDetectionThread(QThread):
    # 로그 메시지와 상태를 본체(GUI)로 보내는 신호
    log_signal = pyqtSignal(dict) 
    
    def __init__(self, template_path, region, hotkey, scales=[0.9, 1.0, 1.1], threshold=0.87, target_window_name="주문"):
        super().__init__()
        self.template_path = template_path
        self.region = region # (x, y, w, h) 또는 None
        self.hotkey = hotkey # 예: ['f1'] 또는 ['ctrl', '1']
        self.scales = scales
        self.threshold = threshold
        self.target_window_name = target_window_name # 활성화할 창 이름
        self.is_running = True
        self.cooldown = 3.0 # 중복 주문 방지 대기 시간
        
        # 템플릿 이미지 미리 로드
        self.template = cv2.imread(template_path)
        if self.template is None:
            print(f"이미지 로드 실패: {template_path}")
            self.is_running = False

    def focus_window(self):
        """주문 창을 찾아 맨 앞으로 가져옴"""
        hwnd = win32gui.FindWindow(None, self.target_window_name) # 정확한 창 이름 필요 (또는 EnumWindows로 검색)
        if hwnd:
            try:
                if win32gui.IsIconic(hwnd): # 최소화 되어있으면 복구
                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                win32gui.SetForegroundWindow(hwnd)
                time.sleep(0.1) # 창이 뜨는 딜레이 확보
                return True
            except:
                pass
        return False

    def run(self):
        self.log_signal.emit({"time": "시스템", "strat": "감시", "prog": "시작", "result": "스레드ON", "note": ""})
        
        with mss.mss() as sct: # mss 사용으로 속도 향상
            last_trigger_time = 0
            
            while self.is_running:
                try:
                    # 1. 고속 화면 캡처
                    if self.region:
                        monitor = {"top": self.region[1], "left": self.region[0], "width": self.region[2], "height": self.region[3]}
                        img_np = np.array(sct.grab(monitor))
                    else:
                        img_np = np.array(sct.grab(sct.monitors[1])) # 전체 화면

                    # mss는 BGRA를 반환하므로 BGR로 변환 (OpenCV용)
                    screen_img = cv2.cvtColor(img_np, cv2.COLOR_BGRA2BGR)

                    # 2. 멀티 스케일 매칭
                    found = False
                    h_t, w_t = self.template.shape[:2]

                    for scale in self.scales:
                        # 리사이징 (속도 최적화를 위해 너무 작거나 큰 스케일 제외 가능)
                        curr_w, curr_h = int(w_t * scale), int(h_t * scale)
                        if curr_w < 10 or curr_h < 10: continue

                        resized_tpl = cv2.resize(self.template, (curr_w, curr_h))
                        
                        # 템플릿 매칭 수행
                        res = cv2.matchTemplate(screen_img, resized_tpl, cv2.TM_CCOEFF_NORMED)
                        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

                        if max_val >= self.threshold:
                            now = time.time()
                            if (now - last_trigger_time) > self.cooldown:
                                found = True
                                # 매칭 성공 로그
                                self.log_signal.emit({
                                    "time": "감지", 
                                    "strat": "이미지", 
                                    "prog": f"정확도{max_val:.2f}", 
                                    "result": "발견", 
                                    "note": f"배율:{scale}"
                                })

                                # 3. 창 활성화 및 주문 전송
                                # 주의: 여기서 창 활성화 로직을 수행하거나, 메인 스레드로 요청해야 안전함
                                # 간단한 구현을 위해 여기서 수행 (관리자 권한 필수)
                                
                                # pyautogui.hotkey(*self.hotkey) # 창 활성화 없이 누르기 (위험)
                                
                                # 안전한 방식: 창 찾기 시도 -> 키 입력
                                # 실제 사용 시에는 창 이름을 정확히 설정해야 합니다.
                                # self.focus_window() 
                                pyautogui.hotkey(*self.hotkey)
                                
                                last_trigger_time = now
                            break # 스케일 루프 탈출
                    
                    if not found:
                        time.sleep(0.2) # CPU 점유율 낮추기
                    
                except Exception as e:
                    self.log_signal.emit({"time": "에러", "strat": "이미지", "prog": "예외", "result": "중단", "note": str(e)})
                    time.sleep(1)

    def stop(self):
        self.is_running = False
        self.wait()