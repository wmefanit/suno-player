#!/usr/bin/env python3
import sys
import os
import re
import html
import requests
import subprocess

# 自动获取脚本所在的目录作为仓库目录
REPO_DIR = os.path.dirname(os.path.abspath(__file__))

def get_base_url():
    """通过 git remote 自动推断 GitHub Pages 的地址"""
    try:
        out = subprocess.check_output(["git", "remote", "get-url", "origin"], cwd=REPO_DIR, text=True).strip()
        # 兼容 https://github.com/user/repo.git 和 git@github.com:user/repo.git
        m = re.search(r'github\.com[:/]([^/]+)/([^/.]+)', out)
        if m:
            user, repo = m.groups()
            # 清理 repo 后面的 .git
            repo = repo.replace(".git", "")
            return f"https://{user}.github.io/{repo}"
    except Exception as e:
        print(f"⚠️ 无法自动获取 Git Origin: {e}")
        pass
    
    # 获取失败的默认兜底
    return "https://YOUR_USERNAME.github.io/YOUR_REPO_NAME"

BASE_URL = get_base_url()

def get_suno_info(url):
    print("⏳ 正在获取 Suno 歌曲信息...")
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0"})
    
    # 提取短链 ID (share_id)
    share_id = url.rstrip("/").split("/")[-1]
    
    try:
        resp = session.get(url, timeout=30, allow_redirects=True)
        resp.raise_for_status()
        m = re.search(r"/song/([0-9a-fA-F\-]{36})", resp.url)
        if not m:
            m = re.search(r"/song/([0-9a-fA-F\-]{36})", resp.text)
        
        if not m:
            return None, "无法提取 song_id"
        song_id = m.group(1)
        
        # 调 API 获取详情
        api_url = f"https://studio-api.prod.suno.com/api/clip/{song_id}"
        api_resp = session.get(api_url, timeout=30).json()
        
        title = api_resp.get("title") or "Untitled"
        audio = api_resp.get("audio_url") or f"https://cdn1.suno.ai/{song_id}.mp3"
        cover = f"https://cdn1.suno.ai/image_{song_id}.jpeg"
        prompt = (api_resp.get("metadata", {}) or {}).get("prompt", "暂无歌词")
        
        return {
            "song_id": song_id,
            "share_id": share_id,
            "title": title,
            "audio": audio,
            "cover": cover,
            "prompt": prompt,
            "original_url": url
        }, None
    except Exception as e:
        return None, str(e)

