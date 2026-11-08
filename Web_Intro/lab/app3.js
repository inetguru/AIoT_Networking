// Step-3 : Node 서버가 Open API를 '대신' 호출한다 (서버 측 프록시)
//   브라우저 --(같은 출처)--> 이 서버(/webapi) --(서버 간 호출)--> 기상청 Open API
const express = require('express')
const app = express()
const port = 3000

// compose.yaml / .env 에서 주입된다. 기본값은 모의 서버(mock-kma)
const KMA_BASE = process.env.KMA_BASE || 'http://mock-kma:4000'
const KMA_KEY = process.env.KMA_KEY || 'mock-key'

// 초단기실황은 매시 40분경 발표되므로, 40분 전 시각의 정시를 기준으로 한다 (한국 시간)
function baseDateTime() {
  const t = new Date(Date.now() + 9 * 3600 * 1000 - 40 * 60 * 1000)
  const iso = t.toISOString()
  return { base_date: iso.slice(0, 10).replace(/-/g, ''), base_time: iso.slice(11, 13) + '00' }
}

app.use(express.static('public'))

app.get('/', (req, res) => res.send('Hello World!'))

app.get('/webapi', async function (req, res) {
  const u = new URL(KMA_BASE + '/1360000/VilageFcstInfoService/getUltraSrtNcst')
  const params = { serviceKey: KMA_KEY, pageNo: 1, numOfRows: 10, dataType: 'JSON', nx: 98, ny: 76, ...baseDateTime() }
  Object.entries(params).forEach(([k, v]) => u.searchParams.set(k, v))
  try {
    const r = await fetch(u)            // Node 내장 fetch (별도 설치 불필요)
    const body = await r.text()
    res.type('application/json').send(body)
  } catch (e) {
    res.status(502).json({ error: String(e) })
  }
})

app.listen(port, () => console.log(`Example app listening at http://localhost:${port}  (API: ${KMA_BASE})`))
