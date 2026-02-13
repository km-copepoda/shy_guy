Shy Guy - 顔モザイクWebアプリケーション 構築プロンプト
以下の仕様に従い、画像をアップロードすると自動で顔を検出してモザイク処理した画像を返すフルスタックWebアプリケーションを構築してください。

#1 プロジェクト概要
アプリ名: Shy Guy

機能: ユーザーが画像をアップロードすると、AIが顔を自動で検出し、ピクセル化モザイクを適用した画像を返す

バックエンド: Python / FastAPI

フロントエンド: React + TypeScript + Vite

デプロイ先: AWS Lambda (Docker) + S3 + CloudFront (Terraformで管理)

#2 ディレクトリ構成
Plaintext
shy_guy/
├── backend/
│   ├── main.py              # FastAPIエントリポイント
│   ├── handler.py           # AWS Lambda用Mangumハンドラ
│   ├── requirements.txt      # Python依存関係
│   ├── Dockerfile           # Lambda コンテナイメージ
│   ├── routers/
│   │   ├── __init__.py
│   │   └── mosaic.py        # POST /api/mosaic エンドポイント
│   ├── services/
│   │   ├── __init__.py
│   │   ├── face_detector.py  # OpenCV/YuNet 抽出
│   │   └── mosaic_processor.py # Pillow モザイク処理
│   ├── models/
│   │   └── YuNet ONNXモデル (自動DL、.gitignore対象)
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py       # テスト用fixture
│       ├── test_api.py       # APIエンドポイントテスト
│       ├── test_face_detector.py # 顔検出ユニットテスト
│       └── test_mosaic_processor.py # モザイク処理ユニットテスト
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── src/
│   │   ├── main.tsx          # エントリポイント
│   │   ├── App.tsx           # メインコンポーネント
│   │   ├── App.css           # スタイル
│   │   ├── index.css         # グローバルCSS
│   │   ├── components/
│   │   │   ├── ImageUploader.tsx # ドラッグ&ドロップ/クリック選択
│   │   │   └── ImagePreview.tsx  # 元画像 & モザイク済み画像表示
│   │   └── hooks/
│   │       └── useMosaicApi.ts   # API通信カスタムフック
└── infra/
    ├── main.tf              # Terraformプロバイダ設定
    ├── variables.tf         # 変数定義 (バリデーション付き)
    ├── lambda.tf            # ECR / IAM / Lambda / API Gateway
    ├── frontend.tf          # S3 / CloudFront / OAC
    ├── outputs.tf           # 出力定義
    └── deploy.sh            # ワンコマンドデプロイスクリプト
#3 バックエンド詳細
#3.1 技術選定と理由
OpenCV/YuNet (cv2.FaceDetectorYN): 高速・軽量。ONNXモデルファイル (~340KB) で完結。pip installのみ。MediaPipeは新バージョンでAPI定義が壊れ、insightfaceはmacOSでのコンパイルに失敗するため不採用。

"opencv-python-headless": サーバー環境にGUIが不要なため。opencv-pythonやopencv-contrib-pythonと共存不可（パッケージ競合する）ので必ずheadless単体を使う！

Pillow: モザイク処理（縮小→拡大）と画像変換に使用。cv2.imencodeは上記パッケージ競合でエラーになり得るので画像の読み書きはすべてPillowで統一！

FastAPI + Mangum: 1バイナリ（ASGI）をAWS Lambdaで動かすためのアダプタ。

#3.2 main.py
Python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from routers import mosaic

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 'lifespan' async context manager で FaceDetector をアプリ起動時に1回だけ初期化。app.state.face_detector に格納
    # CORS 設定: CORS_ORIGINS (カンマ区切り) で設定可能。デフォルトは http://localhost:5173
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(mosaic.router, prefix="/api", tags=["mosaic"])

# CORS設定
origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
    allow_credentials=False
)

@app.get("/health")
def health_check():
    return {"status": "ok"}
#3.3 routers/mosaic.py
エンドポイント: POST /api/mosaic

クエリパラメータ: pixel_size (int, default=20, min=1, max=100)

リクエストバリデーション:

Content-Type: image/jpeg, image/png, image/webp のみ、それ以外は400

ファイルサイズ: 10MB上限、超過は413

処理フロー:

request.app.state.face_detector.detect(image_array[image]) で顔検出

apply_mosaic(image, faces, pixel_size) でモザイク処理

PNG入力→PNG出力、それ以外は JPEG(quality=90) で出力

X-Faces-Detected ヘッダーに検出した顔の数を設定

レスポンスヘッダー: X-Faces-Detected に枚数（通常範囲内ならクリップ済み）

logging.getLogget(__name__) でログ出力 (pytest不使用)

#3.4 services/face_detector.py
YuNet ONNXモデル: backend/models/ に自動ダウンロード (初回のみ)

URL: https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx

FaceDetectorクラス:

コンストラクタ: score_threshold=0.9, nms_threshold=0.3

detect(image_np): cv2.FaceDetectorYN(created) で検出

入力: RGB numpy配列

出力: [[x, y, w, h], ...] の int タプル

