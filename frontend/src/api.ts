export const API=(import.meta.env.VITE_API_BASE||'http://localhost:8081') as string;
const REQUIRE_TOKEN = (import.meta.env.VITE_REQUIRE_TOKEN||'false')==='true';
let TOKEN = localStorage.getItem('life_db_token') || '';
export function setToken(t:string){ TOKEN=t; localStorage.setItem('life_db_token', t||''); }
function headers(base:Record<string,string>={}):HeadersInit{ const h={...base}; if(REQUIRE_TOKEN && TOKEN){ h['Authorization']='Bearer '+TOKEN } return h; }
async function jfetch(url:string, init:any={}): Promise<any>{ const r=await fetch(url, {...init, headers: headers(init.headers||{})}); if(!r.ok) throw new Error(await r.text()); return r.json(); }

export async function listItems(p:any={}){const q=new URLSearchParams();Object.entries(p).forEach(([k,v]:any)=>{if(v!==undefined&&v!=='')q.set(k,String(v))});return jfetch(`${API}/items?${q}`)}
export async function getMeta(id:number){return jfetch(`${API}/items/${id}/meta`)}
export async function putTags(id:number,tags:string[]){return jfetch(`${API}/items/${id}/tags`,{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify({tags})})}
export async function listCategories(){return jfetch(`${API}/categories`)}
export async function addCategory(name:string){return jfetch(`${API}/categories`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name})})}
export async function getGraph(p:any={}){const q=new URLSearchParams();Object.entries(p).forEach(([k,v]:any)=>{if(v!==undefined&&v!=='')q.set(k,String(v))});return jfetch(`${API}/graph?${q}`)}
export async function importItemsJSON(data:any[]){return jfetch(`${API}/import`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)})}
export function exportItems(fmt:'json'|'ndjson'|'csv'='json'){window.open(`${API}/export?fmt=${fmt}`,'_blank')}
export async function health(){return jfetch(`${API}/healthz`)}
export async function renameCategory(oldName:string,newName:string){return jfetch(`${API}/admin/categories/rename`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({old:oldName,new:newName})})}
export async function mergeTags(src:string,dst:string){return jfetch(`${API}/admin/tags/merge`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({src,dst})})}

// Dark mode
export function enableDark(enabled:boolean){ document.documentElement.dataset.theme = enabled ? 'dark' : 'light'; localStorage.setItem('life_db_dark', enabled ? '1':'0'); }
export function isDark():boolean{ return localStorage.getItem('life_db_dark')==='1'; }
