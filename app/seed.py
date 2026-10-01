from sqlalchemy.orm import Session
from .models import Pattern, Exercise

PATTERNS = [
    ("IM_ADJ", 0, "I'm + adjective", "state"),
    ("WANT_NOUN", 0, "I want + noun", "desire_object"),
    ("NEED_NOUN", 0, "I need + noun", "need_object"),
    ("WANT_TO", 1, "I want to + V", "desire_action"),
    ("NEED_TO", 1, "I need to + V", "need_action"),
    ("HAVE_TO", 1, "I have to + V", "obligation"),
    ("CAN", 1, "I can + V", "ability"),
    ("CANT", 1, "I can't + V", "inability"),
    ("GOING_TO", 1, "I'm going to + V", "plan"),
    ("DONT_WANT_TO", 1, "I don't want to + V", "negative_desire"),
]

EXERCISES = {
    "IM_ADJ": [("나 피곤해.", "I'm tired."), ("나 배고파.", "I'm hungry."), ("나 바빠.", "I'm busy."), ("나 준비됐어.", "I'm ready."), ("나 늦었어.", "I'm late.")],
    "WANT_NOUN": [("커피가 마시고 싶어.", "I want some coffee."), ("물 좀 마시고 싶어.", "I want some water."), ("새 휴대폰을 갖고 싶어.", "I want a new phone."), ("휴식이 필요할 만큼 쉬고 싶어.", "I want a break."), ("피자가 먹고 싶어.", "I want some pizza.")],
    "NEED_NOUN": [("물이 필요해.", "I need some water."), ("도움이 필요해.", "I need some help."), ("휴식이 필요해.", "I need a break."), ("시간이 좀 필요해.", "I need some time."), ("새 휴대폰이 필요해.", "I need a new phone.")],
    "WANT_TO": [("집에 가고 싶어.", "I want to go home."), ("커피를 마시고 싶어.", "I want to drink some coffee."), ("좀 쉬고 싶어.", "I want to get some rest."), ("친구를 만나고 싶어.", "I want to meet my friend."), ("오늘 일찍 자고 싶어.", "I want to go to bed early tonight.")],
    "NEED_TO": [("우유를 사야 할 필요가 있어.", "I need to buy some milk."), ("친구에게 전화해야 해.", "I need to call my friend."), ("좀 쉬어야 해.", "I need to get some rest."), ("휴대폰을 충전해야 해.", "I need to charge my phone."), ("영어를 더 연습해야 해.", "I need to practice English more.")],
    "HAVE_TO": [("오늘 야근해야 해.", "I have to work late today."), ("내일 일찍 일어나야 해.", "I have to get up early tomorrow."), ("지금 가야 해.", "I have to go now."), ("오늘 보고서를 끝내야 해.", "I have to finish the report today."), ("주말에 일해야 해.", "I have to work this weekend.")],
    "CAN": [("나는 운전할 수 있어.", "I can drive."), ("도와줄 수 있어.", "I can help."), ("영어를 조금 할 수 있어.", "I can speak a little English."), ("오늘 갈 수 있어.", "I can go today."), ("기다릴 수 있어.", "I can wait.")],
    "CANT": [("오늘 갈 수 없어.", "I can't go today."), ("운전할 수 없어.", "I can't drive."), ("지금 말할 수 없어.", "I can't talk right now."), ("기다릴 수 없어.", "I can't wait."), ("오늘 늦게까지 있을 수 없어.", "I can't stay late today.")],
    "GOING_TO": [("오늘 운동할 거야.", "I'm going to work out today."), ("친구를 만날 거야.", "I'm going to meet my friend."), ("오늘 집에 있을 거야.", "I'm going to stay home today."), ("저녁을 만들 거야.", "I'm going to make dinner."), ("주말에 쉴 거야.", "I'm going to rest this weekend.")],
    "DONT_WANT_TO": [("오늘 나가고 싶지 않아.", "I don't want to go out today."), ("지금 일하고 싶지 않아.", "I don't want to work right now."), ("기다리고 싶지 않아.", "I don't want to wait."), ("그 얘기를 하고 싶지 않아.", "I don't want to talk about it."), ("오늘 요리하고 싶지 않아.", "I don't want to cook today.")],
}


def seed_database(db: Session):
    if db.query(Pattern).count() > 0:
        return
    for code, level, form, function in PATTERNS:
        db.add(Pattern(code=code, level=level, canonical_form=form, function=function))
    db.commit()
    patterns = {p.code: p for p in db.query(Pattern).all()}
    for code, items in EXERCISES.items():
        for prompt, answer in items:
            form = patterns[code].canonical_form
            db.add(Exercise(pattern_id=patterns[code].id, prompt_ko=prompt, reference_answer=answer,
                            hint_1=f"오늘의 핵심 구조는 '{form}'입니다. 구조를 떠올려보세요.",
                            hint_2=f"문장 뼈대: {form}", difficulty=1.0))
    db.commit()
