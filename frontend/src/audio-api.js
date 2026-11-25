import {awaitCompute,request} from './api.js';

export const mixer = {
  patch:()=>request('/patch'), capture:body=>request('/audio',body), windows:()=>request('/audio'),
  diagnosis:body=>request('/feedback/diagnose',body), wait:awaitCompute,
  save:body=>request('/feedback/save',body), findings:()=>request('/feedback'),
  isolate:body=>request('/patch/isolate',body), probe:(code,body)=>request('/patch/'+code+'/probe',body),
  restore:(code,body)=>request('/patch/'+code+'/restore',body),
};
