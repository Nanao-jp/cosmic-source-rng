"""
ローカル環境の「予測不能なゆらぎ」を取得するモジュール
システムのジッターとメモリ使用率を計測する
"""
import time
import psutil


def get_local_jitter():
    """
    ローカル環境のジッター（実行時間のゆらぎ）とメモリ使用率を取得する
    
    Returns:
        dict: {
            'jitter': int,  # ナノ秒単位のジッター値
            'memory_percent': float  # メモリ使用率（パーセント）
        }
    """
    # 微小なループ処理の実行時間を計測
    iterations = 1000
    
    # 最初の計測
    start_time = time.perf_counter_ns()
    
    # 微小なループ処理
    _ = sum(range(iterations))
    
    # 中間計測
    mid_time = time.perf_counter_ns()
    
    # もう一度微小なループ処理
    _ = sum(range(iterations))
    
    # 終了計測
    end_time = time.perf_counter_ns()
    
    # 2つの実行時間の差分（ジッター）を計算
    first_duration = mid_time - start_time
    second_duration = end_time - mid_time
    
    # ジッターは2つの実行時間の差分の絶対値
    jitter = abs(second_duration - first_duration)
    
    # メモリ使用率を取得
    memory_percent = psutil.virtual_memory().percent
    
    return {
        'jitter': jitter,
        'memory_percent': memory_percent
    }

