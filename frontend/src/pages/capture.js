import {el} from '../dom.js';
import {mixer} from '../audio-api.js';
import {desk,feature} from '../audio-state.js';
import {choices,field,run,write} from '../audio-form.js';
import {status,titleBlock} from '../widgets.js';
import {wiring} from '../components/lines.js';
import {sample} from '../components/samples.js';

export async function capture(root,role) {
  const line=el('section',{class:'ledger'});
  const edit=el('section',{class:'action'});
  async function load(message) {
    const [patch,clips]=await Promise.all([mixer.patch(),mixer.windows()]);
    line.replaceChildren(el('h2',{},'线路接入'),...wiring(patch.points),el('h2',{},'试听与复线窗口'),
      ...clips.slice(0,10).map(sample));
    edit.replaceChildren(el('h2',{},'登记声检概要'),message?status(message,'ok'):null);
    if (!write(role)) {edit.append(status('此账号可核对时间窗和接入线路。'));return;}
    edit.append(run('capture',[
      field('code','声检窗编号',{placeholder:'WIN-90-HUB'}),
      choices('point','麦位',patch.points.map(x=>[x.code,x.code+' '+x.location])),
      el('div',{class:'fields'},field('slot','同一演练时间刻度',{type:'number',min:'1',max:'46000',value:'90'}),
        field('frequency','主峰频率（Hz）',{type:'number',min:'60',max:'14000',value:'730'})),
      el('div',{class:'fields'},Object.entries(feature).map(([key,label])=>
        field(key,label,{type:'number',min:'0',max:'1',value:'.2',step:'.01'}))),
    ],'保存声检窗',async form=>{
      const input=Object.fromEntries(form);
      for(const key of ['slot','frequency',...Object.keys(feature)]) input[key]=Number(input[key]);
      const item=await mixer.capture(input);
      desk.window=item.code;
      await load(item.code+' 已保存至 '+item.channel+' · '+(item.purpose==='reline'?'复线试音':'主路试听'));
    }));
  }
  root.replaceChildren(titleBlock('安澜 · 演练音控','麦位与声检窗口','既有配线、声检时间和摘要特征一同记录。隔离状态下的新增声检归入复线试音。'),
    el('div',{class:'mix'},line,edit));
  await load();
}
