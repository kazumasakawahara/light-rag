# インタラクティブセットアップガイド

`.env` を手動で編集する代わりに、LightRAG に設定を案内してもらいたい場合は、インタラクティブセットアップウィザードを使用してください。

ウィザードは `make` ターゲットを通じて公開されています:

- `make env-base`
- `make env-storage`
- `make env-server`
- `make env-validate`
- `make env-security-check`
- `make env-backup`
- `make env-base-rewrite`
- `make env-storage-rewrite`

基盤となるシェルスクリプトを直接呼び出す必要はありません。

## このウィザードの用途

セットアップウィザードは、LightRAG の設定を 3 つのパートで支援します:

- `env-base` は LLM、埋め込みモデル、およびオプションのリランカーを設定します。
- `env-storage` は PostgreSQL、Neo4j、Redis、Milvus、Qdrant、MongoDB、Memgraph などのストレージバックエンドを追加または変更します。
- `env-server` はサーバーのホストとポート、WebUI のラベル、認証、API キー、SSL を設定します。

各ステップは後から再実行できます。ウィザードは既存の `.env` を読み込み、現在の値をデフォルトとして表示するため、変更が必要な部分のみ修正すればよいです。

## 開始前の準備

- リポジトリのルートからコマンドを実行してください。
- `make env-*` ターゲットは互換性のある Bash 4+ インタープリタを自動的に選択します。
- セットアップスクリプトを直接呼び出すのではなく、ドキュメントに記載された `make env-*` ターゲットを使用してください。
- `make env-base` は初期の `.env` を作成するため、通常の開始点です。
- `make env-storage` と `make env-server` は既存の `.env` が必要です。
- ウィザード管理の Docker サービスを選択した場合、ウィザードは Docker 起動パスに向けて LightRAG の準備も行います。

## セットアップパスの選択

何を実行するか判断するためのクイックガイド:

- リモートモデルプロバイダーで最速の初回実行をしたい場合: `make env-base`
- 埋め込みやリランキングを Docker でローカル実行したい場合: `make env-base`
- モデルの設定が完了し、データベースを追加したい場合: `make env-storage`
- モデルの設定が完了し、認証、API キー、SSL を設定したい場合: `make env-server`
- 現在のセットアップが有効か確認したい場合: `make env-validate`
- 公開前に現在のセットアップを監査したい場合: `make env-security-check`
- 設定を変更せずにスタンドアロンバックアップを作成したい場合: `make env-backup`
- バンドルされたテンプレートから生成された Compose サービスを修復する必要がある場合: `make env-base-rewrite` または `make env-storage-rewrite`

## シナリオ 1: 初回ローカルセットアップ

リモートモデルエンドポイントまたは API キーを既にお持ちで、最小限のセットアップで LightRAG を実行したい場合に使用します。

**コマンド**

```bash
make env-base
```

**ウィザードが質問する内容**

- LLM プロバイダー、モデル、エンドポイント、API キー
- 埋め込みモデルを Docker 経由でローカル実行するかどうか
- 埋め込みがリモートの場合: 埋め込みプロバイダー、モデル、次元数、エンドポイント、API キー
- リランキングを有効にするかどうか
- リランキングを有効にした場合: リランクサービスを Docker 経由でローカル実行するかどうか
- リランキングがリモートの場合: リランクプロバイダー、モデル、エンドポイント、API キー

**書き込まれるもの**

- `.env`
- ウィザード管理の Docker サービスを有効にした場合のみ `docker-compose.final.yml`

**次のステップ**

- ウィザード管理の Docker サービスを有効にしなかった場合:

```bash
lightrag-server
```

- ウィザード管理の Docker サービスを有効にした場合:

```bash
docker compose -f docker-compose.final.yml up -d
```

## シナリオ 2: Docker ホスト型の埋め込みまたはリランクを使用したローカルセットアップ

Docker を通じて埋め込みやリランキングのローカル推論サービスを実行したい場合に使用します。

**コマンド**

```bash
make env-base
```

**推奨回答**

- ローカル埋め込みを使用したい場合は `Run embedding model locally via Docker (vLLM)?` に `yes` と回答
- ローカルリランキングを使用したい場合は `Enable reranking?` に `yes` と回答し、次に `Run rerank service locally via Docker?` に `yes` と回答

**ローカルサービスを有効にした後のウィザードの質問内容**

- ローカル vLLM 用の埋め込みモデル名
- ローカル vLLM 用のリランクモデル名
- メイン LLM がまだ外部の場合のリモート LLM の詳細

**書き込まれるもの**

- `.env`
- 選択されたローカルサービスを含む `docker-compose.final.yml`

**次のステップ**

```bash
docker compose -f docker-compose.final.yml up -d
```

これにより、生成された Docker ベースの LightRAG スタックが選択されたローカルサービスとともに起動します。

## シナリオ 3: ベースセットアップ後にストレージを追加

`make env-base` で `.env` を既に作成済みで、デフォルトのローカルファイルストレージからデータベースバックエンドのストレージに切り替えたい場合に使用します。

**コマンド**

```bash
make env-storage
```

**前提条件**

- `.env` が既に存在している必要があります

**ウィザードが質問する内容**

- KV ストレージバックエンド
- ベクトルストレージバックエンド
- グラフストレージバックエンド
- ドキュメントステータスストレージバックエンド
- 必要な各データベースについて、Docker 経由でローカル実行するかどうか
- 必要な各データベースについて、ホスト、URI、ポート、ユーザー、パスワード、データベース名、デバイスタイプなどの接続詳細

**重要なルール**

- ベクトルストレージに `MongoVectorDBStorage` を選択した場合、ウィザードはバンドルされたローカル Docker MongoDB サービスを提供しません。Atlas Search / Vector Search をサポートする MongoDB デプロイメントを用意する必要があります。

