# ADR-0016: 공개 문서의 표기 이름을 RAGSTT4Lyrics 하나로 한다

- 상태: 채택
- 결정일: 2026-11-27
- 대체: ADR-0014의 「Songfinder 는 괄호로 남긴다」. 제목을 저장소 이름 + 한 줄 설명으로 쓰는 것, README 원본·노트북 위치 결정은 그대로다.

## 맥락
- 2026-10-25 저장소 이름을 `LLM_STT_Songfinder` 에서 `RAGSTT4Lyrics` 로 바꿀 때 표기 이름 Songfinder 는 남기기로 했고, ADR-0014 가 README 제목 끝에 「(Songfinder)」를 붙였다.
- 2026-11-27 작성자가 Songfinder 는 옛 이름이니 남은 표기를 없애라고 했다. 이름이 둘이면 읽는 사람이 같은 것인지 따로 확인하게 된다.

## 결정
- 지금 읽히는 공개 문서는 RAGSTT4Lyrics 로만 부른다. 세 언어 README 의 제목·그림 설명, `docs/PORTFOLIO.md` 의 제목·그림 설명, `CLAUDE.md` 의 프로젝트 소개에서 Songfinder 를 뺀다.
- README 의 「옛 이름 `LLM_STT_Songfinder`」는 저장소 이름이 바뀐 사실이라 남긴다. 「모듈 이름 Songfinder」는 뺀다.
- 지난 ADR·`docs/RESEARCH_LOG.md`·`docs/EVALUATION.md`·`docs/DATA.md` 본문의 Songfinder 는 그때의 기록이라 고치지 않는다.
- 코드의 식별자(`SONGFINDER_*` 환경 변수, `~/.cache/songfinder_eval/` 경로)는 그대로 둔다. 바꾸면 기존 설정과 로컬 캐시가 끊긴다.
- 그림 `docs/assets/architecture.png` 와 `eval/results/recall_by_query_type.png` 의 제목에는 Songfinder 가 들어 있다(만드는 코드: `docs/figures.py`, `eval/plot.py`). 이번에는 다시 만들지 않는다.

## 결과
- 제목과 그림 설명이 저장소 이름과 같아진다.
- 그림 두 장의 제목과 코드 식별자에는 옛 이름이 남는다. 그림을 다시 만들 때 제목을 함께 고친다.
