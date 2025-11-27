import sys
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QFileDialog
from PyQt6.QtCore import Qt, QPoint, QRect
from PyQt6.QtGui import QPainter, QColor, QPen, QGuiApplication

class SnippingWidget(QWidget):
    """화면을 어둡게 덮고 마우스로 영역을 선택하는 위젯"""
    def __init__(self, parent=None, filename="capture.png"):
        super().__init__(parent)
        self.filename = filename
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setStyleSheet("background-color: black;")
        self.setWindowOpacity(0.3) # 화면을 30% 투명하게 (어둡게)
        
        # 전체 모니터 영역 커버
        screen_geometry = QGuiApplication.primaryScreen().geometry()
        self.setGeometry(screen_geometry)
        
        self.begin = QPoint()
        self.end = QPoint()
        self.is_snipping = False
        self.show()

    def paintEvent(self, event):
        if self.is_snipping:
            brush_color = QColor(0, 0, 0, 0) # 선택 영역은 투명하게
            lw = 2
            opacity = 0
        else:
            brush_color = QColor(0, 0, 0, 0)
            lw = 0
            opacity = 0

        qp = QPainter(self)
        qp.setPen(QPen(Qt.GlobalColor.red, 2))
        qp.setBrush(brush_color)
        
        # 선택된 사각형 그리기
        rect = QRect(self.begin, self.end)
        qp.drawRect(rect)

    def mousePressEvent(self, event):
        self.begin = event.pos()
        self.end = event.pos()
        self.is_snipping = True
        self.update()

    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        self.is_snipping = False
        self.close() # 오버레이 닫기
        
        # 실제 화면 캡처 진행
        x1 = min(self.begin.x(), self.end.x())
        y1 = min(self.begin.y(), self.end.y())
        x2 = max(self.begin.x(), self.end.x())
        y2 = max(self.begin.y(), self.end.y())
        
        w = x2 - x1
        h = y2 - y1

        if w > 0 and h > 0:
            # 원본 화면(밝은 화면)을 캡처해야 하므로 오버레이가 사라진 뒤 찰칵
            screen = QGuiApplication.primaryScreen()
            # grabWindow(0)은 전체 스크린
            screenshot = screen.grabWindow(0, x1, y1, w, h)
            screenshot.save(self.filename)
            print(f"✅ 저장 완료: {self.filename}")

class CaptureTool(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("신호 캡처 도구")
        self.setGeometry(100, 100, 300, 150)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.lbl_info = QLabel("HTS 차트를 띄워놓고 버튼을 누르세요.")
        self.lbl_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_info)

        # 매수 신호 캡처 버튼
        btn_buy = QPushButton("📈 매수 신호(화살표) 캡처")
        btn_buy.clicked.connect(lambda: self.start_snip("buy_signal.png"))
        btn_buy.setStyleSheet("background-color: #ffcccc; padding: 10px; font-weight: bold;")
        layout.addWidget(btn_buy)

        # 매도 신호 캡처 버튼
        btn_sell = QPushButton("📉 매도 신호(화살표) 캡처")
        btn_sell.clicked.connect(lambda: self.start_snip("sell_signal.png"))
        btn_sell.setStyleSheet("background-color: #ccccff; padding: 10px; font-weight: bold;")
        layout.addWidget(btn_sell)

        self.setLayout(layout)

    def start_snip(self, filename):
        # 캡처 위젯 실행 (파일명 전달)
        self.snipper = SnippingWidget(filename=filename)
        self.lbl_info.setText(f"'{filename}' 저장 중...\n마우스로 드래그하세요!")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = CaptureTool()
    ex.show()
    sys.exit(app.exec())