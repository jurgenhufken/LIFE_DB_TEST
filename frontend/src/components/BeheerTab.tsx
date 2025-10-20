import React,{useEffect,useState} from 'react';
import {getMeta,putTags,listCategories,addCategory} from '../api';

export default function BeheerTab(){
  const[itemId,setItemId]=useState<number>();const[data,setData]=useState<any>();const[tags,setTags]=useState('');
  const[cats,setCats]=useState<string[]>([]);const[cat,setCat]=useState('');
  useEffect(()=>{const m=location.hash.match(/#\/beheer\/(\d+)/);if(m) setItemId(parseInt(m[1]))},[]);
  useEffect(()=>{if(itemId){getMeta(itemId).then(j=>{setData(j);setTags((j.raw?.meta?.tags||[]).join(','));setCat(j.summary?.category||'')})}listCategories().then(r=>setCats(r.categories||[]))},[itemId]);
  const saveTags=async()=>{if(!itemId) return;const arr=tags.split(',').map(s=>s.trim()).filter(Boolean);await putTags(itemId,arr);alert('Tags opgeslagen');};
  const addCatFlow=async()=>{const name=prompt('Nieuwe categorie:');if(!name) return;await addCategory(name);const r=await listCategories();setCats(r.categories||[]);setCat(name);};
  if(!itemId) return <div>Kies een item in Lijst.</div>; if(!data) return <div>laden…</div>;
  const s=data.summary||{};const raw=data.raw||{};
  return (<div className='grid' style={{gridTemplateColumns:'1fr 360px'}}>
    <div className='card'>
      <h3>Metadata</h3>
      <div><b>URL:</b> <a href={s.url} target='_blank'>{s.url}</a></div>
      <div><b>Genormaliseerd:</b> {s.url_norm||'—'}</div>
      <div><b>Titel:</b> {s.title}</div>
      <div><b>Domein:</b> {s.domain}</div>
      <div><b>Categorie:</b>
        <select className='input' value={cat} onChange={e=>setCat(e.target.value)}>
          <option value=''>—</option>{cats.map(c=><option key={c} value={c}>{c}</option>)}
        </select>
        <button className='btn' onClick={addCatFlow} style={{marginLeft:8}}>+ nieuw</button>
      </div>
      <div><b>Gepubliceerd:</b> {s.published||'—'}</div>
      <h4>Koppen</h4>
      <ul>{(raw.headings?.h1||[]).map((h:string,i:number)=><li key={i}>{h}</li>)}</ul>
      <h4>Afbeeldingen</h4>
      <div className='grid' style={{gridTemplateColumns:'repeat(4,1fr)'}}>
        {(raw.images||[]).slice(0,8).map((src:string,i:number)=><img key={i} src={src} style={{width:'100%',objectFit:'cover',borderRadius:6}}/>)}
      </div>
    </div>
    <div className='card'>
      <h3>Tags</h3>
      <textarea className='input' rows={6} value={tags} onChange={e=>setTags(e.target.value)} placeholder='komma-gescheiden'></textarea>
      <div><button className='btn primary' onClick={saveTags} style={{marginTop:6}}>Opslaan</button></div>
      <h3 style={{marginTop:16}}>Raw JSON</h3>
      <pre style={{maxHeight:360,overflow:'auto',background:'var(--bg)',border:'1px solid var(--border)',borderRadius:8,padding:8}}>{JSON.stringify(raw,null,2)}</pre>
    </div>
  </div>);
}