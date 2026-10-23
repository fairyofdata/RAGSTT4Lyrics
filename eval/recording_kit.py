"""Recording kit for a small real-voice test (the user's own Korean-accented reading).

    venv/Scripts/python eval/recording_kit.py

Writes into private/ (gitignored; it holds lyrics):
- recording_script.md   Part A: 20 queries to read aloud, original + reading (hiragana)
- song_list.md          songs in the index, for Part B (speak remembered lines, no script)
- recording_key.json    item id -> song and line indices, for scoring later

Part A reuses the exact 2-6 line queries of audio_local_eval.py, so the real voice can
be compared song by song with the native-voice and Korean-reading TTS results.
"""
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from audio_local_eval import UNSPLIT_CHARS, window  # noqa: E402
from common import REPO_ROOT, SongDB  # noqa: E402
from perturb import kata_to_hira  # noqa: E402
import queries as Q  # noqa: E402

PRIVATE = os.path.join(REPO_ROOT, 'private')
N_ITEMS, SEED = 20, 2026
FUNCTION_POS = {'助詞', '助動詞', '接尾辞'}

_tagger = None


def reading(line):
    """Hiragana reading with a space before each content word; kanji words UniDic does not
    know are kept as written and returned separately so the reader can check them."""
    global _tagger
    if _tagger is None:
        import fugashi
        _tagger = fugashi.Tagger()
    parts, unknown = [], []
    words = list(_tagger(line))
    for i, w in enumerate(words):
        kana = getattr(w.feature, 'kana', None)
        has_kanji = any('一' <= c <= '鿿' for c in w.surface)
        if not has_kanji:
            piece = w.surface                      # kana and katakana words read as written
        elif kana and kana != '*':
            piece = kata_to_hira(kana)
            if w.surface == '何' and i + 1 < len(words) and words[i + 1].surface == 'も':
                piece = 'なに'                     # UniDic reads 何も as なんも; lyrics mostly sing なにも
        else:
            piece = w.surface
            unknown.append(w.surface)
        punct = all(not c.isalnum() for c in w.surface)
        content = getattr(w.feature, 'pos1', '') not in FUNCTION_POS and not punct
        parts.append((' ' if (parts and (content or w.white_space)) else '') + piece)
    return ''.join(parts).strip(), unknown


HEADER = '''# 녹음 대본 (개인용, 커밋 금지)

이 파일에는 가사 원문이 들어 있습니다. `private/`는 git이 무시하는 폴더라 커밋되지 않습니다.

## 녹음 방법
- **장비:** Windows 녹음기도 되고 휴대폰도 됩니다. 실제 앱 사용처럼 평소 쓰는 마이크면 충분합니다.
- **파일 형식:** WAV, MP3, FLAC 중 하나로 저장해 주세요. M4A는 이 PC에서 읽을 수 없습니다(Windows 녹음기 설정 → 녹음 형식에서 변경).
- **저장 위치:** `private/recordings/`

## Part A: 대본 읽기 (20개, 한 파일로 통째로 녹음해도 됨)
- **파일 이름:** `A.wav`(또는 `.mp3`, `.flac`). 여러 파일로 나누면 `A1`, `A2`처럼 이어 붙여도 됩니다.
- **노래하지 말고 말하듯 읽기:** 평소 본인 발음 그대로 읽으면 됩니다. 일본어 원어민처럼 하려고 애쓰지 않아도 됩니다. 이 녹음이 재려는 게 「한국인의 실제 발음」이기 때문입니다.
- **쉬는 법:** 항목과 항목 사이는 **3초쯤 쉬기**. 한 항목 안에서는 줄이 바뀌어도 길게 쉬지 않기.
- **틀렸을 때:** 3초 쉬고 그 항목을 처음부터 다시 읽으면 됩니다. 마지막 시도를 씁니다. 번호는 말하지 않아도 됩니다.
- **읽는 규칙:**
  - 요미가나는 사전(UniDic) 기준이라 원곡과 다르게 부르는 곳이 있을 수 있습니다. 그런 곳은 원곡대로 읽으면 됩니다.
  - 조사 は·へ·を는 わ·え·お로 읽습니다.
  - 「읽기 확인」이 붙은 단어는 사전에 읽기가 없는 단어입니다.

## Part B: 기억으로 말하기 (선택, 5~10곡)
- [song_list.md](song_list.md)에서 **가사를 어느 정도 아는 곡**을 고릅니다.
- **대본 없이** 기억나는 대로 2~4줄을 말합니다. 틀리거나 흐릿해도 그대로가 좋습니다.
- **곡마다 파일 하나:** 파일 이름은 `B_곡번호`입니다(예: `B_123.wav`).

---
'''


def main():
    db = SongDB()
    os.makedirs(os.path.join(PRIVATE, 'recordings'), exist_ok=True)
    bases = {q['song']: q for q in Q.generate(db, 0) if q['type'] == 'exact' and q['id'].endswith('-b0-exact')}
    candidates = []
    for song in sorted(bases):
        lines = window(db, song, bases[song]['src_lines'][0])
        text = ' '.join(db.line_text(x) for x in lines)
        if any(Q.nonspace_len(db.line_text(x)) > UNSPLIT_CHARS for x in lines) or Q.script_class(text) == 'latin':
            continue
        candidates.append((song, lines))
    picks = sorted(random.Random(SEED).sample(candidates, N_ITEMS), key=lambda p: p[0])

    out, key = [HEADER, '## Part A: 대본\n'], {}
    for n, (song, lines) in enumerate(picks, 1):
        item = f'A{n:02d}'
        meta = db.song_metadata[song]
        out.append(f"\n### {item} · {meta.get('artist')} — {meta.get('title')} (곡 #{song})\n")
        unknown_all = []
        for x in lines:
            text = db.line_text(x).strip()
            r, unknown = reading(text)
            unknown_all += unknown
            out.append(f'\n{text}  \n<sub>{r}</sub>\n')
        if unknown_all:
            out.append(f"\n> 읽기 확인: {', '.join(dict.fromkeys(unknown_all))}\n")
        key[item] = {'part': 'A', 'song': song, 'lines': lines}

    with open(os.path.join(PRIVATE, 'recording_script.md'), 'w', encoding='utf-8') as f:
        f.write(''.join(out))
    with open(os.path.join(PRIVATE, 'recording_key.json'), 'w', encoding='utf-8') as f:
        json.dump(key, f, ensure_ascii=False, indent=1)

    rows = ['# 곡 목록 (Part B용)\n\n아는 곡을 골라 `B_곡번호` 파일로 녹음해 주세요.\n\n| 곡 번호 | 아티스트 | 제목 |\n|---:|---|---|\n']
    for song in sorted(db.lines_by_song):
        if any(Q.nonspace_len(db.line_text(x)) > UNSPLIT_CHARS for x in db.lines_by_song[song]):
            continue
        meta = db.song_metadata[song]
        rows.append(f"| {song} | {meta.get('artist')} | {meta.get('title')} |\n")
    with open(os.path.join(PRIVATE, 'song_list.md'), 'w', encoding='utf-8') as f:
        f.write(''.join(rows))
    print(f'{len(picks)} Part A items, {len(rows) - 1} songs in the list -> {PRIVATE}')


if __name__ == '__main__':
    main()
