import os
import time

from flask import Flask, jsonify
from redis import Redis, RedisError
from dotenv import load_dotenv
from pathlib import Path
from flask import send_from_directory
from flask_cors import CORS

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / '.env')

# Конфиг Redis
REDIS_MASTER_HOST = os.getenv('REDIS_MASTER_HOST', 'redis-master')
REDIS_MASTER_PORT = int(os.getenv('REDIS_MASTER_PORT', 6379))
REDIS_SLAVE_HOST = os.getenv('REDIS_SLAVE_HOST', 'redis-slave')
REDIS_SLAVE_PORT = int(os.getenv('REDIS_SLAVE_PORT', 6379))
REDIS_DB = int(os.getenv('REDIS_DB', 0))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD') or None

app = Flask(__name__, static_folder=str(BASE_DIR / 'static'), static_url_path='/')
CORS(app)

# Ленивые клиенты
_r_master = None
_r_slave = None

def _connect_redis(host, port, retries=10, wait=1):
    for i in range(retries):
        try:
            client = Redis(
                host=host,
                port=port,
                db=REDIS_DB,
                password=REDIS_PASSWORD,
                decode_responses=True,
            )
            client.ping()
            return client
        except RedisError:
            if i == retries - 1:
                raise
            time.sleep(wait)
    raise RedisError(f"Cannot connect to Redis {host}:{port}")

def get_master():
    global _r_master
    if _r_master is None:
        _r_master = _connect_redis(REDIS_MASTER_HOST, REDIS_MASTER_PORT)
    return _r_master

def get_slave():
    global _r_slave
    if _r_slave is None:
        _r_slave = _connect_redis(REDIS_SLAVE_HOST, REDIS_SLAVE_PORT)
    return _r_slave

COUNTER_KEY = 'counter:value'

def ensure_counter_initialized():
    try:
        m = get_master()
        if m.get(COUNTER_KEY) is None:
            m.set(COUNTER_KEY, 0)
    except RedisError:
        # если Redis недоступен при старте — просто пропускаем, фронт получит ошибку на первом запросе
        pass

@app.route('/api/counter', methods=['GET'])
def get_counter():
    ensure_counter_initialized()
    try:
        try:
            s = get_slave()
            v = int(s.get(COUNTER_KEY) or 0)
        except RedisError:
            m = get_master()
            v = int(m.get(COUNTER_KEY) or 0)
        return jsonify({"value": v})
    except Exception:
        return jsonify({"error": "Redis error"}), 500

@app.route('/api/counter/increment', methods=['POST'])
def increment():
    try:
        m = get_master()
        v = m.incr(COUNTER_KEY)
        return jsonify({"value": int(v)})
    except Exception:
        return jsonify({"error": "Redis error"}), 500

@app.route('/api/counter/decrement', methods=['POST'])
def decrement():
    try:
        m = get_master()
        v = m.decr(COUNTER_KEY)
        return jsonify({"value": int(v)})
    except Exception:
        return jsonify({"error": "Redis error"}), 500

@app.route('/api/counter/reset', methods=['POST'])
def reset():
    try:
        m = get_master()
        m.set(COUNTER_KEY, 0)
        return jsonify({"value": 0})
    except Exception:
        return jsonify({"error": "Redis error"}), 500

# Healthcheck
@app.route('/health')
def health():
    return jsonify({"status": "ok"})

# Serve SPA
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_spa(path):
    static_dir = BASE_DIR / 'static'
    if path != "" and (static_dir / path).exists():
        return send_from_directory(str(static_dir), path)
    return send_from_directory(str(static_dir), 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8000)))
