import {el} from '../dom.js';
import {channels,patchNames} from '../audio-state.js';
import {badge} from './badge.js';

export function wiring(points) {
  return channels.map(channel=>{
    const patched=points.filter(point=>point.channel===channel);
    return el('div',{class:'channel'},el('strong',{class:'mono'},channel),el('div',{},
      patched.length ? patched.map(point=>el('div',{class:'jack'},el('code',{},point.code),
        el('span',{},point.location+' · v'+point.revision),badge(patchNames,point.patch))) :
        el('p',{},'独立备用，无麦位驻留')));
  });
}
