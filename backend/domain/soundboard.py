from sqlalchemy import CheckConstraint,Column,Float,ForeignKey,Integer,String,Table,UniqueConstraint
from core.db import metadata

points = Table(
    "microphone_points",metadata,
    Column("code",String(20),primary_key=True),
    Column("location",String(64),nullable=False),
    Column("mic_tag",String(20),nullable=False,unique=True),
    Column("channel",String(12),nullable=False),
    Column("revision",Integer,nullable=False,default=1),
    Column("patch",String(14),nullable=False,default="live"),
    CheckConstraint("patch IN ('live','isolated')"),
    CheckConstraint("channel IN ('BUS-A','BUS-B','BUS-C')"),
)

windows = Table(
    "sound_windows",metadata,
    Column("code",String(24),primary_key=True),
    Column("point",String(20),ForeignKey("microphone_points.code"),nullable=False),
    Column("channel",String(12),nullable=False),
    Column("revision",Integer,nullable=False),
    Column("slot",Integer,nullable=False),
    Column("frequency",Integer,nullable=False),
    Column("peak_share",Float,nullable=False),
    Column("ring_index",Float,nullable=False),
    Column("level",Float,nullable=False),
    Column("self_echo",Float,nullable=False),
    Column("purpose",String(12),nullable=False,default="live"),
    UniqueConstraint("point","slot","revision"),
    CheckConstraint("slot BETWEEN 1 AND 46000"),
    CheckConstraint("frequency BETWEEN 60 AND 14000"),
    CheckConstraint("purpose IN ('baseline','live','reline')"),
    CheckConstraint("peak_share BETWEEN 0 AND 1 AND ring_index BETWEEN 0 AND 1 "
                    "AND level BETWEEN 0 AND 1 AND self_echo BETWEEN 0 AND 1"),
)
