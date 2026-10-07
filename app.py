import math
from flask import Flask, request, jsonify
from flask_cors import CORS

# Flask 앱 생성 및 CORS 설정
app = Flask(__name__)
CORS(app)  # 모든 외부 요청을 허용 (HTML 파일 연결용)

# === 핵심 상수 ===
R_E = 6371      # 지구 반경 (km)
k_dB = -228.6   # 볼츠만 상수 (dBW/K/Hz)

@app.route('/calculate', methods=['POST'])
def calculate_link_budget():
    try:
        # 1. HTML로부터 JSON 데이터 받기
        data = request.json
        
        # 2. 입력 파라미터 추출
        El_deg = float(data['current_elevation'])
        H_km = float(data['satAltitude'])
        f_ghz = float(data['frequency'])
        EIRP_dBW = float(data['satPower'])
        GT_dBK = float(data['g_t'])
        L_zenith_dB = float(data['zenithLoss'])
        Req_CN0_dBHz = float(data['required_c_n0'])

        # 3. === 핵심 공학 수식 계산 (Python이 전담) ===
        
        # 3.1. 고도각(rad) 변환 (0에 가까울 때 오류 방지)
        El_rad = El_deg * (math.pi / 180)
        if El_rad <= 0: El_rad = 0.0001 # 0으로 나누기 방지

        # 3.2. 경사 거리 (d_km)
        RE_H = R_E + H_km
        d_km = R_E * (math.sqrt(math.pow(RE_H / R_E, 2) - math.pow(math.cos(El_rad), 2)) - math.sin(El_rad))
        d_m = d_km * 1000

        # 3.3. 자유 공간 경로 손실 (L_fs)
        f_hz = f_ghz * 1e9
        L_fs_dB = 20 * math.log10(d_m) + 20 * math.log10(f_hz) - 147.55

        # 3.4. 대기 손실 (L_a)
        L_a_dB = L_zenith_dB / math.sin(El_rad)

        # 3.5. C/N0 계산 (dB-Hz)
        # C/N0 = EIRP - L_fs - L_a + G/T - k
        C_N0_dBHz = EIRP_dBW - L_fs_dB - L_a_dB + GT_dBK - k_dB

        # 3.6. 링크 마진 계산 (dB)
        linkMargin_dB = C_N0_dBHz - Req_CN0_dBHz

        # 4. 계산 결과를 JSON 형태로 HTML에 돌려주기
        return jsonify({
            'd_km': round(d_km, 1),
            'l_fs': round(L_fs_dB, 1),
            'l_a': round(L_a_dB, 1),
            'c_n0': round(C_N0_dBHz, 1),
            'margin': round(linkMargin_dB, 1)
        })

    except Exception as e:
        # 오류 발생 시
        return jsonify({"error": str(e)}), 400

# === 서버 실행 ===
if __name__ == '__main__':
    print("======================================================")
    print("  LEO 위성 링크 버짓 'Python 계산 서버'가 시작됩니다.  ")
    print("  HTML 시뮬레이터가 이 서버에 접속하여 계산을 요청합니다. ")
    print("  http://127.0.0.1:5000 에서 대기 중...           ")
    print("======================================================")
    app.run(port=5000, debug=True) # 5000번 포트로 서버 실행