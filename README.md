<!-- Source: README_kr.md (Korean is the source; English and Japanese are translations) · synced 2026-10-26 -->

# RAGSTT4Lyrics — find a J-POP song from half-remembered lyrics (Songfinder)

[English](README.md) · [한국어](README_kr.md) · [日本語](README_jp.md)

> 🏆 **Excellence Award (2nd place), 47th SCIT Master project presentation, Korea International Trade Association**, won with the six-person team project URFIT.
> 👤 This repository is the part of URFIT I built alone: speech recognition, search, recommendation and Spotify integration. I also did the 2026 refactoring and the evaluation on my own.
> ℹ️ It started as a prototype on Hugging Face Spaces and was rebuilt as an Angular frontend and a FastAPI backend.

![URFIT screen](./Sample.png)

URFIT is a voice-driven AI playlist community. You say or type the lyrics you half remember, and it finds the J-POP song.
- Speech is transcribed with Whisper and the text is searched, so it does not find songs from humming or melody alone.
- It was planned to fix two limits of existing song search: inexact lyrics find nothing, and nothing follows once a song is found.

The name URFIT carries three meanings:
>  * Korean: 얼핏 (eolpit), "half heard": a place to find, play and share songs you only half heard
>  * English: Your (UR) Fit, music recognition and recommendation
>  * Japanese: 運命のリズム、触れ合う意味の繋がり。

The repository name **RAGSTT4Lyrics** (formerly `LLM_STT_Songfinder`; the module is called Songfinder) spells out the flow: transcribe speech (**STT**), search the lyrics by vector (**R**etrieval), and hand the summaries and tags of the songs found to GPT to write the playlist title and description (**G**eneration). Finding the song itself is embedding search, with no LLM.

## 🎵 Features

  * **Find a song from half-remembered lyrics:** say or type inexact lyrics and get the song. How often it works is in "At a glance" below.
  * **Similar songs:** three recommendations based on the lyrics, mood and tags of the song found.
  * **Spotify playlists:** save the recommendations as a Spotify playlist.
  * **Playlist title and description:** an OpenAI GPT model writes them from the songs' characteristics.
  * **Community:** share searched songs and playlists with other users.

-----

## 🔍 At a glance

![Songfinder architecture and evaluation scope](./docs/assets/architecture.png)

I evaluated the **song identification step** (dashed box) on its own. The numbers come from synthetic queries built from the indexed lyrics and from TTS speech, so they are not real-world accuracy. Human recordings, singing and humming were not measured.

- **Typed lyrics:** the right song at rank 1 for 60.6% of queries, in the top 10 for 76.2%. Robust to typos (79.8%), weak when only the first half of a line is remembered (32.9%).
- **Spoken lyrics (app settings):** 47% with native Japanese pronunciation, **36% with a Korean accent**, 76% when only one line is spoken.
- **Two causes**
  - Whisper hears 35% of Korean-accented Japanese as Korean and writes Hangul.
  - The index is per lyric line, so the longer a user speaks, the worse it gets.
- **Fixes (measured after shipping them in the app)**
  - Transcribe again in Japanese when Whisper detects Korean.
  - Let line-sized pieces of a multi-line query vote for the song.
  - Korean-accented speech went from 36% to 69% and native five-line speech from 47% to 74%. One-line queries and text search behave as before.
- **Other findings:** an index bug in the summary branch of text search (fixed). Two more are next on the list:
  - The "not found" threshold lets 93% of sentences that are not in the database through.
  - Very short lyric lines attract wrong matches.

![Voice search before and after the fixes](./eval/results/voice_fixes.png)

Detailed documents (in Korean): [evaluation](docs/EVALUATION.md) · [data](docs/DATA.md) · [research log](docs/RESEARCH_LOG.md) · [decision records (ADR)](docs/adr/README.md) · [next steps](docs/NEXT_STEPS.md)

-----

## 🛠 Architecture and stack

The single-application prototype was split into a frontend and a backend.

### 1. Frontend (Angular)
  * **Framework:** Angular 17 (ported from the original vanilla JS/HTML)
  * **Styling:** TailwindCSS, SCSS
  * **Features:** Spotify Web Playback SDK, microphone recording (MediaRecorder) and upload

