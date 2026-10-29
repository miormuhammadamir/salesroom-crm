'use strict';
const monthly=document.getElementById('monthly-data');
if(monthly){
 const data=JSON.parse(monthly.textContent), svg=document.getElementById('revenue-chart');
 const ns='http://www.w3.org/2000/svg';
 const el=(tag,attrs,text)=>{const n=document.createElementNS(ns,tag);Object.entries(attrs).forEach(([k,v])=>n.setAttribute(k,v));if(text!==undefined)n.textContent=text;svg.appendChild(n);return n;};
 const max=Math.max(100,...data.map(d=>d.value)), top=Math.ceil(max/100)*100;
 for(let i=0;i<5;i++){const y=20+i*40;el('line',{x1:65,x2:680,y1:y,y2:y,stroke:'#edf1e8','stroke-dasharray':'3 4'});el('text',{x:53,y:y+3,'text-anchor':'end',fill:'#8d9a87','font-size':10},new Intl.NumberFormat('en',{notation:'compact'}).format(top*(1-i/4)));}
 data.forEach((d,i)=>{const x=90+i*98,h=d.value/top*160;const rect=el('rect',{x,y:180-h,width:46,height:h,rx:4,fill:i===5?'#17634d':'#c4d8af'});const title=document.createElementNS(ns,'title');title.textContent=`${d.label}: RM ${d.value.toFixed(2)}`;rect.appendChild(title);el('text',{x:x+23,y:203,'text-anchor':'middle',fill:'#87957f','font-size':10},d.label);});
}
const add=document.getElementById('add-item');
if(add){
 const total=document.getElementById('id_items-TOTAL_FORMS'),rows=document.getElementById('item-rows'),template=document.getElementById('empty-item');
 add.addEventListener('click',()=>{const count=Number(total.value);if(count>=100){alert('Maximum 100 item rows per order.');return;}rows.insertAdjacentHTML('beforeend',template.innerHTML.replaceAll('__prefix__',String(count)));total.value=count+1;});
 const products=JSON.parse(document.getElementById('product-data').textContent);
 rows.addEventListener('change',e=>{if(e.target.tagName!=='SELECT')return;const p=products.find(x=>String(x.id)===e.target.value);if(!p)return;const row=e.target.closest('tr');row.querySelector('[name$="-description"]').value=p.name;row.querySelector('[name$="-unit_price"]').value=p.price;const q=row.querySelector('[name$="-quantity"]');if(!q.value)q.value=1;});
}
document.getElementById('print-order')?.addEventListener('click',()=>window.print());
