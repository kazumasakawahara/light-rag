# LightRAG Docker デプロイ

複数の LLM バックエンドをサポートする軽量なナレッジグラフ検索拡張生成システムです。

## 🚀 準備

### リポジトリのクローン：

```bash
# Linux/MacOS
git clone https://github.com/HKUDS/LightRAG.git
cd LightRAG
```
```powershell
# Windows PowerShell
git clone https://github.com/HKUDS/LightRAG.git
cd LightRAG
```

### 環境の設定：

```bash
# Linux/MacOS
cp .env.example .env
# .env を好みの設定に編集してください
```
```powershell
# Windows PowerShell
Copy-Item .env.example .env
# .env を好みの設定に編集してください
```

LightRAG は `.env` ファイルの環境変数で設定できます：

**サーバー設定**

- `HOST`：サーバーホスト（デフォルト：0.0.0.0）
- `PORT`：サーバーポート（デフォルト：9621）

**LLM 設定**

- `LLM_BINDING`：使用する LLM バックエンド（lollms/ollama/openai）
- `LLM_BINDING_HOST`：LLM サーバーのホスト URL
- `LLM_MODEL`：使用するモデル名

**Embedding 設定**

- `EMBEDDING_BINDING`：Embedding バックエンド（lollms/ollama/openai）
- `EMBEDDING_BINDING_HOST`：Embedding サーバーのホスト URL
- `EMBEDDING_MODEL`：Embedding モデル名

**RAG 設定**

- `MAX_ASYNC`：最大非同期操作数
- `MAX_TOKENS`：最大トークンサイズ
- `EMBEDDING_DIM`：Embedding の次元数

## 🐳 Docker デプロイ

Docker Desktop がインストールされていれば、Docker の手順はすべてのプラットフォームで共通です。

### ビルドの最適化

Dockerfile は BuildKit キャッシュマウントを使用してビルドパフォーマンスを大幅に向上させます：

- **自動キャッシュ管理**：`# syntax=docker/dockerfile:1` ディレクティブにより BuildKit が自動的に有効になります
- **高速な再ビルド**：`uv.lock` または `bun.lock` ファイルが変更された場合のみ、変更された依存関係をダウンロードします
- **効率的なパッケージキャッシュ**：UV および Bun のパッケージダウンロードがビルド間でキャッシュされます
- **手動設定不要**：Docker Compose および GitHub Actions でそのまま動作します

### LightRAG サーバーの起動：

```bash
docker compose up -d
```

インタラクティブセットアップを使用した場合は、生成されたスタックを以下で起動します：

```bash
docker compose -f docker-compose.final.yml up -d
```

インタラクティブセットアップは `.env` をホストで使用可能な状態に保ちます。`postgres` や `host.docker.internal` などのコンテナ専用ホスト名、および `/app/data/certs/` 配下のステージングされた SSL パスは、`.env` に書き戻すのではなく、生成された `docker-compose.final.yml` の `lightrag` サービスに注入されます。
再実行時、`docker-compose.final.yml` 内のウィザード管理のサービスブロックは、変更がなければデフォルトで保持されます。管理対象ブロックを修復または完全に再生成するには、`make env-base-rewrite` または `make env-storage-rewrite` で対応するセットアップターゲットを再実行してください。

生成されたスタックにローカル Milvus が含まれている場合、compose は起動時にリポジトリの `.env` またはエクスポートされたシェル環境から `MINIO_ACCESS_KEY_ID` と `MINIO_SECRET_ACCESS_KEY` を解決します。生成された compose ファイルはこれらの値をスナップショットしないため、いずれかの変数が欠けていると `docker compose` は直ちに終了します。

生成されたスタックを localhost 以外に公開する前に、以下を実行してください：

```bash
make env-security-check
```

このコマンドは、認証の欠如、安全でないホワイトリスト設定、脆弱な JWT シークレット、およびその他のセットアップレベルのセキュリティリスクについて、ファイルを書き換えることなく現在の `.env` を監査します。

LightRAG Server はデータストレージに以下のパスを使用します：

```
data/
├── rag_storage/    # RAG データの永続化
└── inputs/         # 入力ドキュメント
```

### オプション：ローカル vLLM Embedding およびリランカー

Embedding やリランキングを vLLM でローカル実行するには、`make env-base` を実行し、Docker で Embedding モデルとリランクサービスをローカル実行するかどうかの質問に `yes` と答えてください。
これにより、Embedding サービスがポート 8001 でローカル vLLM サーバーを使用して `BAAI/bge-m3` を使用するように設定され、ポート 8000 に `vllm-rerank` サービスも追加できます。

また、後から `make env-base` を再実行し、リランク Docker プロンプトのみを有効にすることで、`vllm-rerank` サービスを自動的に追加することもできます。
vLLM は `cohere` バインディングで動作する `v1/rerank` エンドポイントを提供します。

GPU ホスト向けの `docker-compose.override.yml` の例（Embedding + リランカー）：

```yaml
services:
  vllm-embed:
    image: vllm/vllm-openai:latest
    runtime: nvidia
    command: >
      --model BAAI/bge-m3
      --port 8001
      --dtype float16
    ports:
      - "8001:8001"
    volumes:
      - ./data/hf-cache:/root/.cache/huggingface
    ipc: host
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]

  vllm-rerank:
    image: vllm/vllm-openai:latest
    runtime: nvidia
    command: >
      --model BAAI/bge-reranker-v2-m3
      --port 8000
      --dtype float16
    ports:
      - "8000:8000"
    volumes:
      - ./data/hf-cache:/root/.cache/huggingface
    ipc: host
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
```

