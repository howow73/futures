
from PyQt6.QtCore import Qt, QTimer, QDateTime, QObject, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton,
    QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
    QGroupBox, QGridLayout, QCheckBox, QLineEdit, QSpinBox
)
import sys


class AppController(QObject):
    startStrategy = pyqtSignal(int)
    stopStrategy = pyqtSignal(int)
    scheduleUpdated = pyqtSignal(dict)
    settingsSaved = pyqtSignal(object)

    statusChanged = pyqtSignal(str)
    logAppended = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._running_strategy: int | None = None
        self.startStrategy.connect(self._on_start_strategy)
        self.stopStrategy.connect(self._on_stop_strategy)

    def now_str(self) -> str:
        return QDateTime.currentDateTime().toString("hh:mm:ss")

    def _on_start_strategy(self, n: int):
        self._running_strategy = n
        self.statusChanged.emit(f"★{n}전략 실행중★")
        self.logAppended.emit({"time": self.now_str(),"strat": f"{n}전략","prog": "시작","result": "실행 시작","note": ""})

    def _on_stop_strategy(self, n: int):
        if self._running_strategy == n:
            self._running_strategy = None
            self.statusChanged.emit("★대기중★")
        self.logAppended.emit({"time": self.now_str(),"strat": f"{n}전략","prog": "종료","result": "정지 요청","note": ""})


