from fastapi import HTTPException
from core.audit import record
from core.db import transaction
from domain.catalog import latest,one
from domain.soundboard import points,windows
from domain.states import Patch


def capture(form,user):
    with transaction() as conn:
        point=one(conn,points,form.point,lock=True)
        purpose="reline" if point["patch"]==Patch.ISOLATED else "live"
        previous=latest(conn,point,purpose)
        if previous and form.slot<=previous["slot"]:
            raise HTTPException(409,"本接线版本的声检窗时刻须递增")
        conn.execute(windows.insert().values(**form.model_dump(),channel=point["channel"],
                     revision=point["revision"],purpose=purpose))
        record(conn,user,f"audio:{form.code}:{purpose}")
        return one(conn,windows,form.code)
