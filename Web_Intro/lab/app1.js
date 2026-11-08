// Step-1 : Routing - 요청의 '경로(URI)'와 '메소드(GET, PUT ...)'에 따라 다르게 응답한다
const express = require('express')
const app = express()
const port = 3000

app.get('/', (req, res) => res.send('Hello World!'))

app.get('/Path1', function (req, res) {
  res.send('GET Path1')
})

app.get('/Path2', function (req, res) {
  res.send('GET Path2 : ' + Date())
})

// 브라우저 주소창은 GET만 보낼 수 있다. PUT/POST는 Postman 또는 curl로 호출해 보라.
app.put('/Path1', function (req, res) {
  res.send('PUT Path1')
})

app.post('/Path1', function (req, res) {
  res.send('POST Path1')
})

app.listen(port, () => console.log(`Example app listening at http://localhost:${port}`))
