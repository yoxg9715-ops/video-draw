import os
import random
import re

import json

from flask import Flask, Response

app = Flask(__name__)


def jsonify(data):
    """카카오가 읽기 쉽도록 한글을 그대로, UTF-8 헤더를 붙여서 보내요."""
    return Response(
        json.dumps(data, ensure_ascii=False),
        status=200,
        content_type="application/json; charset=utf-8",
    )

# ------------------------------------------------------------
# 1) 영상 목록 (제목, 링크)
#    영상을 추가/삭제하고 싶으면 이 부분만 고치면 돼요.
# ------------------------------------------------------------
NORMAL_VIDEOS = [
    ("그쪽도 해이재형을 아세요?", "https://youtu.be/krj-SnNnD4A"),
    ("2023", "https://youtu.be/oYBiiV_Bouc"),
    ("10 MONTH", "https://youtu.be/fLhA-IcBSK4"),
    ("반야심경", "https://youtu.be/zmddWwFh83U"),
    ("7월,", "https://youtu.be/fD1wlBYHb1U"),
    ("바다의 왕자", "https://youtu.be/rjrWqENsMLc"),
    ("2024", "https://youtu.be/goja7nwG5nA"),
    ("강원도", "https://youtu.be/ej6BhexI9XQ"),
    ("와이키키 브라더스", "https://youtu.be/sqezLkQ89CI"),
    ("상상속의 너", "https://youtu.be/RpPnFttY9rE"),
    ("은방울", "https://youtu.be/0NYfAtbqfjs"),
    ("뜨거운 안녕", "https://youtu.be/ck7WsR8Jpfk"),
    ("열대야", "https://youtu.be/1wJmokhdC80"),
    ("2025", "https://youtu.be/PELxXk9U44I"),
    ("더 장대한 도전", "https://youtu.be/uXexHfERfRY"),
]

SPECIAL_VIDEOS = [
    ("니는 자연인이다", "https://youtu.be/jpWy7G8mulc"),
    ("그대에게", "https://youtu.be/uBeC1HZWmew"),
    ("기민 프랭크", "https://youtu.be/OzjO7xh-Xt8"),
]

# ------------------------------------------------------------
# 2) 뽑힐 확률 (숫자가 클수록 잘 나와요)
#    일반 10, 특별 2 -> 특별 영상 3개가 합쳐서 약 4% 확률
# ------------------------------------------------------------
NORMAL_WEIGHT = 10
SPECIAL_WEIGHT = 2

QUICK_REPLIES = [
    {
        "label": "🎬 한 번 더 뽑기",
        "action": "message",
        "messageText": "영상 뽑기",
    }
]


def video_id(url):
    """유튜브 링크에서 영상 ID만 꺼내요."""
    m = re.search(r"(?:youtu\.be/|v=)([\w-]{11})", url)
    return m.group(1) if m else ""


def pick_video():
    pool = []
    weights = []
    for title, url in NORMAL_VIDEOS:
        pool.append((title, url, False))
        weights.append(NORMAL_WEIGHT)
    for title, url in SPECIAL_VIDEOS:
        pool.append((title, url, True))
        weights.append(SPECIAL_WEIGHT)
    return random.choices(pool, weights=weights, k=1)[0]


@app.route("/")
def home():
    return "영상 뽑기 서버가 잘 켜져 있어요!"


@app.route("/draw", methods=["POST"])
def draw():
    title, url, is_special = pick_video()
    thumb = "https://img.youtube.com/vi/%s/hqdefault.jpg" % video_id(url)

    outputs = [{"simpleText": {"text": "🥁 두구두구두구... 오늘의 뮤비를 뽑는 중!"}}]

    if is_special:
        outputs.append(
            {
                "simpleText": {
                    "text": "🎉🎉 축하드립니다! 🎉🎉\n특별 영상에 당첨되셨어요!\n이 영상은 이곳에서만 시청 가능합니다."
                }
            }
        )
        card_title = "✨ [특별 영상] " + title
    else:
        card_title = "🎬 " + title

    outputs.append(
        {
            "basicCard": {
                "title": card_title,
                "description": "친구들이 힘들게 만든 뮤직비디오예요. 많이 사랑해 주세요!",
                "thumbnail": {"imageUrl": thumb},
                "buttons": [
                    {"action": "webLink", "label": "▶ 영상 보러가기", "webLinkUrl": url}
                ],
            }
        }
    )

    return jsonify(
        {
            "version": "2.0",
            "template": {"outputs": outputs, "quickReplies": QUICK_REPLIES},
        }
    )


# ------------------------------------------------------------
# 3) 원인 찾기용 테스트 주소 (문제가 해결되면 지워도 돼요)
# ------------------------------------------------------------
@app.route("/t1", methods=["POST"])
def test1():
    """글자 말풍선 1개만"""
    return jsonify(
        {"version": "2.0", "template": {"outputs": [{"simpleText": {"text": "테스트1 성공"}}]}}
    )


@app.route("/t2", methods=["POST"])
def test2():
    """썸네일 없는 카드 + 버튼"""
    return jsonify(
        {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "basicCard": {
                            "title": "테스트2",
                            "description": "썸네일 없는 카드",
                            "buttons": [
                                {
                                    "action": "webLink",
                                    "label": "영상 보기",
                                    "webLinkUrl": "https://youtu.be/krj-SnNnD4A",
                                }
                            ],
                        }
                    }
                ]
            },
        }
    )


@app.route("/t3", methods=["POST"])
def test3():
    """썸네일 있는 카드 (바로가기 버튼 없음)"""
    return jsonify(
        {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "basicCard": {
                            "title": "테스트3",
                            "description": "썸네일 있는 카드",
                            "thumbnail": {
                                "imageUrl": "https://img.youtube.com/vi/krj-SnNnD4A/hqdefault.jpg"
                            },
                            "buttons": [
                                {
                                    "action": "webLink",
                                    "label": "영상 보기",
                                    "webLinkUrl": "https://youtu.be/krj-SnNnD4A",
                                }
                            ],
                        }
                    }
                ]
            },
        }
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
