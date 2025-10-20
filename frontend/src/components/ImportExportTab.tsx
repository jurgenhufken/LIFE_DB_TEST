import React,{useEffect,useState} from 'react';
import { importItemsJSON, exportItems, setToken, health, renameCategory, mergeTags } from '../api';

export default function ImportExportTab(){
  const [text,setText]=useState('');
  const [fmt,setFmt]=useState<'json'|'ndjson'>('json');
  const [token,setTok]=useState(localStorage.getItem('life_db_token')||'');
  const [stats,setStats]=useState<any>({});

  useEffect(()=>{ health().then(setStats).catch(()=>{}) },[]);

  const onImport = async()=>{
    try{
      let data:any[]=[];
      if(fmt==='json'){
        const parsed = JSON.parse(text);
        data = Array.isArray(parsed) ? parsed : [parsed];
      }else{
        data = text.split('\n').map(l=>l.trim()).filter(Boolean).map(l=>JSON.parse(l));
      }
      const r=await importItemsJSON(data);
      alert(`Imported ${r.imported} records`);
    }catch(e:any){ alert('Import error: '+ e?.message); }
  };

  const doRename = async()=>{
    const oldName = prompt('Oude categorie:');
    if(!oldName) return;
    const newName = prompt('Nieuwe categorie:');
    if(!newName) return;
    await renameCategory(oldName,newName);
    alert('Categorie hernoemd.');
  };

  const doMergeTags = async()=>{
    const src = prompt('Tag om samen te voegen (bron):');
    if(!src) return;
    const dst = prompt('Doel-tag:');
    if(!dst) return;
    await mergeTags(src,dst);
    alert('Tags samengevoegd.');
  };

  return (<div className='grid' style={{gridTemplateColumns:'1fr'}}>
    <div className='card'>
      <div style={{display:'flex',gap:8,alignItems:'center',marginBottom:8}}>
        <label>API-token:</label>
        <input className='input' value={token} onChange={e=>{setTok(e.target.value); setToken(e.target.value);}} placeholder="Bearer token"/>
        <span className='small'>Items: {stats.items??'—'} • Tags: {stats.tags??'—'} • Categorieën: {stats.categories??'—'}</span>
      </div>
      <div style={{display:'flex',gap:8,alignItems:'center',marginBottom:8}}>
        <select className='input' value={fmt} onChange={e=>setFmt(e.target.value as any)}>
          <option value="json">JSON</option>
          <option value="ndjson">NDJSON</option>
        </select>
        <button className='btn' onClick={()=>exportItems('json')}>Export JSON</button>
        <button className='btn' onClick={()=>exportItems('ndjson')}>Export NDJSON</button>
        <button className='btn' onClick={()=>exportItems('csv')}>Export CSV</button>
      </div>
      <textarea className='input' placeholder={fmt==='json'?'[{"url":"..."}, ...]':'{"url":"..."}\n{"url":"..."}'} value={text} onChange={e=>setText(e.target.value)} rows={14} style={{width:'100%'}}/>
      <div><button className='btn primary' onClick={onImport} style={{marginTop:8}}>Importeren</button></div>
    </div>
    <div className='card'>
      <h3>Admin (simpel)</h3>
      <div style={{display:'flex',gap:8}}>
        <button className='btn' onClick={doRename}>Categorie hernoemen</button>
        <button className='btn' onClick={doMergeTags}>Tags samenvoegen</button>
      </div>
      <div className='small' style={{marginTop:8}}>Let op: bewerkingen vereisen een geldige Bearer token.</div>
    </div>
  </div>);
}