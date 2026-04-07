#pip install Flask waitress
#啟用 - cmd: python -m flask --app [檔名] run --host 0.0.0.0 --port 8000  | 例如: python -m flask --app test.py run --host 0.0.0.0 --port 8000
#測試 - PowerShell: Invoke-RestMethod -Method POST -Uri http://127.0.0.1:8000/submit -ContentType 'application/json' -Body (@{ text = 'C:\Users\21\Desktop\demo.txt' } | ConvertTo-Json)

from flask import Flask, request, jsonify
from datetime import datetime
from pathlib import Path
import os, threading
import json
from pathlib import Path
import platform

import time
ARTIFICIAL_DELAY = int(os.getenv("ARTIFICIAL_DELAY", "3"))  # 預設 5 秒

app = Flask(__name__)

# 可用環境變數 OUTPUT_FILE 指定寫入檔；預設在程式同資料夾的 received.txt
env_path = os.getenv("OUTPUT_FILE")
if env_path:
    OUTPUT_FILE = Path(env_path)
else:
    system = platform.system()
    if system == "Windows":
        #Windows：寫在程式同資料夾
        OUTPUT_FILE = Path(__file__).with_name("receivedpath.txt")
    else:
        #Liinux（含 Docker）：寫到 /app/data
        OUTPUT_FILE = Path("/app/data/receivedpath.txt")

# 確保資料夾存在
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

# 同進程寫入鎖，避免同時多請求打架
file_lock = threading.Lock()

@app.post("/api/api_system/insert_file")
def submit():
    data = request.get_json(silent=True) or {}
    print("收到資料:", json.dumps(data, ensure_ascii=False))
    text = data.get("filepath")
    if not isinstance(text, str) or not text.strip():
        return jsonify({"status": False, "data": "filepath is required"}), 400

    # 清理換行避免撐亂檔案
    safe_text = text.replace("\r", " ").replace("\n", " ")
    client_ip = (request.headers.get("X-Forwarded-For") or request.remote_addr or "unknown").split(",")[0].strip()
    line = f"{datetime.now().isoformat(timespec='seconds')}\t{client_ip}\t{safe_text}\n"

    # 模擬處理時間（同步阻塞，該 worker 會被占用）
    #time.sleep(ARTIFICIAL_DELAY)
    
    try:
        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        with file_lock, OUTPUT_FILE.open("a", encoding="utf-8", newline="") as f:
            f.write(line)
        time.sleep(ARTIFICIAL_DELAY)
    except Exception as e:
        return jsonify({"status": False, "data": f"write_failed: {e}"}), 500

    return jsonify({"status": True, "data": "ok", "saved_to": str(OUTPUT_FILE), "bytes_written": len(line)})

@app.get("/health")
def health():
    return jsonify({"status": "ok~~~!!!"})
