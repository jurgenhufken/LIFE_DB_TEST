import React,{useEffect,useState} from 'react';
import Tabs from './components/Tabs';
import LijstTab from './components/LijstTab';
import BeheerTab from './components/BeheerTab';
import GraphTab from './components/GraphTab';
import ImportExportTab from './components/ImportExportTab';
import { enableDark, isDark } from './api';

export default function App(){
  const [active,setActive]=useState('list');
  const [dark,setDark]=useState(isDark());

  useEffect(()=>{ if(location.hash.startsWith('#/beheer/')) setActive('beheer') },[]);
  useEffect(()=>{ enableDark(dark) },[dark]);

  // keyboard: 'd' toggles dark mode
  useEffect(()=>{
    const onKey=(e:KeyboardEvent)=>{ if(e.key==='d' && !e.ctrlKey && !e.metaKey){ setDark(d=>!d); } };
    window.addEventListener('keydown',onKey); return ()=>window.removeEventListener('keydown',onKey);
  },[]);

  return (<div style={{fontFamily:'system-ui',padding:16}}>
    <div style={{display:'flex',alignItems:'center',justifyContent:'space-between'}}>
      <h1 style={{margin:0}}>LIFE_DB</h1>
      <button className='btn' onClick={()=>setDark(d=>!d)}>Dark: {dark?'aan':'uit'} (druk 'd')</button>
    </div>
    <Tabs tabs={[
      {key:'list',label:'Lijst'},
      {key:'beheer',label:'Beheer'},
      {key:'graph',label:'Graph'},
      {key:'impex',label:'Import/Export'},
    ]} active={active} onChange={setActive} />
    {active==='list'&&<LijstTab/>}
    {active==='beheer'&&<BeheerTab/>}
    {active==='graph'&&<GraphTab/>}
    {active==='impex'&&<ImportExportTab/>}
  </div>);
}