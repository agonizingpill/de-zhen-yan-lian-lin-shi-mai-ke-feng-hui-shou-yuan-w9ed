from fastapi import HTTPException
from core.audit import record
from core.db import transaction
from core.queueing import result,submit
from domain.catalog import calibration,one,same_slot
from domain.interventions import findings
from domain.soundboard import points,windows
from domain.states import Patch


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
