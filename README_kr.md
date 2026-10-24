[🇺🇸 English](README.md) | [🇯🇵 日本語 (Japanese)](README_jp.md)

# Songfinder: URFIT 팀 프로젝트의 음성·음악 매칭 모듈

> 🏆 **한국무역협회 제47기 SCIT Master 프로젝트 발표회 우수상(2위).** 6인 팀 프로젝트 URFIT으로 받은 상입니다.
> 👤 이 레포는 URFIT 중 백지헌이 혼자 맡은 음성 인식·검색·추천·Spotify 연동 모듈입니다. 2026년 리팩토링과 성능 평가도 혼자 진행했습니다.
> ℹ️ 처음에는 Hugging Face Space에서 동작하던 프로토타입이었고, 이후 Angular 프런트엔드와 FastAPI 백엔드로 나눠 다시 만들었습니다.

![URFIT 화면 예시](./Sample.png)

URFIT은 음성 인식 기반 AI 플레이리스트 생성 커뮤니티입니다. 머릿속에 맴도는 가사를 말하거나 입력하면 그 J-POP 곡을 찾아 줍니다.
- 음성은 Whisper로 가사를 받아 적은 뒤 검색합니다. 그래서 가사 없는 콧노래나 멜로디만으로 찾는 기능은 아닙니다.
- 기존 노래 검색의 두 가지 한계를 풀려고 기획했습니다. 부정확한 가사로는 찾을 수 없다는 점, 그리고 찾은 뒤에 이어지는 경험이 없다는 점입니다.

URFIT이라는 이름에는 세 가지 뜻을 담았습니다.
>  * 한국어: 얼핏 듣다 (얼핏 들은 노래를 찾아 주고, 듣고 공유하는 플랫폼)
>  * 영어: Your(UR) Fit (Music Recognition & Recommendation)
>  * 일본어: 運命のリズム、触れ合う意味の繋がり。

## 🎵 주요 기능

  * **흐릿하게 기억나는 가사로 곡 찾기:** 정확하지 않은 가사를 말하거나 입력해도 곡을 찾습니다. 어느 정도 찾는지는 아래 '한눈에 보기'에 정리했습니다.
  * **유사 곡 추천:** 찾은 곡의 가사, 분위기, 태그를 바탕으로 비슷한 곡 3개를 추천합니다.
  * **Spotify 플레이리스트 생성:** 추천 곡을 모아 Spotify 플레이리스트로 저장합니다.
  * **플레이리스트 제목·설명 생성:** OpenAI GPT 모델이 추천 곡의 특징을 보고 제목과 설명을 씁니다.
  * **커뮤니티 기능:** 검색한 곡과 플레이리스트를 다른 사용자와 공유합니다.

-----

## 🔍 한눈에 보기

![Songfinder 구조와 평가 범위](./docs/assets/architecture.png)

점선 상자인 **곡 식별 단계만 따로 떼어 정량 평가**했습니다. 결과는 색인된 가사로 만든 합성 질의와 TTS 음성을 기준으로 한 값이며, 실사용 정확도가 아닙니다. 사람의 녹음, 노래, 콧노래는 측정하지 않았습니다.

- **가사를 입력할 때:** 1순위 정답률 60.6%, 10위 이내 76.2%입니다. 오타에는 강하고(79.8%) 앞부분만 기억할 때는 약합니다(32.9%).
- **가사를 말할 때 (앱 설정):** 일본어 원어민 발음 47%, **한국인 발음 36%**, 한 줄만 말하면 76%입니다.
- **원인 두 가지**
  - Whisper가 한국인 발음의 35%를 한국어로 판단해 한글로 받아 적습니다.
  - 가사를 한 줄 단위로 색인하기 때문에 길게 말할수록 정답률이 떨어집니다.
- **개선 (앱 반영 후 측정):** 두 가지를 반영했습니다.
  - Whisper가 한국어로 감지하면 일본어로 다시 전사합니다.
  - 여러 줄 질의는 줄 길이로 나눈 조각들의 투표로 곡을 정합니다.
  - 그 결과 한국인 발음은 36% → 69%, 원어민 5줄은 47% → 74%가 됐고, 한 줄 질의와 텍스트 검색 결과는 이전과 같습니다.
- **그 밖의 발견:** 텍스트 검색 요약 분기의 인덱스 버그는 수정했습니다. 다음 두 가지는 다음 단계 과제입니다.
  - '찾지 못함' 판정선이 DB에 없는 문장의 93%를 통과시킵니다.
  - 짧은 가사 줄이 오답을 끌어당깁니다.

![음성 검색 개선 전후](./eval/results/voice_fixes.png)

상세 문서: [평가 상세](docs/EVALUATION.md) · [데이터 안내](docs/DATA.md) · [연구개발 기록](docs/RESEARCH_LOG.md) · [결정 기록(ADR)](docs/adr/README.md) · [이어서 할 일](docs/NEXT_STEPS.md)

