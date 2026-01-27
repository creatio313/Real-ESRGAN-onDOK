import argparse
import boto3
from botocore.config import Config
import glob
import json
import os
import subprocess, sys

# 環境変数からパラメータを取得
arg_parser = argparse.ArgumentParser()
arg_parser.add_argument(
    '--output',
    default='/opt/artifact',
    help='出力先ディレクトリを指定します。',
)
arg_parser.add_argument(
    '--inputbucket', 
    default='bucket', 
    help='入力バケット名を指定します。',
)
arg_parser.add_argument(
    '--outputbucket',
    default='bucket', 
    help='出力バケット名を指定します。',
)
arg_parser.add_argument(
    '--tasks', 
    default='[["input.img", 4, "superresolutioned"]]', 
    help='実行タスクをJSON形式で指定します。',
)
arg_parser.add_argument('--s3-endpoint', help='S3互換エンドポイントのURLを指定します。')
arg_parser.add_argument('--s3-secret', help='S3のシークレットアクセスキーを指定します。')
arg_parser.add_argument('--s3-token', help='S3のアクセスキーIDを指定します。')

args = arg_parser.parse_args()

tasks = json.loads(args.tasks)

s3_config = Config(
    # 互換性担保のため、設定を入れる。
    # https://cloud.sakura.ad.jp/news/2025/02/04/objectstorage_defectversion/?_gl=1%2Awg387d%2A_gcl_aw%2AR0NMLjE3NjgxMjIxMDEuQ2owS0NRaUFzWTNMQmhDd0FSSXNBRjZPNlhqR2V1aDdSejdHZkVUbS1SbTVKSkRBeE9CUGoxQ2FxUjlRQ3BSbFN5Vlo2M1h4UTlXVnVBa2FBdkxyRUFMd193Y0I.%2A_gcl_au%2ANzM1ODg0ODM0LjE3NjA5NjM5MDYuMTQzMDE2MzgwNS4xNzY4MDU2MzU3LjE3NjgwNjE2NTg.
    request_checksum_calculation="when_required",
    response_checksum_validation="when_required",
)
# キー情報を元にS3APIクライアントを作成
s3 = boto3.client(
    's3',
    endpoint_url=args.s3_endpoint if args.s3_endpoint else None,
    aws_access_key_id=args.s3_token,
    aws_secret_access_key=args.s3_secret,
    config=s3_config,
)

print('Start super resolution')
# 超解像処理の実行
for task in tasks:
    inputFileName, outScale, suffix = task
    inpath = os.path.join('/opt/input/', inputFileName)
    print('Downloading super resolution input file from S3:', inputFileName)
    s3.download_file(args.inputbucket, inputFileName, inpath)
    print('Super resolution input file downloaded:', inpath)

    subprocess.run([
        sys.executable, "inference_realesrgan.py",
        "--input", inpath,
        "--output", args.output,
        "--outscale", str(outScale),
        "--suffix", suffix,
    ], check=True)

# さくらのオブジェクトストレージに格納
print('Start uploading to S3')
# 出力フォルダ内のファイルを順々に同名アップロード
files = glob.glob(os.path.join(args.output, '*'))
for file in files:
    print(os.path.basename(file))

    s3.upload_file(
        Filename=file,
        Bucket=args.outputbucket,
        Key=os.path.basename(file),
    )