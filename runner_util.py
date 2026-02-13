import boto3
from botocore.config import Config

def genObjectStorageClient(endpoint: str, token: str, secret: str) -> any:
    """S3互換APIクライアントを生成する。"""
    # S3クライアント作成用の設定
    object_storage_config = Config(
        # 互換性担保のため、設定を入れる。
        # https://cloud.sakura.ad.jp/news/2025/02/04/objectstorage_defectversion/?_gl=1%2Awg387d%2A_gcl_aw%2AR0NMLjE3NjgxMjIxMDEuQ2owS0NRaUFzWTNMQmhDd0FSSXNBRjZPNlhqR2V1aDdSejdHZkVUbS1SbTVKSkRBeE9CUGoxQ2FxUjlRQ3BSbFN5Vlo2M1h4UTlXVnVBa2FBdkxyRUFMd193Y0I.%2A_gcl_au%2ANzM1ODg0ODM0LjE3NjA5NjM5MDYuMTQzMDE2MzgwNS4xNzY4MDU2MzU3LjE3NjgwNjE2NTg.
        request_checksum_calculation="when_required",
        response_checksum_validation="when_required",
    )

    # キー情報を元にS3APIクライアントを作成
    object_storage_client = boto3.client(
        's3',
        endpoint_url=endpoint,
        aws_access_key_id=token,
        aws_secret_access_key=secret,
        config=object_storage_config,
    )

    return object_storage_client