"""Fetch GitHub activity into data/stats.json. Uses GITHUB_TOKEN if set (needed for contributions)."""
import json, os, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
USER = json.loads((ROOT / "data/profile.json").read_text())["user"]
TOKEN = os.environ.get("GITHUB_TOKEN")


def req(url, data=None):
    r = urllib.request.Request(url, data=data)
    r.add_header("User-Agent", "profile-build")
    if TOKEN:
        r.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(r, timeout=30) as f:
        return json.load(f)


out = json.loads((ROOT / "data/stats.json").read_text()) if (ROOT / "data/stats.json").exists() else {}
repos = req(f"https://api.github.com/users/{USER}/repos?per_page=100&type=owner")
repos = [r for r in repos if not r["fork"]]
langs = {}
for r in repos:
    if r["language"]:
        langs[r["language"]] = langs.get(r["language"], 0) + 1
out["repos"] = len(repos)
out["languages"] = sorted(langs.items(), key=lambda kv: -kv[1])[:5]
if TOKEN:
    q = '{user(login:"%s"){contributionsCollection{contributionCalendar{totalContributions}}}}' % USER
    d = req("https://api.github.com/graphql", json.dumps({"query": q}).encode())
    out["contributions"] = d["data"]["user"]["contributionsCollection"]["contributionCalendar"]["totalContributions"]
(ROOT / "data/stats.json").write_text(json.dumps(out, indent=2) + "\n")
print(out)
