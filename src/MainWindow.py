# MainWindow 클래스 내부

    def toggle_strategy_1(self):
        # 1전략 시작 버튼 클릭 시
        if not hasattr(self, 'detector_thread') or not self.detector_thread.isRunning():
            # AdminTab에서 설정한 좌표 가져오기 (예: 신호화면1)
            region = self.tab_admin.get_coordinates("strat1_signal") # (x,y,w,h)
            
            # 스레드 생성 및 시작
            self.detector_thread = ImageDetectionThread(
                template_path="buy_signal.png",
                region=region,
                hotkey=['f1'], # F1키 매수
                threshold=0.85
            )
            # 로그 연결
            self.detector_thread.log_signal.connect(self.controller.logAppended.emit)
            self.detector_thread.start()
            
            self.controller.statusChanged.emit("★이미지 감시 중★")
        else:
            # 중지
            self.detector_thread.stop()
            self.controller.statusChanged.emit("★대기중★")