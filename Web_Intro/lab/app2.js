// Step-2 : Static Files - public 폴더의 HTML/JS/CSS 파일을 그대로 내려 준다
const express = require('express')
const app = express()
const port = 3000

app.use(express.static('public'))

app.get('/', (req, res) => res.send('Hello World!'))

app.get('/Path1', function (req, res) {
  res.send('GET Path1')
})

app.get('/Path2', function (req, res) {
  res.send('GET Path2 : ' + Date())
})

app.listen(port, () => console.log(`Example app listening at http://localhost:${port}`))
