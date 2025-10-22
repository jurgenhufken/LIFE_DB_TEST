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
  
  // Auto-refresh every 5 seconds with visual indicator
  const[refreshing,setRefreshing]=useState(false);
  useEffect(()=>{
    const interval = setInterval(async ()=>{
      setRefreshing(true);
      await load();
      setRefreshing(false);
    }, 5000);
    return ()=>clearInterval(interval);
  },[q,category,domain]);

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
      <button className='btn' onClick={load} style={{opacity:refreshing?0.5:1}}>
        {refreshing ? '🔄 Refreshing...' : 'Filter'}
      </button>
      <input className='input' placeholder='API-token (Bearer)' value={token} onChange={e=>{setTok(e.target.value); setToken(e.target.value);}}/>
    </div>
    <div style={{marginTop:10}}>
      {items.map(it=>(<div key={it.id} className='card' style={{display:'flex',gap:12,alignItems:'start',marginBottom:10}}>
        {it.og_image ? (
          <img 
            src={it.og_image} 
            alt={it.title} 
            style={{width:120,height:80,objectFit:'cover',borderRadius:6,flexShrink:0}}
            onError={(e)=>{
              (e.target as HTMLImageElement).style.display='none';
              (e.target as HTMLImageElement).nextElementSibling?.setAttribute('style', 'display:flex');
            }}
          />
        ) : null}
        <div style={{width:120,height:80,borderRadius:6,flexShrink:0,background:'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',display:it.og_image ? 'none' : 'flex',alignItems:'center',justifyContent:'center',color:'white',fontSize:11,textAlign:'center',padding:8}}>
          {it.domain?.split('.')[0]?.toUpperCase() || '📄'}
        </div>
        <div style={{flex:1,minWidth:0}}>
          <div style={{fontWeight:700}}>{it.title||'(zonder titel)'}</div>
          <div className='small'>{it.domain} • {new Date(it.created_at*1000).toLocaleString()}</div>
          {it.description && <div style={{fontSize:13,marginTop:6,overflow:'hidden',textOverflow:'ellipsis',whiteSpace:'nowrap'}}>{it.description}</div>}
          <a href={`#/beheer/${it.id}`} className='small' style={{marginTop:4,display:'inline-block'}}>Openen →</a>
        </div>
      </div>))}
    </div>
  </div>);
}