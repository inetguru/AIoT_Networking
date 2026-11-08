# 문서(index.html)에 들어가는 설명용 일러스트를 AI 이미지 모델(Gemini)로 생성한다.
#   사용:  GEMINI_API_KEY=키 python gen_images.py [파일이름 ...]      (인자가 없으면 아직 없는 것만 생성)
#   - 키는 환경변수로만 받는다. 모델은 GEMINI_IMAGE_MODEL 로 지정(기본: 아래 후보를 차례로 시도).
#   - 생성한 원본 PNG는 ../img/ 에 저장하고, 문서에는 용량이 작은 JPG를 쓴다 (Pillow 가 있을 때).
#   - 프롬프트는 PROMPTS 에 있다. 그림에 글자를 넣게 하지 않는다(AI는 한글을 잘 못 그린다) -> 설명은 HTML 캡션으로.
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "img")
BASE = "https://generativelanguage.googleapis.com/v1beta"
MODELS = [os.environ["GEMINI_IMAGE_MODEL"]] if os.environ.get("GEMINI_IMAGE_MODEL") else [
    "gemini-2.5-flash-image", "gemini-3.1-flash-image", "gemini-3-pro-image"]

STYLE = ("Clean modern flat vector illustration in isometric view, soft color palette of navy blue, teal and warm orange "
         "accents on a light off-white background, friendly educational infographic style, smooth shapes, subtle shadows. "
         "IMPORTANT: do not include any text, letters, numbers, logos or labels anywhere in the image.")

PROMPTS = {
    "01_factory_floor": "A cutaway isometric diorama of a smart factory production line: a conveyor belt carrying boxes, an "
                        "industrial robot arm, a CNC machine, proximity sensors on the line, a control cabinet, an operator "
                        "touch-screen panel on a stand, and a small rugged edge gateway box with a few network cables.",
    "02_it_vs_ot": "A concept illustration split into two halves joined by a bridge. Left half: a calm modern office world "
                   "with servers, a cloud, laptops and dashboards. Right half: a noisy industrial world with machinery, a "
                   "control cabinet, motors and a yellow safety fence. In the middle a sturdy bridge with a gateway box connects the two.",
    "03_plc_cabinet": "A close-up isometric illustration of an industrial control cabinet with a modular PLC mounted on a DIN rail: "
                      "a CPU module, several input and output modules with small colored LEDs, a 24V power supply. Neat wires "
                      "run from the modules to a proximity sensor, an electric motor and a solenoid valve.",
    "04_gateway_translator": "A conceptual illustration of an industrial edge gateway acting as a translator. Left: several old "
                             "legacy machines connected with many different tangled serial cables. Center: a rugged fanless "
                             "gateway box with a gear symbol. Right: a modern server and cloud dashboard connected by one clean standard cable.",
    "05_amr_warehouse": "An isometric illustration of an autonomous mobile robot carrying a bin through a factory warehouse. "
                        "It has a LiDAR safety scanner on its front, wireless access points on the ceiling emitting wifi waves, "
                        "shelves and a yellow-black safety floor line.",
    "06_edge_ai_separation": "A concept illustration of two separate rugged boxes joined by a short cable: on the left a PLC "
                             "controller driving a motor (real-time control), on the right an edge AI box with a GPU chip "
                             "analyzing images from a camera above a conveyor belt with products.",
    "07_address_space_tree": "A friendly concept illustration of a factory represented as a digital tree map: a factory building "
                             "at the top, branching down into production lines, machines and small sensor nodes, shown as "
                             "connected glowing nodes like a folder tree, with a tablet cursor browsing the tree.",
}


def generate(name, prompt):
    last_err = None
    for model in MODELS:
        body = {"contents": [{"role": "user", "parts": [{"text": prompt + "\n\n" + STYLE}]}],
                "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": "16:9"}}}
        req = urllib.request.Request(f"{BASE}/models/{model}:generateContent", data=json.dumps(body).encode(),
                                     headers={"x-goog-api-key": os.environ["GEMINI_API_KEY"], "Content-Type": "application/json"})
        try:
            data = json.load(urllib.request.urlopen(req, timeout=180))
        except urllib.error.HTTPError as e:
            last_err = f"{model}: HTTP {e.code} {e.read().decode()[:160]}"
            print("   실패 ->", last_err)
            continue
        except Exception as e:
            last_err = f"{model}: {type(e).__name__} {e}"
            print("   실패 ->", last_err)
            continue
        for part in data.get("candidates", [{}])[0].get("content", {}).get("parts", []):
            inline = part.get("inlineData") or part.get("inline_data")
            if inline:
                path = os.path.join(OUT, name + ".png")
                with open(path, "wb") as f:
                    f.write(base64.b64decode(inline["data"]))
                return model, path
        last_err = f"{model}: 이미지가 응답에 없음 -> {json.dumps(data)[:200]}"
        print("   실패 ->", last_err)
    raise RuntimeError(last_err)


def to_jpg(png_path):
    try:
        from PIL import Image
    except ImportError:
        return None
    im = Image.open(png_path).convert("RGB")
    if im.width > 1600:
        im = im.resize((1600, round(im.height * 1600 / im.width)))
    jpg = png_path[:-4] + ".jpg"
    im.save(jpg, quality=85, optimize=True)
    return jpg


if __name__ == "__main__":
    if not os.environ.get("GEMINI_API_KEY"):
        sys.exit("GEMINI_API_KEY 환경변수가 필요하다")
    os.makedirs(OUT, exist_ok=True)
    todo = sys.argv[1:] or [n for n in PROMPTS if not os.path.exists(os.path.join(OUT, n + ".jpg"))]
    for name in todo:
        print(f"[{name}] 생성 중 ...", flush=True)
        t0 = time.time()
        model, png = generate(name, PROMPTS[name])
        jpg = to_jpg(png)
        print(f"   완료 ({time.time() - t0:.0f}초, 모델 {model}) -> {os.path.basename(jpg or png)}", flush=True)
