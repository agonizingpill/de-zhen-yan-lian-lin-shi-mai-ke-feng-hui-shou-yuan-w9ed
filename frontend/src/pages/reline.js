import {el} from '../dom.js';
import {mixer} from '../audio-api.js';
import {desk,patchNames} from '../audio-state.js';
import {choices,run,write} from '../audio-form.js';
import {status,titleBlock} from '../widgets.js';
import {badge} from '../components/badge.js';
import {diagnosis,sample} from '../components/samples.js';

export async function reline(root,role) {
  const rail=el('section',{class:'ledger'});
  const edit=el('section',{class:'action'});
  async function load(message) {
    const [patch,clips]=await Promise.all([mixer.patch(),mixer.windows()]);
    rail.replaceChildren(el('h2',{},'线路切换凭证'),...patch.tickets.map(item=>{
      const point=patch.points.find(x=>x.code===item.point);
      const last=clips.find(x=>x.code===item.reline_window);
      return el('div',{class:'note'},el('button',{type:'button',class:'quiet',onclick:()=>{
        desk.ticket=item.code;select(item);}},item.code),item.point+' · '+point.channel+' ',
        badge(patchNames,item.state),last?sample(last):null);
    }));
    const active=patch.tickets.find(x=>x.code===desk.ticket)||patch.tickets.find(x=>x.state==='isolated');
    select(active,message);
    function select(ticket,note) {
      edit.replaceChildren(el('h2',{},'复线试音与签复位'),note?status(note,'ok'):null);
      if (!ticket || !write(role) || ticket.state!=='isolated') {
        edit.append(status('选中隔离单后提交最新复线窗。'));
        return;
      }
      const valid=clips.filter(x=>x.point===ticket.point&&x.channel===ticket.new_channel&&x.purpose==='reline')
        .sort((a,b)=>b.slot-a.slot);
      if (!valid.length) {edit.append(status('先在声检页采集备用路的复线窗口。'));return;}
      const result=el('div',{});
      edit.append(run('probe',[choices('window','复线证据',valid.map(x=>[x.code,x.code+' / '+x.slot]))],
        '检测备用路',async form=>{
          const job=await mixer.probe(ticket.code,{window:form.get('window')});
          const report=await mixer.wait(job.token,item=>{
            if(item.status==='queued') result.replaceChildren(status('等待复线检测'));
          });
          if(report.status!=='ready') throw new Error(report.detail);
          result.replaceChildren(diagnosis(report.result));
          if(role==='reviewer') result.append(run('restore',[],'签复位',async ()=>{
            await mixer.restore(ticket.code,{token:job.token});
            desk.ticket=ticket.code;
            await load(ticket.code+' 已复位。');
          }));
        }),result);
    }
  }
  root.replaceChildren(titleBlock('安澜 · 备用路复测','复线验证与监听确认','相同麦位、备用路和新声检时间同时吻合，且回响恢复正常，复核员才能签复位。'),
    el('div',{class:'mix'},rail,edit));
  await load();
}
