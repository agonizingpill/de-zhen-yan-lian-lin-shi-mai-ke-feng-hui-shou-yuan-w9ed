from fastapi import APIRouter,Depends
from core.auth import actor,allow
from core.roles import REVIEW,WRITE
from domain import catalog,channel,diagnose,soundcheck
from domain.forms import Capture,Diagnose,Isolate,RelineProbe,Restore,SaveFinding

patch=APIRouter(prefix="/patch")
audio=APIRouter(prefix="/audio")
feedback=APIRouter(prefix="/feedback")
routers=(patch,audio,feedback)


@patch.get("")
def points(user=Depends(actor)):
    return catalog.patchboard()


@audio.get("")
def windows(user=Depends(actor)):
    return catalog.audio()


@audio.post("",status_code=201)
def capture(form:Capture,user=Depends(actor)):
    allow(user,WRITE)
    return soundcheck.capture(form,user)


@feedback.get("")
def findings(user=Depends(actor)):
    return catalog.diagnosis()


@feedback.post("/diagnose",status_code=202)
def probe(form:Diagnose,user=Depends(actor)):
    allow(user,WRITE)
    return diagnose.diagnose(form,user)


@feedback.post("/save",status_code=201)
def save(form:SaveFinding,user=Depends(actor)):
    allow(user,WRITE)
    return diagnose.save(form,user)


@patch.post("/isolate",status_code=201)
def isolate(form:Isolate,user=Depends(actor)):
    allow(user,REVIEW)
    return channel.isolate(form,user)


@patch.post("/{code}/probe",status_code=202)
def verify(code:str,form:RelineProbe,user=Depends(actor)):
    allow(user,WRITE)
    return channel.probe(code,form,user)


@patch.post("/{code}/restore")
def restore(code:str,form:Restore,user=Depends(actor)):
    allow(user,REVIEW)
    return channel.restore(code,form,user)