注意: YuNetは画像サイズが学習時と一致する必要があるので、呼び出しごとにインスタンス生成

#3.5 services/mosaic_processor.py
Python
from PIL import Image

def apply_mosaic(image: Image.Image, faces, pixel_size: int = 20) -> Image.Image:
    # image.copy() で元画像を保護 (非破壊)
    # 各顔領域に対して:
    # 1. crop で領域を切り出し
    # 2. resize((w//pixel_size, h//pixel_size), Image.BILINEAR) で縮小
    # 3. resize((w, h), Image.NEAREST) でサイズに拡大 -> ピクセル化モザイク効果
    # 4. paste で元画像に貼り付け
    # pixel_size が大きいほどモザイクが強い (デフォルト20)
    return image
#3.6 handler.py (Lambda用)
Python
from mangum import Mangum
from main import app

handler = Mangum(app, lifespan="off")
# lifespan="off": Lambda環境では lifespan イベントが使えないための無効化
#3.7 Dockerfile
ベースイメージ: public.ecr.aws/lambda/python:3.12

ビルド時に: python -m ensure_model() を実行してYuNetモデルをコンテナに含める (コールドスタート高速化)

CMD: "handler.handler"

#3.8 requirements.txt
Plaintext
fastapi==0.115.0
pydantic[standard]==2.9.2
python-multipart==0.0.12
mangum==0.19.0
numpy==1.26.0
opencv-python-headless==4.10.0
Pillow==10.0.0
requests==2.27.0
httpcore==0.19.0
重要: opencv-python, opencv-contrib-python と opencv-python-headless は同時使用不可。必ず opencv-python-headless のみ使用すること。

#3.9 テスト
pytest で実行。backend/ をカレントディレクトリにして python -m pytest で実行。

#### conftest.py
sample_rgb_image: 100x100の単色 numpy 配列 (fixture)

sample_pil_image: 100x100の単色 PIL Image (fixture)

create_test_png() / create_test_jpg(): テスト用画像バイト列生成ヘルパー

#### test_face_detector.py (テスト)
戻り値テスト: faces が (x, y, w, h) の int タプル

単色画像でゼロ: 顔がない場合に 0 枚

バウンディングボックスが画像範囲内

高閾値 (score_threshold=0.99) で 0 でない

#### test_mosaic_processor.py (テスト)
画像が保護される

出力サイズ不変

モザイク処理で平均色に近い色になる (グラデーション画像で検証)

非顔領域が変更されない (非破壊確認)

pixel_size=1 で動作

大きな pixel_size で動作

画像が1px未満でクラッシュしない

元画像が変更されない (非破壊確認)

#### test_api.py (テスト)
FastAPI TestClient 使用

ヘルスチェック

JPEG/PNGアップロード→正常レスポンス

返却画像がダウンロード可能、サイズ一致

非対応フォーマット→400

壊れたデータ→400

pixel_size バリデーション: 1~100 (0, -1, 101, 102 はエラー)

X-Faces-Detected ヘッダーが数値

単色画像でゼロ

注意: test_api.py の pixel_size バリデーションテストで pixel_size=50 を 422 として検証しているが、ルーターの抑制は len=100 に変更済み。テスト側も len=100 に合わせて修正が必要（pixel_size=101 で 422 になるようにする）。

#4 フロントエンド詳細
#4.1 技術スタック
React 19 + TypeScript + Vite 7

npm create vite@latest frontend --template react-ts でスキャフォールド

ESLint + typescript-eslint + react-hooks + react-refresh

#4.2 vite.config.ts
開発用プロキシ: /api -> http://localhost:8000 (CORS回避)

#4.3 App.tsx
状態管理:

originalUrl: アップロードした元画像のObjectURL

useMosaicApi フックから processImage, result, isLoading, error, reset を取得

handlerFileSelect:

URL.createObjectURL で元画像プレビュー用URL生成

選択された画像があれば URL.revokeObjectURL でメモリ解放

processImage(file) でAPI呼び出し

reset: で各状態クリア。processImageUrl もAPI側で消し込む

表示: タイトル「Shy Guy」、サブタイトル + ImageUploader + ローディング/エラー表示 + ImagePreview

#4.4 components/ImageUploader.tsx
Props: onFileSelect: (file: File) => void, disabled?: boolean

受け入れ形式: image/jpeg, image/png, image/webp

入力方法:

ドラッグ&ドロップ (onDrop, onDragOver, onDragLeave)

クリックで選択 (input type="file" を隠す)

スタイル: 破線ボーダー、ホバーでハイライト、ドラッグ中は背景色変化

不正な形式は alert() で警告

disabled 時はクリック不可、マウスカーソル無効、CSSで不透明

#4.5 components/ImagePreview.tsx
Props: originalUrl, processedUrl, facesDetected

表示: originalUrl が null なら何も表示しない

レイアウト: 元画像とモザイク済み画像をフレックスボックスで横並び表示

レスポンシブ: 画面サイズに応じて縦並びに変更、レスポンシブ (flex-wrap: wrap)

情報表示:

original: 「元画像」が表示されました

facesDetected: 「N 個の顔が検出されました」

- 0の場合: 「顔が検出されませんでした」

