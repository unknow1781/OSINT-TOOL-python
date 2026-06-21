#!/usr/bin/env python3-python
"""
OSINT TOOLKIT BY 1781 v1.0 - WORKING
Complete OSINT toolkit with 100+ sites
BEFORE START SEE text.txt
"""

import os
import sys
import json
import csv
import re
import time
import socket
import ssl
import hashlib
import datetime
import argparse
import asyncio
import logging
from urllib.parse import urlparse, quote_plus
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor

def install_missing_modules():
    missing = []
    try:
        import requests
    except ImportError:
        missing.append("requests")
    
    try:
        import whois
    except ImportError:
        missing.append("python-whois")
    
    try:
        import dns.resolver
    except ImportError:
        missing.append("dnspython")
    
    try:
        from PIL import Image
    except ImportError:
        missing.append("Pillow")
    
    try:
        import yaml
    except ImportError:
        missing.append("pyyaml")
    
    try:
        import aiohttp
    except ImportError:
        missing.append("aiohttp")
    
    if missing:
        print("[!] Missing required modules. Installing...")
        import subprocess
        for module in missing:
            subprocess.check_call([sys.executable, "-m", "pip", "install", module])
        print("[✓] All modules installed. Please restart the script.")
        sys.exit(0)

install_missing_modules()

import requests
import whois
import dns.resolver
import yaml
import aiohttp
from PIL import Image
from PIL.ExifTags import TAGS

# ============ LOGGING ============
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============ CONFIG ============
CONFIG_FILE = "osint_config.yaml"

