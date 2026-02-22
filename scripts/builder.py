import os
import requests
import re
import json

def get_config_list(env_name, file_path):
    # 优先从 GitHub Actions 环境变量读取
    env_data = os.getenv(env_name)
    if env_data:
        return [line.strip() for line in env_data.split('\n') if line.strip() and not line.startswith('#')]
    
    # 如果没有环境变量，则读取本地 sources/ 目录下的文件
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

def build():
    # 1. 获取源列表
    live_urls = get_config_list('LIVE_SOURCES_CONF', 'sources/live_sources.txt')
    vod_urls = get_config_list('VOD_SOURCES_CONF', 'sources/vod_sources.txt')
    base_url = os.getenv('BASE_URL', '.') # 获取 Pages 网址

    # 2. 采集直播源 (逻辑不变)
    unique_channels = {}
    headers = {'User-Agent': 'Mozilla/5.0'}
    for url in live_urls:
        try:
            r = requests.get(url, headers=headers, timeout=10)
            matches = re.findall(r'#EXTINF:.*?,(.*?)\n(http[s]?://.*)', r.text)
            for name, link in matches:
                clean_name = name.strip()
                if clean_name not in unique_channels:
                    unique_channels[clean_name] = link.strip()
        except: continue

    # 3. 导出 raw_list.json
    raw_list = [{"name": n, "url": u} for n, u in unique_channels.items()]
    with open('raw_list.json', 'w', encoding='utf-8') as f:
        json.dump(raw_list, f, ensure_ascii=False)

    # 4. 缝合点播接口并生成 config_raw.json
    config = {"spider": "", "sites": [], "lives": []}
    for vod_url in vod_urls:
        try:
            resp = requests.get(vod_url, timeout=10)
            config = resp.json()
            if "sites" in config: break
        except: continue

    # 使用环境变量中的 BASE_URL 拼接最终路径
    config["lives"].insert(0, {
        "name": "iPhone 优选源",
        "type": 0,
        "url": f"{base_url}/final.m3u", # 自动拼接完整地址
        "playerType": 1
    })

    with open('config_raw.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    build()
