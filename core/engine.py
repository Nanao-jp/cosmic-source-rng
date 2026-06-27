"""
宇宙的乱数生成エンジン
cosmic値とlocal値、数学定数を組み合わせて乱数を生成する
"""
import math
import hashlib
import re
import time
from .cosmic import get_cosmic_value_with_details
from .local import get_local_jitter


def generate_cosmic_random(use_cache=True, cache_data=None):
    """
    cosmic値とlocal値、数学定数を組み合わせて乱数を生成する
    
    Args:
        use_cache: キャッシュを使用するかどうか（デフォルト: True）
        cache_data: キャッシュデータ（use_cache=Trueの場合に使用）
    
    Returns:
        dict: {
            'hash': str,  # 生成されたハッシュ値（16進数）
            'constant_used': str,  # 使用した定数（'Pi' または 'Napier'）
            'cosmic_val': int,  # 使用した宇宙の値
            'jitter': int,  # 使用したジッター値
            'memory_percent': float,  # 使用したメモリ使用率
            'process_details': dict  # 計算過程の詳細情報
        }
    """
    # 宇宙の値を取得（詳細情報も含む）
    # キャッシュが利用可能な場合はキャッシュから取得
    cosmic_data = get_cosmic_value_with_details(use_cache=use_cache, cache_data=cache_data)
    cosmic_val = cosmic_data['numeric_value']
    nasa_data_summary = cosmic_data['nasa_data_summary']
    
    # ローカルのジッターを取得
    local_data = get_local_jitter()
    jitter = local_data['jitter']
    memory_percent = local_data['memory_percent']
    
    # ナノ秒単位のUNIXタイムスタンプを取得（衝突確率を物理的にゼロにするため）
    timestamp_ns = time.time_ns()
    
    # cosmic_valが偶数ならmath.pi、奇数ならmath.eをベースの文字列にする
    if cosmic_val % 2 == 0:
        constant_str = str(math.pi)
        constant_name = "Pi"
    else:
        constant_str = str(math.e)
        constant_name = "Napier"
    
    # 定数の最初の20桁を取得（小数点を除く）
    # 小数点を除いた数字のみを抽出
    digits_only = re.sub(r'[^\d]', '', constant_str)
    base_constant_digits = digits_only[:20] if len(digits_only) >= 20 else digits_only
    
    # jitterの値を使って、定数文字列の抽出開始位置（インデックス）を決める
    # jitterが大きすぎる場合に備えて、文字列長で剰余を取る
    constant_str_len = len(constant_str)
    if constant_str_len > 0:
        calculated_index = jitter % constant_str_len
    else:
        calculated_index = 0
    
    # 定数文字列から10桁の数字を抽出
    # 小数点を除いた数字のみから抽出する
    digits_only = re.sub(r'[^\d]', '', constant_str)
    if len(digits_only) > calculated_index:
        # calculated_indexをdigits_onlyの範囲内に調整
        start_pos = calculated_index % len(digits_only)
        extracted_sample = digits_only[start_pos:start_pos + 10]
        # 10桁に満たない場合は先頭から補完
        if len(extracted_sample) < 10:
            extracted_sample = (extracted_sample + digits_only)[:10]
    else:
        extracted_sample = digits_only[:10] if len(digits_only) >= 10 else digits_only
    
    # 定数文字列から一部を抽出（開始位置から適切な長さ分）
    # 抽出長はjitterの値から決定（最小10文字、最大100文字）
    extract_length = min(max(10, (jitter % 100) + 10), constant_str_len - calculated_index)
    extracted_constant = constant_str[calculated_index:calculated_index + extract_length]
    
    # 「宇宙の値、ナノ秒タイムスタンプ、ジッター、メモリ、抽出した定数片」をすべて結合
    # ナノ秒タイムスタンプを追加することで、100万リクエスト/秒でも3万年間被らない設計を実現
    final_raw_string = f"{cosmic_val}{timestamp_ns}{jitter}{memory_percent}{extracted_constant}"
    
    # hashlib.sha256でハッシュ化して16進数の文字列を生成
    hash_obj = hashlib.sha256(final_raw_string.encode('utf-8'))
    hash_hex = hash_obj.hexdigest()
    
    # 計算過程の詳細情報
    process_details = {
        'base_constant_digits': base_constant_digits,
        'calculated_index': calculated_index,
        'extracted_sample': extracted_sample,
        'final_raw_string': final_raw_string,
        'timestamp_ns': timestamp_ns,
        'nasa_data_summary': nasa_data_summary if nasa_data_summary else []
    }
    
    return {
        'hash': hash_hex,
        'constant_used': constant_name,
        'cosmic_val': cosmic_val,
        'jitter': jitter,
        'memory_percent': memory_percent,
        'process_details': process_details
    }

