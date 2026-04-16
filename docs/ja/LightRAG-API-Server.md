# LightRAG Server と WebUI

LightRAG Server は、Web UI と API サポートを提供するために設計されています。Web UI は、ドキュメントのインデックス作成、ナレッジグラフの探索、およびシンプルな RAG クエリインターフェースを提供します。LightRAG Server はまた、Ollama 互換インターフェースも提供しており、LightRAG を Ollama チャットモデルとしてエミュレートすることを目指しています。これにより、Open WebUI などの AI チャットボットが LightRAG に簡単にアクセスできるようになります。

![image-20250323122538997](./LightRAG-API-Server.assets/image-20250323122538997.png)

![image-20250323122754387](./LightRAG-API-Server.assets/image-20250323122754387.png)

![image-20250323123011220](./LightRAG-API-Server.assets/image-20250323123011220.png)

## はじめに

### インストール

* PyPI からのインストール

```bash
### Install LightRAG Server as tool using uv (recommended)
uv tool install "lightrag-hku[api]"

### Or using pip
# python -m venv .venv
# source .venv/bin/activate  # Windows: .venv\Scripts\activate
# pip install "lightrag-hku[api]"
```

* ソースからのインストール

```bash
# Clone the repository
git clone https://github.com/HKUDS/lightrag.git

# Change to the repository directory
cd lightrag

# Bootstrap the development environment (recommended)
make dev
source .venv/bin/activate  # Activate the virtual environment (Linux/macOS)
# Or on Windows: .venv\Scripts\activate

# make dev installs the test toolchain plus the full offline stack
# (API, storage backends, and provider integrations), then builds the frontend.
# Run make env-base or copy env.example to .env before starting the server.

# Equivalent manual steps with uv
# Note: uv sync automatically creates a virtual environment in .venv/
uv sync --extra test --extra offline
source .venv/bin/activate  # Activate the virtual environment (Linux/macOS)
# Or on Windows: .venv\Scripts\activate

# Or using pip with virtual environment
# python -m venv .venv
# source .venv/bin/activate  # Windows: .venv\Scripts\activate
# pip install -e ".[test,offline]"

# Build front-end artifacts
cd lightrag_webui
bun install --frozen-lockfile
bun run build
cd ..
```

### LightRAG Server を起動する前に

LightRAG は、ドキュメントのインデックス作成とクエリ操作を効果的に実行するために、LLM（大規模言語モデル）と Embedding モデルの両方の統合が必要です。LightRAG Server の初回デプロイ前に、LLM と Embedding モデルの両方の設定を構成することが不可欠です。LightRAG は、さまざまな LLM/Embedding バックエンドへのバインディングをサポートしています:

* ollama
* lollms
* openai または openai 互換
* azure_openai
* aws_bedrock
* gemini

LightRAG Server の設定には環境変数を使用することを推奨します。プロジェクトのルートディレクトリに `env.example` という名前のサンプル環境変数ファイルがあります。このファイルを起動ディレクトリにコピーし、`.env` にリネームしてください。その後、`.env` ファイル内の LLM と Embedding モデルに関連するパラメータを変更できます。LightRAG Server は起動のたびに `.env` から環境変数をシステム環境変数に読み込むことに注意してください。**LightRAG Server はシステム環境変数の設定を .env ファイルよりも優先します**。

> VS Code の Python 拡張機能が統合ターミナルで .env ファイルを自動的に読み込む場合があるため、.env ファイルを変更するたびに新しいターミナルセッションを開いてください。

以下は、LLM と Embedding モデルの一般的な設定例です:

* OpenAI LLM + Ollama Embedding:

```
LLM_BINDING=openai
LLM_MODEL=gpt-4o
LLM_BINDING_HOST=https://api.openai.com/v1
LLM_BINDING_API_KEY=your_api_key

EMBEDDING_BINDING=ollama
EMBEDDING_BINDING_HOST=http://localhost:11434
EMBEDDING_MODEL=bge-m3:latest
EMBEDDING_DIM=1024
# EMBEDDING_BINDING_API_KEY=your_api_key
```

> Google Gemini を使用する場合は、`LLM_BINDING=gemini` を設定し、`LLM_MODEL=gemini-flash-latest` などのモデルを選択し、`LLM_BINDING_API_KEY`（または `GEMINI_API_KEY`）を通じて Gemini キーを提供してください。

* Ollama LLM + Ollama Embedding:

```
LLM_BINDING=ollama
LLM_MODEL=mistral-nemo:latest
LLM_BINDING_HOST=http://localhost:11434
# LLM_BINDING_API_KEY=your_api_key
###  Ollama Server context length (Must be larger than MAX_TOTAL_TOKENS+2000)
OLLAMA_LLM_NUM_CTX=16384

EMBEDDING_BINDING=ollama
EMBEDDING_BINDING_HOST=http://localhost:11434
EMBEDDING_MODEL=bge-m3:latest
EMBEDDING_DIM=1024
# EMBEDDING_BINDING_API_KEY=your_api_key
```

> **重要な注意事項**: Embedding モデルはドキュメントのインデックス作成前に決定する必要があり、ドキュメントのクエリフェーズでも同じモデルを使用する必要があります。特定のストレージソリューション（例: PostgreSQL）では、ベクトルの次元を初回テーブル作成時に定義する必要があります。そのため、Embedding モデルを変更する場合は、既存のベクトル関連テーブルを削除し、LightRAG に新しい次元で再作成させる必要があります。

### セットアップツールによる .env ファイルの作成

`env.example` を手動で編集する代わりに、対話型セットアップウィザードを使用して、設定済みの `.env` と、必要に応じて `docker-compose.final.yml` を生成できます:

