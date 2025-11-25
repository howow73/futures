# futures_app_starter

## 0) 폴더 열기
VS Code에서 **File → Open Folder…** 로 이 폴더를 엽니다.

## 1) 가상환경 만들기
```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows는 .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 2) 실행
```bash
python src/app.py
```

## 3) VS Code 설정
- 좌측 하단 Python 인터프리터 선택 → `.venv` 선택
- (권장) `.vscode/settings.json`에서 기본 인터프리터 경로를 `.venv/bin/python`으로 고정

## 4) 트러블슈팅
- **macOS 격리 해제**: `xattr -dr com.apple.quarantine <이_폴더_경로>`
- **권한**: `chmod -R u+w <이_폴더_경로>`
- **신뢰 폴더**: VS Code 상단의 Trust 버튼 클릭
