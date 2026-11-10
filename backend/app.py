from flask import Flask, jsonify, request

app = Flask(__name__)
app.json.ensure_ascii = False

booths = {
    1: {"name": "컴공 타코야끼", "category": "먹거리", "location": "우당관 앞", "capacity": 20, "reserved": []},
    2: {"name": "달고나 뽑기", "category": "게임", "location": "우당관 앞", "capacity": 15, "reserved": []},
    3: {"name": "인생네컷 포토부스", "category": "체험", "location": "1층 도서관", "capacity": 30, "reserved": []},
    4: {"name": "수제 레모네이드", "category": "먹거리", "location": "운동장 입구", "capacity": 25, "reserved": []},
    5: {"name": "타로 상담소", "category": "체험", "location": "1층 도서관", "capacity": 3, "reserved": []},
    6: {"name": "학과 굿즈샵", "category": "굿즈", "location": "1층 도서관", "capacity": 40, "reserved": []},
    7: {"name": "취업 상담소", "category": "체험", "location": "1층 도서관", "capacity": 2, "reserved": []},
}

def make_info(booth_id):
    booth = booths[booth_id]
    count = len(booth["reserved"])
    info = {
        "id": booth_id,
        "name": booth["name"],
        "category": booth["category"],
        "location": booth["location"],
        "capacity": booth["capacity"],
        "reserved": count,
        "remaining": booth["capacity"] - count,
    }
    return info

@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})


# ---------------------------------------------
# 기능 1. 부스 검색
# 예) /api/booths?q=타코
# ---------------------------------------------
@app.get("/api/booths")
def search_booths():
    keyword = request.args.get("q", "").strip()   # 주소에서 검색어 꺼내기

    # 검색어가 너무 길면 거절
    if len(keyword) > 15:
        return jsonify({"error": "검색어는 15자 이하로 입력하세요."}), 400

    result = []
    for booth_id in booths:
        booth = booths[booth_id]
        text = booth["name"] + booth["category"] + booth["location"]

        # 검색어가 비어 있으면 전부, 아니면 글자가 포함된 부스만 담기
        if keyword == "" or keyword in text:
            result.append(make_info(booth_id))

    return jsonify(result)


# ---------------------------------------------
# 기능 2. 부스 예약
# 예) /api/booths/1/reserve 로 학번과 이름을 보냄
# ---------------------------------------------
@app.post("/api/booths/<int:booth_id>/reserve")
def reserve_booth(booth_id):
    data = request.get_json(silent=True)   # 화면에서 보낸 값 받기
    if data is None:
        data = {}

    student_id = str(data.get("student_id", "")).strip()
    name = str(data.get("name", "")).strip()

    # 검사 1: 학번이 숫자인가?
    if not student_id.isdigit():
        return jsonify({"error": "학번은 숫자만 입력하세요."}), 400

    # 검사 2: 이름을 썼는가?
    if name == "":
        return jsonify({"error": "이름을 입력하세요."}), 400

    # 검사 3: 그런 부스가 있는가?
    if booth_id not in booths:
        return jsonify({"error": "부스를 찾을 수 없습니다."}), 404

    booth = booths[booth_id]

    # 검사 4: 이미 예약한 학번인가?
    if student_id in booth["reserved"]:
        return jsonify({"error": "이미 예약한 부스입니다."}), 409

    # 검사 5: 자리가 남았는가?
    if len(booth["reserved"]) >= booth["capacity"]:
        return jsonify({"error": "예약이 마감되었습니다."}), 409

    # 모든 검사를 통과하면 예약 명단에 학번 추가
    booth["reserved"].append(student_id)
    return jsonify(make_info(booth_id)), 201


# ---------------------------------------------
# 기능 3. 내 예약 조회
# 예) /api/reservations?student_id=2224052
# ---------------------------------------------
@app.get("/api/reservations")
def my_reservations():
    student_id = request.args.get("student_id", "").strip()

    if not student_id.isdigit():
        return jsonify({"error": "학번은 숫자만 입력하세요."}), 400

    result = []
    for booth_id in booths:
        # 이 부스의 예약 명단에 내 학번이 있으면 담기
        if student_id in booths[booth_id]["reserved"]:
            result.append(make_info(booth_id))

    return jsonify(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)