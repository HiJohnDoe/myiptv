import os, requests, re, json

def build():
    # 从 GitHub Variables 读取
    live_urls = os.getenv('LIVE_SOURCES_CONF', '').split('\n')
    vod_urls = os.getenv('VOD_SOURCES_CONF', '').split('\n')
    
    # 1. 直播源聚合 -> raw_list.json
    unique_channels = {}
    for url in [u.strip() for u in live_urls if u.strip()]:
        try:
            r = requests.get(url, timeout=10)
            matches = re.findall(r'#EXTINF:.*?,(.*?)\n(http[s]?://.*)', r.text)
            for name, link in matches:
                if name.strip() not in unique_channels:
                    unique_channels[name.strip()] = link.strip()
        except: continue
    with open('raw_list.json', 'w', encoding='utf-8') as f:
        json.dump([{"name": n, "url": u} for n, u in unique_channels.items()], f, ensure_ascii=False)

    # 2. 点播源聚合 -> vod_config.json
    vod_combined = {"sites": []}
    for url in [u.strip() for u in vod_urls if u.strip()]:
        try:
            r = requests.get(url, timeout=10)
            data = r.json()
            if "sites" in data: vod_combined["sites"].extend(data["sites"])
        except: continue
    with open('vod_config.json', 'w', encoding='utf-8') as f:
        json.dump(vod_combined, f, ensure_ascii=False)

if __name__ == "__main__":
    build()
