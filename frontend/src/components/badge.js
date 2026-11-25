import {el} from '../dom.js';
export function badge(names,value) {
  return el('span',{class:'signal-tag','data-state':value},names[value] || value);
}
