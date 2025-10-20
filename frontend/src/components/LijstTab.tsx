import React,{useEffect,useRef,useState} from 'react';
import {listItems,listCategories,setToken} from '../api';

export default function LijstTab(){
  const[items,setItems]=useState<any[]>([]);
  const[q,setQ]=useState('');const[category,setCategory]=useState('');const[domain,setDomain]=useState('');
  const[cats,setCats]=useState<string[]>([]);
  const[token,setTok]=useState(localStorage.getItem('life_db_token')||'');
  const searchRef = useRef<HTMLInputElement|null>(null);

  useEffect(()=>{listCategories().then(r=>setCats(r.categories||[]))},[]);
  const load=()=>listItems({q,category,domain,limit:20}).then(r=>setItems(r.items||[]));
  useEffect(()=>{load()},[]);

  // keyboard shortcuts
  useEffect(()=>{
    const onKey=(e:KeyboardEvent)=>{
      if(e.key==='/' && !e.ctrlKey && !e.metaKey){ e.preventDefault(); searchRef.current?.focus(); }
    };
    window.addEventListener('keydown',onKey); return ()=>window.removeEventListener('keydown',onKey);
  },[]);

  return (<div>
    <div className='grid' style={{gridTemplateColumns:'1fr 160px 160px 100px 220px'}}>
      <input ref={searchRef} className='input' placeholder='Zoek… (press / to focus)' value={q} onChange={e=>setQ(e.target.value)}/>
      <input className='input' placeholder='Domein' value={domain} onChange={e=>setDomain(e.target.value)}/>
      <select className='input' value={category} onChange={e=>setCategory(e.target.value)}>
        <option value=''>Alle categorieën</option>
        {cats.map(c=><option key={c} value={c}>{c}</option>)}
      </select>
      <button className='btn' onClick={load}>Filter</button>
      <input className='input' placeholder='API-token (Bearer)' value={token} onChange={e=>{setTok(e.target.value); setToken(e.target.value);}}/>
    </div>
    <div className='grid' style={{marginTop:10}}>
      {items.map(it=>(<div key={it.id} className='card'>
        <div style={{fontWeight:700}}>{it.title||'(zonder titel)'}</div>
        <div className='small'>{it.domain} • {new Date(it.created_at).toLocaleString()}</div>
        <div style={{fontSize:13,marginTop:6,overflow:'hidden',textOverflow:'ellipsis'}}>{it.description}</div>
        <a href={`#/beheer/${it.id}`} className='small'>Openen →</a>
      </div>))}
    </div>
  </div>);
}