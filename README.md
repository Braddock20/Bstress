# Bucket Stress Test 🚀

Continuously generate and upload files to your bucket at maximum speed. Test storage limits, bandwidth, and API reliability.

## What it does

- Generates files of configurable size (default: 500MB each)
- Continuously uploads them to your bucket via PUT requests
- Tracks upload speed and total data transferred
- Sends Telegram alerts on failures
- Runs 24/7 on Render with zero intervention

## Setup

### 1. Create a GitHub repo

```bash
git init
git add .
git commit -m "initial"
git remote add origin https://github.com/YOUR_USERNAME/bucket-stress-test.git
git push -u origin main
```

### 2. Deploy to Render

1. Go to [render.com](https://render.com)
2. Click "New +" → "Background Worker"
3. Connect your GitHub repo
4. Render will auto-detect `render.yaml` and use the config
5. Set environment variables (see below)
6. Deploy

### 3. Configure Environment Variables

In Render dashboard, set these:

**Required:**
- `BUCKET_URL` — Your bucket endpoint (e.g., `https://mybucket.example.com`)
- `API_KEY` — Your bucket API key

**Optional:**
- `FILE_SIZE_BYTES` — Size per file in bytes (default: 524288000 = 500MB)
  - 1GB = 1073741824
  - 5GB = 5368709120
- `TG_BOT_TOKEN` — Telegram bot token (for alerts)
- `TG_CHAT_ID` — Your Telegram chat ID (for alerts)

### 4. (Optional) Set up Telegram alerts

If you want failure notifications:

1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Create a new bot, copy the token
3. Message your new bot once
4. Visit: `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
5. Copy your `chat_id` from the response
6. Add both to Render env vars

## What to expect

- **Throughput**: Depends on your internet and bucket bandwidth. Local fiber ≈ 100-500 MB/s. Render ≈ 50-200 MB/s.
- **Logs**: Check Render's "Logs" tab to watch uploads in real-time
- **Failures**: All failures get logged + Telegram alert (if enabled)
- **Cost**: Render background worker = $7/mo. Bucket storage/egress costs depend on your provider.

## Stopping it

1. Go to Render dashboard
2. Click your service → "Settings" → "Delete Service"

Or just suspend it temporarily without deleting.

## Example output

```
🚀 Starting continuous bucket stress test...
📍 Target: https://my-bucket.com
📦 File size per upload: 0.50GB
🔑 Auth: Bearer token configured
📱 Telegram alerts: ENABLED
--------------------------------------------------------------------------------
[0] ✅ testfile_1723488901_0.bin | 200 | 0.50GB | 12.3s | 0.04GB/s | Total: 0.50TB
[1] ✅ testfile_1723488913_1.bin | 200 | 0.50GB | 11.9s | 0.04GB/s | Total: 1.00TB
[2] ✅ testfile_1723488925_2.bin | 200 | 0.50GB | 12.1s | 0.04GB/s | Total: 1.50TB
...
```

## Troubleshooting

**Uploads failing with 403/401?**
- Check `BUCKET_URL` and `API_KEY` are correct
- Verify the auth format matches your bucket (Bearer token, AWS SigV4, etc.)

**Stuck at one file?**
- Timeout might be too short for your file size
- Check Render logs for the full error

**No logs?**
- Render logs can take 30 seconds to appear
- Refresh the logs tab

**Want to change file size?**
- Update `FILE_SIZE_BYTES` in Render env vars
- Worker will pick it up on next restart (you may need to manually restart)

## License

Use at your own risk. You're responsible for bucket costs.
