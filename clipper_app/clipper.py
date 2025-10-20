#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, tkinter as tk
from tkinter import ttk, messagebox
import requests

APP_TITLE = "LIFE_DB Clipper (Python)"
DEFAULT_API = "http://localhost:8081"
TIMEOUT = 12.0

def headers(key:str=""):
    h={"Content-Type":"application/json"}
    if key: h["Authorization"]=f"Bearer {key}"
    return h

def api_get(api, path, key=""):
    r=requests.get(f"{api}{path}", headers=headers(key), timeout=TIMEOUT); r.raise_for_status(); return r.json()
def api_post(api, path, body, key=""):
    r=requests.post(f"{api}{path}", headers=headers(key), data=json.dumps(body), timeout=TIMEOUT); r.raise_for_status(); return r.json()

class App(tk.Tk):
    def __init__(self):
        super().__init__(); self.title(APP_TITLE); self.geometry("620x240"); self.minsize(540,200)
        self.api=tk.StringVar(value=DEFAULT_API); self.key=tk.StringVar(value=""); self.url=tk.StringVar(value=""); self.cat=tk.StringVar(value=""); self.status=tk.StringVar(value="Gereed.")
        self.build(); self.after(100, self.refresh_cats)

    def build(self):
        pad=10; frm=ttk.Frame(self,padding=pad); frm.pack(fill='both',expand=True)
        r1=ttk.Frame(frm); r1.pack(fill='x',pady=(0,6))
        ttk.Label(r1,text='API:').pack(side='left'); ttk.Entry(r1,textvariable=self.api).pack(side='left',fill='x',expand=True,padx=(6,6))
        ttk.Label(r1,text='Token:').pack(side='left',padx=(6,0)); 
        token_entry=ttk.Entry(r1,textvariable=self.key,show='•',width=20); token_entry.pack(side='left')
        r2=ttk.Frame(frm); r2.pack(fill='x',pady=(0,6))
        ttk.Label(r2,text='URL:').pack(side='left'); ttk.Entry(r2,textvariable=self.url).pack(side='left',fill='x',expand=True,padx=(6,6))
        ttk.Button(r2,text='Plakken',command=self.paste).pack(side='left')
        r3=ttk.Frame(frm); r3.pack(fill='x',pady=(0,6))
        ttk.Label(r3,text='Categorie:').pack(side='left'); self.combo=ttk.Combobox(r3,textvariable=self.cat,state='readonly'); self.combo.pack(side='left',fill='x',expand=True,padx=(6,6))
        ttk.Button(r3,text='+ nieuw',command=self.add_cat).pack(side='left')
        r4=ttk.Frame(frm); r4.pack(fill='x',pady=(6,6))
        ttk.Button(r4,text='Clip → Backend',command=self.on_clip).pack(side='left')
        ttk.Label(frm,textvariable=self.status,anchor='w').pack(fill='x',pady=(6,0))

    def set_status(self,msg): self.status.set(msg)
    def paste(self):
        try: self.url.set(self.clipboard_get().strip()); self.set_status('URL geplakt.')
        except Exception: pass

    def refresh_cats(self):
        try:
            j=api_get(self.api.get().strip(),"/categories",self.key.get().strip())
            cats=j.get("categories",[])
            if cats: self.combo['values']=cats; 
            if cats and not self.cat.get(): self.cat.set(cats[0])
            self.set_status('Categorieën bijgewerkt.')
        except Exception as e:
            self.set_status(f'Kon categorieën niet laden: {e} (controleer token?)')

    def add_cat(self):
        import tkinter.simpledialog as sd
        name=sd.askstring('Nieuwe categorie','Naam categorie:')
        if not name: return
        try:
            api_post(self.api.get().strip(),"/categories",{"name":name.strip()},self.key.get().strip())
            self.refresh_cats(); self.cat.set(name.strip()); self.set_status(f"Categorie '{name}' toegevoegd.")
        except Exception as e:
            messagebox.showerror('Fout', f'Kon categorie niet toevoegen: {e}')

    def on_clip(self):
        u=self.url.get().strip()
        if not (u.startswith('http://') or u.startswith('https://')):
            messagebox.showwarning('Ongeldige URL','Geef een geldige http(s) URL op.'); return
        try:
            j=api_post(self.api.get().strip(),"/capture",{"url":u,"category":self.cat.get().strip()},self.key.get().strip())
            if j.get('ok'): self.set_status(f"Opgeslagen, id={j.get('id')}"); self.url.set('')
            else: self.set_status('Kon niet opslaan.')
        except Exception as e:
            messagebox.showerror('Fout', f'Kon niet opslaan: {e} (controleer token?)')

if __name__=='__main__':
    App().mainloop()