ダウンロードボタン: processedUrl を download="mosaic_result.png" で提供

#4.6 hooks/useMosaicApi.ts
状態: result (ImageURL, facesDetected), null, isLoading, error

Ref: prevUrlRef (前回のObjectURL、メモリリーク防止)、abortRef (AbortController)

processImage(file, pixelSize=20):

ファイルサイズチェック (10MB、バックエンドと同調)

前回のURLを URL.revokeObjectURL で解放

前のリクエストを abortRef.current.abort() でキャンセル

fetch("/api/mosaic?pixel_size=${pixelSize}"): method: "POST", body: FormData, signal で送信

レスポンス (blob): URL.createObjectURL で表示用URL生成

X-Faces-Detected ヘッダーから検出数取得

AbortError は無視 (正常キャンセル)

reset: abort + URL.revoke + 状態クリア

#4.7 スタイル (App.css)
ダークモード対応 (prefers-color-scheme)

uploader: 破線ボーダー、ホバーで青ハイライト、ドラッグ中は背景色変化

preview-container: フレックス横並び、レスポンシブ (flex-wrap: wrap)

image: max-width: 100%, border-radius: 8px

download-btn: 青系ボタン (#007bff)

loading: 青テキスト、error: 赤テキスト + 赤ボーダー

#5 インフラ (Terraform) 詳細
#5.1 ベストプラクティス
"data sources": CloudFront マネージドポリシーは名前参照で取得（マジックIDを使わない）

"aws_iam_policy_document": JSON文字列ではなくTerraformリソースでIAMポリシーを定義

"locals": local_name マリソース名を統一。local_common_tags で共通タグ

"tags": プロジェクト名、作成者、環境、ManagedBy タグを全リソースに付与

"variable validation": project_name に正規表現、lambda_memory_size に範囲制約

"ECR lifecycle policy": 最新イメージのみ保持

#5.2 AWS構成
User -> CloudFront:

/ (デフォルト) -> S3 (React ビルド済みファイル)

--- OAC アクセス制御

--- SPA fallback: 403 -> /index.html (200)

/api/* -> API Gateway (HTTP API) -> Lambda (Docker/ECR)

"CloudFront": フロントとAPIを同一ドメインで配信。CORS設定不要

"S3": パブリックアクセスブロック、OAC経由のみ

"API Gateway": HTTP API (REST API より安い)、CORS設定あり (expose_headers: ["X-Faces-Detected"])

"Lambda": Dockerイメージ、メモリ512MB、タイムアウト30秒、lifecycle でイメージを自動削除

"ECR": scan_on_push=true、lifecycle で古いイメージを自動削除

#5.3 deploy.sh
terraform apply

Docker ビルド (platform linux/amd64) -> ECR push

aws lambda update-function-code でLambda更新

npm run build -> aws s3 sync でフロントエンドデプロイ

aws cloudfront create-invalidation --paths "/*" でキャッシュクリア

#6 起動方法
## ローカル開発
bash:

Bash
# バックエンド
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
PYTHONDONTWRITEBYTECODE=1 python -m uvicorn main:app --reload --port 8000

# フロントエンド (別ターミナル)
cd frontend
npm install
npm run dev
"注意": uvicorn main:app ではなく python -m uvicorn main:app を使うこと（venv外のシステムPythonのuvicornが使われる問題を防ぐ）
YuNetモデルは初回起動時に自動ダウンロードされる

## テスト実行
bash:

Bash
cd backend
python -m pytest -v
## AWS デプロイ
bash:

Bash
cd infra
chmod +x deploy.sh
./deploy.sh
#7 重要な実装上の注意点
## OpenCV/V2パッケージ競合
opencv-python-headless と opencv-python / opencv-contrib-python は共存不可。pip list | grep opencv で確認し、headless以外があればアンインストールすること。

## MediaPipeを使わない理由
mediapipe 0.10.x で mp.solutions.face_detection レガシーAPIが削除され、新しいタスクAPIに移行が必要。さらにmacOSでの動作が不安定。YuNetはOpenCVに内蔵されており追加依存なしで動作する。

## insightfaceを使わない理由
macOSでのコンパイル時にエラー（cmath ヘッダーが見つからない）が発生し、SDKROOTを設定しても解決しなかった。

## 画像の入出力はPillowに統一
cv2.imencode / cv2.imdecode はパッケージ競合で AttributeError になる場合がある。画像の読み書きはすべてPillowで行い、OpenCVは検出（numpy配列操作）のみに使用する。

## フロントエンドのメモリリーク防止
URL.createObjectURL で生成したURLは必ず URL.revokeObjectURL で解放する。useMosaicApi フック内の prevUrlRef と App.tsx の setOriginalUrl コールバック内の両方で管理。

## AbortController
連続アップロード時に前のリクエストをキャンセルする。AbortError はエラー表示せずに無視する。

#8 今後の拡張候補 (未実装)
フロントエンドテスト (Vitest + React Testing Library + MSW)

モザイク強度のスライダー変更

検出モデルの選択 (models/ node_modules/ を除く、terraform.tfstate, .env/, .pytest_cache/, .vercel/, dist/, pycache/)