```bash
make env-base           # Required first step: LLM, embedding, reranker
make env-storage        # Optional: storage backends and database services
make env-server         # Optional: server port, auth, and SSL
make env-security-check # Optional: audit the current .env for security risks
```

すべてのターゲットと各フローの詳細については、[docs/InteractiveSetup.md](./InteractiveSetup.md) を参照してください。
セットアップウィザードは設定のみを更新します。デプロイ前に `make env-security-check` を別途実行して、現在の `.env` のセキュリティリスクを監査してください。

### LightRAG Server の起動

LightRAG Server は2つの動作モードをサポートしています:
* シンプルで効率的な Uvicorn モード:

```
lightrag-server
```
* マルチプロセスの Gunicorn + Uvicorn モード（本番モード、Windows 環境ではサポートされていません）:

```
lightrag-gunicorn --workers 4
```

LightRAG を起動する際、現在の作業ディレクトリに `.env` 設定ファイルが含まれている必要があります。**`.env` ファイルは意図的に起動ディレクトリに配置する設計になっています**。これは、ユーザーが複数の LightRAG インスタンスを同時に起動し、異なるインスタンスに対して異なる `.env` ファイルを設定できるようにするためです。**`.env` ファイルを変更した後、新しい設定を有効にするためにターミナルを再度開く必要があります。** これは、LightRAG Server が起動するたびに `.env` ファイルから環境変数をシステム環境変数に読み込み、システム環境変数の方が優先されるためです。

起動時に、`.env` ファイルの設定はコマンドラインパラメータで上書きできます。一般的なコマンドラインパラメータには以下があります:

- `--host`: サーバーのリッスンアドレス（デフォルト: 0.0.0.0）
- `--port`: サーバーのリッスンポート（デフォルト: 9621）
- `--timeout`: LLM リクエストのタイムアウト（デフォルト: 150秒）
- `--log-level`: ログレベル（デフォルト: INFO）
- `--working-dir`: データベースの永続化ディレクトリ（デフォルト: ./rag_storage）
- `--input-dir`: アップロードファイルのディレクトリ（デフォルト: ./inputs）
- `--workspace`: ワークスペース名、複数の LightRAG インスタンス間でデータを論理的に分離するために使用（デフォルト: 空）

### Docker による LightRAG Server の起動

Docker Compose を使用するのが、LightRAG Server をデプロイおよび実行する最も便利な方法です。