-----

## 🛠 아키텍처 및 기술 스택

단일 애플리케이션이던 프로토타입을 프런트엔드와 백엔드로 분리했습니다.

### 1. Frontend (Angular)
  * **Framework:** Angular 17 (기존 Vanilla JS/HTML 코드를 옮김)
  * **Styling:** TailwindCSS, SCSS
  * **주요 기능:** Spotify Web Playback SDK 연동, 마이크 녹음(MediaRecorder) 및 전송

### 2. Backend (FastAPI)
  * **Framework:** FastAPI (Python 3.10 이상)
  * **AI/ML**
      * OpenAI **Whisper**: 음성 → 텍스트
      * **SentenceTransformer** (`paraphrase-multilingual-MiniLM-L12-v2`) + **FAISS**: 가사 벡터 유사도 검색 (`search.py`)
      * OpenAI **GPT-3.5-turbo**: 플레이리스트 제목·설명 생성
  * **주요 기능:** Spotify OAuth 인증, 음성 검색·텍스트 검색 API, CORS 설정

-----

## 🚀 로컬 실행 방법

프런트엔드와 백엔드를 각각 실행합니다.

### 사전 준비
1. Python 3.10 이상 (3.13 이상에서는 `audioop-lts`가 추가로 필요할 수 있음)
2. Node.js 18 이상, npm
3. [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)에서 앱을 만들고 `Client ID`, `Client Secret` 발급
   * **Redirect URI:** `http://localhost:7860/callback` (https가 아닌 http)
   * 개발 모드 앱은 등록한 사용자만 로그인할 수 있습니다(2026년 기준 최대 5명).
4. `.env` 파일 또는 환경 변수: `OPENAI_API_KEY`, `SPOTIPY_CLIENT_ID`, `SPOTIPY_CLIENT_SECRET`, `SPOTIPY_REDIRECT_URI=http://localhost:7860/callback`
5. 가사 데이터: 저작권 때문에 이 레포에는 없습니다. `line_metadata.json`, `song_metadata.json`을 레포 루트에 두거나 `SONGFINDER_DATA_DIR`로 위치를 지정해야 앱이 동작합니다([데이터 안내](docs/DATA.md)).

### 백엔드
```bash
pip install -r requirements.txt
python app.py
```
* `http://localhost:7860`에서 실행됩니다. 첫 실행 때 임베딩 모델(수백 MB)을 내려받습니다.

### 프런트엔드
새 터미널에서 실행합니다.
```bash
cd frontend
npm install
npm start
```
* `http://localhost:4200`에서 실행됩니다.

### 테스트
```bash
pip install -r requirements-dev.txt
pytest -q tests
```
* 검색 모듈(`search.py`) 테스트입니다. 단위 테스트는 가짜 색인으로 실행됩니다. 가사 데이터가 있으면, 한 줄 질의가 이전 로직과 같은 곡을 고르는지 확인하는 통합 테스트도 함께 실행됩니다.

-----

## 🖼️ 사용 방법

1. **검색 시작:** 메인 화면에서 **음성으로 찾기** 또는 **텍스트로 찾기**를 누릅니다.
2. **음성 검색:** 마이크 권한을 허용하고 기억나는 가사를 5~15초 동안 말합니다. 가사 없는 콧노래는 인식하지 않습니다.
3. **결과 확인과 재생:** 찾은 곡과 추천 곡이 표시됩니다. Spotify에 로그인하면 웹 플레이어로 바로 들을 수 있습니다.
4. **플레이리스트 생성:** "이 곡들로 플레이리스트 만들기"를 누르면 제목과 설명을 생성해 Spotify 계정에 저장합니다.

-----

## 💡 향후 계획

  * 짧은 가사 줄을 앞뒤 줄과 묶어 다시 색인하고, '찾지 못함' 판정선을 다시 정하기
  * 가나 읽기(발음) 기반 보조 색인: 소리가 비슷한 말과 한국인 발음에 대한 강건성 개선
  * 실제 사용자 녹음으로 정확도 측정
  * Spotify 임베드 플레이어로 로그인 없이 미리 듣기, Firebase Hosting(프런트엔드) + Cloud Run(백엔드) 배포
  * 청취 기록 기반 개인화 추천

-----

### 프로젝트 개요

* **프로젝트명:** URFIT (음성 인식 기반 AI 플레이리스트 생성 커뮤니티)
* **과정:** 한국무역협회 무역아카데미 Smart Cloud IT 과정 47기 프로젝트, 이후 리팩토링
* **기간:** 2025년 7월 29일 ~ 9월 29일(초기 개발), 2026년 리팩토링

### 저작권 고지

이 자료의 저작권은 한국무역협회 무역아카데미 Smart Cloud IT 과정 47기 팀 "노래불러조"에 있으며, 허가 없이 복제, 배포, 전송, 전시하는 것을 금지합니다.
