// Step-4 (step2 서버에서 실행) : 브라우저의 JavaScript(AJAX)가 다른 출처의 Open API를 '직접' 호출한다.
// 페이지 출처  : http://localhost:3000
// API 출처     : http://localhost:4000  (포트가 다르면 '다른 출처' = Cross-Origin)
// => 브라우저가 응답 읽기를 막는다 (CORS 오류). F12 > Console 에서 확인해 보라.
function getMyStr1() {
  var outStr = "T1:" + Date();
  onMyStr(outStr);
}

function getMyStr2() {
  var xhr = new XMLHttpRequest();
  xhr.addEventListener("readystatechange", function () {
    if (this.readyState === 4) {
      console.log("status =", this.status);
      if (this.status === 0) {
        onMyStr("요청이 차단되었습니다 (status 0). F12 > Console 의 빨간 오류 메시지를 읽어 보라.");
      } else {
        onMyStr(this.responseText);
      }
    }
  });
  xhr.open("GET", "http://localhost:4000/1360000/VilageFcstInfoService/getUltraSrtNcst?serviceKey=mock-key&dataType=JSON&base_date=20260101&base_time=1200&nx=98&ny=76");
  xhr.send();
}
