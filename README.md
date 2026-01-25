# Holdem_Python

<div align="center">
  <img src="https://github.com/user-attachments/assets/f0b1031d-8308-472f-a34d-787127b10584" width="300" alt="Holdem Logo" />
</div>

## 01. 프로젝트에 대한 정보

### (1) 프로젝트 제목
- Holdem_Python

### (2) 프로젝트 정보 (개발 기간)
- 2026.01.17 ~ 2026.01.25

### (3) 프로젝트 소개
- PySide6 기반의 데스크톱 텍사스 홀덤 게임입니다.
- 1인(휴먼) + AI 플레이어로 기본 규칙을 빠르게 즐길 수 있습니다.

## 02. 요구 사항

- Python 3.10 이상 권장
- Windows / macOS / Linux (PySide6 지원 환경)
- 패키지: `requirements.txt` 참고

## 03. 설치 및 실행

```bash
# 1) Repository clone
git clone <YOUR_REPO_URL>
cd Holdem

# 2) 가상환경 생성/활성화 (선택)
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# 3) 패키지 설치
pip install -r requirements.txt

# 4) 실행
python main.py
```

환경변수: 없음

## 04. 기술 스택

- Language: Python
- UI: PySide6 (Qt)
- 기타: numpy, pandas, matplotlib, opencv-python, pillow

## 05. 주요 기능

- 텍사스 홀덤 기본 게임 진행(프리플랍~리버, 쇼다운)
- AI 난이도(Easy / Normal / Hard) 선택
- 블라인드 및 시작 칩 설정
- 액션 로그 및 좌석 말풍선 표시
- 키보드 단축키(F/C/R/A)

