/* Guided, offline explainer. Scientific estimates are embedded by gerar.py. */
(()=>{'use strict';
const D=window.LAB_DATA,$=id=>document.getElementById(id);
const f=(x,n=2)=>Number(x).toLocaleString('pt-BR',{minimumFractionDigits:n,maximumFractionDigits:n});
const sg=(x,n=2)=>(x>0?'+':'')+f(x,n);
const S={topic:'motor',m:0,g:0,s:0,mYear:2021,equal:false,gDir:'Sul→Norte',gYear:2005,sToy:'half',sRegion:'Sul'};
const dataYear=()=>D.motor.years.find(y=>y.year===S.mYear);
const rep=[.15,.5,.85].map(q=>D.motor.amcs[Math.round(q*(D.motor.amcs.length-1))]);
const ty=()=>D.ty.find(t=>t.direction===S.gDir&&t.p===1);
const stock=()=>D.stocks.find(t=>t.region===S.sRegion);
function pressed(selector,val,key){document.querySelectorAll(selector).forEach(b=>b.setAttribute('aria-pressed',String(b.dataset[key]===String(val))))}
function tab(topic){if(!['motor','granger','estoque'].includes(topic))topic='motor';S.topic=topic;document.querySelectorAll('.scene').forEach(el=>el.hidden=el.id!==topic);pressed('[data-tab]',topic,'tab');location.hash=topic;render()}
document.querySelectorAll('[data-tab]').forEach(b=>b.addEventListener('click',()=>tab(b.dataset.tab)));
window.addEventListener('hashchange',()=>{const h=location.hash.slice(1);if(h!==S.topic)tab(h)});
function stepKey(topic){return topic==='motor'?'m':topic==='granger'?'g':'s'}
function goStep(topic,number){S[stepKey(topic)]=Math.max(0,Math.min(2,number));render();const node=$(stepKey(topic)+'-title');node.scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth',block:'center'});}
for(const [key,topic] of [['m','motor'],['g','granger'],['s','estoque']]){
 document.querySelectorAll(`[data-${key}step]`).forEach(b=>b.addEventListener('click',()=>goStep(topic,+b.dataset[key+'step'])));
 $(key+'-next').addEventListener('click',()=>goStep(topic,S[key]<2?S[key]+1:0));
}
function head(key,step,title,sub){$(key+'-step-label').textContent=`PASSO ${step+1} DE 3`;$(key+'-title').textContent=title;$(key+'-sub').textContent=sub;pressed(`[data-${key}step]`,step,key+'step');$(key+'-next').textContent=step===2?'Recomeçar ↺':'Próximo passo →'}
function button(label,attr,val,active){return `<button type="button" data-${attr}="${val}" aria-pressed="${active}">${label}</button>`}
function bind(attr,fn){document.querySelectorAll(`[data-${attr}]`).forEach(b=>b.addEventListener('click',()=>fn(b.dataset[attr])))}

function renderMotor(){const n=S.m,y=dataYear(),beta=D.motor.models.find(r=>r.spec==='S1'&&r.exposicao==='exp_apt_edafo').beta;
 $('m-interaction').innerHTML=`<span class="control-label">Escolha uma mudança real no câmbio</span><div class="choice">${button('Alta de 2019 → 2020','myear',2021,S.mYear===2021)}${button('Queda de 2021 → 2022','myear',2023,S.mYear===2023)}</div>`+(n===2?`<div class="secondary-action">${button(S.equal?'✓ Exposições iguais':'E se os três lugares fossem iguais?','mequal','toggle',S.equal)}</div>`:'');
 bind('myear',v=>{S.mYear=+v;renderMotor()});bind('mequal',()=>{S.equal=!S.equal;renderMotor()});
 if(n===0){head('m',n,'Uma mudança. Três lugares.','O índice cambial mudou no mesmo ano para todas as 166 AMCs. Primeiro, siga apenas o sinal comum.');
  $('m-art').innerHTML=`<div class="signal-main"><span>ÍNDICE REAL EFETIVO DO CÂMBIO</span><div class="big-change">${f(y.before)} <i>→</i> ${f(y.after)}</div><strong>${sg(y.delta)} pontos</strong><small>${y.shockYear-1} → ${y.shockYear}</small></div><div class="three-arrows"><span>↓</span><span>↓</span><span>↓</span></div><div class="places">${rep.map((a,i)=>`<div class="place"><span>AMC ${i+1}</span><b>${a.code_amc}</b><small>recebe o mesmo ano de câmbio</small></div>`).join('')}</div>`;
  $('m-takeaway').innerHTML='<b>Primeira ideia:</b> o câmbio sozinho não explica por que uma AMC responderia diferente de outra no mesmo ano.';
  $('m-example-label').textContent='Fonte: série real de 1985–2024';
 }else if(n===1){head('m',n,'As condições locais mudam a resposta.','Agora olhe somente para uma diferença entre os lugares: a aptidão edafoclimática.');
  $('m-art').innerHTML=`<div class="signal-strip">A mesma mudança de ${sg(y.delta)} pontos chega às três AMCs <span>→</span></div><div class="condition-grid">${rep.map((a,i)=>`<div class="condition"><span>AMC ${a.code_amc}</span><div class="condition-icon">${'●'.repeat(i+1)}${'○'.repeat(2-i)}</div><b>${['Menor aptidão','Aptidão intermediária','Maior aptidão'][i]}</b><small>Aptidão medida: ${sg(a.exp_apt_edafo)} na escala padronizada</small></div>`).join('')}</div>`;
  $('m-takeaway').innerHTML='<b>Segunda ideia:</b> “exposição” é a característica local que faz o mesmo sinal entrar de modo diferente na comparação estatística.';
  $('m-example-label').textContent='As três AMCs e suas aptidões são reais';
 }else{head('m',n,'O modelo combina sinal × exposição.','Veja somente a parcela que o modelo associa a essa interação. Ela não é a mudança total observada do rebanho.');
  const values=rep.map((a)=>beta*y.z*(S.equal?rep[1].exp_apt_edafo:a.exp_apt_edafo));
  const max=Math.max(.09,...values.map(Math.abs));
  $('m-art').innerHTML=`<div class="formula-line"><span>SINAL COMUM</span><strong>${sg(y.z)} <small>choque padronizado</small></strong><i>×</i><span>CONDIÇÃO LOCAL</span><i>→</i><span>PARCELA ESTIMADA</span></div><div class="effects">${rep.map((a,i)=>`<div class="effect"><span>AMC ${a.code_amc}</span><small>${S.equal?'aptidão igualada':(['menor','intermediária','maior'][i]+' aptidão')}</small><div class="effect-track"><div class="effect-zero"></div><div class="effect-bar ${values[i]<0?'negative':''}" style="--v:${Math.min(47,Math.abs(values[i])/max*47)}%;--side:${values[i]<0?'left':'right'}"></div></div><b>${sg(values[i],3)}</b><small>desvios-padrão · só a interação</small></div>`).join('')}</div>`;
  $('m-takeaway').innerHTML=S.equal?'<b>Você igualou as exposições:</b> as três parcelas ficaram iguais. Sem diferença local, esta interação não produz contraste entre AMCs.':'<b>O modelo estima parcelas diferentes:</b> isso mostra o que a interação compara. O sinal ainda é sensível ao método de inferência e à latitude.';
  $('m-example-label').textContent='Coeficiente estimado: −0,0325';
 }
 $('m-honesty').innerHTML=n<2?'Ao avançar, você verá como o modelo testa se as diferenças locais acompanham respostas distintas.':'<b>Limite importante:</b> o p agrupado é 0,026; por permutação circular é 0,132. Ao incluir latitude, o coeficiente da aptidão encolhe. Trate o “motor comum” como hipótese, não como causa demonstrada.';
}

function renderGranger(){const n=S.g,t=n<2?D.ty.find(v=>v.direction==='Sul→Norte'&&v.p===1):ty(),idx=t.years.indexOf(S.gYear),obs=t.observed[idx],r=t.restricted[idx],u=t.full[idx],target=S.gDir==='Sul→Norte'?'pastagem do Norte':'agricultura do Sul',source=S.gDir==='Sul→Norte'?'agricultura do Sul':'pastagem do Norte';
 $('g-interaction').innerHTML=n<2?`<span class="control-label">Escolha um ano observado</span><div class="choice">${button('2005','gyear',2005,S.gYear===2005)}${button('2019','gyear',2019,S.gYear===2019)}</div>`:`<span class="control-label">Qual direção testar?</span><div class="choice">${button('Sul → Norte','gdir','Sul→Norte',S.gDir==='Sul→Norte')}${button('Norte → Sul','gdir','REVERSO',S.gDir==='REVERSO')}</div>`;
 bind('gyear',v=>{S.gYear=+v;renderGranger()});bind('gdir',v=>{S.gDir=v;renderGranger()});
 if(n===0){head('g',n,`Queremos prever ${S.gYear}.`,'Antes de conhecer aquele ano, uma previsão poderia usar o passado do próprio Norte.');
  $('g-art').innerHTML=`<div class="time-rail"><div><small>ANTES</small><b>${S.gYear-3} · ${S.gYear-2} · ${S.gYear-1}</b><span>pastagem do Norte</span></div><div class="rail-arrow">→</div><div class="time-target"><small>ANO A PREVER</small><strong>${S.gYear}</strong><span>${f(obs,3)} milhões de hectares<br>observados depois</span></div></div><div class="quiet-question">Quanto do resultado do Norte seu próprio passado já permite prever?</div>`;
  $('g-takeaway').innerHTML='<b>Primeira ideia:</b> antes de perguntar pelo Sul, precisamos considerar a memória do próprio Norte.';
  $('g-example-label').textContent='Série regional real · 1985–2024';
 }else if(n===1){head('g',n,'Agora entregue uma informação a mais.','O segundo modelo também vê o passado da agricultura do Sul. Compare os erros dos dois ajustes.');
  const e1=Math.abs(obs-r)*1000,e2=Math.abs(obs-u)*1000;
  $('g-art').innerHTML=`<div class="prediction-question">Observado em ${S.gYear}: <strong>${f(obs,3)} Mha</strong> de pastagem no Norte</div><div class="prediction-grid"><div class="prediction"><span>MODELO A</span><h3>Só o passado do Norte</h3><div class="prediction-value">${f(r,3)} <small>Mha ajustados</small></div><div class="error-meter"><i style="width:${Math.min(100,e1/50*100)}%"></i></div><b>Erro neste ano: ${f(e1,2)} mil ha</b></div><div class="prediction"><span>MODELO B</span><h3>Norte + passado do Sul</h3><div class="prediction-value">${f(u,3)} <small>Mha ajustados</small></div><div class="error-meter added"><i style="width:${Math.min(100,e2/50*100)}%"></i></div><b>Erro neste ano: ${f(e2,2)} mil ha</b></div></div>`;
  $('g-takeaway').innerHTML='<b>A pergunta de Granger:</b> acrescentar o passado do Sul melhora a previsão do Norte de maneira consistente, além do que o Norte já explica por si? Um ano isolado não responde.';
  $('g-example-label').textContent='Ajustes calculados com a série real';
 }else{head('g',n,'Toda–Yamamoto dá memória extra ao teste.','As séries são persistentes. O método estima anos passados adicionais, mas só testa os coeficientes substantivos.');
  const direction=S.gDir==='Sul→Norte'?'Sul → Norte':'Norte → Sul';
  $('g-art').innerHTML=`<div class="memory-explain"><div class="memory-head">PARA PREVER ${target.toUpperCase()}</div><div class="memory-row"><span>Passado do próprio destino</span><div class="memory-box own">1 ano atrás</div><div class="memory-box own">2 anos atrás</div><div class="memory-box own">3 anos atrás</div></div><div class="memory-row"><span>Passado da origem: ${source}</span><div class="memory-box tested">1 ano atrás<b>TESTADO</b></div><div class="memory-box extra">2 anos atrás<b>EXTRA</b></div><div class="memory-box extra">3 anos atrás<b>EXTRA</b></div></div><div class="memory-result"><div><span>DIREÇÃO</span><b>${direction}</b></div><div><span>RESULTADO DO TESTE</span><strong>p = ${f(t.pvalue,4)}</strong></div></div></div>`;
  $('g-takeaway').innerHTML=`<b>Nestes dados, o teste não detecta conteúdo preditivo adicional a 5%.</b> Esse resultado não prova efeito zero. E, mesmo que detectasse, prever não demonstraria causa.`;
  $('g-example-label').textContent='p = 1 testado + 2 defasagens extras';
 }
 $('g-honesty').innerHTML=n===2?'<b>Leia com cuidado:</b> as duas gavetas “extra” continuam no modelo; elas não entram na hipótese testada. O p-valor não é a probabilidade de a hipótese ser verdadeira.':'Os ajustes mostrados são feitos dentro da amostra; o teste estatístico usa todos os anos disponíveis, não só o ano escolhido.';
}

function renderStock(){const n=S.s;
 if(n===0){head('s',n,'Comece com uma conta de 100 hectares.','Imagine que, em um ano, 10% do estoque seja convertido. Quantos hectares saem?');$('s-interaction').innerHTML='';
  $('s-art').innerHTML=`<div class="toy-lead"><div><small>ESTOQUE</small><strong>100 ha</strong></div><span>×</span><div><small>TAXA ANUAL</small><strong>10%</strong></div><span>=</span><div class="toy-answer"><small>FLUXO NO ANO</small><strong>10 ha</strong></div></div><div class="hundred">${Array.from({length:100},(_,i)=>`<i class="${i<10?'converted':''}" aria-hidden="true"></i>`).join('')}</div><div class="hundred-label"><span>10 quadradinhos convertidos</span><span>90 permanecem no estoque</span></div>`;
  $('s-takeaway').innerHTML='<b>Primeira ideia:</b> fluxo = estoque × taxa. “10%” é a fração do estoque que sai naquele ano.';
  $('s-example-label').textContent='Exemplo inventado só para aprender a conta';
 }else if(n===1){head('s',n,'Mude uma peça de cada vez.','Parta dos mesmos 100 ha e 10%. Veja duas maneiras diferentes de chegar a um fluxo menor.');
  $('s-interaction').innerHTML=`<span class="control-label">Escolha o que muda</span><div class="choice">${button('Metade do estoque','stoy','half',S.sToy==='half')}${button('Metade da taxa','stoy','rate',S.sToy==='rate')}${button('Ambos diminuem','stoy','both',S.sToy==='both')}</div>`;
  bind('stoy',v=>{S.sToy=v;renderStock()});
  const Sval=S.sToy==='rate'?100:50,Rval=S.sToy==='half'?10:5,F=Sval*Rval/100;
  $('s-art').innerHTML=`<div class="compare-toy"><div class="compare-base"><small>ANTES</small><div class="simple-equation">100 ha <span>×</span> 10% <span>=</span> <b>10 ha</b></div></div><div class="compare-arrow">↓</div><div class="compare-after"><small>DEPOIS · ${S.sToy==='half'?'ESTOQUE MENOR':S.sToy==='rate'?'TAXA MENOR':'AS DUAS PEÇAS MENORES'}</small><div class="simple-equation"><b class="${Sval<100?'changed':''}">${Sval} ha</b> <span>×</span> <b class="${Rval<10?'changed':''}">${Rval}%</b> <span>=</span> <strong>${f(F,1)} ha</strong></div></div></div>`;
  $('s-takeaway').innerHTML=S.sToy==='both'?'<b>As duas peças menores se multiplicam:</b> metade × metade produz um quarto do fluxo inicial.':`<b>O fluxo caiu de 10 para ${f(F,0)} ha.</b> ${S.sToy==='half'?'Isso aconteceu sem mexer na taxa.':'Isso aconteceu sem mexer no estoque.'} A queda do fluxo sozinha não revela qual peça mudou.`;
  $('s-example-label').textContent='Ainda é um exemplo inventado';
 }else{head('s',n,'Agora veja o que ocorreu no seu estudo.','Compare as médias de dois períodos. Escolha Sul ou Norte e acompanhe estoque, taxa e fluxo.');
  $('s-interaction').innerHTML=`<span class="control-label">Escolha uma região real de Goiás</span><div class="choice">${button('Sul','sregion','Sul',S.sRegion==='Sul')}${button('Norte','sregion','Norte',S.sRegion==='Norte')}${button('Centro','sregion','Centro',S.sRegion==='Centro')}</div>`;
  bind('sregion',v=>{S.sRegion=v;renderStock()});
  const d=stock(),a=d.acts[0],b=d.acts[1];
  $('s-art').innerHTML=`<div class="real-data-head"><span>ATO II · 2001–2019</span><span>ATO III · 2020–2024</span></div><div class="real-rows"><div><span>Estoque de savana e campo</span><b>${f(a.stock,2)} Mha</b><i>→</i><strong>${f(b.stock,2)} Mha</strong></div><div><span>Taxa anual de conversão</span><b>${f(a.rate*100,2)}%</b><i>→</i><strong>${f(b.rate*100,2)}%</strong></div><div class="flow-row"><span>Fluxo anual</span><b>${f(a.flow*1000,2)} mil ha</b><i>→</i><strong>${f(b.flow*1000,2)} mil ha</strong></div></div><div class="real-conclusion">${d.region==='Sul'?'<b>No Sul:</b> o estoque diminuiu e a taxa também. Na decomposição da queda, ~17% é a parcela do estoque e ~83% a da taxa.':d.region==='Norte'?'<b>No Norte:</b> o estoque diminuiu, mas a taxa cresceu. A taxa maior superou a perda de estoque, e o fluxo aumentou.':'<b>No Centro:</b> o estoque diminuiu, mas a taxa cresceu o suficiente para aumentar o fluxo.'}</div>`;
  $('s-takeaway').innerHTML='<b>Agora a pergunta de pesquisa faz sentido:</b> quanto da mudança vem do volume de vegetação ainda existente e quanto vem da taxa? A taxa reúne fatores diferentes que precisam de análise própria.';
  $('s-example-label').textContent='Dados reais da pesquisa · médias por ato';
 }
 $('s-honesty').innerHTML=n<2?'Este cenário de 100 hectares foi criado apenas para tornar a conta visível. Os números da pesquisa aparecem no passo 3.':'<b>Limite importante:</b> a decomposição é uma identidade contábil. Ela não demonstra, por si, por que a taxa mudou nem equivale a dizer que todo o estoque podia ser legalmente convertido.';
}
function render(){if(S.topic==='motor')renderMotor();else if(S.topic==='granger')renderGranger();else renderStock()}
tab(location.hash.slice(1)||document.body.dataset.start);
})();
