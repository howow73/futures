# Git / 원격 저장소 안내

로컬에서 Git 저장소를 초기화하고 원격(GitHub 등)에 푸시하는 빠른 가이드입니다.

1) 로컬에서 초기화 및 첫 커밋
```powershell
Set-Location -Path 'C:\Works\Futures'
git init
git add .
git commit -m "Initial commit"
```

2) 원격 추가 및 푸시
```powershell
# 예: https://github.com/USERNAME/REPO.git
git remote add origin <원격_URL>
git branch -M main
git push -u origin main
```

3) 주의: 커밋 전에 사용자 정보 설정 필요 시
```powershell
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

4) 보안: API 키/비밀번호 등 민감 정보는 절대 커밋하지 마세요. `.env` 사용 및 `.gitignore`에 추가하세요.