**書き込まれるもの**

- `.env`
- ウィザード管理のストレージサービスを選択した場合は `docker-compose.final.yml`

**次のステップ**

- Docker 管理のストレージサービスを選択した場合:

```bash
docker compose -f docker-compose.final.yml up -d
```

- LightRAG を外部データベースに接続する場合は、LightRAG を起動する前にそれらのサービスが到達可能であることを確認してください。

## シナリオ 4: 認証と SSL によるデプロイメントの強化

`.env` が既に存在し、共有または外部利用のためにサーバーを準備する必要がある場合に使用します。

**コマンド**

```bash
make env-server
make env-security-check
```

**前提条件**

- `.env` が既に存在している必要があります

**`env-server` が質問する内容**

- サーバーのホストとポート
- WebUI のタイトルと説明
- サマリー言語
- 認証と API キー設定を構成するかどうか
- 認証アカウント、JWT シークレット、トークン有効期間、API キー、ホワイトリストパス
- SSL/TLS を有効にするかどうか
- SSL 証明書ファイルパスと SSL キーファイルパス

**書き込まれるもの**

- `.env`
- 現在のセットアップが既にウィザード管理の Docker サービスを使用している場合は `docker-compose.final.yml` が更新される場合があります

**次のステップ**

- `make env-security-check` を実行
- スタックが Docker を使用している場合は、Compose ファイルで LightRAG サービスを再作成
- スタックがホスト上で実行されている場合は、`lightrag-server` を再起動

より広範なデプロイメントガイダンスについては、[DockerDeployment.md](/Users/ydh/mycode/ai/paper-RAG/docs/DockerDeployment.md) を参照してください。

## 検証、監査、バックアップ

これらのコマンドは完全なセットアップフローを案内するものではありませんが、通常の運用の一部です。

### 現在の設定を検証

```bash
make env-validate
```

現在の `.env` が内部的に整合しているか確認したい場合に使用します。必須値の欠落、認証設定の不正、無効な URI、無効なポート、SSL ファイルの欠落などの問題を報告します。

### 公開前のセキュリティ監査

```bash
make env-security-check
```

LightRAG を localhost 以外に公開する前に使用します。認証の欠落、脆弱または欠落した JWT シークレット、安全でないホワイトリスト設定、未解決の機密プレースホルダーなどのリスクのある設定を報告します。

### スタンドアロンバックアップの作成

```bash
make env-backup
```

セットアップフローを実行せずに手動バックアップを作成したい場合に使用します。

## 出力とその意味

### `.env`

ウィザードはリポジトリルートに `.env` を書き込みます。このファイルは、最新のウィザード実行によって生成された現在のランタイム設定となります。

実際には以下を意味します:

- ウィザードを再実行すると `.env` が更新されます
- 既存の値は後続の実行でデフォルトとして再利用されます
- `.env` は最後に設定したワークフローのアクティブな設定として扱う必要があります
- `env-base`、`env-storage`、`env-server` が `.env` を書き込む前に、既存のファイルが存在する場合、ウィザードは自動的にタイムスタンプ付きバックアップを作成します

### `docker-compose.final.yml`

ウィザードは、ウィザード管理の Docker サービスを選択した場合、または既存のウィザード生成 Compose セットアップを新しいサーバー設定と整合させる必要がある場合にのみ、`docker-compose.final.yml` を作成または更新します。

セットアップフローの一つが既存の生成された Compose ファイルを置換または削除しようとする場合、事前にタイムスタンプ付きバックアップを自動的に作成します。

生成された Docker スタックを起動する際にこのファイルを使用してください:

```bash
docker compose -f docker-compose.final.yml up -d
```

ベースの `docker-compose.yml` は汎用プロジェクト Compose ファイルのままです。生成された `docker-compose.final.yml` はウィザード管理の出力です。

## トラブルシューティングと高度な注意事項

- `make env-storage` または `make env-server` が `.env` が見つからないと表示する場合は、まず `make env-base` を実行してください。
- `env-base`、`env-storage`、`env-server` を再実行する前に `make env-backup` を実行する必要はありません。これらのフローは既に既存の `.env` をバックアップし、変更前に生成された Compose ファイルもバックアップします。
- 現在のバンドルテンプレートからウィザード管理の Compose サービスを完全に再構築する必要がある場合は、`make env-base-rewrite` または `make env-storage-rewrite` を使用してください。
- ホスト指向と Docker 指向のワークフロー間で切り替える場合は、古い設定を手動でマージしようとせず、関連するセットアップステップを再実行してください。
- 生成されたスタックにローカル Milvus が含まれている場合は、`docker compose -f docker-compose.final.yml up -d` を実行する前に `MINIO_ACCESS_KEY_ID` と `MINIO_SECRET_ACCESS_KEY` が利用可能であることを確認してください。
- インタラクティブウィザード以外の Docker デプロイメントの詳細については、[DockerDeployment.md](/Users/ydh/mycode/ai/paper-RAG/docs/DockerDeployment.md) を参照してください。

## 典型的なコマンドシーケンス

### リモートモデル、ローカルサーバー

```bash
make env-base
lightrag-server
```

### リモート LLM、Docker でのローカル埋め込みとリランク

```bash
make env-base
docker compose -f docker-compose.final.yml up -d
```

### ベースセットアップ後にストレージを追加

```bash
make env-base
make env-storage
docker compose -f docker-compose.final.yml up -d
```

### 公開前にセキュリティと SSL を追加

```bash
make env-base
make env-storage
make env-server
make env-security-check
docker compose -f docker-compose.final.yml up -d
```
