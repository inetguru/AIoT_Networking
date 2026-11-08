# 일러스트 프롬프트

문서의 분위기용 일러스트 7장을 AI 이미지 모델로 만들기 위한 프롬프트다. Gemini 앱, Google AI Studio, 또는 `gen_images.py`(API 결제 필요)에서 쓴다.
그림 파일은 이름을 아래 파일명으로 맞춰 `img/` 폴더에 넣으면 문서(`index.html`)에 **자동으로 나타난다**. (없으면 그 자리는 비어 있다)

## 공통 스타일 (모든 프롬프트 뒤에 붙인다)

Clean modern flat vector illustration in isometric view, soft color palette of navy blue, teal and warm orange accents on a light off-white background, friendly educational infographic style, smooth shapes, subtle shadows. IMPORTANT: do not include any text, letters, numbers, logos or labels anywhere in the image.

## 이미지별 프롬프트

비율은 16:9 가 좋다. AI는 글자를 잘 못 그리므로 **그림에 글자를 넣지 않도록** 요청하고, 설명은 문서의 캡션이 맡는다.

### `img/01_factory_floor.jpg`

A cutaway isometric diorama of a smart factory production line: a conveyor belt carrying boxes, an industrial robot arm, a CNC machine, proximity sensors on the line, a control cabinet, an operator touch-screen panel on a stand, and a small rugged edge gateway box with a few network cables.

### `img/02_it_vs_ot.jpg`

A concept illustration split into two halves joined by a bridge. Left half: a calm modern office world with servers, a cloud, laptops and dashboards. Right half: a noisy industrial world with machinery, a control cabinet, motors and a yellow safety fence. In the middle a sturdy bridge with a gateway box connects the two.

### `img/03_plc_cabinet.jpg`

A close-up isometric illustration of an industrial control cabinet with a modular PLC mounted on a DIN rail: a CPU module, several input and output modules with small colored LEDs, a 24V power supply. Neat wires run from the modules to a proximity sensor, an electric motor and a solenoid valve.

### `img/04_gateway_translator.jpg`

A conceptual illustration of an industrial edge gateway acting as a translator. Left: several old legacy machines connected with many different tangled serial cables. Center: a rugged fanless gateway box with a gear symbol. Right: a modern server and cloud dashboard connected by one clean standard cable.

### `img/05_amr_warehouse.jpg`

An isometric illustration of an autonomous mobile robot carrying a bin through a factory warehouse. It has a LiDAR safety scanner on its front, wireless access points on the ceiling emitting wifi waves, shelves and a yellow-black safety floor line.

### `img/06_edge_ai_separation.jpg`

A concept illustration of two separate rugged boxes joined by a short cable: on the left a PLC controller driving a motor (real-time control), on the right an edge AI box with a GPU chip analyzing images from a camera above a conveyor belt with products.

### `img/07_address_space_tree.jpg`

A friendly concept illustration of a factory represented as a digital tree map: a factory building at the top, branching down into production lines, machines and small sensor nodes, shown as connected glowing nodes like a folder tree, with a tablet cursor browsing the tree.
