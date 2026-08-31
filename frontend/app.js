const base='http://localhost:8000',S={t:localStorage.token||'',a:null,i:0,r:null,s:null,ans:{},sel:null};const $=x=>document.getElementById(x);
async function api(u,o={}){let r=await fetch(base+u,{...o,headers:{...(o.body?{'Content-Type':'application/json'}:{}),...(S.t?{Authorization:'Bearer '+S.t}:{})}}),d=await r.json().catch(()=>({}));if(!r.ok)throw Error(d.detail||'Request failed');return d}function page(p){document.querySelectorAll('.page').forEach(x=>x.classList.add('hide'));$(p).classList.remove('hide');if(p==='vocab')vocab();if(p==='admin')admin()}function msg(id,x){$(id).textContent=x||''}function timer(id,start,secs){clearInterval(S[id]);S[id]=setInterval(()=>{let n=Math.max(0,secs-Math.floor((Date.now()-new Date(start))/1000));$(id+'-timer').textContent=`${String(n/60|0).padStart(2,'0')}:${String(n%60).padStart(2,'0')}`;if(!n)clearInterval(S[id])},1000)}function session(t){S.t=t;localStorage.token=t;let p=JSON.parse(atob(t.split('.')[1].replace(/-/g,'+').replace(/_/g,'/')));$('nav').classList.remove('hide');$('logout').classList.remove('hide');$('admin-link').classList.toggle('hide',p.role!=='admin');page('home');home()}document.onclick=e=>{let p=e.target.dataset.page;if(p){e.preventDefault();page(p)}};$('login').onsubmit=async e=>{e.preventDefault();try{session((await api('/auth/login',{method:'POST',body:JSON.stringify({email:$('email').value,password:$('password').value})})).access_token)}catch(e){msg('auth-msg',e.message)}};$('token-btn').onclick=()=>{if($('token').value.trim())session($('token').value.trim())};$('logout').onclick=()=>{localStorage.removeItem('token');S.t='';location.reload()};
async function home(){
  try{
    const status=await api('/assessment/status');
    if(!status.completed){$('onboard').classList.remove('hide');$('dashboard').classList.add('hide');return}
    $('onboard').classList.add('hide');$('dashboard').classList.remove('hide');
    $('level-select').value=status.level;$('level-title').textContent=status.level+' reading practice';
  }catch(e){msg('home-msg',e.message)}
  try{$('due').textContent=(await api('/vocabularies/today')).length}catch{}
}$('assessment-btn').onclick=async()=>{try{let x=await api('/assessment/start',{method:'POST'});S.a=await api('/assessment');S.i=0;page('assess');timer('assessment',x.started_at,1200);assessment()}catch(e){msg('home-msg',e.message)}};$('skip-btn').onclick=async()=>{try{await api('/assessment/skip',{method:'POST'});home()}catch(e){msg('home-msg',e.message)}};function assessment(){let q=S.a.pages[S.i].question;$('progress').textContent=`Question ${S.i+1} of ${S.a.pages.length}`;$('bar').style.width=(S.i/S.a.pages.length*100)+'%';$('passage').textContent=q.passage;$('question').textContent=q.question;$('options').innerHTML='';$('answer').disabled=true;q.options.forEach(o=>{let b=document.createElement('div');b.className='option';b.textContent=o.id.toUpperCase()+'. '+o.text;b.onclick=()=>{document.querySelectorAll('.option').forEach(x=>x.classList.remove('selected'));b.classList.add('selected');S.pick=o.id;$('answer').disabled=false};$('options').append(b)})}$('answer').onclick=async()=>{try{let d=await api('/assessment/answer',{method:'POST',body:JSON.stringify({question_id:S.a.pages[S.i].question.id,selected_answer:S.pick})});if(d.status==='completed'||d.message==='Assessment time expired')return result('Your level is ready',`${d.score} / 5`,`You can now explore ${d.level} readings.`);S.i++;assessment()}catch(e){msg('assess-msg',e.message)}};
async function reading(days){try{S.r=await api(days?'/readings/review/?days='+days:'/readings');S.s=await api('/readings/'+S.r.id+'/start',{method:'POST'});S.ans={};$('reading-empty').classList.add('hide');$('reading-body').classList.remove('hide');$('meta').textContent=`${S.r.reading_level} · ${S.r.topic} · ${S.r.estimated_reading_time} min`;$('reading-title').textContent=S.r.title;$('reading-passage').textContent=S.r.passage;timer('reading',S.s.started_at,600);$('quiz').innerHTML='';S.r.quiz.forEach((q,i)=>{let d=document.createElement('div');d.className='q';d.innerHTML='<b>'+`${i+1}. ${q.question}`+'</b>';q.options.forEach(o=>{let b=document.createElement('button');b.className='secondary choice';b.textContent=o;b.onclick=async()=>{S.ans[q.question_id]=o;d.querySelectorAll('button').forEach(x=>x.classList.remove('selected'));b.classList.add('selected');try{await api('/readings/'+S.r.id+'/answer',{method:'POST',body:JSON.stringify({session_id:S.s.session_id,question_id:q.question_id,selected_answer:o})})}catch(e){msg('quiz-msg',e.message)}};d.append(b)});$('quiz').append(d)})}catch(e){msg('read-msg',e.message)}}$('load-reading').onclick=()=>reading();$('reading-passage').onmouseup=()=>{let x=getSelection().toString().trim();if(!x)return;let p=$('reading-passage').textContent,S0=getSelection().getRangeAt(0),r=S0.cloneRange();r.selectNodeContents($('reading-passage'));r.setEnd(S0.startContainer,S0.startOffset);S.sel={x,start:r.toString().length,end:r.toString().length+x.length};$('explain-actions').classList.remove('hide')};async function explain(type){try{let s=S.sel,d=await api(`/readings/${S.r.id}/explanation?selected_text=${encodeURIComponent(s.x)}&type=${type}&start_position=${s.start}&end_position=${s.end}`),x=d.result;$('explain').innerHTML=`<h3>${d.selected_text}</h3><b>${x.bangla_meaning}</b><p>${x.bangla_explanation||''}</p>`}catch(e){$('explain').textContent=e.message}}$('word').onclick=()=>explain('vocabulary');$('sentence').onclick=()=>explain('sentence');$('finish').onclick=async()=>{try{let d=await api('/readings/'+S.r.id+'/submit',{method:'POST',body:JSON.stringify({session_id:S.s.session_id})});result('Reading complete',`${d.current_score} / 5`,'Your reading is now scheduled for spaced repetition.',d.correct_answer)}catch(e){msg('quiz-msg',e.message)}};function result(t,s,c,details=[]){$('result-title').textContent=t;$('result-score').textContent=s;$('result-copy').textContent=c;$('details').innerHTML=details.map(x=>`<p class="answer-detail">Question ${x.question_id}: ${x.status} · Correct: ${x.answer}</p>`).join('');page('result')}
async function vocab(){try{
  const [due, all]=await Promise.all([api('/vocabularies/today'),api('/vocabularies/my')]);
  const dueIds=new Set(due.map(x=>x.id));
  $('words').innerHTML=all.length?all.map(x=>`<article class="card word"><small>${dueIds.has(x.id)?'Due now':'Next review: '+new Date(x.next_review_at).toLocaleDateString()} ? Stage ${x.stage}</small><h2>${x.word}</h2><p>${x.bangla_meaning}</p><p>${x.example_context}</p>${dueIds.has(x.id)?`<button data-v="${x.id}" data-a="NOT_MASTER">Remembered</button><button data-v="${x.id}" data-a="MASTER" class="secondary">Mastered</button>`:'<p class="muted">This word is saved and will appear for review on its due date.</p>'}</article>`).join(''):'<article class="card">No vocabulary saved yet.</article>';
}catch(e){msg('vocab-msg',e.message)}}$('words').onclick=async e=>{let b=e.target.dataset;if(b.v)try{await api('/vocabularies/my/'+b.v+'/review',{method:'POST',body:JSON.stringify({action:b.a})});vocab()}catch(e){msg('vocab-msg',e.message)}};document.querySelectorAll('[data-review]').forEach(b=>b.onclick=()=>{page('read');reading(b.dataset.review)});if(S.t)session(S.t);
async function admin(){try{let r=await api('/admin/readings');$('admin-list').innerHTML=r.map(x=>`<article class="card admin-item"><div><b>${x.title}</b><p>${x.reading_level} · ${x.topic}</p></div></article>`).join('')||'<p>No readings yet.</p>'}catch(e){$('admin-list').textContent=e.message}}function fields(n){return `<div class="admin-q"><label>Question ${n}<input class="aq" required></label><label>Options (separate with |)<input class="ao" required></label><label>Correct answer<input class="ac" required></label></div>`}$('new-reading').onclick=()=>{$('reading-form').classList.remove('hide');$('admin-questions').innerHTML=[1,2,3,4,5].map(fields).join('')};$('cancel').onclick=()=>$('reading-form').classList.add('hide');$('reading-form').onsubmit=async e=>{e.preventDefault();let q=[...document.querySelectorAll('.admin-q')].map((x,i)=>({question_id:String(i+1),question:x.querySelector('.aq').value,options:x.querySelector('.ao').value.split('|').map(a=>a.trim()),correct_answer:x.querySelector('.ac').value}));try{await api('/admin/readings',{method:'POST',body:JSON.stringify({title:$('r-title').value,topic:$('r-topic').value,reading_level:$('r-level').value,estimated_reading_time:+$('r-time').value,passage:$('r-passage').value,quiz:q})});$('reading-form').classList.add('hide');admin()}catch(e){msg('admin-msg',e.message)}};