class LogTable(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(0, 5, parent)
        self.setHorizontalHeaderLabels(["시간", "전략", "진입", "결과", "기타"])
        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.verticalHeader().setVisible(False)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.setShowGrid(True)

    def add_row(self, time_str, strat, prog, result, note=""):
        row = self.rowCount()
        self.insertRow(row)
        for col, val in enumerate([time_str, strat, prog, result, note]):
            item = QTableWidgetItem(val)
            align = Qt.AlignmentFlag.AlignCenter if col != 3 else (Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            item.setTextAlignment(align)
            self.setItem(row, col, item)
        self.scrollToBottom()


class MainTab(QWidget):
    def __init__(self, controller: AppController, parent=None):
        super().__init__(parent)
        self.controller = controller
        lay = QVBoxLayout(self)

        top = QHBoxLayout()
        self.status = QLabel("★대기중★")
        self.status.setObjectName("statusLabel")
        self.status.setStyleSheet("#statusLabel { background: #efefef; padding: 4px 8px; border-radius: 6px; font-weight: 600; }")
        top.addWidget(self.status)
        top.addStretch(1)

        self.btn_start1 = QPushButton("1전략")
        self.btn_start2 = QPushButton("2전략")
        self.btn_start3 = QPushButton("3전략")
        self.btn_stop = QPushButton("정지")
        for b in (self.btn_start1, self.btn_start2, self.btn_start3, self.btn_stop):
            b.setFixedHeight(28)
            top.addWidget(b)

        lay.addLayout(top)
        line = QFrame(); line.setFrameShape(QFrame.Shape.HLine); line.setFrameShadow(QFrame.Shadow.Sunken)
        lay.addWidget(line)

        self.table = LogTable()
        lay.addWidget(self.table, 1)

        self.btn_start1.clicked.connect(lambda: self.controller.startStrategy.emit(1))
        self.btn_start2.clicked.connect(lambda: self.controller.startStrategy.emit(2))
        self.btn_start3.clicked.connect(lambda: self.controller.startStrategy.emit(3))
        self.btn_stop.clicked.connect(lambda: self.controller.stopStrategy.emit(1))

        self.controller.statusChanged.connect(self.status.setText)
        self.controller.logAppended.connect(self._append_log)

        samples = [("08:15:33", "1전략", "감시시작", "0", ""), ("05:29:00", "1전략", "감시종료", "", "")]
        for r in samples:
            self.table.add_row(*r)

    def _append_log(self, payload: dict):
        self.table.add_row(payload.get("time",""), payload.get("strat",""), payload.get("prog",""), payload.get("result",""), payload.get("note",""))


class StrategyTab(QWidget):
    def __init__(self, controller: AppController, parent=None):
        super().__init__(parent)
        self.controller = controller
        root = QVBoxLayout(self)
        root.addWidget(self._make_strategy_box("1전략"))
        root.addWidget(self._make_strategy_box("2전략", checked=True))
        root.addWidget(self._make_strategy_box("3전략"))
        root.addStretch(1)

    def _make_strategy_box(self, title: str, checked: bool=False) -> QGroupBox:
        box = QGroupBox(title)
        gl = QGridLayout(box)
        labels = [("완성봉", checked), ("현재봉", False), ("마감", False), ("올진입", checked), ("통진입", False), ("숏진입", False)]
        for i, (text, chk) in enumerate(labels):
            cb = QCheckBox(text); cb.setChecked(chk)
            r, c = divmod(i, 3)
            gl.addWidget(cb, r, c)
        return box


class ScheduleTab(QWidget):
    def __init__(self, controller: AppController, parent=None):
        super().__init__(parent)
        self.controller = controller
        root = QVBoxLayout(self)
        box = QGroupBox("실행 / 종료(유지) / 종료(청)")
        grid = QGridLayout(box)

        headers = ["", "실행(6자리)", "종료(유지) 수치", "종료(청) 시각(4자리)", "청"]
        for c, h in enumerate(headers):
            lbl = QLabel(h); lbl.setStyleSheet("font-weight:600")
            grid.addWidget(lbl, 0, c)

        def row_widgets(row_idx: int, name: str):
            grid.addWidget(QLabel(name), row_idx, 0)
            t_exec = QLineEdit(); t_exec.setMaxLength(6); t_exec.setPlaceholderText("HHMMSS")
            t_keep = QLineEdit(); t_keep.setMaxLength(6)
            t_close = QLineEdit(); t_close.setMaxLength(4); t_close.setPlaceholderText("HHMM")
            cb = QCheckBox()
            grid.addWidget(t_exec, row_idx, 1)
            grid.addWidget(t_keep, row_idx, 2)
            grid.addWidget(t_close, row_idx, 3)
            grid.addWidget(cb, row_idx, 4)

        row_widgets(1, "1전략")
        row_widgets(2, "2전략")
        row_widgets(3, "3전략")

        root.addWidget(box)
        tip = QLabel("지정한 시간에 전략을 시작/종료/청산합니다.\n종료(유지)는 보유계약을 유지한 채 종료, 종료(청산)는 보유계약을 청산하고 종료")
        tip.setWordWrap(True)
        root.addWidget(tip)

        hts_box = QGroupBox("HTS 자동재실행(영웅문G)")
        hb = QHBoxLayout(hts_box)
        self.cb_hts = QCheckBox("실행")
        self.le_hts_code = QLineEdit(); self.le_hts_code.setMaxLength(4); self.le_hts_code.setPlaceholderText("0701")
        hb.addWidget(self.cb_hts); hb.addWidget(self.le_hts_code); hb.addStretch(1)
        root.addWidget(hts_box)
        root.addStretch(1)


class SettingsTab(QWidget):
    def __init__(self, controller: AppController, parent=None):
        super().__init__(parent)
        self.controller = controller
        root = QVBoxLayout(self)

        pos_box = QGroupBox("프로그램 위치 저장")
        hb = QHBoxLayout(pos_box)
        self.btn_save_pos = QPushButton("위치저장")
        hb.addWidget(self.btn_save_pos); hb.addStretch(1)
        root.addWidget(pos_box)

        goal_box = QGroupBox("전략별 목표달성 종료설정")
        grid = QGridLayout(goal_box)
        headers = ["", "횟수", "익절", "손절"]
        for c, h in enumerate(headers):
            lbl = QLabel(h); lbl.setStyleSheet("font-weight:600"); grid.addWidget(lbl, 0, c)

        def add_row(r: int, name: str):
            grid.addWidget(QLabel(name), r, 0)
            sp_cnt = QSpinBox(); sp_cnt.setRange(0, 999)
            sp_tp = QSpinBox(); sp_tp.setRange(-9999, 9999)
            sp_sl = QSpinBox(); sp_sl.setRange(-9999, 9999)
            grid.addWidget(sp_cnt, r, 1); grid.addWidget(sp_tp, r, 2); grid.addWidget(sp_sl, r, 3)

        add_row(1, "1전략"); add_row(2, "2전략"); add_row(3, "3전략")
        root.addWidget(goal_box); root.addStretch(1)


class AdminTab(QWidget):
    def __init__(self, controller: AppController, parent=None):
        super().__init__(parent)
        self.controller = controller
        root = QVBoxLayout(self)

        auth_box = QGroupBox("고객인증확인")
        hb = QHBoxLayout(auth_box)
        for text in ("고객인증", "키움설팅", "기타설팅"):
            hb.addWidget(QPushButton(text))
        hb.addStretch(1)

        cfg_box = QGroupBox("프로그램설정")
        grid = QGridLayout(cfg_box)
        grid.addWidget(QLabel("LimitSP"), 0, 0)
        self.le_limit = QLineEdit("100"); grid.addWidget(self.le_limit, 0, 1)

        def row(label: str, r: int):
            grid.addWidget(QLabel(label), r, 0)
            for c in range(1, 6):
                grid.addWidget(QLineEdit(), r, c)

        headers = ["X", "Y", "W", "H"]
        for i, h in enumerate(headers, start=1):
            grid.addWidget(QLabel(h), 1, i)
        row("주문화면1", 2); row("신호화면1", 3); row("주문화면2", 4); row("신호화면2", 5); row("주문화면3", 6); row("신호화면3", 7)

        root.addWidget(auth_box); root.addWidget(cfg_box); root.addStretch(1)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("해외선물프로그램 (Controller 적용)")
        self.setFixedSize(380, 610)

        self.controller = AppController(self)

        root = QVBoxLayout(self)
        self.time_label = QLabel("08:14:19")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.time_label.setFont(QFont("Helvetica", 32, QFont.Weight.Bold))
        self.date_label = QLabel("2025.10.14(화)")
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.date_label.setFont(QFont("Helvetica", 12))
        root.addWidget(self.time_label); root.addWidget(self.date_label)

        tabs = QTabWidget()
        tabs.addTab(MainTab(self.controller), "메인")
        tabs.addTab(StrategyTab(self.controller), "전략설정")
        tabs.addTab(ScheduleTab(self.controller), "예약실행")
        tabs.addTab(SettingsTab(self.controller), "설정")
        tabs.addTab(AdminTab(self.controller), "관리자")
        root.addWidget(tabs, 1)

        btn_bar = QHBoxLayout()
        for label in ["저장", "원격", "화면", "설명", "종료"]:
            btn = QPushButton(label); btn.setFixedHeight(28); btn_bar.addWidget(btn)
        root.addLayout(btn_bar)

        self.timer = QTimer(self); self.timer.timeout.connect(self.update_clock); self.timer.start(1000); self.update_clock()

    def update_clock(self):
        now = QDateTime.currentDateTime()
        self.time_label.setText(now.toString("hh:mm:ss"))
        day_ko = ["월","화","수","목","금","토","일"][now.date().dayOfWeek()-1]
        self.date_label.setText(now.toString(f"yyyy.MM.dd({day_ko})"))


def main():
    app = QApplication(sys.argv)
    win = MainWindow(); win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
