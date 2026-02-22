import requests
import re
import json
import os

def collect_live():
    with open('sources/live_sources.txt', 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    unique_channels = {}
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

    for url in urls:
        try:
            print(f"正在采集直播源: {url}")
            r = requests.get(url, headers=headers, timeout=15)
            matches = re.findall(r'#EXTINF:.*?,(.*?)\n(http[s]?://.*)', r.text)
            for name, link in matches:
                clean_name = name.strip().replace(" ", "")
                if clean_name not in unique_channels:
                    unique_channels[clean_name] = link.strip()
        except: continue

    # 导出给 iPhone 用的 JSON
    raw_list = [{"name": n, "url": u} for n, u in unique_channels.items()]
    with open('raw_list.json', 'w', encoding='utf-8') as f:
        json.dump(raw_list, f, ensure_ascii=False)
    return unique_channels

def build_config():
    collect_live()
    with open('sources/vod_sources.txt', 'r', encoding='utf-8') as f:
        vod_urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]

    config = {"spider": "", "sites": [], "lives": []}
    for vod_url in vod_urls:
        try:
            resp = requests.get(vod_url, timeout=10)
            config = resp.json()
            if "sites" in config: break
        except: continue

    # 这里的 URL 需要在部署 Cloudflare Pages 后，修改为你的最终域名
    config["lives"].insert(0, {
        "name": "iPhone 优选源",
        "type": 0,
        "url": "./final.m3u", 
        "playerType": 1
    })

    with open('config_raw.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    build_config()