const originalExplain = explain;
explain = async function(type) {
  await originalExplain(type);
  if (type === "vocabulary" && $("explain").querySelector("b")) {
    const save = document.createElement("button");
    save.id = "save-word";
    save.className = "secondary";
    save.textContent = "Save for review";
    $("explain").append(save);
  }
};
$("word").onclick = () => explain("vocabulary");

document.addEventListener("click", async event => {
  if (event.target.id !== "save-word") return;
  const meaning = $("explain").querySelector("b")?.textContent;
  if (!meaning || !S.r || !S.sel) return;
  event.target.disabled = true;
  try {
    await api("/vocabularies/from-reading", {
      method: "POST",
      body: JSON.stringify({
        word: S.sel.x,
        bangla_meaning: meaning,
        example_context: S.r.passage,
        reading_id: S.r.id
      })
    });
    event.target.textContent = "Saved for review";
  } catch (error) {
    event.target.disabled = false;
    $("explain").insertAdjacentHTML("beforeend", `<p class="message">${error.message}</p>`);
  }
});

$("change-level").onclick = async () => {
  try {
    const level = $("level-select").value;
    await api("/readings/level", {method: "PATCH", body: JSON.stringify({level})});
    $("level-msg").textContent = `Your reading level is now ${level}.`;
    $("level-msg").style.color = "var(--green)";
    $("level-title").textContent = `${level} reading practice`;
  } catch (error) {
    msg("level-msg", error.message);
  }
};
