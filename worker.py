import os
import time
import requests
import itertools

BUCKET_URL = os.environ["BUCKET_URL"]
API_KEY = os.environ["API_KEY"]
FILE_SIZE = int(os.environ.get("FILE_SIZE_BYTES", 500 * 1024 * 1024))  # default 500MB
CHUNK_SIZE = 1024 * 1024  # 1MB buffer

TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN")
TG_CHAT_ID = os.environ.get("TG_CHAT_ID")

chunk = os.urandom(CHUNK_SIZE)

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
        yield chunk[:to_write]
        written += to_write

def push_forever():
    """Continuously generate and push files to bucket"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/octet-stream"
    }
    
    total_uploaded = 0
    success_count = 0
    error_count = 0
    
    for i in itertools.count():
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
            
            if resp.status_code < 400:
                status = "✅"
                success_count += 1
                total_uploaded += FILE_SIZE
            else:
                status = "⚠️"
                error_count += 1
                notify(f"⚠️ Upload {i} failed: {filename} | status {resp.status_code}")
            
            log_msg = f"[{i}] {status} {filename} | {resp.status_code} | {FILE_SIZE/1e9:.2f}GB | {elapsed:.1f}s | {speed_gbps:.2f}GB/s | Total: {total_uploaded/1e12:.2f}TB"
            print(log_msg, flush=True)
            
        except Exception as e:
            error_count += 1
            print(f"[{i}] ❌ FAILED: {e}", flush=True)
            notify(f"🔴 Upload {i} error: {str(e)[:100]}")
            time.sleep(5)  # back off on error
    
if __name__ == "__main__":
    print("🚀 Starting continuous bucket stress test...")
    print(f"📍 Target: {BUCKET_URL}")
    print(f"📦 File size per upload: {FILE_SIZE/1e9:.2f}GB")
    print(f"🔑 Auth: Bearer token configured")
    if TG_BOT_TOKEN:
        print(f"📱 Telegram alerts: ENABLED")
    else:
        print(f"📱 Telegram alerts: DISABLED")
    print("-" * 80)
    push_forever()
