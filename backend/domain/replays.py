from sqlalchemy import CheckConstraint,Column,ForeignKey,Integer,JSON,String,Table
from core.db import metadata

# 假设改线回放：只保存开回放当刻已入账的读数、基线和走线快照，
# 不改动任何实际配线；回放凭证与现场隔离单严格隔离。
replays = Table(
    "routing_replays",metadata,
    Column("code",String(24),primary_key=True),
    Column("token",String(32),nullable=False,unique=True),
    Column("focus_window",String(24),ForeignKey("sound_windows.code"),nullable=False),
    Column("point",String(20),ForeignKey("microphone_points.code"),nullable=False),
    Column("reline_slot",Integer,nullable=False),
    Column("target_channel",String(12),nullable=False),
    Column("baseline",JSON,nullable=False),
    Column("snapshot",JSON,nullable=False),
    Column("result",JSON,nullable=False),
    Column("created_by",String(80),nullable=False),
    CheckConstraint("target_channel IN ('BUS-A','BUS-B','BUS-C')"),
    CheckConstraint("reline_slot BETWEEN 1 AND 46000"),
)
