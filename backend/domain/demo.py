from random import Random
from domain.channel import patch_mutex
from domain.soundboard import points, windows
from domain.states import FEATURES

PLACES = [
    ("MIC-PAV","东门棚台","TAG-E01","BUS-A"),
    ("MIC-WALK","西风雨连廊","TAG-W09","BUS-A"),
    ("MIC-INFO","入口咨询桌","TAG-Z03","BUS-A"),
    ("MIC-HUB","室内总音控","TAG-N26","BUS-B"),
]


def capture(code, location, slot, frequency, levels, purpose="live"):
    channel=next(item[3] for item in PLACES if item[0]==location)
    return {"code":code,"point":location,"channel":channel,"revision":1,"slot":slot,
            "frequency":frequency,"purpose":purpose,**dict(zip(FEATURES,levels,strict=True))}


def bench():
    rng=Random(217)
    return [capture(f"REF-{index+1:02}",PLACES[index%4][0],index+1,550+index*13,
                    [max(.03,min(.42,rng.gauss(center,.033))) for center in (.20,.24,.30,.15)],"baseline")
            for index in range(32)]


FIXTURES=(
    (patch_mutex,[{"code":1}]),
    (points,[{"code":code,"location":name,"mic_tag":tag,"channel":channel} for code,name,tag,channel in PLACES]),
    (windows,bench()+[
        capture("WIN-C-01","MIC-PAV",80,1320,(.79,.73,.55,.59)),
        capture("WIN-C-02","MIC-WALK",80,1324,(.80,.72,.57,.53)),
        capture("WIN-C-03","MIC-INFO",80,1311,(.83,.74,.56,.57)),
        capture("WIN-L-01","MIC-HUB",82,2210,(.91,.87,.62,.70)),
        capture("WIN-N-01","MIC-WALK",84,730,(.22,.25,.31,.15)),
    ]),
)
