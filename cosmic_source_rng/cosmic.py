"""
宇宙の値（Cosmic Value）を取得するモジュール
NASA DONKI APIから太陽活動データを取得し、数値に変換する
"""
import os
import requests
import time
import hashlib
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()


def get_cosmic_value():
    """
    NASA DONKI APIから太陽活動データを取得し、数値に変換する
    
    Returns:
        int: データから生成された数値（ハッシュの総和など）
             エラー時やデータ空時は現在のUnixタイムスタンプ
    """
    result = get_cosmic_value_with_details()
    return result['numeric_value']


def _fetch_nasa_data():
    """
    NASA DONKI APIから太陽活動データを取得する内部関数
    
    Returns:
        dict: {
            'numeric_value': int,  # データから生成された数値
            'nasa_data_summary': list  # NASAの生のIDやイベント名のリスト
        }
    """
    # .envファイルからAPIキーを取得
    api_key = os.getenv('NASA_API_KEY', 'DEMO_KEY')
    
    # APIキーが設定されていない場合の警告（DEMO_KEYは使用可能だが制限あり）
    if api_key == 'DEMO_KEY':
        print("Warning: Using DEMO_KEY. For better results, set NASA_API_KEY in .env file")
    
    base_url = "https://api.nasa.gov/DONKI"
    
    # 複数のエンドポイントからデータを取得を試みる
    # CME（Coronal Mass Ejections）を優先的に取得
    endpoints = [
        ("/CME", "activityID"),  # Coronal Mass Ejections - 太陽風CME
        ("/FLR", "flrID"),       # Solar Flares
        ("/GST", "gstID"),       # Geomagnetic Storms
        ("/RBE", "rbeID"),       # Radiation Belt Enhancements
        ("/HSS", "hssID"),       # High Speed Streams
    ]
    
    all_seed_data = []
    nasa_data_summary = []  # 生のIDやイベント名を保存
    
    for endpoint, id_field in endpoints:
        try:
            url = f"{base_url}{endpoint}"
            params = {
                "api_key": api_key,
            }
            
            # 最新のデータを取得するため、過去30日間のデータをリクエスト
            # （startDateパラメータはオプショナル）
            
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            # データがリストの場合（通常のケース）
            if isinstance(data, list) and len(data) > 0:
                # 最新のデータから取得（リストの最後の要素が最新の可能性が高い）
                # または最初の要素から取得
                for item in data[-5:]:  # 最新5件を取得
                    if isinstance(item, dict):
                        # 指定されたIDフィールドを探す
                        if id_field in item and item[id_field]:
                            id_value = str(item[id_field])
                            all_seed_data.append(id_value)
                            nasa_data_summary.append(f"{endpoint}:{id_value}")
                        
                        # activityIDも探す（一部のエンドポイントで使用）
                        if "activityID" in item and item["activityID"]:
                            activity_id = str(item["activityID"])
                            if activity_id not in all_seed_data:
                                all_seed_data.append(activity_id)
                                nasa_data_summary.append(f"{endpoint}:activityID:{activity_id}")
                        
                        # CMEの場合は、startTimeやsourceLocationも追加してシードを強化
                        if endpoint == "/CME":
                            if "startTime" in item and item["startTime"]:
                                start_time = str(item["startTime"])
                                all_seed_data.append(start_time)
                                nasa_data_summary.append(f"CME:startTime:{start_time}")
                            if "sourceLocation" in item and item["sourceLocation"]:
                                source_loc = str(item["sourceLocation"])
                                all_seed_data.append(source_loc)
                                nasa_data_summary.append(f"CME:sourceLocation:{source_loc}")
                            
                            # CMEの場合は、noteやlinkも追加（イベント名として）
                            if "note" in item and item["note"]:
                                nasa_data_summary.append(f"CME:note:{item['note'][:100]}")  # 最初の100文字
                            if "link" in item and item["link"]:
                                nasa_data_summary.append(f"CME:link:{item['link']}")
            
            # データが辞書の場合
            elif isinstance(data, dict):
                if id_field in data and data[id_field]:
                    id_value = str(data[id_field])
                    all_seed_data.append(id_value)
                    nasa_data_summary.append(f"{endpoint}:{id_value}")
                if "activityID" in data and data["activityID"]:
                    activity_id = str(data["activityID"])
                    if activity_id not in all_seed_data:
                        all_seed_data.append(activity_id)
                        nasa_data_summary.append(f"{endpoint}:activityID:{activity_id}")
                # ネストされたデータも探索
                for key, value in data.items():
                    if isinstance(value, (dict, list)):
                        _extract_ids(value, all_seed_data, nasa_data_summary, endpoint)
        
        except requests.exceptions.RequestException as e:
            # ネットワークエラーやAPIエラーの場合、次のエンドポイントを試す
            continue
        except (ValueError, KeyError) as e:
            # JSONパースエラーなどの場合、次のエンドポイントを試す
            continue
    
    # 取得したデータを数値シードに変換
    if all_seed_data:
        # すべてのデータを結合してハッシュの総和を計算
        combined_string = "|".join(all_seed_data)  # 区切り文字で結合
        
        # SHA256ハッシュを計算
        hash_obj = hashlib.sha256(combined_string.encode('utf-8'))
        hash_hex = hash_obj.hexdigest()
        
        # 16進数を10進数の数値に変換
        # ハッシュ全体を使用してより大きな数値を生成
        numeric_value = int(hash_hex, 16)
        
        return {
            'numeric_value': numeric_value,
            'nasa_data_summary': nasa_data_summary
        }
    else:
        # データが空の場合は現在のUnixタイムスタンプを返す
        return {
            'numeric_value': int(time.time()),
            'nasa_data_summary': []
        }


def get_cosmic_value_with_details(use_cache=True, cache_data=None):
    """
    NASA DONKI APIから太陽活動データを取得し、数値と詳細情報を返す
    キャッシュが利用可能な場合はキャッシュから取得する
    
    Args:
        use_cache: キャッシュを使用するかどうか（デフォルト: True）
        cache_data: キャッシュデータ（use_cache=Trueの場合に使用）
    
    Returns:
        dict: {
            'numeric_value': int,  # データから生成された数値
            'nasa_data_summary': list  # NASAの生のIDやイベント名のリスト
        }
    """
    # キャッシュが利用可能で、use_cacheがTrueの場合はキャッシュから取得
    if use_cache and cache_data is not None:
        return cache_data
    
    # キャッシュが利用できない場合は直接APIを呼び出す
    return _fetch_nasa_data()


def _extract_ids(data, id_list, nasa_data_summary=None, endpoint=""):
    """
    再帰的にIDを抽出するヘルパー関数
    
    Args:
        data: 探索するデータ（dict, list, その他）
        id_list: IDを追加するリスト
        nasa_data_summary: NASAデータのサマリーリスト（オプション）
        endpoint: エンドポイント名（オプション）
    """
    if isinstance(data, dict):
        for key, value in data.items():
            if "ID" in key.upper() and isinstance(value, (str, int)):
                id_value = str(value)
                id_list.append(id_value)
                if nasa_data_summary is not None:
                    nasa_data_summary.append(f"{endpoint}:{key}:{id_value}")
            elif isinstance(value, (dict, list)):
                _extract_ids(value, id_list, nasa_data_summary, endpoint)
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, (dict, list)):
                _extract_ids(item, id_list, nasa_data_summary, endpoint)

