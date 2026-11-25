import {capture} from './capture.js';
import {findings} from './findings.js';
import {isolate} from './isolate.js';
import {reline} from './reline.js';

export const info={title:'安澜演练临时音控',customer:'安澜社区 · 临时音控组',
  purpose:'记录声检来源，区分局部回授与协作同频，并留档备用路复线。'};
export const pages=[
  {key:'capture',title:'麦位与声检',render:capture},{key:'findings',title:'邻域诊断',render:findings},
  {key:'isolate',title:'单点隔离',render:isolate},{key:'reline',title:'复线验证',render:reline},
];