def generate_html(info):
    safe_title = html.escape(info["title"])
    safe_prompt = html.escape(info["prompt"])
    page_url = f"{BASE_URL}/{info['song_id']}.html"
    
    html_content = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{safe_title} - Suno Player</title>

  <!-- Twitter/X 卡片静态 meta -->
  <meta name="twitter:card" content="player">
  <meta name="twitter:title" content="{safe_title} · Suno AI Music">
  <meta name="twitter:description" content="AI-generated music. Click to listen with lyrics.">
  <meta name="twitter:image" content="{info['cover']}">
  <meta name="twitter:player" content="{page_url}">
  <meta name="twitter:player:width" content="480">
  <meta name="twitter:player:height" content="600">
  <meta property="og:title" content="{safe_title} - Suno">
  <meta property="og:image" content="{info['cover']}">

  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/aplayer@1.10.1/dist/APlayer.min.css">
  <style>
    body {{ background:#121212; color:#fff; font-family:sans-serif; display:flex; flex-direction:column; align-items:center; min-height:100vh; margin:0; padding:20px 0; }}
    #wrap {{ width:90%; max-width:480px; background:#1e1e1e; padding:20px; border-radius:12px; margin-bottom:16px; }}
    .lang-bar {{ width:90%; max-width:480px; display:flex; justify-content:flex-end; gap:8px; margin-bottom:8px; }}
    .lang-btn {{ background:transparent; border:1px solid #555; color:#999; border-radius:12px; padding:3px 12px; font-size:12px; cursor:pointer; }}
    .lang-btn.active {{ border-color:#ffa500; color:#ffa500; }}
    .footer-link {{ text-align:center; font-size:14px; margin-bottom:20px; }}
    .footer-link a {{ color:#ffa500; text-decoration:none; padding:10px 20px; border:1px solid #ffa500; border-radius:20px; transition:0.3s; }}
    .footer-link a:hover {{ background:#ffa500; color:#121212; }}
    #lyrics-label {{ width:90%; max-width:480px; font-size:12px; color:#555; margin-bottom:6px; letter-spacing:0.05em; text-transform:uppercase; }}
    #lyrics-box {{ width:90%; max-width:480px; background:#1e1e1e; padding:20px; border-radius:12px; white-space:pre-wrap; line-height:1.8; font-size:15px; color:#ccc; margin-bottom:30px; }}
    .aplayer {{ background:#2a2a2a !important; color:#fff !important; }}
    .aplayer-lrc {{ display:none !important; }}
  </style>
</head>
<body>
  <div class="lang-bar">
    <button class="lang-btn" id="btn-zh" onclick="setLang('zh')">中文</button>
    <button class="lang-btn" id="btn-en" onclick="setLang('en')">EN</button>
  </div>
  <div id="wrap"><div id="player"></div></div>
  <div class="footer-link">
    <a id="suno-link" href="{info['original_url']}" target="_blank"></a>
  </div>
  <div id="lyrics-label"></div>
  <div id="lyrics-box">{safe_prompt}</div>

  <script src="https://cdn.jsdelivr.net/npm/aplayer@1.10.1/dist/APlayer.min.js"></script>
  <script>
    const i18n = {{
      zh: {{
        sunoLink: '🔗 点击在 Suno 官网原址收听',
        lyricsLabel: '歌词 / Lyrics',
      }},
      en: {{
        sunoLink: '🔗 Listen on Suno',
        lyricsLabel: 'Lyrics',
      }}
    }};

    function setLang(lang) {{
      const t = i18n[lang];
      document.getElementById('suno-link').textContent = t.sunoLink;
      document.getElementById('lyrics-label').textContent = t.lyricsLabel;
      document.getElementById('btn-zh').classList.toggle('active', lang === 'zh');
      document.getElementById('btn-en').classList.toggle('active', lang === 'en');
      localStorage.setItem('suno_lang', lang);
    }}

    // 自动检测浏览器语言，默认跟随系统
    const saved = localStorage.getItem('suno_lang');
    const auto = (navigator.language || 'en').toLowerCase().startsWith('zh') ? 'zh' : 'en';
    setLang(saved || auto);

    new APlayer({{
      container: document.getElementById('player'),
      audio: [{{
        name: '{safe_title}',
        artist: 'Suno AI',
        url: '{info['audio']}',
        cover: '{info['cover']}',
        theme: '#ffa500'
      }}]
    }});
  </script>
</body>
</html>
"""
    file_path = os.path.join(REPO_DIR, f"{info['song_id']}.html")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    return file_path, page_url

def push_to_github(file_name, title):
    print("🚀 正在推送到 GitHub，生成卡片...")
    try:
        subprocess.run(["git", "add", file_name], cwd=REPO_DIR, check=True)
        subprocess.run(["git", "commit", "-m", f"add song: {title}"], cwd=REPO_DIR, check=True)
        subprocess.run(["git", "push", "origin", "main"], cwd=REPO_DIR, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Git 推送失败: {e} \n(请检查你的网络或 Git 权限，但 HTML 页面已成功在本地生成)")
        sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print("用法: python gen_suno_link.py <Suno链接>")
        sys.exit(1)
        
    url = sys.argv[1]
    if "suno.com" not in url:
        print("❌ 输入的不是有效的 Suno 链接")
        sys.exit(1)
        
    info, err = get_suno_info(url)
    if err:
        print(f"❌ {err}")
        sys.exit(1)
        
    print(f"✅ 解析成功: {info['title']}")
    
    # 1. 在仓库生成静态页面
    file_path, page_url = generate_html(info)
    
    # 2. 推送到 Github
    push_to_github(os.path.basename(file_path), info['title'])
    
    print("\n🎉 全部完成！页面已推送。大约 1 分钟后即可生效。")
    print("\n📌 【请复制下面这个链接，发到 X / 推特】：\n")
    print(f"{page_url}")

if __name__ == "__main__":
    main()
