#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Desktop clipper application for LIFE_DB.

Adds always-on-top support, retrieves the active browser tab on macOS, and
normalizes URLs so the backend accepts them reliably.
"""

import json
import platform
import subprocess
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Dict, Tuple
from urllib.parse import urlsplit

import requests

APP_TITLE = "LIFE_DB Clipper (Python)"
DEFAULT_API = "http://localhost:8081"
TIMEOUT = 12.0


def headers(key: str = ""):
    header = {"Content-Type": "application/json"}
    if key:
        header["Authorization"] = f"Bearer {key}"
    return header


def api_get(api, path, key=""):
    response = requests.get(
        f"{api}{path}", headers=headers(key), timeout=TIMEOUT
    )
    response.raise_for_status()
    return response.json()


def api_post(api, path, body, key=""):
    response = requests.post(
        f"{api}{path}", headers=headers(key), data=json.dumps(body), timeout=TIMEOUT
    )
    response.raise_for_status()
    return response.json()


def normalize_url(url: str) -> str:
    """Ensure the URL has an HTTP(S) scheme if none is provided."""

    url = (url or "").strip()
    if not url:
        return ""

    scheme = urlsplit(url).scheme
    if scheme:
        # Preserve the original when the user explicitly typed a scheme. The caller will
        # still validate that only HTTP(S) URLs are accepted before submitting to the
        # backend.
        return url

    return "https://" + url


def mac_run_osascript(script: str) -> str:
    """Run a small AppleScript snippet and return its stdout or ``""``."""

    try:
        output = subprocess.check_output(["osascript", "-e", script], text=True)
    except Exception:  # noqa: BLE001 - best effort; caller will fall back
        return ""
    output = output.strip()
    if not output or output == "missing value":
        return ""
    return output


def _firefox_toolbar_script(process_name: str) -> str:
    return (
        "if application \"{0}\" is running then "
        "tell application \"System Events\" to "
        "tell process \"{0}\" to "
        "if exists (window 1) then "
        "value of attribute \"AXURL\" of first UI element of "
        "first group of first toolbar of window 1"
    ).format(process_name)


def mac_get_active_tab_url() -> str:
    """Return the URL of the active tab for popular macOS browsers."""

    if platform.system() != "Darwin":
        return ""

    browser_scripts: Dict[str, Tuple[str, ...]] = {
        # Chromium family
        "Google Chrome": (
            'tell application "Google Chrome" to if (count of windows) > 0 then get URL of active tab of front window',
        ),
        "Google Chrome Canary": (
            'tell application "Google Chrome Canary" to if (count of windows) > 0 then get URL of active tab of front window',
        ),
        "Chromium": (
            'tell application "Chromium" to if (count of windows) > 0 then get URL of active tab of front window',
        ),
        "Brave Browser": (
            'tell application "Brave Browser" to if (count of windows) > 0 then get URL of active tab of front window',
        ),
        "Brave Browser Beta": (
            'tell application "Brave Browser Beta" to if (count of windows) > 0 then get URL of active tab of front window',
        ),
        "Brave Browser Nightly": (
            'tell application "Brave Browser Nightly" to if (count of windows) > 0 then get URL of active tab of front window',
        ),
        "Microsoft Edge": (
            'tell application "Microsoft Edge" to if (count of windows) > 0 then get URL of active tab of front window',
        ),
        "Arc": (
            'tell application "Arc" to tell front window to tell active tab to get URL',
        ),
        # Safari family
        "Safari": (
            'tell application "Safari" to if (count of windows) > 0 then get URL of current tab of front window',
        ),
        "Safari Technology Preview": (
            'tell application "Safari Technology Preview" to if (count of windows) > 0 then get URL of current tab of front window',
        ),
        "Orion": (
            'tell application "Orion" to tell front window to tell active tab to get URL',
        ),
        # Firefox family (accessibility attribute)
        "Firefox": (_firefox_toolbar_script("Firefox"),),
        "Firefox Developer Edition": (
            _firefox_toolbar_script("Firefox Developer Edition"),
        ),
        "Firefox Nightly": (
            _firefox_toolbar_script("Firefox Nightly"),
        ),
        "Vivaldi": (
            'tell application "Vivaldi" to if (count of windows) > 0 then get URL of active tab of front window',
        ),
        "Opera": (
            'tell application "Opera" to if (count of windows) > 0 then get URL of active tab of front window',
        ),
    }

    frontmost = mac_run_osascript(
        'tell application "System Events" to get name of first process whose frontmost is true'
    )
    attempted: set[str] = set()

    if frontmost and frontmost in browser_scripts:
        for script in browser_scripts[frontmost]:
            attempted.add(script)
            url = mac_run_osascript(script)
            if url:
                return url

    # Fall back to trying all known browsers, skipping scripts we've already tried.
    for script_group in browser_scripts.values():
        for script in script_group:
            if script in attempted:
                continue
            url = mac_run_osascript(script)
            if url:
                return url

    return ""


class App(tk.Tk):
    """Tkinter-based frontend for clipping URLs into LIFE_DB."""

    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("640x260")
        self.minsize(560, 200)

        self.topmost = tk.BooleanVar(value=True)
        self.attributes("-topmost", True)

        self.api = tk.StringVar(value=DEFAULT_API)
        self.key = tk.StringVar(value="")
        self.url = tk.StringVar(value="")
        self.cat = tk.StringVar(value="")
        self.status = tk.StringVar(value="Gereed.")

        self.build()
        self.after(150, self.refresh_cats)

    def build(self):
        pad = 10
        frame = ttk.Frame(self, padding=pad)
        frame.pack(fill="both", expand=True)

        row0 = ttk.Frame(frame)
        row0.pack(fill="x", pady=(0, 6))
        ttk.Label(row0, text="API:").pack(side="left")
        ttk.Entry(row0, textvariable=self.api, width=36).pack(
            side="left", fill="x", expand=True, padx=(6, 6)
        )
        ttk.Label(row0, text="Token:").pack(side="left", padx=(6, 0))
        ttk.Entry(row0, textvariable=self.key, show="•", width=24).pack(side="left")
        ttk.Checkbutton(
            row0,
            text="Always on top",
            variable=self.topmost,
            command=lambda: self.attributes("-topmost", self.topmost.get()),
        ).pack(side="left", padx=(8, 0))

        row1 = ttk.Frame(frame)
        row1.pack(fill="x", pady=(0, 6))
        ttk.Button(row1, text="Plak URL", command=self.paste).pack(side="left")
        ttk.Button(row1, text="Huidige Tab", command=self.fill_from_active_tab).pack(
            side="left", padx=(6, 0)
        )
        ttk.Button(row1, text="Refresh", command=self.refresh_cats).pack(
            side="left", padx=(6, 0)
        )

        row2 = ttk.Frame(frame)
        row2.pack(fill="x", pady=(0, 6))
        ttk.Label(row2, text="URL *").pack(side="left")
        entry = ttk.Entry(row2, textvariable=self.url)
        entry.pack(side="left", fill="x", expand=True, padx=(6, 6))
        entry.bind("<Return>", lambda _event: self.on_clip())

        row3 = ttk.Frame(frame)
        row3.pack(fill="x", pady=(0, 6))
        ttk.Label(row3, text="Categorie").pack(side="left")
        self.combo = ttk.Combobox(row3, textvariable=self.cat, state="readonly")
        self.combo.pack(side="left", fill="x", expand=True, padx=(6, 6))
        ttk.Button(row3, text="+ nieuw", command=self.add_cat).pack(side="left")

        row4 = ttk.Frame(frame)
        row4.pack(fill="x", pady=(6, 6))
        ttk.Button(row4, text="Wissen", command=lambda: self.url.set("")).pack(
            side="left"
        )
        ttk.Button(row4, text="📌 Clip naar Database", command=self.on_clip).pack(
            side="right"
        )

        ttk.Label(frame, textvariable=self.status, anchor="w").pack(
            fill="x", pady=(6, 0)
        )

        # Shortcuts for quick clipping
        if platform.system() == "Darwin":
            self.bind_all("<Command-v>", lambda _event: self.paste())
            self.bind_all("<Command-Return>", lambda _event: self.on_clip())
        else:
            self.bind_all("<Control-v>", lambda _event: self.paste())
            self.bind_all("<Control-Return>", lambda _event: self.on_clip())

    def set_status(self, message):
        self.status.set(message)

    def paste(self):
        try:
            self.url.set(self.clipboard_get().strip())
            self.set_status("URL geplakt.")
        except Exception:  # noqa: BLE001 - clipboard errors are non-fatal
            self.set_status("Kon geen URL uit klembord lezen.")

    def fill_from_active_tab(self):
        url = mac_get_active_tab_url()
        if not url:
            try:
                url = self.clipboard_get().strip()
            except Exception:  # noqa: BLE001 - clipboard errors are non-fatal
                url = ""
        if url:
            self.url.set(url)
            self.set_status("Huidige tab opgehaald.")
        else:
            if platform.system() == "Darwin":
                self.set_status(
                    "Kon actieve tab niet lezen. Sta Automation/Accessibility toe of plak de URL (Cmd/Ctrl+V)."
                )
            else:
                self.set_status(
                    "Kon actieve tab niet lezen. Plak de URL aub (Cmd/Ctrl+V)."
                )

    def refresh_cats(self):
        try:
            categories = api_get(
                self.api.get().strip(), "/categories", self.key.get().strip()
            )
            items = categories.get("categories", [])
            if items:
                self.combo["values"] = items
            if items and not self.cat.get():
                self.cat.set(items[0])
            self.set_status("Categorieën bijgewerkt.")
        except Exception as exc:  # noqa: BLE001 - network errors bubbled up via status
            self.set_status(
                f"Kon categorieën niet laden: {exc} (controleer API en token)"
            )

    def add_cat(self):
        import tkinter.simpledialog as simpledialog

        name = simpledialog.askstring("Nieuwe categorie", "Naam categorie:")
        if not name:
            return
        try:
            api_post(
                self.api.get().strip(),
                "/categories",
                {"name": name.strip()},
                self.key.get().strip(),
            )
            self.refresh_cats()
            self.cat.set(name.strip())
            self.set_status(f"Categorie '{name}' toegevoegd.")
        except Exception as exc:  # noqa: BLE001 - show dialog with the error
            messagebox.showerror("Fout", f"Kon categorie niet toevoegen: {exc}")

    def on_clip(self):
        url = normalize_url(self.url.get())
        if not (url.startswith("http://") or url.startswith("https://")):
            messagebox.showwarning(
                "Ongeldige URL", "Geef een geldige http(s) URL op."
            )
            return
        try:
            result = api_post(
                self.api.get().strip(),
                "/capture",
                {"url": url, "category": self.cat.get().strip()},
                self.key.get().strip(),
            )
            if result.get("ok"):
                self.set_status(f"Opgeslagen, id={result.get('id')}")
                self.url.set("")
            else:
                self.set_status("Kon niet opslaan.")
        except Exception as exc:  # noqa: BLE001 - show dialog with the error
            messagebox.showerror(
                "Fout", f"Kon niet opslaan: {exc} (API/token controleren?)"
            )


if __name__ == "__main__":
    App().mainloop()
