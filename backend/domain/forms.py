from typing import Annotated,Literal
from pydantic import BaseModel,ConfigDict,Field,StringConstraints

Code=Annotated[str,StringConstraints(strip_whitespace=True,pattern=r"^[A-Z0-9][A-Z0-9-]{2,23}$")]
Token=Annotated[str,StringConstraints(pattern=r"^[0-9a-f]{32}$")]
Ratio=Annotated[float,Field(ge=0,le=1,allow_inf_nan=False)]


class Input(BaseModel):
    model_config=ConfigDict(extra="forbid")


class Capture(Input):
    code: Code
    point: Code
    slot: Annotated[int,Field(ge=1,le=46000)]
    frequency: Annotated[int,Field(ge=60,le=14000)]
    peak_share: Ratio
    ring_index: Ratio
    level: Ratio
    self_echo: Ratio


class Diagnose(Input):
    window: Code


class SaveFinding(Input):
    code: Code
    token: Token


class Isolate(Input):
    code: Code
    finding: Code
    destination: Literal["BUS-A","BUS-B","BUS-C"]


class RelineProbe(Input):
    window: Code


class Restore(Input):
    token: Token
