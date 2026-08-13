import os
import time
import requests
import threading
import itertools
from flask import Flask, jsonify
from datetime import datetime

app = Flask(__name__)

BUCKET_URL = os.environ["BUCKET_URL"]
API_KEY = os.environ["API_KEY"]
FILE_SIZE = int(os.environ.get("FILE_SIZE_BYTES", 500 * 1024 * 1024))  # default 500MB
CHUNK_SIZE = 1024 * 1024  # 1MB buffer

TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN")
TG_CHAT_ID = os.environ.get("TG_CHAT_ID")

# Pre-generate one chunk buffer to reuse (faster than generating random each time)
_chunk_cache = os.urandom(CHUNK_SIZE)

# Global stats (updated by background thread)
stats = {
    "uploads_completed": 0,
    "total_bytes_uploaded": 0,
    "errors": 0,
    "started_at": datetime.now().isoformat(),
    "last_upload": None,
    "running": True
}

def notify(text):
    """Send a Telegram message if configured"""
    if not (TG_BOT_TOKEN and TG_CHAT_ID):
        return
    try:
        requests.post(
            f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage",
            json={"chat_id": TG_CHAT_ID, "text": text},
            timeout=10
        )
    except:
        pass

def data_generator(total_size):
    """Generator that yields file data without loading it all into memory"""
    written = 0
    while written < total_size:
        to_write = min(CHUNK_SIZE, total_size - written)
        yield _chunk_cache[:to_write]
        written += to_write

def continuous_push():
    """Background thread that continuously pushes files forever"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/octet-stream"
    }
    
    for i in itertools.count():
        if not stats["running"]:
            break
            
        filename = f"testfile_{int(time.time())}_{i}.bin"
        start = time.time()
        
        try:
            resp = requests.put(
                f"{BUCKET_URL}/{filename}",
                data=data_generator(FILE_SIZE),
                headers=headers,
                timeout=120
            )
            elapsed = time.time() - start
            speed_gbps = (FILE_SIZE / 1024 / 1024 / 1024) / elapsed if elapsed > 0 else 0
            
            # Update stats
            stats["uploads_completed"] += 1
            stats["total_bytes_uploaded"] += FILE_SIZE
            stats["last_upload"] = {
                "file": filename,
                "status": resp.status_code,
                "elapsed_s": round(elapsed, 1),
                "speed_gbps": round(speed_gbps, 2),
                "timestamp": datetime.now().isoformat()
            }
            
            log_msg = f"[{i}] ✅ {filename} | {resp.status_code} | {FILE_SIZE/1e9:.2f}GB | {elapsed:.1f}s | {speed_gbps:.2f}GB/s | Total: {stats['total_bytes_uploaded']/1e12:.2f}TB"
            print(log_msg, flush=True)
            
            if resp.status_code >= 400:
                stats["errors"] += 1
                notify(f"⚠️ Upload {i} failed: {filename} | status {resp.status_code}")
                
        except Exception as e:
            stats["errors"] += 1
            print(f"[{i}] ❌ FAILED: {e}", flush=True)
            notify(f"🔴 Upload {i} error: {str(e)[:100]}")
            time.sleep(2)  # brief backoff on error, then keep pushing

@app.route("/")
def health():
    """Health check - shows real-time stats"""
    uptime_seconds = (datetime.fromisoformat(stats["started_at"]) - datetime.now()).total_seconds() * -1
    uptime_hours = uptime_seconds / 3600
    
    return jsonify({
        "status": "streaming 🚀",
        "running": stats["running"],
        "uptime_seconds": int(uptime_seconds),
        "uploads_completed": stats["uploads_completed"],
        "total_data_gb": round(stats["total_bytes_uploaded"] / 1e9, 2),
        "total_data_tb": round(stats["total_bytes_uploaded"] / 1e12, 2),
        "errors": stats["errors"],
        "last_upload": stats["last_upload"],
        "bucket": BUCKET_URL
    })

@app.route("/stats")
def get_stats():
    """Detailed stats view"""
    uptime_seconds = (datetime.fromisoformat(stats["started_at"]) - datetime.now()).total_seconds() * -1
    avg_speed_gbps = (stats["total_bytes_uploaded"] / 1e9) / (uptime_seconds / 3600) if uptime_seconds > 0 else 0
    
    return jsonify({
        "uptime_seconds": int(uptime_seconds),
        "uploads": stats["uploads_completed"],
        "total_gb": round(stats["total_bytes_uploaded"] / 1e9, 2),
        "total_tb": round(stats["total_bytes_uploaded"] / 1e12, 3),
        "errors": stats["errors"],
        "file_size_gb": round(FILE_SIZE / 1e9, 2),
        "avg_speed_gbps": round(avg_speed_gbps, 2),
        "last_upload": stats["last_upload"],
        "started_at": stats["started_at"]
    })

# Start background thread on app startup
def start_background_thread():
    """Start the continuous pusher thread"""
    thread = threading.Thread(target=continuous_push, daemon=True)
    thread.start()
    print("🚀 Background thread started - streaming continuously...", flush=True)

# Start on first request
@app.before_request
def startup():
    if not hasattr(app, 'bg_thread_started'):
        start_background_thread()
        app.bg_thread_started = True

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"Starting Flask service on port {port}", flush=True)
    print(f"Bucket: {BUCKET_URL}", flush=True)
    print(f"File size: {FILE_SIZE/1e9:.2f}GB", flush=True)
    app.run(host="0.0.0.0", port=port, debug=False)
