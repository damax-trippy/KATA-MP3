# KATA-MP3

A simple Linux desktop app that downloads YouTube audio as MP3.
Paste a URL, pick a quality, hit download.

## 1. Quick Install (one command)

Copy and paste this whole block into your terminal:

```bash
# Install required packages first (pick your distro)
sudo apt install git python3 python3-venv ffmpeg       # Debian / Ubuntu / Mint
# sudo pacman -S git python ffmpeg                     # Arch / Manjaro
# sudo dnf install git python3 ffmpeg                  # Fedora
# sudo zypper install git python3 ffmpeg               # openSUSE

# Then install KATA-MP3
git clone git@github.com:damax-trippy/KATA-MP3.git ~/KATA-MP3 && cd ~/KATA-MP3 && ./install.sh
```

That's it. The installer sets up the virtualenv and adds **KATA-MP3** to
your app menu.

> **SSH clone failed?** Use the HTTPS URL instead:
> ```bash
> git clone https://github.com/damax-trippy/KATA-MP3.git ~/KATA-MP3 && cd ~/KATA-MP3 && ./install.sh
> ```

**What you need:** git, python3, python3-venv, ffmpeg.
The command above installs all four for you.

## 2. Manual Install

If the script doesn't work, do it yourself.

**Step 1 — Install packages**

```bash
# Debian / Ubuntu / Mint
sudo apt install git python3 python3-venv ffmpeg

# Arch / Manjaro
sudo pacman -S git python ffmpeg

# Fedora
sudo dnf install git python3 ffmpeg

# openSUSE
sudo zypper install git python3 ffmpeg

# Alpine
sudo apk add git python3 py3-virtualenv ffmpeg
```

**Step 2 — Clone**

```bash
git clone git@github.com:damax-trippy/KATA-MP3.git ~/KATA-MP3
cd ~/KATA-MP3
```

**Step 3 — Set up Python environment**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

**Step 4 — Run**

```bash
python main.py
```

## 3. Uninstall

```bash
rm ~/.local/share/applications/kata-mp3.desktop
rm -rf ~/KATA-MP3
```

Done.
