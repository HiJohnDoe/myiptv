import os, requests, re, json, time

def get_env_list(name):
    data = os.getenv(name, "")
    return [line.strip() for line in data.split('\n') if line.strip() and not line.startswith('#')]

def build():
    live_urls = get_env_list('LIVE_SOURCES_CONF')
    vod_urls = get_env_list('VOD_SOURCES_CONF')
    base_url = os.getenv('BASE_URL', '').rstrip('/')
    worker_url = os.getenv('CF_WORKER_URL', '')

    unique_channels = {}
    for url in live_urls:
        try:
            r = requests.get(url, timeout=10)
            matches = re.findall(r'#EXTINF:.*?,(.*?)\n(http[s]?://.*)', r.text)
            for name, link in matches:
                if name.strip() not in unique_channels:
                    unique_channels[name.strip()] = link.strip()
        except: continue

    # 生成待检清单
    raw_list = [{"name": n, "url": u} for n, u in unique_channels.items()]
    with open('raw_list.json', 'w', encoding='utf-8') as f:
        json.dump(raw_list, f, ensure_ascii=False)

    # 生成捷径配置
    with open('shortcut_cfg.json', 'w', encoding='utf-8') as f:
        json.dump({"worker_url": worker_url}, f, ensure_ascii=False)

    # 生成 TVBox 配置
    config = {"spider": "", "sites": [], "lives": []}
    for vod_url in vod_urls:
        try:
            config = requests.get(vod_url, timeout=10).json()
            if "sites" in config: break
        except: continue
        
    config["lives"].insert(0, {"name": "iPhone 优选源", "type": 0, "url": f"{base_url}/final.m3u", "playerType": 1})
    with open('config_raw.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    build()
