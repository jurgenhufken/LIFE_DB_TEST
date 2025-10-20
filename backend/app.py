
import os, json, asyncio
from typing import Optional, List, Iterable, Tuple
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode

import httpx
from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, Header, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, PlainTextResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool
from neo4j import GraphDatabase
from bs4 import BeautifulSoup

DATABASE_URL = os.environ.get("DATABASE_URL")
NEO4J_URI = os.environ.get("NEO4J_URI")
NEO4J_USER = os.environ.get("NEO4J_USER","neo4j")
NEO4J_PASS = os.environ.get("NEO4J_PASS","test123")
API_TOKEN = os.environ.get("API_TOKEN","")

engine = create_engine(DATABASE_URL, poolclass=NullPool, future=True)
neo4j_driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))

app = FastAPI(title="LIFE_DB API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# ---------- Auth helper ----------
def require_bearer(authorization: Optional[str] = Header(default=None)):
    if not API_TOKEN:
        return  # auth disabled
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(401, "missing bearer token")
    token = authorization.split(" ",1)[1].strip()
    if token != API_TOKEN:
        raise HTTPException(403, "invalid token")

# ---------- URL normalization ----------
DROP_QUERY_KEYS = {"utm_source","utm_medium","utm_campaign","utm_term","utm_content","utm_id","utm_name","gclid","fbclid","igshid","mc_cid","mc_eid","ref","ref_src","ref_url"}

def normalize_url(u: str) -> str:
    try:
        p = urlparse(u.strip())
        scheme = p.scheme.lower()
        netloc = (p.hostname or "").lower()
        if p.port and ((scheme=="http" and p.port!=80) or (scheme=="https" and p.port!=443)):
            netloc = f"{netloc}:{p.port}"
        # clean query
        q = [(k,v) for k,v in parse_qsl(p.query, keep_blank_values=True) if k not in DROP_QUERY_KEYS]
        q.sort()
        query = urlencode(q)
        # drop fragment
        frag = ""
        return urlunparse((scheme, netloc, p.path or "/", p.params, query, frag))
    except Exception:
        return u

# ---------- Models ----------
class CategoryBody(BaseModel): name: str
class TagsBody(BaseModel): tags: List[str]
class CaptureBody(BaseModel):
    url: str
    category: Optional[str] = ""

# ---------- Scraper ----------
async def fetch_url(url: str) -> str:
    headers = {"User-Agent": "LIFE_DB/1.0 (+https://localhost)"}
    async with httpx.AsyncClient(timeout=12.0, headers=headers, follow_redirects=True) as client:
        r = await client.get(url)
        r.raise_for_status()
        return r.text

def parse_meta(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    def gm(attr, val):
        el = soup.find("meta", attrs={attr: val})
        return el["content"].strip() if el and el.has_attr("content") else ""
    meta = {
        "og:title": gm("property","og:title"),
        "og:description": gm("property","og:description"),
        "og:image": gm("property","og:image"),
        "twitter:title": gm("name","twitter:title"),
        "twitter:description": gm("name","twitter:description"),
        "twitter:image": gm("name","twitter:image"),
        "article:published_time": gm("property","article:published_time") or gm("name","article:published_time"),
    }
    title = (soup.title.string.strip() if soup.title and soup.title.string else "")
    desc_tag = soup.find("meta", attrs={"name":"description"})
    desc = (desc_tag.get("content","").strip() if desc_tag else "")
    h1 = [h.get_text(strip=True) for h in soup.find_all("h1")][:20]
    h2 = [h.get_text(strip=True) for h in soup.find_all("h2")][:20]
    imgs = [img.get("src","") for img in soup.find_all("img")][:20]
    return {"meta": meta, "title": title, "description": desc, "headings": {"h1": h1, "h2": h2}, "images": imgs}

def ensure_category(conn, name: str):
    if not name: return
    conn.execute(text("INSERT INTO categories(name) VALUES(:n) ON CONFLICT (name) DO NOTHING"), {"n": name})

def push_neo4j(item_id: int, url: str, title: str, domain: str, category: str):
    cy = """
    MERGE (d:Domain {name:$domain})
    MERGE (i:Item {id:$id})
      SET i.title=$title, i.url=$url
    MERGE (i)-[:BELONGS_TO]->(d)
    WITH i
    MERGE (c:Category {name:$category})
    MERGE (i)-[:IN_CATEGORY]->(c)
    """
    with neo4j_driver.session() as s:
        s.run(cy, id=item_id, url=url, title=title or "", domain=domain or "", category=category or "")

# ---------- API ----------
@app.get("/healthz")
def healthz():
    with engine.begin() as conn:
        c_items = conn.execute(text("SELECT count(*) FROM items")).scalar() or 0
        c_tags = conn.execute(text("SELECT count(*) FROM tags")).scalar() or 0
        c_cats = conn.execute(text("SELECT count(*) FROM categories")).scalar() or 0
        last_created = conn.execute(text("SELECT max(created_at) FROM items")).scalar()
    return {"ok": True, "items": int(c_items), "tags": int(c_tags), "categories": int(c_cats), "last_item_created_at": str(last_created) if last_created else None}

@app.get("/categories")
def list_categories():
    with engine.begin() as conn:
        rows = conn.execute(text("SELECT name FROM categories ORDER BY name")).all()
    return {"categories": [r[0] for r in rows]}

@app.post("/categories")
def add_category(body: CategoryBody, _=Depends(require_bearer)):
    name = (body.name or "").strip()
    if not name: raise HTTPException(400, "name required")
    with engine.begin() as conn:
        ensure_category(conn, name)
    return {"ok": True, "name": name}

@app.post("/admin/categories/rename")
def rename_category(old: str = Body(..., embed=True), new: str = Body(..., embed=True), _=Depends(require_bearer)):
    old = (old or "").strip(); new = (new or "").strip()
    if not old or not new: raise HTTPException(400, "old/new required")
    with engine.begin() as conn:
        ensure_category(conn, new)
        conn.execute(text("UPDATE items SET category=:new WHERE category=:old"), {"old": old, "new": new})
        conn.execute(text("DELETE FROM categories WHERE name=:old"), {"old": old})
    return {"ok": True, "renamed": {"from": old, "to": new}}

@app.post("/admin/tags/merge")
def merge_tags(src: str = Body(..., embed=True), dst: str = Body(..., embed=True), _=Depends(require_bearer)):
    src = (src or "").strip(); dst = (dst or "").strip()
    if not src or not dst or src==dst: raise HTTPException(400, "invalid src/dst")
    with engine.begin() as conn:
        conn.execute(text("INSERT INTO tags(name) VALUES(:n) ON CONFLICT (name) DO NOTHING"), {"n": dst})
        dst_id = conn.execute(text("SELECT id FROM tags WHERE name=:n"), {"n": dst}).scalar()
        src_id = conn.execute(text("SELECT id FROM tags WHERE name=:n"), {"n": src}).scalar()
        if src_id and dst_id:
            conn.execute(text("UPDATE item_tags SET tag_id=:d WHERE tag_id=:s"), {"d": dst_id, "s": src_id})
            conn.execute(text("DELETE FROM tags WHERE id=:s"), {"s": src_id})
    return {"ok": True, "merged": {"from": src, "to": dst}}

class CaptureBody(BaseModel):
    url: str
    category: Optional[str] = ""

@app.post("/capture")
async def capture(body: CaptureBody, _=Depends(require_bearer)):
    url = body.url.strip()
    if not (url.startswith("http://") or url.startswith("https://")):
        raise HTTPException(400, "Invalid URL")
    url_n = normalize_url(url)
    html = await fetch_url(url)
    data = parse_meta(html)
    domain = urlparse(url_n).hostname or ""
    with engine.begin() as conn:
        ensure_category(conn, body.category or "")
        row = conn.execute(text("SELECT id FROM items WHERE url_norm=:un OR url=:u"), {"un": url_n, "u": url}).first()
        if row:
            item_id = int(row[0])
            conn.execute(text("""UPDATE items SET url=:u, url_norm=:un, title=:t, description=:d, domain=:dm, category=:c WHERE id=:id"""),
                         {"u": url, "un": url_n, "t": data.get("title",""), "d": data.get("description",""), "dm": domain, "c": body.category or "", "id": item_id})
        else:
            r = conn.execute(text("""INSERT INTO items(url,url_norm,title,description,domain,category) VALUES(:u,:un,:t,:d,:dm,:c) RETURNING id"""),
                             {"u": url, "un": url_n, "t": data.get("title",""), "d": data.get("description",""), "dm": domain, "c": body.category or ""})
            item_id = int(r.scalar())
        conn.execute(text("""INSERT INTO item_meta(item_id, meta_json) VALUES(:id,:m)
                             ON CONFLICT (item_id) DO UPDATE SET meta_json=EXCLUDED.meta_json"""),
                     {"id": item_id, "m": json.dumps(data)})
    push_neo4j(item_id, url, data.get("title",""), domain, body.category or "")
    return {"ok": True, "id": item_id}

@app.get("/items")
def list_items(q: Optional[str]=None, domain: Optional[str]=None, category: Optional[str]=None, limit: int=20, offset:int=0):
    base = "SELECT i.id,i.url,i.title,i.description,i.domain,i.created_at,i.category FROM items i"
    where = []; params = {}
    if domain: where.append("i.domain=:domain"); params["domain"]=domain
    if category: where.append("i.category=:cat"); params["cat"]=category
    if q:
        where.append("to_tsvector('simple', coalesce(title,'') || ' ' || coalesce(description,'') || ' ' || coalesce(url,'')) @@ plainto_tsquery('simple', :q)")
        params["q"]=q
    sql = base + (" WHERE " + " AND ".join(where) if where else "") + " ORDER BY i.created_at DESC LIMIT :lim OFFSET :off"
    params["lim"]=limit; params["off"]=offset
    with engine.begin() as conn:
        rows = conn.execute(text(sql), params).all()
    out = [{"id":r[0],"url":r[1],"title":r[2],"description":r[3],"domain":r[4],"created_at":str(r[5]),"category":r[6]} for r in rows]
    return {"items": out}

@app.get("/items/{item_id}/meta")
def item_meta(item_id: int):
    with engine.begin() as conn:
        r = conn.execute(text("""SELECT i.url,i.url_norm,i.title,i.domain,i.category,i.created_at, COALESCE(m.meta_json,'{}')
                                 FROM items i LEFT JOIN item_meta m ON m.item_id=i.id WHERE i.id=:id"""), {"id": item_id}).first()
    if not r: raise HTTPException(404, "Not found")
    url, url_norm, title, domain, category, created, meta_json = r
    meta = json.loads(meta_json or "{}")
    summary = {"id": item_id,"url": url,"url_norm": url_norm,"title": title,"domain": domain,"created_at": str(created),"category": category,
               "published": meta.get("meta",{}).get("article:published_time",""),
               "thumb": meta.get("meta",{}).get("og:image",""),
               "og_title": meta.get("meta",{}).get("og:title",""),
               "og_description": meta.get("meta",{}).get("og:description",""),
               "headings": meta.get("headings",{}), "images": meta.get("images",[])}
    return {"summary": summary, "raw": meta}

@app.put("/items/{item_id}/tags")
def put_tags(item_id: int, body: TagsBody, _=Depends(require_bearer)):
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM item_tags WHERE item_id=:i"), {"i": item_id})
        for name in body.tags:
            conn.execute(text("INSERT INTO tags(name) VALUES(:n) ON CONFLICT (name) DO NOTHING"), {"n": name})
            tid = conn.execute(text("SELECT id FROM tags WHERE name=:n"), {"n": name}).scalar()
            if tid:
                conn.execute(text("INSERT INTO item_tags(item_id, tag_id) VALUES(:i,:t) ON CONFLICT DO NOTHING"), {"i": item_id, "t": tid})
    return {"ok": True, "tags": body.tags}

# --------- Import / Export ---------
@app.post("/import")
async def import_items(file: Optional[UploadFile]=File(default=None), body: Optional[List[dict]]=None, _=Depends(require_bearer)):
    count = 0
    rows: Iterable[dict] = []
    if file:
        raw = (await file.read()).decode("utf-8", errors="ignore")
        if raw.lstrip().startswith("{") or raw.lstrip().startswith("["):
            data = json.loads(raw)
            if isinstance(data, dict): data = [data]
            rows = data
        else:
            rows = (json.loads(line) for line in raw.splitlines() if line.strip())
    elif body:
        rows = body
    else:
        raise HTTPException(400, "No data")

    with engine.begin() as conn:
        for obj in rows:
            url = (obj.get("url") or "").strip()
            if not url: continue
            url_n = normalize_url(url)
            category = (obj.get("category") or "").strip()
            ensure_category(conn, category)
            r = conn.execute(text("SELECT id FROM items WHERE url_norm=:un OR url=:u"), {"un": url_n, "u": url}).first()
            if r: continue
            conn.execute(text("INSERT INTO items(url,url_norm,title,description,domain,category) VALUES(:u,:un,'','',:dm,:c)"),
                         {"u": url, "un": url_n, "dm": (urlparse(url_n).hostname or ""), "c": category})
            count += 1
    return {"ok": True, "imported": count}

@app.get("/export")
def export_items(fmt: Optional[str] = "json", limit: int=1000):
    with engine.begin() as conn:
        rows = conn.execute(text("SELECT id,url,url_norm,title,description,domain,created_at,category FROM items ORDER BY id DESC LIMIT :l"), {"l": limit}).all()
    def gen_json():
        yield "["
        first = True
        for r in rows:
            rec = {"id":r[0],"url":r[1],"url_norm":r[2],"title":r[3],"description":r[4],"domain":r[5],"created_at":str(r[6]),"category":r[7]}
            if not first: yield ","
            yield json.dumps(rec)
            first = False
        yield "]"
    def gen_ndjson():
        for r in rows:
            rec = {"id":r[0],"url":r[1],"url_norm":r[2],"title":r[3],"description":r[4],"domain":r[5],"created_at":str(r[6]),"category":r[7]}
            yield json.dumps(rec)+"\n"
    def gen_csv():
        yield "id,url,url_norm,title,description,domain,created_at,category\n"
        import csv, io
        sio = io.StringIO()
        w = csv.writer(sio)
        for r in rows:
            w.writerow([r[0], r[1], r[2], r[3] or "", r[4] or "", r[5] or "", str(r[6]), r[7] or ""])
            yield sio.getvalue(); sio.seek(0); sio.truncate(0)
    if fmt == "ndjson":
        return StreamingResponse(gen_ndjson(), media_type="application/x-ndjson")
    if fmt == "csv":
        return StreamingResponse(gen_csv(), media_type="text/csv")
    return StreamingResponse(gen_json(), media_type="application/json")

# --------- Graph ---------
@app.get("/graph")
def graph(tag: Optional[str]=None, domain: Optional[str]=None, category: Optional[str]=None, limit: int=50):
    wh = []
    cy = ["MATCH (i:Item)-[:BELONGS_TO]->(d:Domain)","OPTIONAL MATCH (i)-[:IN_CATEGORY]->(c:Category)"]
    if tag: cy.append("MATCH (i)-[:HAS_TAG]->(t:Tag)") or wh.append("t.name = $tag")
    if domain: wh.append("d.name = $domain")
    if category: wh.append("c.name = $category")
    if wh: cy.append("WHERE " + " AND ".join(wh))
    cy.append("RETURN i.id AS id, i.title AS title, d.name AS domain, c.name AS category LIMIT $limit")
    with neo4j_driver.session() as s:
        rows = s.run("\n".join(cy), tag=tag, domain=domain, category=category, limit=limit).data()
    nodes, edges, seen = [], [], set()
    for r in rows:
        iid=r["id"]; title=r["title"] or f"Item {iid}"; dom=r["domain"] or ""; cat=r["category"] or ""
        nodes.append({"id": f"item:{iid}", "label": title, "group": "item"})
        if ("domain", dom) not in seen:
            nodes.append({"id": f"domain:{dom}", "label": dom, "group": "domain"}); seen.add(("domain", dom))
        edges.append({"from": f"item:{iid}", "to": f"domain:{dom}", "label": "domain"})
        if cat:
            if ("cat", cat) not in seen:
                nodes.append({"id": f"cat:{cat}", "label": cat, "group": "category"}); seen.add(("cat", cat))
            edges.append({"from": f"item:{iid}", "to": f"cat:{cat}", "label": "category"})
    return {"nodes": nodes, "edges": edges}
