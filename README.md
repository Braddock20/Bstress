# Bucket Stress Test (Continuous Streaming) 🚀

**Truly continuous data streaming to your bucket. No pings. No delays. Just flows.**

The Flask app runs a background thread that continuously generates and uploads files at maximum speed while you watch in real-time. Zero intervention needed.

## How it works

- Flask web service + background thread
- Thread starts on first request and **never stops**
- Continuously generates files and uploads at full bandwidth
- Web endpoints (`/` and `/stats`) show live streaming stats
- Render free tier keeps it alive 24/7
- **Cost: $0/month** (uses Render's free tier)

## Endpoints

- `GET /` — Live stream status + last upload details
- `GET /stats` — Detailed stats (uptime, throughput, totals)

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
2. Click "New +" → "Web Service"
3. Connect your GitHub repo
4. Render auto-detects `render.yaml`
5. Set environment variables (see below)
6. Deploy — streaming starts immediately

### 3. Configure Environment Variables

In Render dashboard:

**Required:**
- `BUCKET_URL` — Your bucket endpoint
- `API_KEY` — Your bucket API key

**Optional:**
- `FILE_SIZE_BYTES` — Size per file in bytes (default: 524288000 = 500MB)
  - 100MB = 104857600
  - 1GB = 1073741824
  - 5GB = 5368709120
- `TG_BOT_TOKEN` — Telegram bot token (for failure alerts)
- `TG_CHAT_ID` — Your Telegram chat ID (for alerts)

### 4. (Optional) Set up Telegram alerts

If you want failure notifications:

1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Create a new bot, copy the token
3. Message your new bot once
4. Visit: `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
5. Copy your `chat_id`
6. Add both to Render env vars

## Monitoring

Once deployed, visit your service URL anytime:

**Live status:**
```
https://bucket-stress-test.onrender.com/
```

Returns:
```json
{
  "status": "streaming 🚀",
  "running": true,
  "uptime_seconds": 3600,
  "uploads_completed": 290,
  "total_data_gb": 145.0,
  "total_data_tb": 0.145,
  "errors": 0,
  "last_upload": {
    "file": "testfile_1723488913_290.bin",
    "status": 200,
    "elapsed_s": 12.1,
    "speed_gbps": 0.04,
    "timestamp": "2026-08-13T14:15:25.123456"
  }
}
```

**Detailed stats:**
```
https://bucket-stress-test.onrender.com/stats
```

Returns:
```json
{
  "uptime_seconds": 7200,
  "uploads": 580,
  "total_gb": 290.0,
  "total_tb": 0.290,
  "errors": 0,
  "file_size_gb": 0.5,
  "avg_speed_gbps": 0.04,
  "last_upload": { ... },
  "started_at": "2026-08-13T12:00:00.000000"
}
```

**Render logs tab** shows every upload in real-time:
```
[289] ✅ testfile_1723488913_289.bin | 200 | 0.50GB | 12.1s | 0.04GB/s | Total: 144.50TB
[290] ✅ testfile_1723488925_290.bin | 200 | 0.50GB | 12.3s | 0.04GB/s | Total: 145.00TB
[291] ✅ testfile_1723488937_291.bin | 200 | 0.50GB | 12.0s | 0.04GB/s | Total: 145.50TB
```

## Expected Throughput

Depends on your internet, bucket bandwidth, and file size:

**Example (500MB files):**
- Local fiber (1Gbps): ~100 files/hour → 50GB/hour → 1.2TB/day
- Standard residential (100Mbps): ~10 files/hour → 5GB/hour → 120GB/day
- Render egress: ~50-200 MB/s typical → 1-4 files/hour → 0.5-2GB/hour

**To increase throughput:**
- Reduce `FILE_SIZE_BYTES` (smaller files = more frequent uploads)
- Increase bandwidth (upgrade internet or bucket provider)
- Run multiple instances (add more Render web services)

## How it stays alive (no spin-down)

Render's free tier web services normally spin down after 15 min of no incoming HTTP traffic. **This version never sleeps:**

- The background thread runs forever independently
- Flask keeps HTTP port open continuously
- Render sees "active service" and never spins down

So you truly get 24/7 continuous streaming on free tier.

## Stopping it

1. Go to Render dashboard
2. Click your service → "Settings" → "Delete Service"

Or suspend it temporarily without deleting.

## Troubleshooting

**Uploads failing with 403/401?**
- Double-check `BUCKET_URL` and `API_KEY`
- Verify auth format (Bearer token vs AWS SigV4 etc.)

**Not seeing uploads in logs?**
- Check Render's "Logs" tab (can lag 30s)
- Visit `https://your-service.onrender.com/` to verify it's running
- If 500 error, check deployment logs

**Want to change file size?**
- Update `FILE_SIZE_BYTES` in Render env vars
- Render will restart the service, streaming resumes

**Thread crashed?**
- Check Render logs for errors
- If it fails repeatedly, may be auth or bucket limit issue
- Telegram alert will notify you of failures

**Cost is high?**
- Render free tier = free (yes really)
- Cost comes from **bucket storage + egress**
- Adjust `FILE_SIZE_BYTES` smaller to reduce data volume

## License

Use at your own risk. Responsible for bucket costs.
