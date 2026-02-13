import runner_util
import argparse
import json
import logging
from pathlib import Path
import subprocess, sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')

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
    default='[["input.jpg", 4, "superresolutioned"]]', 
    help='実行タスクをJSON形式で指定します。',
)
arg_parser.add_argument('--s3-endpoint', help='S3互換エンドポイントのURLを指定します。')
arg_parser.add_argument('--s3-secret', help='S3のシークレットアクセスキーを指定します。')
arg_parser.add_argument('--s3-token', help='S3のアクセスキーIDを指定します。')
args = arg_parser.parse_args()

# キー情報を元にS3APIクライアントを作成
# S3互換APIクライアントの生成
if args.s3_token and args.s3_secret and args.s3_endpoint:
    s3_client = runner_util.genObjectStorageClient(endpoint=args.s3_endpoint,
                            token=args.s3_token,
                            secret=args.s3_secret)
else:
    logging.error('S3互換APIクライアントの情報が不足しています。処理を中断します。')
    sys.exit(1)

logging.info('主処理開始')
tasks = json.loads(args.tasks)
for task in tasks:
    input_file_path, out_scale, suffix = task
    # タスク情報を取得し、ファイルパス・プロンプトが存在しない場合はスキップ
    if not input_file_path or not out_scale:
        logging.warning(f'必須パラメータが不足しているため、処理をスキップしました。: {task}')
        continue

    logging.info(f'超解像タスク開始 -> ファイルパス: {input_file_path}, 出力倍率: {out_scale}, 接尾辞: {suffix}')

    # ローカルの保存先パスを生成。フォルダがない場合は作成する。
    local_orgin_path = Path("/opt/input") / input_file_path
    local_orgin_path.parent.mkdir(parents=True, exist_ok=True)
    local_output_dir = ( Path(args.output) / input_file_path ).parent
    local_output_dir.mkdir(parents=True, exist_ok=True)

    try:
        logging.info(f'入力画像を取得します。バケット: {args.inputbucket}, ファイルパス: {input_file_path}')
        s3_client.download_file(
            Bucket=args.inputbucket,
            Key=input_file_path,
            Filename=local_orgin_path
            )
    except Exception as e:
        logging.error(f'入力画像の取得に失敗しました。: {e}')
        continue
    else:
        logging.info('入力画像の取得に成功しました。')

    logging.info('超解像処理を実行します。')
    subprocess.run([
        sys.executable, "inference_realesrgan.py",
        "--input", local_orgin_path,
        "--output", local_output_dir,
        "--outscale", str(out_scale),
        "--suffix", suffix,
    ], check=True)
    logging.info('超解像処理が完了しました。')

# さくらのオブジェクトストレージに格納
logging.info('出力フォルダ内のファイルを順々にオブジェクトストレージにアップロードします。')

for file in Path(args.output).rglob("*"):
    if not file.is_file():
        continue
    # artifact配下の相対パスをキーにする
    key = str(file.relative_to(Path(args.output)))

    logging.info(f'ファイル{key}をオブジェクトストレージにアップロードします。')
    s3_client.upload_file(
        Filename=file,
        Bucket=args.outputbucket,
        Key=key,
    )
    logging.info('オブジェクトストレージへのアップロードが完了しました。')

logging.info('主処理終了')