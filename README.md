# LEO Satellite Link-Budget Simulator

A browser dashboard and Python/Flask calculation API for exploring how satellite elevation, altitude, frequency, EIRP, ground-station G/T and atmospheric loss affect a LEO communications link.

Developed for the **2025 ICT Convergence Project Competition (차세대통신 ICT 융합 프로젝트 경진대회)** by Team **전삼이들 (Jeonsamideul)**. The project records list **LEE SANGYEOP** as team lead, with teammates **이정우 and 최준영**. Sangyeop led the project and worked on the Python link-budget calculation logic and JSON API; the dashboard was a team deliverable. Participation is documented; no award or ranking is claimed.

## Run locally

Python 3.10+ is sufficient for the source. Install the two API dependencies into an isolated environment:

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -m flask --app app run --host 127.0.0.1 --port 5000
```

Open `index.html` in a browser. It sends JSON requests to `http://127.0.0.1:5000/calculate`. Keep the Flask terminal running. The UI does not require Node.js.

Alternatively, serve the HTML locally in a second terminal:

```powershell
python -m http.server 8000 --bind 127.0.0.1
```

Then open `http://127.0.0.1:8000/index.html`. The API remains on port 5000. The original `app.py` also has a development-only `python app.py` entry point with Flask debug mode; the command above runs without that debug setting.

## Calculation model

The API accepts a JSON object containing `current_elevation` (deg), `satAltitude` (km), `frequency` (GHz), `satPower` (EIRP in dBW), `g_t` (dB/K), `zenithLoss` (dB), and `required_c_n0` (dB-Hz).

For Earth radius R = 6371 km, altitude h, and elevation e:

- Slant range: d = R × (sqrt(((R+h)/R)² − cos²(e)) − sin(e)).
- Free-space loss: 20 log10(d in metres) + 20 log10(f in Hz) − 147.55 dB.
- Atmospheric loss: zenith loss / sin(e).
- C/N₀: EIRP − free-space loss − atmospheric loss + G/T − (−228.6).
- Link margin: C/N₀ − required C/N₀.

The response contains `d_km`, `l_fs`, `l_a`, `c_n0` and `margin`, rounded to one decimal. A missing field or calculation error returns HTTP 400 with an `error` message.

Example request:

```json
{
  "current_elevation": 90,
  "satAltitude": 550,
  "frequency": 12.5,
  "satPower": 20,
  "g_t": 15,
  "zenithLoss": 0.5,
  "required_c_n0": 50
}
```

## What the demonstration can and cannot show

Try increasing G/T by 3 dB: the calculated C/N₀ and margin each increase by 3 dB. Doubling frequency at unchanged range increases free-space loss by about 6 dB. Lower elevation increases both slant range and the simple atmospheric-loss term.

The animated pass is a **synthetic 15-second visualization**, not an orbital propagator or live satellite feed. The Earth is spherical, and the atmospheric model is a simple secant approximation; it becomes unsuitable close to the horizon. Non-positive elevation is clamped to a small positive angle by the original demo. Doppler, rain models, antenna pattern, polarization, interference, real ephemerides and physical hardware are not modeled. Input validation is limited, so use physically meaningful positive altitude/frequency and an elevation between 0 and 90 degrees. This is a local educational prototype, not a validated operational communications-planning service.

## Files and verification

- `app.py`: original calculation API.
- `index.html`: original HTML/CSS/JavaScript UI; only its filename was normalized.
- `tests/test_link_budget.py`: independent API checks for zenith geometry, frequency scaling, G/T scaling and malformed requests. Run with `python -m unittest discover -s tests -v` after installing requirements.
- `examples/drone-websocket/`: separate takeoff/land/altitude WebSocket prototype found in the original archive. It is not used by the link-budget simulator. With Node.js installed, run `npm install` then `npm start` in that folder; it listens on port 8080 and has no included controller UI.

Source syntax and the calculation function were checked during packaging. Dependency-free mathematical checks passed; the Flask HTTP layer and browser animation were not executed in the packaging environment because Flask was not installed. The project source contains no authentication; keep the demo local. No repository-wide open-source license has been assigned; see [LICENSE-NOTE.md](LICENSE-NOTE.md).

## 한국어 소개

전삼이들 팀장으로 2025 ICT 융합 프로젝트 경진대회에 참가하며 개발한 LEO 위성 통신 링크 버짓 시뮬레이터입니다. 이상엽은 프로젝트 총괄과 Python 백엔드의 링크 버짓 수식·JSON API 개발을 맡았고, HTML 대시보드는 팀 결과물입니다. 고도·고도각·주파수·EIRP·G/T를 바꾸면서 경사 거리, 자유공간 경로 손실, 대기 손실, C/N₀와 링크 마진을 확인할 수 있습니다.

기존 계산 코드와 UI를 보존하고 실행 안내·검증을 추가했습니다. 애니메이션은 실제 궤도가 아닌 합성 통과 경로이며, 대기 손실도 단순 근사입니다. 실제 위성 운용을 검증한 도구로 표현하지 않습니다. 수상 근거가 없어 참가 경험으로 기록합니다.