- プロジェクトディレクトリを作成します。
- LightRAG リポジトリから `docker-compose.yml` ファイルをプロジェクトディレクトリにコピーします。
- `.env` ファイルを準備します: サンプルファイル [`env.example`](https://ai.znipower.com:5013/c/env.example) を複製してカスタマイズした `.env` ファイルを作成し、要件に応じて LLM と Embedding のパラメータを設定します。
- 以下のコマンドで LightRAG Server を起動します:

```shell
docker compose up
# If you want the program to run in the background after startup, add the -d parameter at the end of the command.
```

公式の Docker Compose ファイルはこちらから取得できます: [docker-compose.yml](https://raw.githubusercontent.com/HKUDS/LightRAG/refs/heads/main/docker-compose.yml)。LightRAG Docker イメージの過去のバージョンについては、こちらのリンクを参照してください: [LightRAG Docker Images](https://github.com/HKUDS/LightRAG/pkgs/container/lightrag)。Docker デプロイの詳細については、[DockerDeployment.md](./DockerDeployment.md) を参照してください。

### Nginx リバースプロキシの設定

LightRAG Server の前段に Nginx をリバースプロキシとして使用する場合、大きなファイルのアップロードを処理するために `/documents/upload` エンドポイントの `client_max_body_size` を設定する必要があります。この設定がないと、Nginx はリクエストが LightRAG に到達する前に、1MB（デフォルトの制限）を超えるファイルを `413 Request Entity Too Large` エラーで拒否します。

**推奨設定:**

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Global default: 8MB for LLM queries with long context
    client_max_body_size 8M;

    # Upload endpoint: 100MB for large file uploads
    location /documents/upload {
        client_max_body_size 100M;

        proxy_pass http://localhost:9621;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Increase timeouts for large file uploads
        proxy_read_timeout 300s;
        proxy_send_timeout 300s;
    }

    # Streaming endpoints: LLM response streaming
    location ~ ^/(query/stream|api/chat|api/generate) {
        gzip off;  # Disable compression for streaming responses

        proxy_pass http://localhost:9621;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Long timeout for LLM generation
        proxy_read_timeout 300s;
    }

    # Other endpoints
    location / {
        proxy_pass http://localhost:9621;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**重要なポイント:**

1. **グローバル制限（8MB）**: 長い会話履歴とコンテキストを含む LLM クエリに十分です（128K トークン ≈ 512KB + JSON オーバーヘッド）。
2. **アップロードエンドポイント（100MB）**: `.env` ファイルの `MAX_UPLOAD_SIZE` と同じかそれ以上に設定する必要があります。デフォルトの `MAX_UPLOAD_SIZE` は 100MB です。
3. **ストリーミングエンドポイント**: リアルタイムのレスポンス配信を確保するために、ストリーミングエンドポイントでは gzip 圧縮を無効にします（`gzip off`）。LightRAG はレスポンスバッファリングを無効にするために `X-Accel-Buffering: no` ヘッダーを自動的に設定します。
4. **タイムアウト設定**: 大きなファイルのアップロードと LLM の生成にはより長いタイムアウトが必要です。`proxy_read_timeout` と `proxy_send_timeout` を適宜調整してください。
5. **サイズ検証レイヤー**:
   - Nginx がまず `Content-Length` ヘッダーを検証します
   - LightRAG がアップロード中にストリーミング検証を実行します
   - 両方のレイヤーで適切な制限を設定することで、より良いエラーメッセージとセキュリティが確保されます

### オフラインデプロイメント

公式の LightRAG Docker イメージは、オフラインまたはエアギャップ環境と完全に互換性があります。独自のオフライン環境を構築したい場合は、[オフラインデプロイメントガイド](./OfflineDeployment.md) を参照してください。

### 複数の LightRAG インスタンスの起動

複数の LightRAG インスタンスを起動するには2つの方法があります。最初の方法は、各インスタンスに完全に独立した作業環境を設定することです。これには、各インスタンスに個別の作業ディレクトリを作成し、そのディレクトリに専用の `.env` 設定ファイルを配置する必要があります。異なるインスタンスの設定ファイルのサーバーリッスンポートは同じにすることはできません。その後、作業ディレクトリで `lightrag-server` を実行してサービスを起動できます。

2番目の方法は、すべてのインスタンスが同じ `.env` 設定ファイルのセットを共有し、コマンドライン引数で各インスタンスに異なるサーバーリッスンポートとワークスペースを指定する方法です。同じ作業ディレクトリで異なるコマンドライン引数を使用して複数の LightRAG インスタンスを起動できます。例えば:

```
# Start instance 1
lightrag-server --port 9621 --workspace space1

# Start instance 2
lightrag-server --port 9622 --workspace space2
```

ワークスペースの目的は、異なるインスタンス間のデータ分離を実現することです。そのため、`workspace` パラメータは異なるインスタンスで異なる値にする必要があります。そうしないと、データの混乱や破損につながります。

Docker Compose を使用して複数の LightRAG インスタンスを起動する場合は、`docker-compose.yml` 内の各コンテナに一意の `WORKSPACE` と `PORT` 環境変数を指定するだけです。すべてのインスタンスが共通の `.env` ファイルを共有していても、Compose で定義されたコンテナ固有の環境変数が優先され、各インスタンスの独立した設定が保証されます。

### LightRAG インスタンス間のデータ分離

各インスタンスに独立した作業ディレクトリと専用の `.env` 設定ファイルを構成することで、一般的にインメモリデータベースのローカル永続化ファイルがそれぞれの作業ディレクトリに保存され、データ分離が実現できます。デフォルトでは、LightRAG はすべてインメモリデータベースを使用しており、この方法のデータ分離で十分です。ただし、外部データベースを使用しており、異なるインスタンスが同じデータベースインスタンスにアクセスする場合は、ワークスペースを使用してデータ分離を実現する必要があります。そうしないと、異なるインスタンスのデータが競合し破壊されます。

コマンドラインの `workspace` 引数と `.env` ファイルの `WORKSPACE` 環境変数の両方を使用して、現在のインスタンスのワークスペース名を指定できます（コマンドライン引数の方が優先度が高いです）。以下は、異なるタイプのストレージにおけるワークスペースの実装方法です:

- **ローカルファイルベースのデータベースでは、ワークスペースサブディレクトリによってデータ分離を実現:** `JsonKVStorage`、`JsonDocStatusStorage`、`NetworkXStorage`、`NanoVectorDBStorage`、`FaissVectorDBStorage`。
- **コレクションにデータを保存するデータベースでは、コレクション名にワークスペースプレフィックスを追加:** `RedisKVStorage`、`RedisDocStatusStorage`、`MilvusVectorDBStorage`、`MongoKVStorage`、`MongoDocStatusStorage`、`MongoVectorDBStorage`、`MongoGraphStorage`、`PGGraphStorage`。
- **Qdrant ベクトルデータベースでは、ペイロードベースのパーティショニング（Qdrant 推奨のマルチテナンシーアプローチ）によってデータ分離を実現:** `QdrantVectorDBStorage` は、無制限のワークスペーススケーラビリティのために、ペイロードフィルタリングを備えた共有コレクションを使用します。
- **リレーショナルデータベースでは、テーブルに `workspace` フィールドを追加して論理的なデータ分離を実現:** `PGKVStorage`、`PGVectorStorage`、`PGDocStatusStorage`。
- **グラフデータベースでは、ラベルによって論理的なデータ分離を実現:** `Neo4JStorage`、`MemgraphStorage`
- **OpenSearch では、インデックス名のプレフィックスによってデータ分離を実現:** `OpenSearchKVStorage`、`OpenSearchDocStatusStorage`、`OpenSearchGraphStorage`、`OpenSearchVectorDBStorage`

レガシーデータとの互換性を維持するため、ワークスペースが設定されていない場合、PostgreSQL のデフォルトワークスペースは `default`、Neo4j のデフォルトワークスペースは `base` です。すべての外部ストレージに対して、システムは共通の `WORKSPACE` 環境変数設定を上書きするための専用ワークスペース環境変数を提供しています。これらのストレージ固有のワークスペース環境変数は: `REDIS_WORKSPACE`、`MILVUS_WORKSPACE`、`QDRANT_WORKSPACE`、`MONGODB_WORKSPACE`、`POSTGRES_WORKSPACE`、`NEO4J_WORKSPACE`、`MEMGRAPH_WORKSPACE`、`OPENSEARCH_WORKSPACE` です。

### Gunicorn + Uvicorn の複数ワーカー

LightRAG Server は `Gunicorn + Uvicorn` プリロードモードで動作できます。Gunicorn の複数ワーカー（マルチプロセス）機能により、ドキュメントのインデックスタスクが RAG クエリをブロックすることを防ぎます。docling のような CPU 集約型のドキュメント抽出ツールを使用すると、純粋な Uvicorn モードではシステム全体がブロックされる可能性があります。

LightRAG Server はドキュメントインデックスパイプラインの処理に1つのワーカーを使用しますが、Uvicorn の非同期タスクサポートにより、複数のファイルを並列で処理できます。ドキュメントインデックスの速度のボトルネックは主に LLM にあります。LLM が高い同時実行をサポートしている場合、LLM の同時実行レベルを上げることでドキュメントのインデックスを高速化できます。以下は、並行処理に関連するいくつかの環境変数とそのデフォルト値です:

```
### Number of worker processes, not greater than (2 x number_of_cores) + 1
WORKERS=2
### Number of parallel files to process in one batch
MAX_PARALLEL_INSERT=2
### Max concurrent requests to the LLM
MAX_ASYNC=4
```

### LightRAG を Linux サービスとしてインストール

サンプルファイル `lightrag.service.example` からサービスファイル `lightrag.service` を作成します。サービスファイルの起動オプションを変更します:

```text
# Set Enviroment to your Python virtual enviroment
Environment="PATH=/home/netman/lightrag-xyj/venv/bin"
WorkingDirectory=/home/netman/lightrag-xyj
# ExecStart=/home/netman/lightrag-xyj/venv/bin/lightrag-server
ExecStart=/home/netman/lightrag-xyj/venv/bin/lightrag-gunicorn
```

> ExecStart コマンドは `lightrag-gunicorn` または `lightrag-server` のいずれかでなければなりません。ラッパースクリプトは使用できません。これは、サービスの終了時にメインプロセスがこれら2つの実行可能ファイルのいずれかである必要があるためです。

LightRAG サービスをインストールします。システムが Ubuntu の場合、以下のコマンドが動作します:

```shell
sudo cp lightrag.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl start lightrag.service
sudo systemctl status lightrag.service
sudo systemctl enable lightrag.service
```

## Ollama エミュレーション

LightRAG 向けに Ollama 互換インターフェースを提供しており、LightRAG を Ollama チャットモデルとしてエミュレートすることを目指しています。これにより、Open WebUI のような Ollama をサポートする AI チャットフロントエンドが LightRAG に簡単にアクセスできるようになります。

### Open WebUI から LightRAG への接続

lightrag-server を起動した後、Open WebUI の管理パネルで Ollama タイプの接続を追加できます。すると、`lightrag:latest` という名前のモデルが Open WebUI のモデル管理インターフェースに表示されます。ユーザーはチャットインターフェースを通じて LightRAG にクエリを送信できます。このユースケースでは、LightRAG をサービスとしてインストールすることを推奨します。

Open WebUI は LLM を使用してセッションタイトルとセッションキーワードの生成タスクを行います。そのため、Ollama チャット補完 API は Open WebUI のセッション関連リクエストを検出し、基盤となる LLM に直接転送します。Open WebUI のスクリーンショット:

![image-20250323194750379](./LightRAG-API-Server.assets/image-20250323194750379.png)

### チャットでのクエリモードの選択

LightRAG の Ollama インターフェースからメッセージ（クエリ）を送信する場合、デフォルトのクエリモードは `hybrid` です。クエリプレフィックス付きのメッセージを送信することで、クエリモードを選択できます。

クエリ文字列内のクエリプレフィックスにより、レスポンスの生成に使用される LightRAG のクエリモードが決定されます。サポートされているプレフィックスは以下の通りです:

```
/local
/global
/hybrid
/naive
/mix

/bypass
/context
/localcontext
/globalcontext
/hybridcontext
/naivecontext
/mixcontext
```

例えば、チャットメッセージ `/mix What's LightRAG?` は LightRAG の mix モードクエリをトリガーします。クエリプレフィックスのないチャットメッセージは、デフォルトで hybrid モードクエリをトリガーします。

`/bypass` は LightRAG のクエリモードではありません。これは API Server にクエリをチャット履歴を含めて基盤の LLM に直接渡すように指示します。そのため、ユーザーはチャット履歴に基づいて LLM に質問に回答させることができます。Open WebUI をフロントエンドとして使用している場合は、`/bypass` プレフィックスを使用する代わりに、モデルを通常の LLM に切り替えるだけで済みます。

`/context` も LightRAG のクエリモードではありません。これは LightRAG に LLM 用に準備されたコンテキスト情報のみを返すように指示します。コンテキストが期待通りかどうかを確認したり、コンテキストを自分で処理したりできます。

### チャットでのユーザープロンプトの追加

LightRAG をコンテンツクエリに使用する場合、検索プロセスと無関係な出力処理を組み合わせることは避けてください。これはクエリの有効性に大きく影響します。ユーザープロンプトはこの問題に対処するために特別に設計されています — RAG の検索フェーズには参加せず、クエリ完了後に取得された結果をどのように処理するかを LLM に指示します。クエリプレフィックスに角括弧を追加して、LLM にユーザープロンプトを提供できます:

```
/[Use mermaid format for diagrams] Please draw a character relationship diagram for Scrooge
/mix[Use mermaid format for diagrams] Please draw a character relationship diagram for Scrooge
```

## API キーと認証

デフォルトでは、LightRAG Server は認証なしでアクセスできます。API キーまたはアカウント資格情報を設定してサーバーを保護できます。

* API キー:

```
LIGHTRAG_API_KEY=your-secure-api-key-here
WHITELIST_PATHS=/health,/api/*
```

> ヘルスチェックと Ollama エミュレーションのエンドポイントは、デフォルトで API キーチェックから除外されています。セキュリティ上の理由から、Ollama サービスが不要な場合は `WHITELIST_PATHS` から `/api/*` を削除してください。

API キーはリクエストヘッダー `X-API-Key` を使用して渡されます。以下は API 経由で LightRAG Server にアクセスする例です:

```
curl -X 'POST' \
  'http://localhost:9621/documents/scan' \
  -H 'accept: application/json' \
  -H 'X-API-Key: your-secure-api-key-here-123' \
  -d ''
```

* アカウント資格情報（Web UI ではアクセスが許可される前にログインが必要です）:

LightRAG API Server は HS256 アルゴリズムを使用した JWT ベースの認証を実装しています。安全なアクセス制御を有効にするには、以下の環境変数が必要です:

```bash
# For jwt auth
AUTH_ACCOUNTS='admin:{bcrypt}$2b$12$replace-with-generated-hash,user1:pass456'
TOKEN_SECRET='your-key'
TOKEN_EXPIRE_HOURS=4
```

プレフィックスのないパスワードはプレーンテキストとして扱われます。bcrypt パスワードを保存するには、生成されたハッシュの前に `{bcrypt}` を付けます。`AUTH_ACCOUNTS` に直接貼り付けられる値を生成する最も簡単な方法は:

```bash
lightrag-hash-password --username admin
```

このコマンドはパスワードの入力を求め、`.env` に貼り付け可能な `admin:{bcrypt}...` エントリを出力します。

> 現在、管理者アカウントとパスワードの設定のみがサポートされています。包括的なアカウントシステムは今後開発・実装される予定です。

アカウント資格情報が設定されていない場合、Web UI はゲストとしてシステムにアクセスします。したがって、API キーのみが設定されている場合でも、すべての API はゲストアカウントを通じてアクセスでき、これは安全ではありません。そのため、API を保護するには、両方の認証方法を同時に設定する必要があります。

## Azure OpenAI バックエンドの場合

Azure OpenAI API は、Azure CLI で以下のコマンドを使用して作成できます（最初に [https://docs.microsoft.com/en-us/cli/azure/install-azure-cli](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli) から Azure CLI をインストールする必要があります）:

```bash
# Change the resource group name, location, and OpenAI resource name as needed
RESOURCE_GROUP_NAME=LightRAG
LOCATION=swedencentral
RESOURCE_NAME=LightRAG-OpenAI

az login
az group create --name $RESOURCE_GROUP_NAME --location $LOCATION
az cognitiveservices account create --name $RESOURCE_NAME --resource-group $RESOURCE_GROUP_NAME  --kind OpenAI --sku S0 --location swedencentral
az cognitiveservices account deployment create --resource-group $RESOURCE_GROUP_NAME  --model-format OpenAI --name $RESOURCE_NAME --deployment-name gpt-4o --model-name gpt-4o --model-version "2024-08-06"  --sku-capacity 100 --sku-name "Standard"
az cognitiveservices account deployment create --resource-group $RESOURCE_GROUP_NAME  --model-format OpenAI --name $RESOURCE_NAME --deployment-name text-embedding-3-large --model-name text-embedding-3-large --model-version "1"  --sku-capacity 80 --sku-name "Standard"
az cognitiveservices account show --name $RESOURCE_NAME --resource-group $RESOURCE_GROUP_NAME --query "properties.endpoint"
az cognitiveservices account keys list --name $RESOURCE_NAME -g $RESOURCE_GROUP_NAME

```

最後のコマンドの出力で、OpenAI API のエンドポイントとキーが取得できます。これらの値を使用して `.env` ファイルの環境変数を設定できます。

```
# Azure OpenAI Configuration in .env:
LLM_BINDING=azure_openai
LLM_BINDING_HOST=your-azure-endpoint
LLM_MODEL=your-model-deployment-name
LLM_BINDING_API_KEY=your-azure-api-key
### API version is optional, defaults to latest version
AZURE_OPENAI_API_VERSION=2024-08-01-preview

### If using Azure OpenAI for embeddings
EMBEDDING_BINDING=azure_openai
EMBEDDING_MODEL=your-embedding-deployment-name
```

## LightRAG Server の詳細設定

API Server は2つの方法で設定できます（優先度の高い順）:

* コマンドライン引数
* 環境変数または .env ファイル

ほとんどの設定にはデフォルト値があります。詳細はサンプルファイル `.env.example` を確認してください。ストレージの設定も環境変数または `.env` ファイルを通じて行う必要があります。

### サポートされている LLM と Embedding バックエンド

LightRAG はさまざまな LLM/Embedding バックエンドへのバインディングをサポートしています:

* ollama
* openai（openai 互換を含む）
* azure_openai
* lollms
* aws_bedrock

環境変数 `LLM_BINDING` または CLI 引数 `--llm-binding` を使用して LLM バックエンドタイプを選択します。環境変数 `EMBEDDING_BINDING` または CLI 引数 `--embedding-binding` を使用して Embedding バックエンドタイプを選択します。

LLM と Embedding の設定例については、プロジェクトのルートディレクトリにある `env.example` ファイルを参照してください。OpenAI および Ollama 互換の LLM インターフェースの設定可能なオプションの完全なリストを表示するには、以下のコマンドを使用してください:
```
lightrag-server --llm-binding openai --help
lightrag-server --llm-binding ollama --help
lightrag-server --embedding-binding ollama --help
```

> OpenRouter や vLLM/SGLang でデプロイされた LLM にアクセスするには、OpenAI 互換メソッドを使用してください。`OPENAI_LLM_EXTRA_BODY` 環境変数を通じて OpenRouter や vLLM/SGLang に追加パラメータを渡すことで、推論モードの無効化やその他のパーソナライズされた制御を実現できます。

大規模言語モデル（LLM）のレスポンスにおけるエンティティ関係抽出フェーズでの**過度に長いまたは無限の出力ループを防止する**ために max_tokens を設定してください。max_tokens パラメータを設定する目的は、タイムアウトが発生する前に LLM の出力を切り詰め、ドキュメント抽出の失敗を防ぐことです。これは、多数のエンティティと関係を含む特定のテキストブロック（例: テーブルや引用）が LLM の過度に長いまたは無限ループの出力を引き起こす可能性がある問題に対処します。この設定は、ローカルにデプロイされた小規模パラメータモデルにとって特に重要です。max tokens の値は次の式で計算できます: `LLM_TIMEOUT * llm_output_tokens/second`（例: `180s * 50 tokens/s = 9000`）

```
# For vLLM/SGLang doployed models, or most of OpenAI compatible API provider
OPENAI_LLM_MAX_TOKENS=9000

# For Ollama Deployed Modeles
OLLAMA_LLM_NUM_PREDICT=9000

# For OpenAI o1-mini or newer modles
OPENAI_LLM_MAX_COMPLETION_TOKENS=9000
```

### エンティティ抽出の設定

* ENABLE_LLM_CACHE_FOR_EXTRACT: エンティティ抽出の LLM キャッシュを有効にする（デフォルト: true）

テスト環境では LLM 呼び出しのコストを削減するために `ENABLE_LLM_CACHE_FOR_EXTRACT` を true に設定することが非常に一般的です。

### サポートされているストレージタイプ

LightRAG はさまざまな目的で4種類のストレージを使用しています:

* KV_STORAGE: LLM レスポンスキャッシュ、テキストチャンク、ドキュメント情報
* VECTOR_STORAGE: エンティティベクトル、関係ベクトル、チャンクベクトル
* GRAPH_STORAGE: エンティティ関係グラフ
* DOC_STATUS_STORAGE: ドキュメントのインデックスステータス

LightRAG Server はさまざまなストレージ実装を提供しており、デフォルトは WORKING_DIR ディレクトリにデータを永続化するインメモリデータベースです。さらに、LightRAG は PostgreSQL、MongoDB、FAISS、Milvus、Qdrant、Neo4j、Memgraph、Redis を含む幅広いストレージソリューションをサポートしています。サポートされているストレージオプションの詳細については、ルートディレクトリの README.md ファイルのストレージセクションを参照してください。

**Milvus インデックス設定:** LightRAG は、環境変数を通じて Milvus ベクトルストレージの設定可能なインデックスタイプ（AUTOINDEX、HNSW、HNSW_SQ、IVF_FLAT など）をサポートするようになりました。HNSW_SQ は Milvus 2.6.8+ が必要で、大幅なメモリ節約を実現します。完全な設定オプションについては、メインの README.md の「Using Milvus for Vector Storage」セクションを参照してください。

環境変数を設定することで、ストレージ実装を選択できます。例えば、API サーバーの初回起動前に、以下の環境変数を設定して希望のストレージ実装を指定できます:

```
LIGHTRAG_KV_STORAGE=PGKVStorage
LIGHTRAG_VECTOR_STORAGE=PGVectorStorage
LIGHTRAG_GRAPH_STORAGE=PGGraphStorage
LIGHTRAG_DOC_STATUS_STORAGE=PGDocStatusStorage
```

LightRAG にドキュメントを追加した後にストレージ実装の選択を変更することはできません。あるストレージ実装から別のストレージ実装へのデータ移行はまだサポートされていません。詳細については、サンプルの `.env.example` ファイルを参照してください。

### ストレージタイプ間の LLM キャッシュ移行

LightRAG のストレージ実装を切り替える際、LLM キャッシュを既存のストレージから新しいストレージに移行できます。その後、新しいストレージにファイルを再アップロードする際、既存の LLM キャッシュがファイル処理を大幅に高速化します。LLM キャッシュ移行ツールの使用方法の詳細については、[README_MIGRATE_LLM_CACHE.md](../lightrag/tools/README_MIGRATE_LLM_CACHE.md) を参照してください。

### LightRAG API Server のコマンドラインオプション

| パラメータ             | デフォルト     | 説明                                                                                                                     |
| --------------------- | ------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| --host                | 0.0.0.0       | サーバーホスト                                                                                                                     |
| --port                | 9621          | サーバーポート                                                                                                                     |
| --working-dir         | ./rag_storage | RAG ストレージの作業ディレクトリ                                                                                               |
| --input-dir           | ./inputs      | 入力ドキュメントを含むディレクトリ                                                                            |
| --max-async           | 4             | 非同期操作の最大数                                                                                              |
| --log-level           | INFO          | ログレベル（DEBUG、INFO、WARNING、ERROR、CRITICAL）                                                                           |
| --verbose             | -             | 詳細なデバッグ出力（True、False）                                                                                              |
| --key                 | None          | 認証用 API キー。LightRAG サーバーを不正アクセスから保護します                                            |
| --ssl                 | False         | HTTPS を有効にする                                                                                                                    |
| --ssl-certfile        | None          | SSL 証明書ファイルのパス（--ssl が有効な場合に必要）                                                                     |
| --ssl-keyfile         | None          | SSL 秘密鍵ファイルのパス（--ssl が有効な場合に必要）                                                                     |
| --llm-binding         | ollama        | LLM バインディングタイプ（lollms、ollama、openai、openai-ollama、azure_openai、aws_bedrock）                                                          |
| --embedding-binding   | ollama        | Embedding バインディングタイプ（lollms、ollama、openai、azure_openai、aws_bedrock）                                                                   |

### リランキング設定

クエリで呼び出されたチャンクのリランキングにより、最適化された関連性スコアリングモデルに基づいてドキュメントを再順序付けすることで、検索品質を大幅に向上させることができます。LightRAG は現在、以下のリランクプロバイダーをサポートしています:

- **Cohere / vLLM**: Cohere AI の `v2/rerank` エンドポイントとの完全な API 統合を提供します。vLLM は Cohere 互換のリランカー API を提供しているため、vLLM 経由でデプロイされたすべてのリランカーモデルもサポートされます。
- **Jina AI**: すべての Jina リランクモデルとの完全な実装互換性を提供します。
- **Aliyun**: Aliyun のリランク API フォーマットをサポートするように設計されたカスタム実装を提供します。

リランクプロバイダーは `.env` ファイルで設定します。以下は、vLLM を使用してローカルにデプロイされたリランクモデルの設定例です:

```
RERANK_BINDING=cohere
RERANK_MODEL=BAAI/bge-reranker-v2-m3
RERANK_BINDING_HOST=http://localhost:8000/rerank
RERANK_BINDING_API_KEY=your_rerank_api_key_here
```

以下は、Aliyun が提供する Reranker サービスを利用するための設定例です:

```
RERANK_BINDING=aliyun
RERANK_MODEL=gte-rerank-v2
RERANK_BINDING_HOST=https://dashscope.aliyuncs.com/api/v1/services/rerank/text-rerank/text-rerank
RERANK_BINDING_API_KEY=your_rerank_api_key_here
```

包括的なリランカー設定例については、`env.example` ファイルを参照してください。

### リランキングの有効化

リランキングはクエリごとに有効または無効にできます。

`/query` および `/query/stream` API エンドポイントには `enable_rerank` パラメータがあり、デフォルトでは `true` に設定されており、現在のクエリでリランキングが有効かどうかを制御します。`enable_rerank` パラメータのデフォルト値を `false` に変更するには、以下の環境変数を設定してください:

```
RERANK_BY_DEFAULT=False
```

### リファレンスにチャンクコンテンツを含める

デフォルトでは、`/query` および `/query/stream` エンドポイントは `reference_id` と `file_path` のみを含むリファレンスを返します。評価、デバッグ、または引用のために、実際に取得されたチャンクコンテンツをリファレンスに含めるようリクエストできます。

`include_chunk_content` パラメータ（デフォルト: `false`）は、取得されたチャンクの実際のテキストコンテンツがレスポンスのリファレンスに含まれるかどうかを制御します。これは以下の場合に特に有用です:

- **RAG 評価**: 取得されたコンテキストへのアクセスが必要な RAGAS のようなテストシステム
- **デバッグ**: 回答の生成に実際に使用されたコンテンツの検証
- **引用表示**: レスポンスを裏付ける正確なテキスト箇所のユーザーへの表示
- **透明性**: RAG 検索プロセスの完全な可視性の提供

**重要**: `content` フィールドは**文字列の配列**であり、各文字列は同じファイルからのチャンクを表します。1つのファイルが複数のチャンクに対応する場合があるため、チャンクの境界を保持するためにコンテンツはリストとして返されます。

**API リクエスト例:**

```json
{
  "query": "What is LightRAG?",
  "mode": "mix",
  "include_references": true,
  "include_chunk_content": true
}
```

**レスポンス例（チャンクコンテンツあり）:**

```json
{
  "response": "LightRAG is a graph-based RAG system...",
  "references": [
    {
      "reference_id": "1",
      "file_path": "/documents/intro.md",
      "content": [
        "LightRAG is a retrieval-augmented generation system that combines knowledge graphs with vector similarity search...",
        "The system uses a dual-indexing approach with both vector embeddings and graph structures for enhanced retrieval..."
      ]
    },
    {
      "reference_id": "2",
      "file_path": "/documents/features.md",
      "content": [
        "The system provides multiple query modes including local, global, hybrid, and mix modes..."
      ]
    }
  ]
}
```

**注意事項**:
- このパラメータは `include_references=true` の場合にのみ機能します。リファレンスを含めずに `include_chunk_content=true` を設定しても効果はありません。
- **破壊的変更**: 以前のバージョンでは `content` を連結された単一の文字列として返していました。現在は個々のチャンクの境界を保持するために文字列の配列を返します。単一の文字列が必要な場合は、配列要素を任意のセパレータで結合してください（例: `"\n\n".join(content)`）。

### .env の例

```bash
### Server Configuration
# HOST=0.0.0.0
PORT=9621
WORKERS=2

### Settings for document indexing
ENABLE_LLM_CACHE_FOR_EXTRACT=true
SUMMARY_LANGUAGE=Chinese
MAX_PARALLEL_INSERT=2

### LLM Configuration (Use valid host. For local services installed with docker, you can use host.docker.internal)
TIMEOUT=150
MAX_ASYNC=4

LLM_BINDING=openai
LLM_MODEL=gpt-4o-mini
LLM_BINDING_HOST=https://api.openai.com/v1
LLM_BINDING_API_KEY=your-api-key

### Embedding Configuration (Use valid host. For local services installed with docker, you can use host.docker.internal)
# see also env.ollama-binding-options.example for fine tuning ollama
EMBEDDING_MODEL=bge-m3:latest
EMBEDDING_DIM=1024
EMBEDDING_BINDING=ollama
EMBEDDING_BINDING_HOST=http://localhost:11434

### For JWT Auth
# AUTH_ACCOUNTS='admin:{bcrypt}$2b$12$replace-with-generated-hash,user1:pass456'
# TOKEN_SECRET=your-key-for-LightRAG-API-Server-xxx
# TOKEN_EXPIRE_HOURS=48

# LIGHTRAG_API_KEY=your-secure-api-key-here-123
# WHITELIST_PATHS=/api/*
# WHITELIST_PATHS=/health,/api/*
```

## ドキュメントとチャンクの処理

LightRAG のドキュメント処理パイプラインはやや複雑で、主に2つのステージに分かれています: 抽出ステージ（エンティティと関係の抽出）とマージステージ（エンティティと関係のマージ）。パイプラインの同時実行を制御する2つの主要なパラメータがあります: 並列処理される最大ファイル数（MAX_PARALLEL_INSERT）と LLM への最大同時リクエスト数（MAX_ASYNC）。ワークフローは以下の通りです:

1. MAX_ASYNC は、クエリ、抽出、マージを含むシステム内の同時 LLM リクエストの総数を制限します。LLM リクエストには異なる優先度があり、クエリ操作が最も高く、次にマージ、そして抽出の順です。
2. MAX_PARALLEL_INSERT は、抽出ステージで並列処理されるファイルの数を制御します。最適なパフォーマンスのために、MAX_PARALLEL_INSERT は 2 から 10 の間に設定することを推奨します（通常は MAX_ASYNC/3）。この値を高く設定しすぎると、マージフェーズで異なるドキュメント間のエンティティと関係の命名の競合が発生する可能性が高くなり、全体的な効率が低下します。
3. 単一ファイル内では、異なるテキストブロックからのエンティティと関係の抽出が同時に処理され、同時実行の度合いは MAX_ASYNC で設定されます。MAX_ASYNC 個のテキストブロックが処理された後にのみ、同じファイル内の次のバッチに進みます。
4. ファイルのエンティティと関係の抽出が完了すると、エンティティと関係のマージステージに入ります。このステージでも複数のエンティティと関係が同時に処理され、同時実行レベルは `MAX_ASYNC` によって制御されます。
5. マージステージの LLM リクエストは抽出ステージよりも優先され、マージフェーズのファイルが迅速に処理され、その結果がベクトルデータベースに速やかに更新されるようにします。
6. 競合状態を防ぐために、マージステージでは同じエンティティや関係の同時処理を回避します。複数のファイルがマージ対象の同じエンティティや関係を含む場合、それらはシリアルに処理されます。
7. 各ファイルはパイプラインにおけるアトミックな処理単位として扱われます。ファイルは、すべてのテキストブロックが抽出とマージを完了した場合にのみ、正常に処理されたとマークされます。処理中にエラーが発生した場合、ファイル全体が失敗とマークされ、再処理が必要になります。
8. エラーによりファイルが再処理される場合、LLM キャッシュのおかげで、以前に処理されたテキストブロックは素早くスキップできます。LLM キャッシュはマージステージでも利用されますが、マージ順序の不一致により、このステージでの有効性が制限される場合があります。
9. 抽出中にエラーが発生した場合、システムは中間結果を保持しません。マージ中にエラーが発生した場合、既にマージされたエンティティと関係は保持される可能性があります。同じファイルが再処理されると、再抽出されたエンティティと関係が既存のものとマージされ、クエリ結果に影響を与えません。
10. マージステージの終了時に、すべてのエンティティと関係のデータがベクトルデータベースに更新されます。この時点でエラーが発生した場合、一部の更新が保持される可能性があります。ただし、次の処理試行で以前の結果が上書きされるため、正常に再処理されたファイルは将来のクエリ結果の整合性に影響を与えません。

大きなファイルは、増分処理を可能にするために小さなセグメントに分割する必要があります。失敗したファイルの再処理は、Web UI の「Scan」ボタンを押すことで開始できます。

## API エンドポイント

すべてのサーバー（LoLLMs、Ollama、OpenAI、Azure OpenAI）は、RAG 機能のための同じ REST API エンドポイントを提供します。API Server が実行中の場合、以下にアクセスしてください:

- Swagger UI: http://localhost:9621/docs
- ReDoc: http://localhost:9621/redoc

提供されている curl コマンドまたは Swagger UI インターフェースを使用して API エンドポイントをテストできます。以下を確認してください:

1. 適切なバックエンドサービス（LoLLMs、Ollama、または OpenAI）を起動する
2. RAG サーバーを起動する
3. ドキュメント管理エンドポイントを使用していくつかのドキュメントをアップロードする
4. クエリエンドポイントを使用してシステムにクエリを実行する
5. inputs ディレクトリに新しいファイルが配置された場合、ドキュメントスキャンをトリガーする

## 非同期ドキュメントインデックスと進捗追跡

LightRAG は、フロントエンドがドキュメント処理の進捗を監視およびクエリできるように、非同期ドキュメントインデックスを実装しています。指定されたエンドポイントを通じてファイルをアップロードしたりテキストを挿入したりすると、リアルタイムの進捗監視を容易にするために一意の Track ID が返されます。

**Track ID 生成をサポートする API エンドポイント:**

* `/documents/upload`
* `/documents/text`
* `/documents/texts`

**ドキュメント処理ステータスのクエリエンドポイント:**
* `/track_status/{track_id}`

このエンドポイントは、以下を含む包括的なステータス情報を提供します:
* ドキュメント処理ステータス（pending/processing/processed/failed）
* コンテンツの概要とメタデータ
* 処理が失敗した場合のエラーメッセージ
* 作成と更新のタイムスタンプ
