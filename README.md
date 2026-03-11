# Suno-To-X Player Generator 🎵

A lightweight script that magically converts any Suno.com song link into a dedicated streaming webpage, complete with full lyrics and a perfect **Twitter/X Player Card**.

> Write a quick command to share your Suno AI music on X without losing the fancy preview player!

## 🌟 Features
- **Zero Config**: Automatically detects your GitHub Pages URL via git remote.
- **Perfect Twitter Cards**: Generates static HTML to ensure X crawlers accurately pick up your song's title, cover image, and player embed.
- **Smart i18n**: The music player interface automatically switches between English and Chinese based on the visitor's browser language.
- **Full Lyrics**: Shows the complete, beautifully formatted lyrics (prompt) below the player.

---

## 🛠 How to Use (For Anyone)

### 1. Fork & Setup Pages
1. Fork this repository.
2. Go to your repository **Settings** -> **Pages**.
3. Select **Deploy from a branch**, choose `main`, and click Save.
4. Clone your forked repo to your local machine:
   ```bash
   git clone https://github.com/YOUR_USERNAME/suno-player.git
   cd suno-player
   ```

### 2. Generate and Share!
Whenever you make a great song on Suno and get a link like `https://suno.com/s/xxxx`, run the script inside this directory:

```bash
python gen_suno_link.py "https://suno.com/s/xxxx"
```

**What the script does for you:**
- Fetches the song's audio direct link, cover, and lyrics via Suno API.
- Generates a static `{song_id}.html` file in your local directory.
- **Automatically commits and pushes** the new HTML file to your GitHub repository.
- Prints out your personal GitHub Pages URL ready to be pasted on X!

Simply paste the generated URL at the bottom of your tweet, and watch the beautiful player card appear!

---

## 💻 想要给别人用？（中文使用说明）

这个工具的作用是：**帮你把你做的 Suno 歌曲，一键转化成带有全篇歌词、并且能在推特 (X) 上显示为可以直接播放的精美音乐卡片的主页。**

### 第一步：Fork 和开启 Pages
1. Fork 这个仓库到你自己的 GitHub。
2. 在刚 Fork 出来的仓库点击右上角 **Settings**，在侧边栏找到 **Pages**。
3. 把源 (Source) 选择为 **`main`** 分支的 `/(root)` 目录，并保存。
4. 把仓库 Clone 到你自己的电脑/服务器上。

### 第二步：一键生成发推链接
在终端进入本目录，把你拿到的 Suno 分享链接（通常是 `/s/[xxx]` 格式）丢给脚本：

```bash
python gen_suno_link.py "https://suno.com/s/歌曲ID"
```

执行后，脚本会自动拉取原唱音频直链和歌词，在本地创建一个网页，**并自动帮你推送到 GitHub 上**。等个一两分钟，把终端最后吐出来的那条链接贴到推特里即可。

## Requirements
- `python 3.6+`
- `requests` (`pip install requests`)
- Git commands must be available in your environment.
