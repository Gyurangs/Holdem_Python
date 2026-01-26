# Holdem_Python

<div align="center">
  <img src="https://github.com/user-attachments/assets/f0b1031d-8308-472f-a34d-787127b10584" width="400" alt="Holdem Logo" />
</div>

**PySide6 (Qt)** 로 UI를 구성하고, **간결한 게임 루프 + AI 선택** 구조로 구현한 텍사스 홀덤 데스크톱 앱입니다.

---

## 01. 프로젝트 개요
- **프로젝트명**: Holdem_Python  
- **개발 기간**: 2026.01.17 ~ 2026.01.25  
- **한 줄 소개**: 사람 1명 + AI 플레이어가 대결하는 텍사스 홀덤 데스크톱 게임

## 02. 데모 시나리오 (발표 흐름)
1) 홈 화면에서 **AI 인원 / 난이도 / 시작 칩 / 블라인드**를 설정  
2) GAME START → 테이블 진입  
3) **홀덤 진행**(프리플랍 → 플랍 → 턴 → 리버)  
4) **액션 로그/말풍선**으로 진행 상황 확인  
5) **게임 종료 → 홈으로 복귀**

## 03. 핵심 기능
- **게임 진행 UI**: 좌석 배치, 커뮤니티 카드, 팟/콜 금액 HUD
- **AI 난이도 선택**: Easy / Normal / Hard
- **블라인드 자동 계산**: BB 입력 시 SB 자동 반영
- **액션 패널**: Fold / Call / Raise / All-in
- **게임 중 종료**: 좌상단 Exit 버튼으로 홈 복귀
- **액션 로그 & 말풍선**: 플레이어 행동 시각화

## 04. 기본 설정값 (현재 코드 기준)
- **AI 인원수**: 2명  
- **난이도**: Hard  
- **시작 칩**: 500  
- **Big Blind**: 20 (SB는 자동으로 10)

## 05. 조작 키
- **F**: Fold  
- **C**: Call  
- **R**: Raise  
- **A**: All-in  
- **Esc**: Exit (홈으로 복귀)

## 06. 실행 방법
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

## 07. 기술 스택
- **Language**: Python 3.10+
- **UI**: PySide6 (Qt)
- **기타**: requirements.txt 참고

## 08. 폴더 구조 요약
```
.
├─ core/            # 게임 로직 및 상태
├─ ui/              # PySide6 UI
├─ assets/          # 카드 이미지
├─ players/         # 플레이어/AI 관련
└─ main.py          # 엔트리포인트
```