DEFAULT_CONFIG = {
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0",
    "timeout": 10,
    "max_threads": 20,
    "output_dir": "output"
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return yaml.safe_load(f)
    else:
        with open(CONFIG_FILE, 'w') as f:
            yaml.dump(DEFAULT_CONFIG, f)
        return DEFAULT_CONFIG

# ============ DATA CLASS ============
@dataclass
class UsernameResult:
    site: str
    url: str
    exists: bool
    status_code: int
    error: str = ""

# ============ USERNAME SEARCH - 100+ SITES ============
class UsernameSearcher:
    def __init__(self, config):
        self.config = config
        self.sites = self._load_sites()
    
    def _load_sites(self):
        sites = {}
        base = "https://"
        
        sites.update({
            "github": base + "github.com/{}",
            "reddit": base + "reddit.com/user/{}",
            "tiktok": base + "tiktok.com/@{}",
            "twitter": base + "twitter.com/{}",
            "instagram": base + "instagram.com/{}/",
            "facebook": base + "facebook.com/{}",
            "youtube": base + "youtube.com/@{}",
            "twitch": base + "twitch.tv/{}",
            "discord": base + "discord.com/users/{}",
            "spotify": base + "open.spotify.com/user/{}",
            "pinterest": base + "pinterest.com/{}/",
            "tumblr": base + "{}.tumblr.com",
            "medium": base + "medium.com/@{}",
            "patreon": base + "patreon.com/{}",
            "vk": base + "vk.com/{}",
            "steam": base + "steamcommunity.com/id/{}",
            "xbox": base + "account.xbox.com/en-us/Profile?Gamertag={}",
            "psn": base + "psnprofiles.com/{}",
            "pastebin": base + "pastebin.com/u/{}",
            "hackernews": base + "news.ycombinator.com/user?id={}",
            "devto": base + "dev.to/{}",
            "sourceforge": base + "sourceforge.net/u/{}/profile/",
            "bitbucket": base + "bitbucket.org/{}/",
            "gitlab": base + "gitlab.com/{}",
            "keybase": base + "keybase.io/{}",
            "telegram": base + "t.me/{}",
            "snapchat": base + "snapchat.com/add/{}",
            "linkedin": base + "linkedin.com/in/{}",
            "vimeo": base + "vimeo.com/{}",
            "dribbble": base + "dribbble.com/{}",
            "behance": base + "behance.net/{}",
            "flickr": base + "flickr.com/people/{}/",
            "500px": base + "500px.com/p/{}",
            "soundcloud": base + "soundcloud.com/{}",
            "mixcloud": base + "mixcloud.com/{}/",
            "bandcamp": base + "bandcamp.com/{}",
            "replit": base + "replit.com/@{}",
            "codepen": base + "codepen.io/{}",
            "jsfiddle": base + "jsfiddle.net/user/{}",
            "hackthebox": base + "hackthebox.com/home/users/profile/{}",
            "tryhackme": base + "tryhackme.com/p/{}",
            "bugcrowd": base + "bugcrowd.com/{}",
            "hackerone": base + "hackerone.com/{}",
            "intigriti": base + "app.intigriti.com/researchers/{}",
            "producthunt": base + "producthunt.com/@{}",
            "indiehackers": base + "indiehackers.com/{}",
            "imgur": base + "imgur.com/user/{}",
            "giphy": base + "giphy.com/{}",
            "tenor": base + "tenor.com/users/{}",
            "vsco": base + "vsco.co/{}/gallery",
            "ello": base + "ello.co/{}",
            "mastodon": base + "mastodon.social/@{}",
            "bluesky": base + "bsky.app/profile/{}",
            "threads": base + "threads.net/@{}",
            "lemmy": base + "lemmy.world/u/{}",
            "kbin": base + "kbin.social/u/{}",
            "matrix": base + "matrix.to/#/@{}:matrix.org",
            "gitee": base + "gitee.com/{}",
            "codeberg": base + "codeberg.org/{}",
            "sourcehut": base + "sr.ht/~{}/",
            "launchpad": base + "launchpad.net/~{}",
            "openhub": base + "openhub.net/accounts/{}",
            "crates": base + "crates.io/users/{}",
            "npm": base + "npmjs.com/~{}",
            "pypi": base + "pypi.org/user/{}/",
            "rubygems": base + "rubygems.org/profiles/{}",
            "packagist": base + "packagist.org/users/{}",
            "docker": base + "hub.docker.com/u/{}",
            "quay": base + "quay.io/user/{}",
            "circleci": base + "circleci.com/gh/{}",
            "travis": base + "travis-ci.com/{}",
            "jenkins": base + "ci.jenkins.io/user/{}",
            "gitpod": base + "gitpod.io/@{}",
            "codesandbox": base + "codesandbox.io/u/{}",
            "stackblitz": base + "stackblitz.com/@{}",
            "glitch": base + "glitch.com/@{}",
            "observable": base + "observablehq.com/@{}",
            "nbviewer": base + "nbviewer.org/github/{}",
            "colab": base + "colab.research.google.com/github/{}",
            "kaggle": base + "kaggle.com/{}",
            "gogs": base + "gogs.io/{}",
            "gitea": base + "gitea.com/{}",
            "archive": base + "archive.org/details/@{}",
            "openlibrary": base + "openlibrary.org/people/{}",
            "goodreads": base + "goodreads.com/user/show/{}",
            "anilist": base + "anilist.co/user/{}/",
            "myanimelist": base + "myanimelist.net/profile/{}",
            "letterboxd": base + "letterboxd.com/{}/",
            "trakt": base + "trakt.tv/users/{}",
            "hubski": base + "hubski.com/user?id={}",
            "tildes": base + "tildes.net/user/{}",
            "saidit": base + "saidit.net/u/{}",
            "fark": base + "fark.com/users/{}",
            "digg": base + "digg.com/u/{}",
            "slashdot": base + "slashdot.org/~{}",
            "substack": base + "substack.com/@{}",
            "bitchute": base + "bitchute.com/channel/{}/",
            "odysee": base + "odysee.com/@{}",
            "lbry": base + "lbry.tv/@{}",
            "rumble": base + "rumble.com/user/{}",
            "periscope": base + "periscope.tv/{}",
            "mewe": base + "mewe.com/i/{}",
            "parler": base + "parler.com/profile/{}/",
            "truthsocial": base + "truthsocial.com/@{}",
            "gettr": base + "gettr.com/user/{}",
            "triller": base + "triller.co/@{}",
            "anchor": base + "anchor.fm/{}",
            "deezer": base + "deezer.com/us/user/{}",
            "tidal": base + "tidal.com/user/{}",
            "qobuz": base + "qobuz.com/us-en/profile/{}",
            "codewars": base + "codewars.com/users/{}",
            "codingame": base + "codingame.com/profile/{}",
            "hackerrank": base + "hackerrank.com/{}",
            "leetcode": base + "leetcode.com/{}/",
            "codeforces": base + "codeforces.com/profile/{}",
            "topcoder": base + "topcoder.com/members/{}/",
            "atcoder": base + "atcoder.jp/users/{}",
            "codechef": base + "codechef.com/users/{}",
            "coursera": base + "coursera.org/learner/{}",
            "edx": base + "edx.org/learner/{}",
            "udemy": base + "udemy.com/user/{}/",
            "udacity": base + "udacity.com/user/{}",
            "pluralsight": base + "pluralsight.com/profile/{}",
            "skillshare": base + "skillshare.com/profile/{}",
            "brilliant": base + "brilliant.org/profiles/{}/",
            "datacamp": base + "datacamp.com/profile/{}",
            "codecademy": base + "codecademy.com/profiles/{}",
            "freecodecamp": base + "freecodecamp.org/{}",
            "theodinproject": base + "theodinproject.com/users/{}",
            "cssbattle": base + "cssbattle.dev/players/{}",
            "frontendmentor": base + "frontendmentor.io/profile/{}",
            "hashnode": base + "hashnode.dev/{}",
            "hackernoon": base + "hackernoon.com/@{}",
            "ghost": base + "{}.ghost.io",
            "blogger": base + "{}.blogspot.com",
            "livejournal": base + "{}.livejournal.com",
            "xanga": base + "{}.xanga.com",
            "typepad": base + "{}.typepad.com",
            "weebly": base + "{}.weebly.com",
            "wix": base + "{}.wixsite.com/mysite",
            "squarespace": base + "{}.squarespace.com",
            "shopify": base + "{}.myshopify.com",
            "etsy": base + "etsy.com/people/{}",
            "ebay": base + "ebay.com/usr/{}",
            "aliexpress": base + "aliexpress.com/store/{}",
            "wish": base + "wish.com/people/{}",
            "doordash": base + "doordash.com/user/{}",
            "grubhub": base + "grubhub.com/user/{}",
            "deliveroo": base + "deliveroo.co.uk/user/{}",
            "justeat": base + "just-eat.com/user/{}",
            "ubereats": base + "ubereats.com/user/{}",
            "postmates": base + "postmates.com/user/{}",
            "instacart": base + "instacart.com/user/{}",
            "walmart": base + "walmart.com/user/{}",
            "target": base + "target.com/user/{}",
            "costco": base + "costco.com/user/{}",
            "amazon": base + "amazon.com/gp/profile/{}",
            "uber": base + "uber.com/people/{}",
            "lyft": base + "lyft.com/profile/{}",
            "bolt": base + "bolt.eu/user/{}",
            "grab": base + "grab.com/user/{}",
            "gojek": base + "gojek.com/user/{}",
            "airbnb": base + "airbnb.com/users/show/{}",
            "booking": base + "booking.com/users/{}",
            "expedia": base + "expedia.com/user/{}",
            "kayak": base + "kayak.com/user/{}",
            "skyscanner": base + "skyscanner.com/user/{}",
            "tripadvisor": base + "tripadvisor.com/Profile/{}",
            "ctrip": base + "ctrip.com/user/{}",
            "dianping": base + "dianping.com/user/{}",
            "meituan": base + "meituan.com/user/{}",
            "jd": base + "jd.com/user/{}",
            "pinduoduo": base + "pinduoduo.com/people/{}",
            "taobao": base + "taobao.com/people/{}",
            "qq": base + "qq.com/@{}",
            "weibo": base + "weibo.com/u/{}",
            "baidu": base + "baidu.com/s?wd={}",
            "yandex": base + "yandex.ru/search/?text={}",
            "duckduckgo": base + "duckduckgo.com/?q={}",
            "google": base + "google.com/search?q={}",
            "bing": base + "bing.com/search?q={}",
            "yahoo": base + "search.yahoo.com/search?p={}",
            "seznam": base + "search.seznam.cz/?q={}",
            "naver": base + "search.naver.com/search.naver?query={}",
            "daum": base + "search.daum.net/search?q={}",
            "kakao": base + "kakao.com/search?q={}"
        })
        
        return sites

    async def check_site(self, session, site_name, url_pattern, username):
        url = url_pattern.format(username)
        try:
            async with session.get(url, timeout=10) as response:
                return UsernameResult(
                    site=site_name,
                    url=url,
                    exists=response.status == 200,
                    status_code=response.status,
                    error=""
                )
        except Exception as e:
            return UsernameResult(
                site=site_name,
                url=url,
                exists=False,
                status_code=0,
                error=str(e)
            )

    async def search(self, username):
        logger.info(f"Searching username: {username} across {len(self.sites)} sites")
        headers = {"User-Agent": self.config.get("user_agent", "Mozilla/5.0")}
        
        async with aiohttp.ClientSession(headers=headers) as session:
            tasks = []
            for site_name, url_pattern in self.sites.items():
                tasks.append(self.check_site(session, site_name, url_pattern, username))
            results = await asyncio.gather(*tasks)
        
        found = [r for r in results if r.exists]
        print(f"\n[+] Found {len(found)} profiles for {username}")
        for r in found:
            print(f"    ✓ {r.site}: {r.url}")
        
        return results

# ============ MAIN ============
async def main():
    parser = argparse.ArgumentParser(description="OSINT Toolkit v3.2")
    parser.add_argument("-u", "--username", help="Search username")
    parser.add_argument("-o", "--output", help="Output file (json)")
    
    args = parser.parse_args()
    
    if args.username:
        config = load_config()
        searcher = UsernameSearcher(config)
        results = await searcher.search(args.username)
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump([asdict(r) for r in results], f, indent=2)
            print(f"\n[+] Results saved to {args.output}")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    asyncio.run(main())