CPU のみのホストの場合は、代わりに公式の CPU イメージを使用してください：

```yaml
services:
  vllm-embed:
    image: vllm/vllm-openai-cpu:latest
    command: >
      --model BAAI/bge-m3
      --port 8001
      --dtype float32
    ports:
      - "8001:8001"
    volumes:
      - ./data/hf-cache:/root/.cache/huggingface

  vllm-rerank:
    image: vllm/vllm-openai-cpu:latest
    command: >
      --model BAAI/bge-reranker-v2-m3
      --port 8000
      --dtype float32
    ports:
      - "8000:8000"
    volumes:
      - ./data/hf-cache:/root/.cache/huggingface
```

Embedding とリランクの設定を `.env` に追加します：

```bash
EMBEDDING_BINDING=openai
EMBEDDING_MODEL=BAAI/bge-m3
EMBEDDING_DIM=1024
EMBEDDING_BINDING_HOST=http://localhost:8001/v1
EMBEDDING_BINDING_API_KEY=local-key
VLLM_EMBED_DEVICE=cpu

RERANK_BINDING=cohere
RERANK_MODEL=BAAI/bge-reranker-v2-m3
RERANK_BINDING_HOST=http://localhost:8000/rerank
RERANK_BINDING_API_KEY=local-key
VLLM_RERANK_DEVICE=cpu
```

LightRAG が Docker 内で実行され、vLLM がホスト上で実行されている場合、生成された compose ファイルはこれらのエンドポイントを以下のように書き換えます：

```bash
EMBEDDING_BINDING_HOST=http://host.docker.internal:8001/v1
RERANK_BINDING_HOST=http://host.docker.internal:8000/rerank
```

GPU を使用する場合は、以下を設定します：

```bash
VLLM_EMBED_DEVICE=cuda
VLLM_RERANK_DEVICE=cuda
```

NVIDIA Container Toolkit がインストールされており、ホストに CUDA ドライバーが利用可能であることを確認してください。
セットアップウィザードは、`cpu` デバイスの場合はデフォルトで CPU イメージを、`cuda` デバイスの場合は GPU イメージを使用します。
`make env-base` を再実行する際、既存の `VLLM_EMBED_DEVICE` / `VLLM_RERANK_DEVICE` の値は、新しい GPU 自動検出結果で上書きされるのではなく保持されます。
これらのテンプレートは対応する vLLM の `--dtype`（CPU では `float32`、CUDA では `float16`）を既にピン留めしているため、別途 `VLLM_*_DTYPE` 環境変数は不要です。

### SSL 証明書

セットアップウィザードは、compose ファイルを生成する前に TLS 証明書ファイルを `./data/certs/` 配下にステージングします。
これにより、生成されたホストマウントがデフォルトの Docker デプロイで使用される同じ `./data` ルート配下に維持されます。

### PostgreSQL イメージ

インタラクティブセットアップでは、PostgreSQL のデフォルトとして `gzdaniel/postgres-for-rag:16.6` を使用します。
このイメージには Apache AGE と pgvector の両方がバンドルされているため、追加のエクステンションセットアップなしで `PGGraphStorage` および `PGVectorStorage` で生成されたスタックが動作します。

### アップデート

Docker コンテナを更新するには：
```bash
docker compose pull
docker compose down
docker compose up
```

### オフラインデプロイ

`transformers`、`torch`、`cuda` を必要とするソフトウェアパッケージは、Docker イメージにプリインストールされていません。そのため、Docling などのドキュメント抽出ツールや、Hugging Face や LMDeploy などのローカル LLM モデルは、オフライン環境では使用できません。これらの高い計算リソースを要求するサービスは、LightRAG に統合すべきではありません。Docling は分離され、スタンドアロンサービスとしてデプロイされる予定です。

## 📦 Docker イメージのビルド

### ローカル開発・テスト用

```bash
# Docker Compose でビルドして実行（BuildKit は自動的に有効）
docker compose up --build

# または、必要に応じて BuildKit を明示的に有効化
DOCKER_BUILDKIT=1 docker compose up --build
```

**注意**：BuildKit は Dockerfile の `# syntax=docker/dockerfile:1` ディレクティブにより自動的に有効化され、最適なキャッシュパフォーマンスが保証されます。

### 本番リリース用

**マルチアーキテクチャのビルドとプッシュ**：

```bash
# 提供されたビルドスクリプトを使用
./docker-build-push.sh
```

**ビルドスクリプトの動作**：

- Docker レジストリのログイン状態を確認
- buildx ビルダーを自動的に作成/使用
- AMD64 と ARM64 の両アーキテクチャ向けにビルド
- GitHub Container Registry（ghcr.io）にプッシュ
- マルチアーキテクチャマニフェストを検証

**前提条件**：

マルチアーキテクチャイメージをビルドする前に、以下を確認してください：

- Buildx サポートのある Docker 20.10+
- 十分なディスク容量（オフラインイメージ用に 20GB+ を推奨）
- レジストリアクセス認証情報（イメージをプッシュする場合）
