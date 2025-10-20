#!/usr/bin/env python3
"""Simple LIFE_DB Clipper - werkt zonder Tkinter issues"""
import json
import requests

API_BASE = "http://localhost:8081"
API_TOKEN = ""  # Optioneel: "devtoken123"

def get_categories():
    """Haal alle categorieën op"""
    headers = {"Content-Type": "application/json"}
    if API_TOKEN:
        headers["Authorization"] = f"Bearer {API_TOKEN}"
    
    try:
        r = requests.get(f"{API_BASE}/categories", headers=headers, timeout=10)
        r.raise_for_status()
        return r.json().get("categories", [])
    except Exception as e:
        print(f"❌ Fout bij ophalen categorieën: {e}")
        return []

def add_category(name):
    """Voeg nieuwe categorie toe"""
    headers = {"Content-Type": "application/json"}
    if API_TOKEN:
        headers["Authorization"] = f"Bearer {API_TOKEN}"
    
    try:
        r = requests.post(
            f"{API_BASE}/categories",
            headers=headers,
            json={"name": name},
            timeout=10
        )
        r.raise_for_status()
        print(f"✅ Categorie '{name}' toegevoegd")
        return True
    except Exception as e:
        print(f"❌ Fout bij toevoegen categorie: {e}")
        return False

def clip_url(url, category="", tags=None):
    """Clip een URL naar de database"""
    headers = {"Content-Type": "application/json"}
    if API_TOKEN:
        headers["Authorization"] = f"Bearer {API_TOKEN}"
    
    payload = {
        "url": url,
        "category": category,
        "tags": tags or []
    }
    
    try:
        r = requests.post(
            f"{API_BASE}/capture",
            headers=headers,
            json=payload,
            timeout=10
        )
        r.raise_for_status()
        result = r.json()
        print(f"✅ URL geclipped! ID: {result.get('id')}")
        return True
    except Exception as e:
        print(f"❌ Fout bij clippen: {e}")
        return False

def main():
    """Interactieve clipper"""
    print("=" * 60)
    print("LIFE_DB Simple Clipper")
    print("=" * 60)
    print()
    
    while True:
        print("\nOpties:")
        print("1) Toon categorieën")
        print("2) Voeg categorie toe")
        print("3) Clip URL")
        print("4) Quit")
        print()
        
        choice = input("Kies (1-4): ").strip()
        
        if choice == "1":
            print("\n📁 Categorieën:")
            cats = get_categories()
            if cats:
                for i, cat in enumerate(cats, 1):
                    print(f"  {i}. {cat['name']} (ID: {cat['id']})")
            else:
                print("  (geen categorieën)")
        
        elif choice == "2":
            name = input("\nNieuwe categorie naam: ").strip()
            if name:
                add_category(name)
        
        elif choice == "3":
            url = input("\nURL: ").strip()
            if not url:
                print("❌ URL is verplicht")
                continue
            
            cats = get_categories()
            if cats:
                print("\nBeschikbare categorieën:")
                for i, cat in enumerate(cats, 1):
                    print(f"  {i}. {cat['name']}")
                cat_choice = input("\nKies categorie nummer (of Enter voor geen): ").strip()
                category = ""
                if cat_choice.isdigit() and 1 <= int(cat_choice) <= len(cats):
                    category = cats[int(cat_choice) - 1]["name"]
            else:
                category = ""
            
            tags_input = input("Tags (komma gescheiden, optioneel): ").strip()
            tags = [t.strip() for t in tags_input.split(",") if t.strip()] if tags_input else []
            
            clip_url(url, category, tags)
        
        elif choice == "4":
            print("\n👋 Tot ziens!")
            break
        
        else:
            print("❌ Ongeldige keuze")

if __name__ == "__main__":
    main()
