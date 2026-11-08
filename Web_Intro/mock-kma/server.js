// 기상청 '초단기실황조회(getUltraSrtNcst)' 응답을 흉내 내는 모의 서버
// 실제 서비스키 없이도 수업을 진행할 수 있게 하고, CORS 오류를 재현하기 위한 용도이다.
// 주의: Access-Control-Allow-Origin 헤더를 '일부러' 보내지 않는다.
const http = require('http');

const PORT = 4000;
const PATH = '/1360000/VilageFcstInfoService/getUltraSrtNcst';

function makeItems(q) {
  const baseDate = q.get('base_date') || '20260101';
  const baseTime = q.get('base_time') || '1200';
  const nx = parseInt(q.get('nx') || '98', 10);
  const ny = parseInt(q.get('ny') || '76', 10);
  const hour = parseInt(baseTime.slice(0, 2), 10);
  // 하루 주기로 오르내리는 그럴듯한 기온 (오후 3시 최고)
  const temp = (14 + 8 * Math.sin(((hour - 9) / 24) * 2 * Math.PI)).toFixed(1);
  const values = { PTY: '0', REH: '55', RN1: '0', T1H: temp, UUU: '1.2', VEC: '240', VVV: '-0.8', WSD: '2.4' };
  return Object.entries(values).map(([category, obsrValue]) => ({
    baseDate, baseTime, category, nx, ny, obsrValue,
  }));
}

const server = http.createServer((req, res) => {
  const u = new URL(req.url, `http://${req.headers.host}`);
  // 서버는 요청을 정상 수신한다. 막는 것은 '브라우저'라는 점을 로그로 확인할 수 있다.
  console.log(`${new Date().toISOString()} ${req.method} ${u.pathname} Origin=${req.headers.origin || '-'}`);

  if (u.pathname === PATH) {
    const items = makeItems(u.searchParams);
    const body = {
      response: {
        header: { resultCode: '00', resultMsg: 'NORMAL_SERVICE' },
        body: {
          dataType: 'JSON',
          items: { item: items },
          pageNo: 1, numOfRows: 10, totalCount: items.length,
        },
      },
    };
    res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
    res.end(JSON.stringify(body));
  } else if (u.pathname === '/') {
    res.writeHead(200, { 'Content-Type': 'text/plain; charset=utf-8' });
    res.end(`mock-kma 동작 중\n예) ${PATH}?serviceKey=x&base_date=20260101&base_time=1200&nx=98&ny=76\n`);
  } else {
    res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
    res.end('Not Found');
  }
});

server.listen(PORT, () => console.log(`mock-kma listening on http://localhost:${PORT}`));