### 2. Backend (FastAPI)
  * **Framework:** FastAPI (Python 3.10+)
  * **AI/ML**
      * OpenAI **Whisper**: speech to text
      * **SentenceTransformer** (`paraphrase-multilingual-MiniLM-L12-v2`) + **FAISS**: lyric vector search (`search.py`)
      * OpenAI **GPT-3.5-turbo**: playlist titles and descriptions
  * **Features:** Spotify OAuth, voice and text search APIs, CORS settings

-----

## 🚀 Running locally

Run the frontend and the backend separately.

### Prerequisites
1. Python 3.10+ (3.13+ may also need `audioop-lts`)
2. Node.js 18+ and npm
3. A Spotify app from the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard) with its `Client ID` and `Client Secret`
   * **Redirect URI:** `http://localhost:7860/callback` (http, not https)
   * Apps in development mode only let allowlisted users log in (up to five as of 2026).
4. A `.env` file or environment variables: `OPENAI_API_KEY`, `SPOTIPY_CLIENT_ID`, `SPOTIPY_CLIENT_SECRET`, `SPOTIPY_REDIRECT_URI=http://localhost:7860/callback`
5. Lyric data: not in this repository for copyright reasons. Put `line_metadata.json` and `song_metadata.json` in the repository root or point `SONGFINDER_DATA_DIR` at them ([data](docs/DATA.md)).

### Backend
```bash
pip install -r requirements.txt
python app.py
```
* Serves on `http://localhost:7860`. The first start downloads the embedding model (a few hundred MB).

### Frontend
In a second terminal:
```bash
cd frontend
npm install
npm start
```
* Serves on `http://localhost:4200`.

### Tests
```bash
pip install -r requirements-dev.txt
pytest -q tests
```
* Tests for the search module (`search.py`). Unit tests use a synthetic index. With the lyric data present, an integration test also checks that one-line queries pick the same song as the previous logic.

-----

## 🖼️ How to use

1. **Start:** choose **음성으로 찾기** (search by voice) or **텍스트로 찾기** (search by text) on the main screen.
2. **Voice search:** allow the microphone and say the lyrics you remember for 5 to 15 seconds. Humming without words is not recognized.
3. **Results and playback:** the song found and the recommendations appear. After logging in to Spotify you can play them in the web player.
4. **Playlist:** "이 곡들로 플레이리스트 만들기" (make a playlist from these songs) writes a title and description and saves the playlist to your Spotify account.

-----

## 📁 Layout

```
app.py                 FastAPI backend (STT, search and recommendation APIs, Spotify, playlist text)
search.py              song identification and recommendation (SongIndex: FAISS search, window voting)
*_embeddings.npy       line, song and summary embeddings (read from the root by search.py, Git LFS)
frontend/              Angular frontend
eval/                  song identification evaluation scripts and results
tests/                 tests for search.py
notebooks/             data collection, preprocessing and tagging notebooks (from the 2025 build)
docs/                  evaluation, data notes, research log, ADRs
```

-----

## 💡 Next

  * Re-index very short lyric lines together with their neighbours, and set the "not found" threshold again
  * A secondary index on kana readings (pronunciation), for sound-alike words and Korean-accented speech
  * Measure accuracy on real users' recordings
  * Spotify embed player for previews without login; deploy on Firebase Hosting (frontend) and Cloud Run (backend)
  * Personalized recommendations from listening history

-----

### Project

* **Name:** URFIT, a voice-driven AI playlist community
* **Program:** 47th Smart Cloud IT course, Korea International Trade Association Trade Academy; refactored afterwards
* **Period:** July 29 to September 29, 2025 (initial development); refactoring in 2026

### License and copyright

* The **code** in this repository is licensed under the [Apache License 2.0](LICENSE) (since the first commit).
* The **URFIT** name, its planning and the team's presentation materials belong to team "노래불러조" of the 47th Smart Cloud IT course, Korea International Trade Association Trade Academy.
* **Lyrics** are not included in this repository for copyright reasons ([data](docs/DATA.md)).
