from fastapi import HTTPException
from sqlalchemy import select
from core.audit import record
from core.db import transaction
from core.queueing import result,submit
from domain.catalog import calibration,one,same_slot
from domain.interventions import findings
from domain.replays import replays
from domain.soundboard import points,windows
from domain.states import Patch


def reject_replay_token(conn,token):
    # 回放凭证只用于假设演算，不能据此签入现场发现或隔离单。
    if conn.execute(select(replays.c.code).where(replays.c.token==token)).first():
        raise HTTPException(409,"假设改线回放凭证不能签发现场判别，请使用原始诊断凭证")


def sound_snapshot(conn,focus):
    return {"focus":focus,"baseline":calibration(conn),"simultaneous":same_slot(conn,focus)}


def diagnose(form,user):
    with transaction() as conn:
        focus=one(conn,windows,form.window)
        point=one(conn,points,focus["point"])
        if focus["purpose"]!="live" or point["patch"]!=Patch.LIVE:
            raise HTTPException(409,"仅在播窗口用于判别；隔离后的试音须到复线页")
        return submit(user,{"kind":"diagnosis",**sound_snapshot(conn,focus)})


def save(form,user):
    with transaction() as conn:
        reject_replay_token(conn,form.token)
        computation=result(user,form.token)
    captured=computation["input"]
    rating=computation["result"]
    if captured["kind"]!="diagnosis":
        raise HTTPException(409,"请使用原始诊断凭证签入发现")
    focus=captured["focus"]
    with transaction() as conn:
        point=one(conn,points,focus["point"],lock=True)
        if point["patch"]!=Patch.LIVE or point["revision"]!=focus["revision"]:
            raise HTTPException(409,"该声检窗口属于旧接线版本")
        current=same_slot(conn,focus)
        if {x["code"] for x in current}!={x["code"] for x in captured["simultaneous"]}:
            raise HTTPException(409,"同期同频证据有新增，请重新判别")
        conn.execute(findings.insert().values(code=form.code,focus_window=focus["code"],category=rating["category"],
                    score=rating["score"],neighbors=rating["neighbors"],shared_points=rating["shared_points"],
                    reviewed_by=user["sub"],compute_token=form.token))
        record(conn,user,f"finding:{form.code}:{rating['category']}")
        return one(conn,findings,form.code)
