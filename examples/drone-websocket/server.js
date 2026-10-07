const WebSocket = require('ws');

const wss = new WebSocket.Server({ port: 8080 });

// 드론의 상태를 시뮬레이션하는 객체
let droneState = {
    status: '대기 중 (착륙됨)',
    altitude: 0,
    isLanded: true
};

console.log('드론 시뮬레이션 서버가 8080 포트에서 실행 중입니다...');

wss.on('connection', ws => {
    console.log('클라이언트(관제소)가 연결되었습니다.');

    // 클라이언트에게 현재 드론 상태 전송
    ws.send(JSON.stringify({
        type: 'status',
        message: '초기 상태 전송',
        state: droneState
    }));

    // 클라이언트로부터 메시지(명령) 수신
    ws.on('message', message => {
        try {
            const data = JSON.parse(message);
            
            if (data.type === 'command') {
                console.log(`명령 수신: ${data.command}`);
                handleCommand(data.command, ws);
            }
        } catch (e) {
            console.error('잘못된 메시지 형식:', e.message);
        }
    });

    ws.on('close', () => {
        console.log('클라이언트 연결이 끊겼습니다.');
    });

    ws.on('error', (err) => {
        console.error('WebSocket 오류:', err.message);
    });
});

// 드론 명령 처리 함수
function handleCommand(command, ws) {
    let responseMessage = '';

    switch (command) {
        case 'takeoff':
            if (droneState.isLanded) {
                droneState.isLanded = false;
                droneState.status = '이륙 중...';
                broadcastStatus(ws, '이륙 명령 수신');

                // 3초 후 호버링 상태로 변경 (시뮬레이션)
                setTimeout(() => {
                    droneState.altitude = 50;
                    droneState.status = '호버링 중';
                    broadcastStatus(ws, '이륙 완료. 고도 50m');
                }, 3000);
            } else {
                responseMessage = '이미 비행 중입니다.';
            }
            break;

        case 'land':
            if (!droneState.isLanded) {
                droneState.status = '착륙 중...';
                broadcastStatus(ws, '착륙 명령 수신');

                // 3초 후 착륙 완료 (시뮬레이션)
                setTimeout(() => {
                    droneState.altitude = 0;
                    droneState.isLanded = true;
                    droneState.status = '대기 중 (착륙됨)';
                    broadcastStatus(ws, '착륙 완료.');
                }, 3000);
            } else {
                responseMessage = '이미 착륙해 있습니다.';
            }
            break;

        case 'alt_up':
            if (!droneState.isLanded) {
                droneState.altitude += 10;
                responseMessage = `고도 상승. 현재 고도: ${droneState.altitude}m`;
            } else {
                responseMessage = '이륙 상태에서만 고도를 변경할 수 있습니다.';
            }
            break;

        case 'alt_down':
            if (!droneState.isLanded) {
                if (droneState.altitude > 10) {
                    droneState.altitude -= 10;
                    responseMessage = `고도 하강. 현재 고도: ${droneState.altitude}m`;
                } else {
                    responseMessage = '더 이상 하강할 수 없습니다. (최저 10m)';
                }
            } else {
                responseMessage = '이륙 상태에서만 고도를 변경할 수 있습니다.';
            }
            break;
    }

    if (responseMessage) {
        broadcastStatus(ws, responseMessage);
    }
}

// 모든 연결된 클라이언트에게 현재 상태 브로드캐스트
function broadcastStatus(ws, message) {
    const response = JSON.stringify({
        type: 'status',
        message: message,
        state: droneState
    });
    
    // wss.clients.forEach(client => {
    //     if (client.readyState === WebSocket.OPEN) {
    //         client.send(response);
    //     }
    // });
    
    // [수정] 명령을 보낸 클라이언트에게만 응답 (1:1 데모용)
    if (ws.readyState === WebSocket.OPEN) {
        ws.send(response);
    }
}