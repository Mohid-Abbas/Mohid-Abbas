"""Fetch everything the profile needs in ONE GraphQL call.

Token: PROFILE_TOKEN (optional personal access token, classic with `read:user`)
wins over the workflow's built-in GITHUB_TOKEN. The built-in token only sees
PUBLIC activity; a PAT is needed if your profile graph includes private work.
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request

REPO_FIELDS = """
  name description url stargazerCount forkCount isPrivate
  primaryLanguage { name color }
  repositoryTopics(first: 10) { nodes { topic { name } } }
"""

QUERY = """
query($login: String!) {
  user(login: $login) {
    login
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount contributionLevel weekday } }
      }
    }
    pinnedItems(first: 6, types: REPOSITORY) { nodes { ... on Repository { %(f)s } } }
    recent: repositories(first: 12, isFork: false, ownerAffiliations: OWNER,
                         privacy: PUBLIC, orderBy: {field: PUSHED_AT, direction: DESC}) {
      nodes { %(f)s }
    }
    langs: repositories(first: 100, isFork: false, ownerAffiliations: OWNER,
                        privacy: PUBLIC) {
      nodes {
        name
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name } }
        }
      }
    }
  }
}
""" % {"f": REPO_FIELDS}

LEVELS = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2,
          "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}


def _post(token: str, login: str) -> dict:
    body = json.dumps({"query": QUERY, "variables": {"login": login}}).encode()
    req = urllib.request.Request(
        "https://api.github.com/graphql", data=body,
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json",
                 "User-Agent": "profile-readme-generator"})
    last: Exception | None = None
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except (urllib.error.URLError, TimeoutError) as e:      # retry transient errors
            last = e
            time.sleep(2 ** attempt)
    raise RuntimeError(f"GitHub API unreachable: {last}")


def _repo(n: dict) -> dict:
    return {
        "name": n["name"], "description": n.get("description") or "", "url": n["url"],
        "stars": n["stargazerCount"], "forks": n["forkCount"],
        "language": (n.get("primaryLanguage") or {}).get("name"),
        "topics": [t["topic"]["name"] for t in n["repositoryTopics"]["nodes"]],
    }


def fetch(login: str) -> dict:
    token = os.environ.get("PROFILE_TOKEN") or os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        sys.exit("No token: set PROFILE_TOKEN or GITHUB_TOKEN (or run with --demo).")
    res = _post(token, login)
    if res.get("errors") or not (res.get("data") or {}).get("user"):
        # Fail loudly: the workflow stops and NOTHING is committed, so a bad
        # run can never overwrite a good profile with garbage.
        sys.exit(f"GraphQL error: {json.dumps(res.get('errors') or res)[:600]}")
    u = res["data"]["user"]
    cal = u["contributionsCollection"]["contributionCalendar"]
    weeks = [[{"date": d["date"], "count": d["contributionCount"],
               "level": LEVELS[d["contributionLevel"]], "weekday": d["weekday"]}
              for d in w["contributionDays"]] for w in cal["weeks"]]

    pinned = [_repo(n) for n in u["pinnedItems"]["nodes"] if n]
    recent = [_repo(n) for n in u["recent"]["nodes"] if n and n["name"].lower() != login.lower()]

    langs: dict[str, int] = {}
    for r in u["langs"]["nodes"]:
        for e in r["languages"]["edges"]:
            langs[e["node"]["name"]] = langs.get(e["node"]["name"], 0) + e["size"]

    return {"demo": False, "login": u["login"], "total": cal["totalContributions"],
            "weeks": weeks, "pinned": pinned, "recent": recent, "languages": langs}
