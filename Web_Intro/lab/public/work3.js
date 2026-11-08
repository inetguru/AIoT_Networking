// Step-6 (step3 서버에서 실행) : 브라우저는 '같은 출처'의 /webapi 만 호출한다.
// 기상청(또는 mock) API 호출은 Node 서버(app3.js)가 대신 수행한다.
function getMyStr1() {
  var xhr = new XMLHttpRequest();
  xhr.addEventListener("readystatechange", function () {
    if (this.readyState === 4) {
      console.log(this.responseText);
      onMyStr(summarize(this.responseText));
    }
  });
  xhr.open("GET", "/webapi");
  xhr.send();
}

function getMyStr2() {
  var outStr = "T2:" + Date();
  onMyStr(outStr);
}

// 응답 JSON에서 기온(T1H)만 뽑아 보기 좋게 표시
function summarize(text) {
  try {
    var items = JSON.parse(text).response.body.items.item;
    var t1h = items.filter(function (i) { return i.category === "T1H"; })[0];
    return "부산 현재 기온: " + t1h.obsrValue + " ℃ (기준 " + t1h.baseDate + " " + t1h.baseTime + ")";
  } catch (e) {
    return "응답을 해석하지 못했습니다: " + text;
  }
}
