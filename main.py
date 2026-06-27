import os
import asyncio
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from cosmic_source_rng.engine import generate_cosmic_random
from cosmic_source_rng.cosmic import _fetch_nasa_data
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

# APIの土台を作る
app = FastAPI(title="CosmicSource RNG")

# RapidAPI Proxy Secret（環境変数から取得）
PROXY_SECRET = os.getenv('PROXY_SECRET')


@app.middleware("http")
async def verify_rapidapi_proxy_secret(request: Request, call_next):
    """
    RapidAPI Proxy Secretチェックミドルウェア
    X-RapidAPI-Proxy-Secretヘッダーを検証し、環境変数PROXY_SECRETと一致するか確認
    """
    # PROXY_SECRETが設定されていない場合はチェックをスキップ（開発環境など）
    if PROXY_SECRET is None:
        return await call_next(request)
    
    # X-RapidAPI-Proxy-Secretヘッダーを取得
    proxy_secret_header = request.headers.get("X-RapidAPI-Proxy-Secret")
    
    # ヘッダーが存在しない、または一致しない場合は403 Forbiddenを返す
    if proxy_secret_header != PROXY_SECRET:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "error": "Forbidden",
                "message": "Invalid or missing X-RapidAPI-Proxy-Secret header"
            }
        )
    
    # 検証成功時は次の処理に進む
    return await call_next(request)

# キャッシュ用のグローバル変数
nasa_cache = None
cache_lock = asyncio.Lock()


async def update_nasa_cache():
    """NASAデータのキャッシュを更新する（バックグラウンドタスク）"""
    global nasa_cache
    try:
        # ブロッキングI/Oなので、executorで実行
        loop = asyncio.get_event_loop()
        cache_data = await loop.run_in_executor(None, _fetch_nasa_data)
        
        async with cache_lock:
            nasa_cache = cache_data
        
        print(f"[Cache Update] NASA data cached successfully at {asyncio.get_event_loop().time()}")
    except Exception as e:
        print(f"[Cache Update Error] Failed to update cache: {e}")


async def cache_update_loop():
    """1時間ごとにキャッシュを更新するループ"""
    # 初回は即座に更新
    await update_nasa_cache()
    
    # その後は1時間ごとに更新
    while True:
        await asyncio.sleep(3600)  # 3600秒 = 1時間
        await update_nasa_cache()


@app.on_event("startup")
async def startup_event():
    """アプリケーション起動時にキャッシュを初期化し、バックグラウンドタスクを開始"""
    print("[Startup] Initializing NASA cache...")
    # バックグラウンドタスクを開始
    asyncio.create_task(cache_update_loop())


@app.get("/generate")
async def get_random():
    """宇宙とローカルのゆらぎを混ぜた乱数を生成するエンドポイント"""
    # キャッシュからデータを取得（ブロッキングI/Oなのでexecutorで実行）
    loop = asyncio.get_event_loop()
    
    # キャッシュが利用可能な場合はそれを使用、なければ直接取得
    if nasa_cache is not None:
        result = await loop.run_in_executor(
            None,
            lambda: generate_cosmic_random(use_cache=True, cache_data=nasa_cache)
        )
    else:
        # キャッシュがまだない場合は直接取得（初回起動時など）
        result = await loop.run_in_executor(
            None,
            lambda: generate_cosmic_random(use_cache=False, cache_data=None)
        )
    
    return result


@app.get("/cache/status")
async def cache_status():
    """キャッシュの状態を確認するエンドポイント"""
    return {
        "cached": nasa_cache is not None,
        "cache_data": nasa_cache if nasa_cache else None
    }


@app.post("/cache/refresh")
async def refresh_cache():
    """手動でキャッシュを更新するエンドポイント"""
    await update_nasa_cache()
    return {"status": "Cache refreshed", "cache_data": nasa_cache}

# サーバー起動用の設定
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)