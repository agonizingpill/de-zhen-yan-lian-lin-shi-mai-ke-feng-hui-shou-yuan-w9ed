from enum import StrEnum

BANDS = ("BUS-A", "BUS-B", "BUS-C")
FEATURES = ("peak_share", "ring_index", "level", "self_echo")
SCORE_LIMIT = -1.55
HERTZ_TOLERANCE = 25
MIN_SHARED_POINTS = 3


class Patch(StrEnum):
    LIVE = "live"
    ISOLATED = "isolated"


class Finding(StrEnum):
    LOCAL = "local"
    COORDINATED = "coordinated"
    NORMAL = "normal"


class Ticket(StrEnum):
    ISOLATED = "isolated"
    RESTORED = "restored"
