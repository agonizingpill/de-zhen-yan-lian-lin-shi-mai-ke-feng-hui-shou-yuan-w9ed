import {el} from '../dom.js';
import {mixer} from '../audio-api.js';
import {channels,desk,labels} from '../audio-state.js';
import {choices,field,run,write} from '../audio-form.js';
import {status,titleBlock} from '../widgets.js';
import {replayCompare} from '../components/samples.js';

export async function replay(root,role) {
  const edit=el('section',{class:'action'});
  const box=el('section',{class:'ledger'});
  async function load(message) {
    const [clips,items]=await Promise.all([mixer.windows(),mixer.replays()]);
    const active=clips.filter(clip=>clip.purpose==='live');
    box.replaceChildren(el('h2',{},'假设改线回放履历'),
      el('p',{class:'note'},'回放只保存开回放当刻已入账的读数、基线和走线，重跑不新增记录；回放凭证不能签现场隔离。'),
      ...items.map(item=>el('details',{class:'clip'},
        el('summary',{},item.code+' · '+item.focus_window+' · 刻度 '+item.reline_slot+' → '+item.target_channel),
        replayCompare(item.result),
        el('p',{},'麦位 '+item.point+' · 建单人 '+item.created_by),
        write(role)?el('button',{type:'button',class:'quiet',onclick:async event=>{
          const output=event.target.nextElementSibling;
          event.target.disabled=true;
          try {
            const rerun=await mixer.rerun(item.code);
            output.replaceChildren(rerunNote(rerun));
          } catch(error) {
            output.replaceChildren(status(error.message,'error'));
          } finally {event.target.disabled=false;}
        }},'用保存时快照重跑'):null,
        el('div',{class:'rerun-output'})));
    edit.replaceChildren(el('h2',{},'假设改线判别'),message?status(message,'ok'):null);
    if (!write(role)) {edit.append(status('只读账号可展开回放履历对照。'));return;}
    const focus=active.find(item=>item.code===desk.window)||active[0];
    edit.append(run('replay',[
      field('code','回放编号',{placeholder:'RP-1124-PAV'}),
      choices('window','声检窗',active.map(x=>[x.code,x.code+' / '+x.point+' / 刻度 '+x.slot]),focus?.code),
      el('div',{class:'fields'},
        field('reline_slot','改线刻度',{type:'number',min:'1',max:'46000',value:focus?focus.slot:''}),
        choices('target_channel','假设线路',channels.map(code=>[code,code]),'BUS-C')),
    ],'开假设回放',async form=>{
      const input=Object.fromEntries(form);
      input.reline_slot=Number(input.reline_slot);
      const created=await mixer.replay(input);
      await load(created.code+' 已保存假设判别，实际配线未改动。');
    }));
  }
  root.replaceChildren(titleBlock('安澜 · 假设改线回放','早挪线的同频判别对照',
    '从选定刻度起按假设线路重分同频麦，与原走线判别并列。整段只取开回放时已入账的读数，重跑沿用保存时快照。'),
    el('div',{class:'mix invert'},edit,box));
  await load();
}

function rerunNote(rerun) {
  return el('p',{class:'note'},'重跑完成：冻结同刻度读数 '+rerun.frozen_readings+
    ' 条、基线 '+rerun.frozen_baseline+' 窗，判别 '+labels[rerun.result.hypothetical.category]+
    '（原走线 '+labels[rerun.result.original.category]+'），未新增记录。');
}
