import {el} from '../dom.js';
import {feature,labels,purpose} from '../audio-state.js';
import {badge} from './badge.js';

export function metrics(clip) {
  return el('div',{class:'sampler','aria-label':'样本声检特征'},Object.entries(feature).flatMap(([key,label])=>
    [el('span',{},label),el('meter',{min:'0',max:'1',value:clip[key],'aria-label':label}),
      el('code',{},clip[key].toFixed(2))]));
}
export function sample(clip) {
  return el('details',{class:'clip'},
    el('summary',{},clip.code+' · '+clip.point+' · '+clip.slot+' / '+clip.frequency+' Hz · '+purpose[clip.purpose]),
    metrics(clip));
}
export function diagnosis(item) {
  return el('div',{class:'note'},badge(labels,item.category),el('p',{class:'mono'},
    'LOF '+item.score.toFixed(4)+' · 邻居 '+item.neighbors),
    el('p',{},item.shared_points.length ? '同期相符麦位 '+item.shared_points.join(' · ') : '没有同期相符的麦位。'));
}
function verdict(side,data) {
  return el('div',{class:'note'},el('strong',{},side),badge(labels,data.category),
    el('p',{},data.shared_points.length ? '同频麦位 '+data.shared_points.join(' · ') : '没有同频相符的麦位。'));
}
export function replayCompare(result) {
  return el('div',{class:'replay-compare'},
    el('p',{class:'mono'},'LOF '+result.score.toFixed(4)+' · 阈值 '+result.threshold+' · 邻居 '+result.neighbors),
    verdict('原走线判别',result.original),
    verdict('假设线路判别',result.hypothetical),
    el('p',{},result.original.category===result.hypothetical.category
      ?'改线假设未改变判别结论。':'判别结论发生变化，仅作假设演算参考。'));
}
