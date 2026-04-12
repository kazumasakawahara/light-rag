# LightRAG オフラインデプロイガイド

このガイドでは、インターネットアクセスが制限されている、または利用できないオフライン環境で LightRAG をデプロイするための包括的な手順を説明します。

Docker を使用して LightRAG をデプロイする場合は、LightRAG Docker イメージはオフライン運用向けに事前設定されているため、このドキュメントを参照する必要はありません。

> `transformers`、`torch`、または `cuda` を必要とするソフトウェアパッケージは、オフライン依存関係グループに含まれません。そのため、Docling などのドキュメント抽出ツールや、Hugging Face や LMDeploy などのローカル LLM モデルは、オフラインインストールサポートの対象外です。これらの高い計算リソースを要求するサービスは、LightRAG に統合すべきではありません。Docling は分離され、スタンドアロンサービスとしてデプロイされる予定です。

## 目次

- [概要](#概要)
- [クイックスタート](#クイックスタート)
- [階層化された依存関係](#階層化された依存関係)
- [Tiktoken キャッシュ管理](#tiktoken-キャッシュ管理)
- [完全なオフラインデプロイワークフロー](#完全なオフラインデプロイワークフロー)
- [トラブルシューティング](#トラブルシューティング)

## 概要

LightRAG はファイルタイプや設定に基づいてオプション機能の動的パッケージインストール（`pipmaster`）を使用します。オフライン環境では、これらの動的インストールは失敗します。このガイドでは、必要なすべての依存関係とキャッシュファイルを事前にインストールする方法を説明します。

### 動的にインストールされるもの

LightRAG は以下のパッケージを動的にインストールします：

- **ストレージバックエンド**: `redis`, `neo4j`, `pymilvus`, `pymongo`, `asyncpg`, `qdrant-client`
- **LLM プロバイダー**: `openai`, `anthropic`, `ollama`, `zhipuai`, `aioboto3`, `voyageai`, `llama-index`, `lmdeploy`, `transformers`, `torch`
- **Tiktoken モデル**: OpenAI CDN からダウンロードされる BPE エンコーディングモデル

**注意**: ドキュメント処理の依存関係（`pypdf`, `python-docx`, `python-pptx`, `openpyxl`）は `api` extras グループにプリインストールされるようになり、動的インストールは不要になりました。

## クイックスタート

### オプション 1: pip でオフライン extras を使用

```bash
# Online environment: Install all offline dependencies
pip install lightrag-hku[offline]

# Download tiktoken cache
lightrag-download-cache

# Create offline package
pip download lightrag-hku[offline] -d ./offline-packages
tar -czf lightrag-offline.tar.gz ./offline-packages ~/.tiktoken_cache

# Transfer to offline server
scp lightrag-offline.tar.gz user@offline-server:/path/to/

# Offline environment: Install
tar -xzf lightrag-offline.tar.gz
pip install --no-index --find-links=./offline-packages lightrag-hku[offline]
export TIKTOKEN_CACHE_DIR=~/.tiktoken_cache
```

### オプション 2: requirements ファイルを使用

```bash
# Online environment: Download packages
pip download -r requirements-offline.txt -d ./packages

# Transfer to offline server
tar -czf packages.tar.gz ./packages
scp packages.tar.gz user@offline-server:/path/to/

# Offline environment: Install
tar -xzf packages.tar.gz
pip install --no-index --find-links=./packages -r requirements-offline.txt
```

## 階層化された依存関係

LightRAG はさまざまなユースケースに対応する柔軟な依存関係グループを提供します：

### 利用可能な依存関係グループ

| グループ | 説明 | ユースケース |
| ----- | ----------- | -------- |
| `api` | API サーバー + ドキュメント処理 | PDF, DOCX, PPTX, XLSX サポート付き FastAPI サーバー |
| `offline-storage` | ストレージバックエンド | Redis, Neo4j, MongoDB, PostgreSQL 等 |
| `offline-llm` | LLM プロバイダー | OpenAI, Anthropic, Ollama 等 |
| `offline` | 完全なオフラインパッケージ | API + Storage + LLM（全機能） |

**注意**: ドキュメント処理（PDF, DOCX, PPTX, XLSX）は `api` extras グループに含まれています。以前の `offline-docs` グループは、より良い統合のために `api` に統合されました。

> `transformers`、`torch`、または `cuda` を必要とするソフトウェアパッケージは、オフライン依存関係グループに含まれません。

### インストール例

```bash
# Install API with document processing
pip install lightrag-hku[api]

# Install API and storage backends
pip install lightrag-hku[api,offline-storage]

# Install all offline dependencies (recommended for offline deployment)
pip install lightrag-hku[offline]
```

### 個別の requirements ファイルを使用

```bash
# Storage backends only
pip install -r requirements-offline-storage.txt

# LLM providers only
pip install -r requirements-offline-llm.txt

# All offline dependencies
pip install -r requirements-offline.txt
```

## Tiktoken キャッシュ管理

Tiktoken は初回使用時に BPE エンコーディングモデルをダウンロードします。オフライン環境では、これらのモデルを事前にダウンロードしておく必要があります。

### CLI コマンドの使用

LightRAG をインストール後、組み込みコマンドを使用します：

```bash
# Download to default location (see output for exact path)
lightrag-download-cache

# Download to specific directory
lightrag-download-cache --cache-dir ./tiktoken_cache

# Download specific models only
lightrag-download-cache --models gpt-4o-mini gpt-4
```

### ダウンロードされるデフォルトモデル

- `gpt-4o-mini`（LightRAG デフォルト）
- `gpt-4o`
- `gpt-4`
- `gpt-3.5-turbo`
- `text-embedding-ada-002`
- `text-embedding-3-small`
- `text-embedding-3-large`

### オフライン環境でのキャッシュ場所の設定

```bash
# Option 1: Environment variable (temporary)
export TIKTOKEN_CACHE_DIR=/path/to/tiktoken_cache

# Option 2: Add to ~/.bashrc or ~/.zshrc (persistent)
echo 'export TIKTOKEN_CACHE_DIR=~/.tiktoken_cache' >> ~/.bashrc
source ~/.bashrc

# Option 3: Copy to default location
cp -r /path/to/tiktoken_cache ~/.tiktoken_cache/
```

## 完全なオフラインデプロイワークフロー

### ステップ 1: オンライン環境での準備

```bash
# 1. Install LightRAG with offline dependencies
pip install lightrag-hku[offline]

# 2. Download tiktoken cache
lightrag-download-cache --cache-dir ./offline_cache/tiktoken

# 3. Download all Python packages
pip download lightrag-hku[offline] -d ./offline_cache/packages

# 4. Create archive for transfer
tar -czf lightrag-offline-complete.tar.gz ./offline_cache

# 5. Verify contents
tar -tzf lightrag-offline-complete.tar.gz | head -20
```

### ステップ 2: オフライン環境への転送

```bash
# Using scp
scp lightrag-offline-complete.tar.gz user@offline-server:/tmp/

# Or using USB/physical media
# Copy lightrag-offline-complete.tar.gz to USB drive
```

### ステップ 3: オフライン環境でのインストール

```bash
# 1. Extract archive
cd /tmp
tar -xzf lightrag-offline-complete.tar.gz

# 2. Install Python packages
pip install --no-index \
    --find-links=/tmp/offline_cache/packages \
    lightrag-hku[offline]

# 3. Set up tiktoken cache
mkdir -p ~/.tiktoken_cache
cp -r /tmp/offline_cache/tiktoken/* ~/.tiktoken_cache/
export TIKTOKEN_CACHE_DIR=~/.tiktoken_cache

# 4. Add to shell profile for persistence
echo 'export TIKTOKEN_CACHE_DIR=~/.tiktoken_cache' >> ~/.bashrc
```

### ステップ 4: インストールの確認

```bash
# Test Python import
python -c "from lightrag import LightRAG; print('✓ LightRAG imported')"

# Test tiktoken
python -c "from lightrag.utils import TiktokenTokenizer; t = TiktokenTokenizer(); print('✓ Tiktoken working')"

# Test optional dependencies (if installed)
python -c "import docling; print('✓ Docling available')"
python -c "import redis; print('✓ Redis available')"
```

## トラブルシューティング

### 問題: Tiktoken がネットワークエラーで失敗する

**現象**: `Unable to load tokenizer for model gpt-4o-mini`

**解決策**:
```bash
# Ensure TIKTOKEN_CACHE_DIR is set
echo $TIKTOKEN_CACHE_DIR

# Verify cache files exist
ls -la ~/.tiktoken_cache/

# If empty, you need to download cache in online environment first
```

### 問題: 動的パッケージインストールが失敗する

**現象**: `Error installing package xxx`

**解決策**:
```bash
# Pre-install the specific package you need
# For API with document processing:
pip install lightrag-hku[api]

# For storage backends:
pip install lightrag-hku[offline-storage]

# For LLM providers:
pip install lightrag-hku[offline-llm]
```

### 問題: 実行時に依存関係が見つからない

**現象**: `ModuleNotFoundError: No module named 'xxx'`

**解決策**:
```bash
# Check what you have installed
pip list | grep -i xxx

# Install missing component
pip install lightrag-hku[offline]  # Install all offline deps
```

### 問題: Tiktoken キャッシュへのアクセス権限が拒否される

**現象**: `PermissionError: [Errno 13] Permission denied`

**解決策**:
```bash
# Ensure cache directory has correct permissions
chmod 755 ~/.tiktoken_cache
chmod 644 ~/.tiktoken_cache/*

# Or use a user-writable directory
export TIKTOKEN_CACHE_DIR=~/my_tiktoken_cache
mkdir -p ~/my_tiktoken_cache
```

## ベストプラクティス

1. **まずオンライン環境でテスト**: オフラインにする前に、必ずオンライン環境で完全なセットアップをテストしてください。

2. **キャッシュを最新に保つ**: 新しいモデルがリリースされたら、オフラインキャッシュを定期的に更新してください。

3. **セットアップを文書化する**: 実際に必要なオプション依存関係についてメモを残してください。

4. **バージョンの固定**: 本番環境では特定のバージョンを固定することを検討してください：
   ```bash
   pip freeze > requirements-production.txt
   ```

5. **最小限のインストール**: 必要なものだけをインストールしてください：
   ```bash
   # If you only need API with document processing
   pip install lightrag-hku[api]
   # Then manually add specific LLM: pip install openai
   ```

## その他のリソース

- [LightRAG GitHub リポジトリ](https://github.com/HKUDS/LightRAG)
- [Docker デプロイガイド](./DockerDeployment.md)
- [API サーバードキュメント](./LightRAG-API-Server.md)

## サポート

このガイドでカバーされていない問題が発生した場合：

1. [GitHub Issues](https://github.com/HKUDS/LightRAG/issues) を確認してください
2. [プロジェクトドキュメント](../README.md) を参照してください
3. オフラインデプロイの詳細を記載した新しい Issue を作成してください
