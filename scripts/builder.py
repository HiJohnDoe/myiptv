import os, requests, re, json

def build():
    # --- 路径处理逻辑 ---
    # 获取当前脚本所在目录的绝对路径 (scripts 文件夹)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # 定位到父目录下的 sources 文件夹
    sources_dir = os.path.join(os.path.dirname(base_dir), 'sources')
    
    live_file = os.path.join(sources_dir, 'live_sources.txt')
    vod_file = os.path.join(sources_dir, 'vod_sources.txt')

    # --- 1. 读取本地直播源列表 ---
    live_urls = []
    if os.path.exists(live_file):
        with open(live_file, 'r', encoding='utf-8') as f:
            live_urls = [line.strip() for line in f if line.strip()]
    else:
        print(f"⚠️ 警告: 未找到直播源文件 {live_file}")

    # 直播源聚合 -> raw_list.json
    unique_channels = {}
    for url in live_urls:
        try:
            r = requests.get(url, timeout=10)
            # 匹配 m3u 格式的频道名和链接
            matches = re.findall(r'#EXTINF:.*?,(.*?)\n(http[s]?://.*)', r.text)
            for name, link in matches:
                clean_name = name.strip()
                clean_link = link.strip()
                if clean_name not in unique_channels:
                    unique_channels[clean_name] = clean_link
        except Exception as e:
            print(f"❌ 解析直播源出错 {url}: {e}")

    # 写入供检测使用的列表
    with open('raw_list.json', 'w', encoding='utf-8') as f:
        json.dump([{"name": n, "url": u} for n, u in unique_channels.items()], f, ensure_ascii=False)

    # --- 2. 读取本地点播源列表 ---
    vod_urls = []
    if os.path.exists(vod_file):
        with open(vod_file, 'r', encoding='utf-8') as f:
            vod_urls = [line.strip() for line in f if line.strip()]
    else:
        print(f"⚠️ 警告: 未找到点播源文件 {vod_file}")

    # 点播源聚合 -> vod_config.json
    vod_combined = {"sites": []}
    for url in vod_urls:
        try:
            r = requests.get(url, timeout=10)
            data = r.json()
            if "sites" in data:
                vod_combined["sites"].extend(data["sites"])
        except Exception as e:
            print(f"❌ 解析点播源出错 {url}: {e}")
            
    with open('vod_config.json', 'w', encoding='utf-8') as f:
        json.dump(vod_combined, f, ensure_ascii=False)

if __name__ == "__main__":
    build()
