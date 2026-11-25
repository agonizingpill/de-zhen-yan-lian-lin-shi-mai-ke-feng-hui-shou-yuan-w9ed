from uuid import uuid4

from fastapi import HTTPException
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import RobustScaler
from sqlalchemy import select

from core.audit import record
from core.db import transaction
from domain.catalog import one
from domain.learning import relative_to,vector
from domain.replays import replays
from domain.soundboard import points,windows
from domain.states import FEATURES,Finding,MIN_SHARED_POINTS,SCORE_LIMIT

# 回放是只读的假设演算：只重分同频麦位，不触碰 microphone_points 的实际配线，
# 也不经过现场隔离/复线凭证流程。


def _point(snapshot,code):
    return next(item for item in snapshot["points"] if item["code"]==code)


def hypothetical_channel(snapshot,row,point_code,reline_slot,target):
    """从改线刻度起，被假设挪动的麦位走目标线路，其余麦位保持快照走线。"""
    if row["point"]==point_code and row["slot"]>=reline_slot:
        return target
    return _point(snapshot,row["point"])["channel"]


def lof_score(baseline,focus):
    scale=RobustScaler()
    samples=scale.fit_transform([vector(row) for row in baseline])
    neighbors=min(8,len(baseline)-1)
    model=LocalOutlierFactor(n_neighbors=neighbors,novelty=True)
    model.fit(samples)
    return float(model.score_samples(scale.transform([vector(focus)]))[0]),neighbors


def classify(score,focus,shared):
    if score>=SCORE_LIMIT:
        return str(Finding.NORMAL)
    if len(shared)>=MIN_SHARED_POINTS and focus["point"] in shared:
        return str(Finding.COORDINATED)
    return str(Finding.LOCAL)


def evaluate(snapshot,point_code,reline_slot,target):
    baseline=snapshot["baseline"]
    if len(baseline)<12:
        raise HTTPException(409,"保存时基线不足 12 个声检窗，无法回放")
    focus=snapshot["focus"]
    score,neighbors=lof_score(baseline,focus)
    original=sorted(set(relative_to(focus,snapshot["same_slot"])))
    # 假设线路：仅替换同刻度窗口内各麦位的归属总线，读数本身不变。
    imagined=[]
    for row in snapshot["same_slot"]:
        imagined.append({**row,"channel":hypothetical_channel(
            snapshot,row,point_code,reline_slot,target)})
    imagined_focus={**focus,"channel":target}
    hypothetical=sorted(set(relative_to(imagined_focus,imagined)))
    return {"score":score,"neighbors":neighbors,"threshold":SCORE_LIMIT,
            "features":{field:focus[field] for field in FEATURES},
            "original":{"category":classify(score,focus,original),"shared_points":original},
            "hypothetical":{"category":classify(score,focus,hypothetical),"shared_points":hypothetical}}


def create(form,user):
    with transaction() as conn:
        focus=one(conn,windows,form.window)
        if focus["purpose"]!="live":
            raise HTTPException(409,"回放仅针对主路试听窗口；复线试音不参与假设改线")
        point=one(conn,points,focus["point"],lock=True)
        if form.reline_slot>focus["slot"]:
            raise HTTPException(409,"改线刻度不能晚于所选声检窗刻度，否则该窗仍走原线")
        if form.target_channel==point["channel"]:
            raise HTTPException(409,"目标线路与当前走线相同，不构成改线")
        # 整段只取开回放当刻已入账的读数：基线、同刻度现场窗、当时配线在同一事务内冻结。
        baseline=[dict(row) for row in conn.execute(
            select(windows).where(windows.c.purpose=="baseline")
            .order_by(windows.c.code)).mappings()]
        same_slot=[dict(row) for row in conn.execute(
            select(windows).where(windows.c.slot==focus["slot"],windows.c.purpose=="live")
            .order_by(windows.c.code)).mappings()]
        board=[dict(row) for row in conn.execute(
            select(points).order_by(points.c.code)).mappings()]
        snapshot={"focus":dict(focus),"baseline":baseline,"same_slot":same_slot,
                  "points":board,"captured_at_slot":focus["slot"]}
        result=evaluate(snapshot,point["code"],form.reline_slot,form.target_channel)
        token=uuid4().hex
        conn.execute(replays.insert().values(
            code=form.code,token=token,focus_window=focus["code"],point=point["code"],
            reline_slot=form.reline_slot,target_channel=form.target_channel,
            baseline=baseline,snapshot=snapshot,result=result,created_by=user["sub"]))
        record(conn,user,f"replay:{form.code}:{point['code']}:{form.target_channel}")
        return one(conn,replays,form.code)


def rerun(code,user):
    # 重跑不新增任何记录：只读取保存时的快照、基线和走线重新判别。
    with transaction() as conn:
        item=one(conn,replays,code)
        result=evaluate(item["snapshot"],item["point"],item["reline_slot"],item["target_channel"])
        return {"code":item["code"],"focus_window":item["focus_window"],
                "reline_slot":item["reline_slot"],"target_channel":item["target_channel"],
                "token":item["token"],"result":result,
                "frozen_readings":len(item["snapshot"]["same_slot"]),
                "frozen_baseline":len(item["snapshot"]["baseline"])}


def listing():
    with transaction() as conn:
        return [dict(row) for row in conn.execute(
            select(replays.c.code,replays.c.focus_window,replays.c.point,replays.c.reline_slot,
                   replays.c.target_channel,replays.c.created_by,replays.c.result)
            .order_by(replays.c.code.desc()).limit(160)).mappings()]
