import {el} from '../dom.js';
import {mixer} from '../audio-api.js';
import {channels,desk,labels,patchNames} from '../audio-state.js';
import {choices,field,run} from '../audio-form.js';
import {status,titleBlock} from '../widgets.js';
import {badge} from '../components/badge.js';
import {wiring} from '../components/lines.js';

export async function isolate(root,role) {
  const board=el('section',{class:'ledger'});
  const edit=el('section',{class:'action'});
  async function load(message) {
    const [patch,findings,clips]=await Promise.all([mixer.patch(),mixer.findings(),mixer.windows()]);
    const used=new Set(patch.tickets.map(item=>item.finding));
    const local=findings.filter(item=>item.category==='local'&&!used.has(item.code));
    board.replaceChildren(el('h2',{},'接线状态'),...wiring(patch.points),
      el('h2',{},'同频协作保留记录'),...findings.filter(item=>item.category==='coordinated').map(item=>
        el('p',{class:'note'},item.code+' · '+item.shared_points.join(' / ')+' ',badge(labels,item.category))),
      el('h2',{},'隔离单'),...patch.tickets.map(item=>el('p',{},item.code+' · '+item.point+
        ' · '+item.old_channel+' → '+item.new_channel+' ',badge(patchNames,item.state))));
    edit.replaceChildren(el('h2',{},'仅变更单麦位'),message?status(message,'ok'):null);
    if (role!=='reviewer'||!local.length) {edit.append(status('复核员可对尚未处理的本地异常申请独立备用路。'));return;}
    edit.append(run('isolate',[
      field('code','隔离单号',{placeholder:'ISO-1124-HUB'}),
      choices('finding','单点异常',local.map(item=>[item.code,item.code+' · '+clips.find(x=>x.code===item.focus_window)?.point]),desk.finding),
      choices('destination','备用线路',channels.map(code=>[code,code]),'BUS-C'),
    ],'隔离并切至备用路',async form=>{
      const item=await mixer.isolate(Object.fromEntries(form));
      desk.ticket=item.code;
      await load(item.code+' 已隔离，等待复线试音。');
    }));
  }
  root.replaceChildren(titleBlock('安澜 · 仅单点变更','异常麦位隔离','每张隔离单只改动一个麦位。备用路必须空闲，协作线路保留。'),
    el('div',{class:'mix'},board,edit));
  await load();
}
