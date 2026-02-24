import os, requests, re, json

def build():
    # 从 GitHub Variables 读取配置
    live_urls = os.getenv('LIVE_SOURCES_CONF', '').split('\n')
    vod_urls = os.getenv('VOD_SOURCES_CONF', '').split('\n')
    
    # 1. 直播源聚合 -> raw_list.json (加入兼容性优化)
    unique_channels = {}
    for url in [u.strip() for u in live_urls if u.strip()]:
        try:
            r = requests.get(url, timeout=10)
            # 匹配 m3u 格式的频道名和链接
            matches = re.findall(r'#EXTINF:.*?,(.*?)\n(http[s]?://.*)', r.text)
            for name, link in matches:
                clean_name = name.strip()
                clean_link = link.strip()
                
                # # ✨ 核心兼容性优化：将 https 强制降级为 http
                # # 解决电视端、盒子端常见的 SSL 证书过期或未知机构导致的解析失败
                # if clean_link.startswith("https://"):
                #     clean_link = clean_link.replace("https://", "http://", 1)
                
                # 去重：如果频道名已存在则跳过，保证列表纯净
                if clean_name not in unique_channels:
                    unique_channels[clean_name] = clean_link
        except Exception as e:
            print(f"解析直播源出错 {url}: {e}")
            continue

    # 写入供手机网页检测使用的“生肉”列表
    with open('raw_list.json', 'w', encoding='utf-8') as f:
        json.dump([{"name": n, "url": u} for n, u in unique_channels.items()], f, ensure_ascii=False)

    # 2. 点播源聚合 -> vod_config.json (保持原样，确保接口安全)
    vod_combined = {"sites": []}
    for url in [u.strip() for u in vod_urls if u.strip()]:
        try:
            r = requests.get(url, timeout=10)
            data = r.json()
            if "sites" in data:
                vod_combined["sites"].extend(data["sites"])
        except Exception as e:
            print(f"解析点播源出错 {url}: {e}")
            continue
            
    with open('vod_config.json', 'w', encoding='utf-8') as f:
        json.dump(vod_combined, f, ensure_ascii=False)

if __name__ == "__main__":
    build()
