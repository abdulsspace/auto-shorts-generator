# 🚀 Complete Setup Guide

Step-by-step instructions to get Auto Shorts Generator running.

## Prerequisites

- Python 3.8 or higher
- Git
- FFmpeg
- ~2GB free disk space

## Step 1: Install Python & Git

### Windows
- Download Python from https://www.python.org/downloads/
- Download Git from https://git-scm.com/
- During Python install, **CHECK** "Add Python to PATH"

### Mac
```bash
brew install python3
brew install git
```

### Linux
```bash
sudo apt update
sudo apt install python3 python3-pip git
```

## Step 2: Install FFmpeg

### Windows
```bash
# Using Chocolatey (recommended)
choco install ffmpeg

# Or download from: https://ffmpeg.org/download.html
# Add FFmpeg to PATH
```

### Mac
```bash
brew install ffmpeg
```

### Linux
```bash
sudo apt install ffmpeg
```

**Verify installation:**
```bash
ffmpeg -version
```

## Step 3: Clone Repository

```bash
git clone https://github.com/abdulsspace/auto-shorts-generator.git
cd auto-shorts-generator
```

## Step 4: Create Virtual Environment (Optional but Recommended)

### Windows
```bash
python -m venv venv
venv\Scripts\activate
```

### Mac/Linux
```bash
python3 -m venv venv
source venv/bin/activate
```

## Step 5: Install Python Dependencies

```bash
pip install -r requirements.txt
```

**Wait for installation to complete** (~5-10 minutes)

## Step 6: Get Google Gemini API Key

1. Go to https://ai.google.dev
2. Click **"Get API Key"** button
3. Click **"Create API Key in new project"**
4. Copy the API key

## Step 7: Set Up YouTube API (Optional for uploads)

### If you want to upload to YouTube:

1. Go to https://console.cloud.google.com
2. Create a new project
   - Click "Select a Project" → "New Project"
   - Name: "Auto Shorts Generator"
   - Click "Create"
3. Enable YouTube Data API
   - Search for "YouTube Data API v3"
   - Click on it → "Enable"
4. Create OAuth 2.0 credentials
   - Go to "Credentials" in left menu
   - Click "Create Credentials" → "OAuth client ID"
   - Choose "Desktop application"
   - Click "Create"
   - Download the JSON file
5. Save the file as `credentials.json` in your project folder

## Step 8: Create Environment File

Create `.env` file in the project root:

### On Windows (using Notepad)
1. Open Notepad
2. Paste this:
```
GEMINI_API_KEY=paste_your_key_here
```
3. Save as `.env` in project folder (not `.txt`)

### On Mac/Linux
```bash
cat > .env << EOF
GEMINI_API_KEY=paste_your_key_here
EOF
```

**Replace `paste_your_key_here` with your actual Gemini API key**

## Step 9: Create Output Directory

```bash
mkdir output
```

## Step 10: Test Installation

```bash
python main.py --stats
```

If you see no errors, you're ready! 🎉

## Troubleshooting

### "Python not found" or "pip not found"

Make sure Python is added to PATH:

**Windows:**
- Reinstall Python
- During installation, CHECK "Add Python to PATH"
- Restart command prompt

**Mac/Linux:**
```bash
which python3
# Should show a path like /usr/bin/python3
```

### "FFmpeg not found"

```bash
ffmpeg -version
```

If command doesn't work, install FFmpeg and add to PATH.

### "Module not found" errors

Make sure you're in virtual environment and installed requirements:

```bash
# Activate venv first (see Step 4)
pip install -r requirements.txt
```

### "GEMINI_API_KEY not found"

1. Check `.env` file exists in project root
2. Make sure it's named `.env` (not `.env.txt`)
3. Verify API key is correct in `.env`
4. Restart your terminal after creating `.env`

## Your First Run

Once everything is set up:

```bash
# Generate 1 short (without upload)
python main.py

# Generate 5 shorts
python main.py --generate 5

# Generate and upload to YouTube
python main.py --generate 1 --upload
```

## File Structure Check

After setup, you should have:

```
auto-shorts-generator/
├── src/
├── main.py
├── config.yaml
├── requirements.txt
├── .env              ← Your API key here
├── credentials.json  ← YouTube OAuth (if uploading)
└── output/           ← Generated videos
```

## Next Steps

1. **Customize config.yaml** - Change topics, video settings
2. **Test generation** - Generate 1-2 shorts
3. **Review output** - Check quality in `output/` folder
4. **Upload to YouTube** - Use `--upload` flag
5. **Schedule automation** - Set up task scheduler to run daily

## Creating YouTube Channel

1. Go to https://youtube.com
2. Click your profile icon
3. Click "Create a channel"
4. Choose channel name (make it catchy!)
5. Customize channel art and description
6. Add channel description focused on your niche

### Channel Description Tips

```
🤯 Mind-blowing facts and science explained
✨ New shorts daily!
📚 Educational & entertaining content

Subscribe for more! 🔔
```

## Scheduling Automatic Uploads

### Windows (Task Scheduler)

1. Open Task Scheduler
2. Create Basic Task
3. Name: "Auto Shorts Generator"
4. Set trigger (daily at 10 AM)
5. Set action: Run program
6. Program: `C:\path\to\python.exe`
7. Arguments: `main.py --generate 1 --upload`
8. Start in: `C:\path\to\project\`

### Mac/Linux (Cron)

```bash
# Edit crontab
crontab -e

# Add this line to run daily at 10 AM
0 10 * * * cd /path/to/project && python main.py --generate 1 --upload
```

## Monitoring

Check logs in `output/` folder for generated shorts.

Each short creates a folder with metadata showing when it was created and uploaded.

## Support

If you get stuck:
1. Check the README.md
2. Review error messages carefully
3. Make sure all API keys are correct
4. Verify FFmpeg is installed
5. Check internet connection (for API calls)

---

**You're all set! 🚀 Now start creating amazing YouTube Shorts!**
