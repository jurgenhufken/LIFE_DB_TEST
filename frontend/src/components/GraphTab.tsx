import React,{useEffect,useRef,useState} from 'react';
import {getGraph,listCategories} from '../api';
import { Network } from 'vis-network/standalone';

const groupColors: Record<string,string> = {
  item: '#4F46E5', domain:'#059669', category:'#DB2777', tag:'#F59E0B'
};

export default function GraphTab(){
  const [tag,setTag]=useState(''); const [domain,setDomain]=useState(''); const [category,setCategory]=useState(''); const [limit,setLimit]=useState(50);
  const [cats,setCats]=useState<string[]>([]);
  const containerRef = useRef<HTMLDivElement|null>(null);
  const [graph,setGraph]=useState<any>({nodes:[],edges:[]});

  useEffect(()=>{ listCategories().then(r=> setCats(r.categories||[])) },[]);
  const load=()=> getGraph({tag,domain,category,limit}).then(j=> setGraph(j));
  useEffect(()=>{ load() },[]);

  useEffect(()=>{
    if(!containerRef.current) return;
    const nodes = (graph.nodes||[]).map((n:any)=>({...n, color: groupColors[n.group] || undefined }));
    const network = new Network(containerRef.current, {nodes, edges:graph.edges||[]}, {
      physics:{stabilization:true},
      nodes:{shape:'dot', size:12, font:{color:'var(--fg)'}},
      edges:{arrows:{to:false}, smooth:true, color:{color:'#94a3b8'}}
    });
    return ()=>{ network.destroy(); };
  }, [graph]);

  return (<div>
    <div className='grid' style={{gridTemplateColumns:'160px 200px 200px 100px 100px',marginBottom:10}}>
      <input className='input' placeholder='Tag' value={tag} onChange={e=>setTag(e.target.value)}/>
      <input className='input' placeholder='Domein' value={domain} onChange={e=>setDomain(e.target.value)}/>
      <select className='input' value={category} onChange={e=>setCategory(e.target.value)}>
        <option value=''>Alle categorieën</option>{cats.map(c=><option key={c} value={c}>{c}</option>)}
      </select>
      <input className='input' type='number' min={5} max={200} value={limit} onChange={e=>setLimit(parseInt(e.target.value)||50)}/>
      <button className='btn' onClick={load}>Filter</button>
    </div>
    <div ref={containerRef} style={{height:480,border:'1px solid var(--border)',borderRadius:8}}/>
  </div>);
}