# LightRAG Core を使ったプログラミング

> LightRAG をプロジェクトに統合する場合は、LightRAG Server が提供する REST API の使用を推奨します。LightRAG Core は、組み込みアプリケーションや研究・評価を行う研究者向けです。

## シンプルなプログラム

```python
import os
import asyncio
from lightrag import LightRAG, QueryParam
from lightrag.llm.openai import gpt_4o_mini_complete, gpt_4o_complete, openai_embed
from lightrag.utils import setup_logger

setup_logger("lightrag", level="INFO")

WORKING_DIR = "./rag_storage"
if not os.path.exists(WORKING_DIR):
    os.mkdir(WORKING_DIR)

async def initialize_rag():
    rag = LightRAG(
        working_dir=WORKING_DIR,
        embedding_func=openai_embed,
        llm_model_func=gpt_4o_mini_complete,
    )
    # IMPORTANT: Both initialization calls are required!
    await rag.initialize_storages()  # Initialize storage backends
    return rag

async def main():
    try:
        # Initialize RAG instance
        rag = await initialize_rag()
        await rag.ainsert("Your text")

        # Perform hybrid search
        mode = "hybrid"
        print(
          await rag.aquery(
              "What are the top themes in this story?",
              param=QueryParam(mode=mode)
          )
        )

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if rag:
            await rag.finalize_storages()

if __name__ == "__main__":
    asyncio.run(main())
```

注意事項:
- 実行前に環境変数 `OPENAI_API_KEY` をエクスポートしてください。
- すべてのデータは `WORKING_DIR` に永続化されます。

**重要:**

**LightRAG は使用前に明示的な初期化が必要です。** LightRAG インスタンスを作成した後、`await rag.initialize_storages()` を呼び出す必要があります。呼び出さない場合、エラーが発生します。


## LightRAG 初期化パラメータ

**パラメータ**

| **パラメータ** | **型** | **説明** | **デフォルト** |
| -------------- | ---------- | ----------------- | ------------- |
| **working_dir** | `str` | キャッシュが保存されるディレクトリ | `lightrag_cache+timestamp` |
| **workspace** | str | 異なる LightRAG インスタンス間のデータ分離のためのワークスペース名 | |
| **kv_storage** | `str` | ドキュメントとテキストチャンクのストレージタイプ。サポートされるタイプ: `JsonKVStorage`,`PGKVStorage`,`RedisKVStorage`,`MongoKVStorage`,`OpenSearchKVStorage` | `JsonKVStorage` |
| **vector_storage** | `str` | 埋め込みベクトルのストレージタイプ。サポートされるタイプ: `NanoVectorDBStorage`,`PGVectorStorage`,`MilvusVectorDBStorage`,`ChromaVectorDBStorage`,`FaissVectorDBStorage`,`MongoVectorDBStorage`,`QdrantVectorDBStorage`,`OpenSearchVectorDBStorage` | `NanoVectorDBStorage` |
| **graph_storage** | `str` | グラフのエッジとノードのストレージタイプ。サポートされるタイプ: `NetworkXStorage`,`Neo4JStorage`,`PGGraphStorage`,`AGEStorage`,`OpenSearchGraphStorage` | `NetworkXStorage` |
| **doc_status_storage** | `str` | ドキュメント処理ステータスのストレージタイプ。サポートされるタイプ: `JsonDocStatusStorage`,`PGDocStatusStorage`,`MongoDocStatusStorage`,`OpenSearchDocStatusStorage` | `JsonDocStatusStorage` |
| **chunk_token_size** | `int` | ドキュメント分割時のチャンクあたりの最大トークンサイズ | `1200` |
| **chunk_overlap_token_size** | `int` | ドキュメント分割時の2つのチャンク間のオーバーラップトークンサイズ | `100` |
| **tokenizer** | `Tokenizer` | テキストをトークン（数値）に変換し、`.encode()` および `.decode()` 関数で元に戻す関数。`TokenizerInterface` プロトコルに従います。指定しない場合、デフォルトの Tiktoken トークナイザーが使用されます。 | `TiktokenTokenizer` |
| **tiktoken_model_name** | `str` | デフォルトの Tiktoken トークナイザーを使用する場合、使用する特定の Tiktoken モデルの名前です。独自のトークナイザーを提供した場合、この設定は無視されます。 | `gpt-4o-mini` |
| **entity_extract_max_gleaning** | `int` | エンティティ抽出プロセスにおけるループ回数。履歴メッセージを追加します | `1` |
| **node_embedding_algorithm** | `str` | ノード埋め込みのアルゴリズム（現在未使用） | `node2vec` |
| **node2vec_params** | `dict` | ノード埋め込みのパラメータ | `{"dimensions": 1536,"num_walks": 10,"walk_length": 40,"window_size": 2,"iterations": 3,"random_seed": 3,}` |
| **embedding_func** | `EmbeddingFunc` | テキストから埋め込みベクトルを生成する関数 | `openai_embed` |
| **embedding_batch_num** | `int` | 埋め込み処理の最大バッチサイズ（バッチごとに複数テキストを送信） | `32` |
| **embedding_func_max_async** | `int` | 非同期埋め込み処理の最大同時実行数 | `16` |
| **llm_model_func** | `callable` | LLM 生成用の関数 | `gpt_4o_mini_complete` |
| **llm_model_name** | `str` | 生成用の LLM モデル名 | `meta-llama/Llama-3.2-1B-Instruct` |
| **summary_context_size** | `int` | エンティティ・リレーションのマージ用サマリー生成時に LLM に送信する最大トークン数 | `10000`（環境変数 SUMMARY_CONTEXT_SIZE で設定可能） |
| **summary_max_tokens** | `int` | エンティティ/リレーションの説明の最大トークンサイズ | `500`（環境変数 SUMMARY_MAX_TOKENS で設定可能） |
| **llm_model_max_async** | `int` | 非同期 LLM 処理の最大同時実行数 | `4`（環境変数 MAX_ASYNC でデフォルト値を変更可能） |
| **llm_model_kwargs** | `dict` | LLM 生成用の追加パラメータ | |
| **vector_db_storage_cls_kwargs** | `dict` | ベクトルデータベース用の追加パラメータ。ノードとリレーション取得の閾値設定など | cosine_better_than_threshold: 0.2（環境変数 COSINE_THRESHOLD でデフォルト値を変更可能） |
| **enable_llm_cache** | `bool` | `TRUE` の場合、LLM の結果をキャッシュに保存します。同じプロンプトにはキャッシュされたレスポンスを返します | `TRUE` |
| **enable_llm_cache_for_entity_extract** | `bool` | `TRUE` の場合、エンティティ抽出の LLM 結果をキャッシュに保存します。アプリケーションのデバッグに役立ちます | `TRUE` |
| **addon_params** | `dict` | 追加パラメータ。例: `{"language": "Simplified Chinese", "entity_types": ["organization", "person", "location", "event"]}`: サンプル制限やエンティティ/リレーション抽出の出力言語を設定します | language: English` |
| **embedding_cache_config** | `dict` | 質問応答キャッシュの設定。3つのパラメータを含みます: `enabled`: キャッシュ検索機能の有効/無効を切り替えるブール値。有効にすると、新しい回答を生成する前にキャッシュされたレスポンスを確認します。`similarity_threshold`: 浮動小数点値（0-1）、類似度の閾値。新しい質問とキャッシュされた質問の類似度がこの閾値を超えると、LLM を呼び出さずにキャッシュされた回答を直接返します。`use_llm_check`: LLM による類似度検証の有効/無効を切り替えるブール値。有効にすると、キャッシュされた回答を返す前に、LLM を二次チェックとして使用して質問間の類似度を検証します。 | デフォルト: `{"enabled": False, "similarity_threshold": 0.95, "use_llm_check": False}` |


## QueryParam

`QueryParam` を使用してクエリの動作を制御します:

```python
class QueryParam:
    """Configuration parameters for query execution in LightRAG."""

    mode: Literal["local", "global", "hybrid", "naive", "mix", "bypass"] = "global"
    """Specifies the retrieval mode:
    - "local": Focuses on context-dependent information.
    - "global": Utilizes global knowledge.
    - "hybrid": Combines local and global retrieval methods.
    - "naive": Performs a basic search without advanced techniques.
    - "mix": Integrates knowledge graph and vector retrieval.
    """

    only_need_context: bool = False
    """If True, only returns the retrieved context without generating a response."""

    only_need_prompt: bool = False
    """If True, only returns the generated prompt without producing a response."""

    response_type: str = "Multiple Paragraphs"
    """Defines the response format. Examples: 'Multiple Paragraphs', 'Single Paragraph', 'Bullet Points'."""

    stream: bool = False
    """If True, enables streaming output for real-time responses."""

    top_k: int = int(os.getenv("TOP_K", "60"))
    """Number of top items to retrieve. Represents entities in 'local' mode and relationships in 'global' mode."""

    chunk_top_k: int = int(os.getenv("CHUNK_TOP_K", "20"))
    """Number of text chunks to retrieve initially from vector search and keep after reranking.
    If None, defaults to top_k value.
    """

    max_entity_tokens: int = int(os.getenv("MAX_ENTITY_TOKENS", "6000"))
    """Maximum number of tokens allocated for entity context in unified token control system."""

    max_relation_tokens: int = int(os.getenv("MAX_RELATION_TOKENS", "8000"))
    """Maximum number of tokens allocated for relationship context in unified token control system."""

    max_total_tokens: int = int(os.getenv("MAX_TOTAL_TOKENS", "30000"))
    """Maximum total tokens budget for the entire query context (entities + relations + chunks + system prompt)."""

    # History messages are only sent to LLM for context, not used for retrieval
    conversation_history: list[dict[str, str]] = field(default_factory=list)
    """Stores past conversation history to maintain context.
    Format: [{"role": "user/assistant", "content": "message"}].
    """

    # Deprecated (ids filter lead to potential hallucination effects)
    ids: list[str] | None = None
    """List of ids to filter the results."""

    model_func: Callable[..., object] | None = None
    """Optional override for the LLM model function to use for this specific query.
    If provided, this will be used instead of the global model function.
    This allows using different models for different query modes.
    """

    user_prompt: str | None = None
    """User-provided prompt for the query.
    Addition instructions for LLM. If provided, this will be inject into the prompt template.
    It's purpose is the let user customize the way LLM generate the response.
    """

    enable_rerank: bool = True
    """Enable reranking for retrieved text chunks. If True but no rerank model is configured, a warning will be issued.
    Default is True to enable reranking when rerank model is available.
    """
```

> `top_k` のデフォルト値は環境変数 `TOP_K` で変更できます。


## LLM と Embedding の注入

LightRAG は、ドキュメントのインデクシングとクエリのために LLM と Embedding モデルを必要とします。初期化時に、関連するモデル関数を LightRAG に注入します。

### モデル選択の要件

- **LLM**: 32B パラメータ以上、32KB コンテキスト（64KB 推奨）。インデクシング時は推論モデルを避け、クエリ時はより強力なモデルを使用してください。
- **Embedding**: インデクシングとクエリで一貫したモデルを使用する必要があります。推奨: `BAAI/bge-m3`、`text-embedding-3-large`。モデルを変更する場合、ベクトルストレージのクリアが必要です。
- **Reranker**: 検索品質を大幅に向上させます。有効にする場合、クエリモードを `mix` に設定してください。推奨: `BAAI/bge-reranker-v2-m3`、Jina reranker。

#### OpenAI 互換 API の使用

LightRAG は OpenAI 互換の chat/embeddings API をサポートしています:

```python
import os
import numpy as np
from lightrag.utils import wrap_embedding_func_with_attrs
from lightrag.llm.openai import openai_complete_if_cache, openai_embed

async def llm_model_func(
    prompt, system_prompt=None, history_messages=[], keyword_extraction=False, **kwargs
) -> str:
    return await openai_complete_if_cache(
        "solar-mini",
        prompt,
        system_prompt=system_prompt,
        history_messages=history_messages,
        api_key=os.getenv("UPSTAGE_API_KEY"),
        base_url="https://api.upstage.ai/v1/solar",
        **kwargs
    )

@wrap_embedding_func_with_attrs(embedding_dim=4096, max_token_size=8192, model_name="solar-embedding-1-large-query")
async def embedding_func(texts: list[str]) -> np.ndarray:
    return await openai_embed.func(
        texts,
        model="solar-embedding-1-large-query",
        api_key=os.getenv("UPSTAGE_API_KEY"),
        base_url="https://api.upstage.ai/v1/solar"
    )

async def initialize_rag():
    rag = LightRAG(
        working_dir=WORKING_DIR,
        llm_model_func=llm_model_func,
        embedding_func=embedding_func  # Pass the decorated function directly
    )
    await rag.initialize_storages()
    return rag
```

> **Embedding 関数のラッピングに関する重要な注意事項:**
>
> `EmbeddingFunc` はネストできません。`@wrap_embedding_func_with_attrs` でデコレートされた関数（`openai_embed`、`ollama_embed` など）は、`EmbeddingFunc()` で再度ラップすることができません。このため、カスタム Embedding 関数を作成する際は、`xxx_embed` を直接使用するのではなく、`xxx_embed.func`（アンラップされた基底関数）を呼び出します。

#### Hugging Face モデルの使用

`lightrag_hf_demo.py` を参照してください。

```python
from functools import partial
from transformers import AutoTokenizer, AutoModel

# Pre-load tokenizer and model
tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
embed_model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

# Initialize LightRAG with Hugging Face model
rag = LightRAG(
    working_dir=WORKING_DIR,
    llm_model_func=hf_model_complete,  # Use Hugging Face model for text generation
    llm_model_name='meta-llama/Llama-3.1-8B-Instruct',  # Model name from Hugging Face
    # Use Hugging Face embedding function
    embedding_func=EmbeddingFunc(
        embedding_dim=384,
        max_token_size=2048,
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        func=partial(
            hf_embed.func,  # Use .func to access the unwrapped function
            tokenizer=tokenizer,
            embed_model=embed_model
        )
    ),
)
```

#### Ollama モデルの使用

使用するモデルと Embedding モデル（例: `nomic-embed-text`）をプルしてください:

```python
import numpy as np
from lightrag.utils import wrap_embedding_func_with_attrs
from lightrag.llm.ollama import ollama_model_complete, ollama_embed

@wrap_embedding_func_with_attrs(embedding_dim=768, max_token_size=8192, model_name="nomic-embed-text")
async def embedding_func(texts: list[str]) -> np.ndarray:
    return await ollama_embed.func(texts, embed_model="nomic-embed-text")

# Initialize LightRAG with Ollama model
rag = LightRAG(
    working_dir=WORKING_DIR,
    llm_model_func=ollama_model_complete,
    llm_model_name='your_model_name',
    embedding_func=embedding_func,
)
```

#### コンテキストサイズの拡大

LightRAG は最低 32k のコンテキストトークンを必要とします。Ollama のデフォルトは 8k です。2つのアプローチがあります:

*アプローチ 1: Modelfile の編集*

```bash
ollama pull qwen2
ollama show --modelfile qwen2 > Modelfile
# Add this line to Modelfile:
# PARAMETER num_ctx 32768
ollama create -f Modelfile qwen2m
```

*アプローチ 2: `llm_model_kwargs` で `num_ctx` を設定*

```python
rag = LightRAG(
    working_dir=WORKING_DIR,
    llm_model_func=ollama_model_complete,
    llm_model_name='your_model_name',
    llm_model_kwargs={"options": {"num_ctx": 32768}},
    embedding_func=embedding_func,
)
```

> **Embedding 関数のラッピングに関する重要な注意事項:**
>
> `EmbeddingFunc` はネストできません。アンラップされた基底関数にアクセスするには `xxx_embed.func` を使用してください。

**低 RAM GPU**

低 RAM GPU（例: 6GB）の場合、小さなモデルを選択し、コンテキストウィンドウを調整してください。例えば、`gemma2:2b` で `num_ctx=26000` を設定すると、`book.txt` で約197のエンティティと19のリレーションを検出できます。

#### LlamaIndex

LightRAG は LlamaIndex との統合をサポートしています（`llm/llama_index_impl.py`）:

```python
import asyncio
from lightrag import LightRAG
from lightrag.llm.llama_index_impl import llama_index_complete_if_cache, llama_index_embed
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from lightrag.utils import setup_logger

setup_logger("lightrag", level="INFO")

async def initialize_rag():
    rag = LightRAG(
        working_dir="your/path",
        llm_model_func=llama_index_complete_if_cache,
        embedding_func=EmbeddingFunc(
            embedding_dim=1536,
            max_token_size=2048,
            model_name=embed_model,
            func=partial(llama_index_embed.func, embed_model=embed_model)
        ),
    )
    await rag.initialize_storages()
    return rag
```

**参考資料:**
- [LlamaIndex Documentation](https://developers.llamaindex.ai/python/framework/)
- [Direct OpenAI Example](examples/unofficial-sample/lightrag_llamaindex_direct_demo.py)
- [LiteLLM Proxy Example](examples/unofficial-sample/lightrag_llamaindex_litellm_demo.py)
- [LiteLLM Proxy with Opik Example](examples/unofficial-sample/lightrag_llamaindex_litellm_opik_demo.py)

#### Azure OpenAI モデルの使用

```python
import os
import numpy as np
from lightrag.utils import wrap_embedding_func_with_attrs
from lightrag.llm.azure_openai import azure_openai_complete_if_cache, azure_openai_embed

async def llm_model_func(
    prompt, system_prompt=None, history_messages=[], keyword_extraction=False, **kwargs
) -> str:
    return await azure_openai_complete_if_cache(
        prompt,
        system_prompt=system_prompt,
        history_messages=history_messages,
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        **kwargs
    )

@wrap_embedding_func_with_attrs(
    embedding_dim=1536,
    max_token_size=8192,
    model_name=os.getenv("AZURE_OPENAI_EMBEDDING_MODEL")
)
async def embedding_func(texts: list[str]) -> np.ndarray:
    return await azure_openai_embed.func(
        texts,
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        deployment_name=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME")
    )

rag = LightRAG(
    working_dir=WORKING_DIR,
    llm_model_func=llm_model_func,
    embedding_func=embedding_func
)
```

#### Google Gemini モデルの使用

```python
import os
import numpy as np
from lightrag.utils import wrap_embedding_func_with_attrs
from lightrag.llm.gemini import gemini_model_complete, gemini_embed

async def llm_model_func(
    prompt, system_prompt=None, history_messages=[], keyword_extraction=False, **kwargs
) -> str:
    return await gemini_model_complete(
        prompt,
        system_prompt=system_prompt,
        history_messages=history_messages,
        api_key=os.getenv("GEMINI_API_KEY"),
        model_name="gemini-2.0-flash",
        **kwargs
    )

@wrap_embedding_func_with_attrs(
    embedding_dim=768,
    max_token_size=2048,
    model_name="models/text-embedding-004"
)
async def embedding_func(texts: list[str]) -> np.ndarray:
    return await gemini_embed.func(
        texts,
        api_key=os.getenv("GEMINI_API_KEY"),
        model="models/text-embedding-004"
    )

rag = LightRAG(
    working_dir=WORKING_DIR,
    llm_model_func=llm_model_func,
    llm_model_name="gemini-2.0-flash",
    embedding_func=embedding_func
)
```

### Rerank 関数の注入

検索品質を向上させるために、より効果的な関連性スコアリングモデルに基づいてドキュメントを再ランク付けできます。`rerank.py` ファイルは3つの Reranker プロバイダドライバ関数を提供しています:

- **Cohere / vLLM**: `cohere_rerank`
- **Jina AI**: `jina_rerank`
- **Aliyun**: `ali_rerank`

これらの関数のいずれかを LightRAG オブジェクトの `rerank_model_func` 属性に注入してください。詳細な使用方法については、`examples/rerank_example.py` を参照してください。

### User Prompt とクエリの関係

LightRAG をコンテンツクエリに使用する際、検索プロセスと無関係な出力処理を組み合わせないでください。クエリの効果に大きく影響します。`QueryParam` の `user_prompt` パラメータは RAG 検索フェーズには関与しません。クエリ完了後に取得された結果をどのように処理するかを LLM に指示するものです。

```python
query_param = QueryParam(
    mode="hybrid",
    user_prompt="For diagrams, use mermaid format with English/Pinyin node names and Chinese display labels",
)

response_default = rag.query(
    "Please draw a character relationship diagram for Scrooge",
    param=query_param
)
print(response_default)
```


## ストレージバックエンド

### ストレージタイプ

LightRAG は、異なる目的に応じて4種類のストレージを使用します:

| ストレージタイプ | 目的 |
|---|---|
| **KV_STORAGE** | LLM レスポンスキャッシュ、テキストチャンク、ドキュメント情報 |
| **VECTOR_STORAGE** | エンティティ/リレーション/チャンクの埋め込みベクトル |
| **GRAPH_STORAGE** | エンティティ・リレーションのグラフ構造 |
| **DOC_STATUS_STORAGE** | ドキュメントのインデクシングステータス |

### サポートされる実装

**KV_STORAGE**
```
JsonKVStorage        JsonFile (default)
PGKVStorage          Postgres
RedisKVStorage       Redis
MongoKVStorage       MongoDB
OpenSearchKVStorage  OpenSearch
```

**GRAPH_STORAGE**
```
NetworkXStorage          NetworkX (default)
Neo4JStorage             Neo4J
PGGraphStorage           PostgreSQL with AGE plugin
MemgraphStorage          Memgraph
OpenSearchGraphStorage   OpenSearch
```

> テストにより、本番環境では Neo4J が PostgreSQL with AGE plugin と比較して優れたパフォーマンスを発揮することが示されています。

**VECTOR_STORAGE**
```
NanoVectorDBStorage         NanoVector (default)
PGVectorStorage             Postgres
MilvusVectorDBStorage       Milvus
FaissVectorDBStorage        Faiss
QdrantVectorDBStorage       Qdrant
MongoVectorDBStorage        MongoDB
OpenSearchVectorDBStorage   OpenSearch
```

**DOC_STATUS_STORAGE**
```
JsonDocStatusStorage        JsonFile (default)
PGDocStatusStorage          Postgres
MongoDocStatusStorage       MongoDB
OpenSearchDocStatusStorage  OpenSearch
```

各ストレージタイプの接続設定例は、リポジトリの `env.example` ファイルにあります。接続文字列内のデータベースインスタンスは事前に作成する必要があります。LightRAG はインスタンス内のテーブルのみを作成し、インスタンス自体は作成しません。

### バックエンド固有のセットアップ

#### Neo4J Storage の使用

本番レベルのシナリオでは、KG ストレージにエンタープライズソリューションを活用することを推奨します。シームレスなローカルテストには、Docker での Neo4J の実行を推奨します。参照: https://hub.docker.com/_/neo4j

```bash
export NEO4J_URI="neo4j://localhost:7687"
export NEO4J_USERNAME="neo4j"
export NEO4J_PASSWORD="password"
export NEO4J_DATABASE="neo4j"  # Required for community edition
```

```python
from lightrag.utils import setup_logger

setup_logger("lightrag", level="INFO")

async def initialize_rag():
    rag = LightRAG(
        working_dir=WORKING_DIR,
        llm_model_func=gpt_4o_mini_complete,
        graph_storage="Neo4JStorage",
    )
    await rag.initialize_storages()
    return rag
```

動作例については `test_neo4j.py` を参照してください。

#### PostgreSQL Storage の使用

PostgreSQL は、KV ストア、VectorDB（pgvector）、GraphDB（apache AGE）のワンストップソリューションを提供できます。PostgreSQL バージョン 16.6 以上がサポートされています。

- PostgreSQL は軽量で、必要なプラグインを含むバイナリディストリビューション全体を 40MB に圧縮できます: Linux/Mac では簡単にインストールできるため、[Windows Release](https://github.com/ShanGor/apache-age-windows/releases/tag/PG17%2Fv1.5.0-rc0) を参照してください。
- Docker を使用する場合は、このイメージから始めてください（デフォルトのユーザーパスワード: rag/rag）: https://hub.docker.com/r/gzdaniel/postgres-for-rag
- 始め方: [examples/lightrag_gemini_postgres_demo.py](https://github.com/HKUDS/LightRAG/blob/main/examples/lightrag_gemini_postgres_demo.py) を参照
- 高性能グラフデータベースが必要な場合は、Apache AGE のパフォーマンスは競争力が低いため、Neo4j を推奨します。

#### Faiss Storage の使用

Faiss を使用する前に、`faiss-cpu` または `faiss-gpu` を手動でインストールしてください:

```bash
pip install faiss-cpu
```

```python
async def embedding_func(texts: list[str]) -> np.ndarray:
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode(texts, convert_to_numpy=True)
    return embeddings

rag = LightRAG(
    working_dir=WORKING_DIR,
    llm_model_func=llm_model_func,
    embedding_func=EmbeddingFunc(
        embedding_dim=384,
        max_token_size=2048,
        model_name="all-MiniLM-L6-v2",
        func=embedding_func,
    ),
    vector_storage="FaissVectorDBStorage",
    vector_db_storage_cls_kwargs={
        "cosine_better_than_threshold": 0.3
    }
)
```

#### Memgraph をストレージに使用

Memgraph は、Neo4j Bolt プロトコルと互換性のある高性能インメモリグラフデータベースです。参照: https://memgraph.com/download

```bash
export MEMGRAPH_URI="bolt://localhost:7687"
```

```python
async def initialize_rag():
    rag = LightRAG(
        working_dir=WORKING_DIR,
        llm_model_func=gpt_4o_mini_complete,
        graph_storage="MemgraphStorage",
    )
    await rag.initialize_storages()
    return rag
```

#### Milvus をベクトルストレージに使用

Milvus は、本番レベルのベクトルストレージ向けの高性能でスケーラブルなベクトルデータベースです。インデックスタイプ（HNSW、HNSW_SQ、IVF、DISKANN など）やメトリックタイプを含む完全な設定オプションについては、[docs/MilvusConfigurationGuide.md](./MilvusConfigurationGuide.md) を参照してください。

**環境変数によるクイックセットアップ:**

```bash
MILVUS_URI=http://localhost:19530
MILVUS_DB_NAME=lightrag
LIGHTRAG_VECTOR_STORAGE=MilvusVectorDBStorage
```

**Python SDK によるクイックセットアップ:**

```python
rag = LightRAG(
    working_dir="./rag_storage",
    llm_model_func=...,
    embedding_func=...,
    vector_storage="MilvusVectorDBStorage",
    vector_db_storage_cls_kwargs={
        "milvus_uri": "http://localhost:19530",
        "milvus_db_name": "lightrag",
        "cosine_better_than_threshold": 0.2,
    },
)
```

#### MongoDB Storage の使用

MongoDB は、ネイティブ KV ストレージとベクトルストレージによる LightRAG のワンストップストレージソリューションを提供します。LightRAG は MongoDB コレクションを使用してシンプルなグラフストレージを実装しています。

`MongoVectorDBStorage` は、Atlas Search / Vector Search をサポートする MongoDB デプロイメント（例: MongoDB Atlas または Atlas local）が必要です。セットアップウィザードにバンドルされたローカル Docker MongoDB サービスは MongoDB Community Edition であり、KV/graph/doc-status ストレージには使用できますが、`MongoVectorDBStorage` には使用**できません**。

#### Redis Storage の使用

LightRAG は KV ストレージとして Redis をサポートしています。永続化とメモリ使用量を慎重に設定してください。推奨 Redis 設定:

```
save 900 1
save 300 10
save 60 1000
stop-writes-on-bgsave-error yes
maxmemory 4gb
maxmemory-policy noeviction
maxclients 500
```

インタラクティブセットアップがローカル Redis コンテナを管理する場合、ユーザー編集可能な設定を `./data/config/redis.conf` にステージングし、コンテナにマウントします。セットアップは再実行時にこのファイルを保持するため、手動の編集を失うことなくローカル Redis のチューニングを調整できます。

#### OpenSearch Storage の使用

OpenSearch は、LightRAG の4つのストレージタイプ（KV、Vector、Graph、DocStatus）すべてに対応した統合ストレージソリューションを提供します。クラウド限定の制限なしに、ネイティブ k-NN ベクトル検索、全文検索、水平スケーラビリティを提供します。

**要件**: k-NN プラグインが有効な OpenSearch 3.x 以上。

Docker でインストール（プラグインなし）:
```bash
docker run -d -p 9200:9200 -e "discovery.type=single-node" \
  -e "OPENSEARCH_INITIAL_ADMIN_PASSWORD=<custom-admin-password>" \
  opensearchproject/opensearch:latest
```

Docker Compose でインストール（推奨、プラグイン付き）:
```bash
curl -O https://raw.githubusercontent.com/opensearch-project/opensearch-build/main/docker/release/dockercomposefiles/docker-compose-3.x.yml
OPENSEARCH_INITIAL_ADMIN_PASSWORD=<custom-admin-password> docker-compose -f docker-compose-3.x.yml up -d
```

**設定**（完全なリストは `env.example` を参照）:
```bash
export OPENSEARCH_HOSTS=localhost:9200
export OPENSEARCH_USER=admin
export OPENSEARCH_PASSWORD=<custom-admin-password>
export OPENSEARCH_USE_SSL=true
export OPENSEARCH_VERIFY_CERTS=false
```

**使用方法**:
```python
rag = LightRAG(
    working_dir=WORKING_DIR,
    llm_model_func=your_llm_func,
    embedding_func=your_embed_func,
    kv_storage="OpenSearchKVStorage",
    doc_status_storage="OpenSearchDocStatusStorage",
    graph_storage="OpenSearchGraphStorage",
    vector_storage="OpenSearchVectorDBStorage",
)
```

**グラフ走査**: PPL サポート付きの OpenSearch SQL プラグインが利用可能な場合、グラフクエリは `graphlookup` コマンドによるサーバーサイド BFS を使用して最適なパフォーマンスを実現します。それ以外の場合、クライアントサイドのバッチ BFS にフォールバックします。起動時に自動検出されますが、`OPENSEARCH_USE_PPL_GRAPHLOOKUP=true|false` で強制することもできます。

**統合テスト**:

1. Docker Compose で OpenSearch を起動:
```bash
OPENSEARCH_INITIAL_ADMIN_PASSWORD=<custom-admin-password> docker-compose -f docker-compose-3.x.yml up -d
```

2. クラスタの動作を確認:
```bash
curl -sk -u admin:<custom-admin-password> https://localhost:9200
curl -sk -u admin:<custom-admin-password> https://localhost:9200/_cat/plugins?v
```

3. ユニットテストを実行（OpenSearch 不要 - モックを使用）:
```bash
python -m pytest tests/test_opensearch_storage.py -v
```

4. OpenSearch ストレージデモを実行:
```bash
export OPENSEARCH_HOSTS=localhost:9200
export OPENSEARCH_USER=admin
export OPENSEARCH_PASSWORD=<custom-admin-password>
export OPENSEARCH_USE_SSL=true
export OPENSEARCH_VERIFY_CERTS=false
python examples/opensearch_storage_demo.py
```

5. 完全な OpenAI + OpenSearch デモを実行（`OPENAI_API_KEY` が必要）:
```bash
export OPENAI_API_KEY=your-api-key
python examples/lightrag_openai_opensearch_graph_demo.py
```

6. LightRAG WebUI でナレッジグラフを可視化:
```bash
LIGHTRAG_KV_STORAGE=OpenSearchKVStorage \
LIGHTRAG_DOC_STATUS_STORAGE=OpenSearchDocStatusStorage \
LIGHTRAG_GRAPH_STORAGE=OpenSearchGraphStorage \
LIGHTRAG_VECTOR_STORAGE=OpenSearchVectorDBStorage \
LLM_BINDING=openai \
EMBEDDING_BINDING=openai \
EMBEDDING_MODEL=text-embedding-3-large \
EMBEDDING_DIM=3072 \
OPENAI_API_KEY=your-api-key \
lightrag-server
```


## LightRAG インスタンス間のデータ分離

`workspace` パラメータは、異なる LightRAG インスタンス間のデータ分離を保証します。初期化後、`workspace` は変更不可です。

| ストレージタイプ | 分離方法 |
|---|---|
| `JsonKVStorage`, `JsonDocStatusStorage`, `NetworkXStorage`, `NanoVectorDBStorage`, `FaissVectorDBStorage` | ワークスペースサブディレクトリ |
| `RedisKVStorage`, `MilvusVectorDBStorage`, `MongoKVStorage`, `MongoVectorDBStorage`, `MongoGraphStorage`, `PGGraphStorage` | コレクション名のワークスペースプレフィックス |
| `QdrantVectorDBStorage` | ペイロードベースのパーティショニング（Qdrant マルチテナンシー） |
| `PGKVStorage`, `PGVectorStorage`, `PGDocStatusStorage` | テーブル内の `workspace` フィールド |
| `Neo4JStorage` | ラベル |
| `OpenSearch*` | インデックス名のプレフィックス |

**レガシー互換性**: PostgreSQL 非グラフストレージのデフォルトワークスペースは `default`、PostgreSQL AGE グラフストレージは null、Neo4j グラフストレージは `base` です。

ストレージ固有のワークスペース環境変数は、共通の `WORKSPACE` 変数をオーバーライドします: `REDIS_WORKSPACE`, `MILVUS_WORKSPACE`, `QDRANT_WORKSPACE`, `MONGODB_WORKSPACE`, `POSTGRES_WORKSPACE`, `NEO4J_WORKSPACE`, `OPENSEARCH_WORKSPACE`。

複数の分離されたナレッジベースを管理する実践的なデモについては、[Workspace Demo](examples/lightrag_gemini_workspace_demo.py) を参照してください。


## Insert

* 基本的な Insert

```python
rag.insert("Text")
```

* バッチ Insert

```python
# Basic Batch Insert
rag.insert(["TEXT1", "TEXT2", ...])

# Batch Insert with custom batch size
rag = LightRAG(
    ...
    working_dir=WORKING_DIR,
    max_parallel_insert=4
)
rag.insert(["TEXT1", "TEXT2", "TEXT3", ...])  # Processed in batches of 4
```

`max_parallel_insert` パラメータは、同時に処理されるドキュメント数を決定します。デフォルトは **2** です。ボトルネックは通常 LLM にあるため、**10 未満** に保つことを推奨します。

* ID 付き Insert

ドキュメント数と ID 数は同じである必要があります。

```python
# Single text with ID
rag.insert("TEXT1", ids=["ID_FOR_TEXT1"])

# Multiple texts with IDs
rag.insert(["TEXT1", "TEXT2", ...], ids=["ID_FOR_TEXT1", "ID_FOR_TEXT2"])
```

* Pipeline を使用した Insert

`apipeline_enqueue_documents` と `apipeline_process_enqueue_documents` を使用すると、メインスレッドの実行を継続しながら、バックグラウンドでドキュメントを段階的に挿入できます。

```python
rag = LightRAG(..)
await rag.apipeline_enqueue_documents(input)
# Your routine in loop
await rag.apipeline_process_enqueue_documents(input)
```

* マルチファイルタイプサポートの Insert

`textract` ライブラリは TXT、DOCX、PPTX、CSV、PDF の読み取りをサポートしています:

```python
import textract

file_path = 'TEXT.pdf'
text_content = textract.process(file_path)
rag.insert(text_content.decode('utf-8'))
```

* 引用機能

ファイルパスを提供することで、ソースを元のドキュメントまで追跡できることを保証します:

```python
documents = ["Document content 1", "Document content 2"]
file_paths = ["path/to/doc1.txt", "path/to/doc2.txt"]

rag.insert(documents, file_paths=file_paths)
```


## エンティティとリレーションの編集

LightRAG は包括的なナレッジグラフ管理をサポートしています: エンティティとリレーションシップの作成、編集、削除。

* エンティティとリレーションの作成

```python
# Create entity
entity = rag.create_entity("Google", {
    "description": "Google is a multinational technology company specializing in internet-related services and products.",
    "entity_type": "company"
})

product = rag.create_entity("Gmail", {
    "description": "Gmail is an email service developed by Google.",
    "entity_type": "product"
})

# Create relation
relation = rag.create_relation("Google", "Gmail", {
    "description": "Google develops and operates Gmail.",
    "keywords": "develops operates service",
    "weight": 2.0
})
```

* エンティティとリレーションの編集

```python
# Edit entity attributes
updated_entity = rag.edit_entity("Google", {
    "description": "Google is a subsidiary of Alphabet Inc., founded in 1998.",
    "entity_type": "tech_company"
})

# Rename entity (with all its relationships properly migrated)
renamed_entity = rag.edit_entity("Gmail", {
    "entity_name": "Google Mail",
    "description": "Google Mail (formerly Gmail) is an email service."
})

# Edit relation
updated_relation = rag.edit_relation("Google", "Google Mail", {
    "description": "Google created and maintains Google Mail service.",
    "keywords": "creates maintains email service",
    "weight": 3.0
})
```

すべての操作は同期版と非同期版の両方で利用できます。非同期版はプレフィックス "a" が付きます（例: `acreate_entity`, `aedit_relation`）。

* カスタム KG の Insert

```python
custom_kg = {
    "chunks": [
        {
            "content": "Alice and Bob are collaborating on quantum computing research.",
            "source_id": "doc-1",
            "file_path": "test_file",
        }
    ],
    "entities": [
        {
            "entity_name": "Alice",
            "entity_type": "person",
            "description": "Alice is a researcher specializing in quantum physics.",
            "source_id": "doc-1",
            "file_path": "test_file"
        },
        {
            "entity_name": "Bob",
            "entity_type": "person",
            "description": "Bob is a mathematician.",
            "source_id": "doc-1",
            "file_path": "test_file"
        },
        {
            "entity_name": "Quantum Computing",
            "entity_type": "technology",
            "description": "Quantum computing utilizes quantum mechanical phenomena for computation.",
            "source_id": "doc-1",
            "file_path": "test_file"
        }
    ],
    "relationships": [
        {
            "src_id": "Alice",
            "tgt_id": "Bob",
            "description": "Alice and Bob are research partners.",
            "keywords": "collaboration research",
            "weight": 1.0,
            "source_id": "doc-1",
            "file_path": "test_file"
        },
        {
            "src_id": "Alice",
            "tgt_id": "Quantum Computing",
            "description": "Alice conducts research on quantum computing.",
            "keywords": "research expertise",
            "weight": 1.0,
            "source_id": "doc-1",
            "file_path": "test_file"
        },
        {
            "src_id": "Bob",
            "tgt_id": "Quantum Computing",
            "description": "Bob researches quantum computing.",
            "keywords": "research application",
            "weight": 1.0,
            "source_id": "doc-1",
            "file_path": "test_file"
        }
    ]
}

rag.insert_custom_kg(custom_kg)
```

* その他のエンティティとリレーション操作
  - **create_entity**: 指定された属性で新しいエンティティを作成
  - **edit_entity**: 既存のエンティティの属性を更新またはリネーム
  - **create_relation**: 既存のエンティティ間に新しいリレーションを作成
  - **edit_relation**: 既存のリレーションの属性を更新

これらの操作は、グラフデータベースとベクトルデータベースの両方のコンポーネント間でデータの一貫性を維持します。


## 削除機能

LightRAG は包括的な削除機能を提供します。

### エンティティの削除

```python
# Synchronous
rag.delete_by_entity("Google")

# Asynchronous
await rag.adelete_by_entity("Google")
```

エンティティを削除する場合:
- ナレッジグラフからエンティティノードを削除
- 関連するすべてのリレーションシップを削除
- ベクトルデータベースから関連する埋め込みベクトルを削除
- ナレッジグラフの整合性を維持

### リレーションの削除

```python
# Synchronous
rag.delete_by_relation("Google", "Gmail")

# Asynchronous
await rag.adelete_by_relation("Google", "Gmail")
```

リレーションシップを削除する場合:
- 指定されたリレーションシップエッジを削除
- リレーションシップの埋め込みベクトルを削除
- 両方のエンティティノードとその他のリレーションシップは保持

### ドキュメント ID による削除

```python
# Asynchronous only (complex reconstruction process)
await rag.adelete_by_doc_id("doc-12345")
```

削除プロセス:
1. ドキュメントに関連するすべてのテキストチャンクを削除
2. このドキュメントにのみ属するエンティティ/リレーションシップを特定して削除
3. 他のドキュメントにまだ存在するエンティティ/リレーションシップを再構築
4. 関連するすべてのベクトルインデックスを更新
5. ドキュメントステータスレコードをクリーンアップ

**重要な注意事項:**
1. すべての削除操作は**不可逆**です。慎重に使用してください
2. 大量のデータを削除する場合、特にドキュメント ID による削除は時間がかかることがあります
3. 削除操作は、グラフデータベースとベクトルデータベース間の一貫性を自動的に維持します
4. 重要な削除を実行する前にデータのバックアップを検討してください


## エンティティのマージ

**エンティティとそのリレーションシップのマージ**

```python
# Basic merge
rag.merge_entities(
    source_entities=["Artificial Intelligence", "AI", "Machine Intelligence"],
    target_entity="AI Technology"
)

# With custom merge strategy
rag.merge_entities(
    source_entities=["John Smith", "Dr. Smith", "J. Smith"],
    target_entity="John Smith",
    merge_strategy={
        "description": "concatenate",  # Combine all descriptions
        "entity_type": "keep_first",   # Keep the type from the first entity
        "source_id": "join_unique"     # Combine all unique source IDs
    }
)

# With custom target entity data
rag.merge_entities(
    source_entities=["New York", "NYC", "Big Apple"],
    target_entity="New York City",
    target_entity_data={
        "entity_type": "LOCATION",
        "description": "New York City is the most populous city in the United States.",
    }
)

# Advanced: combining both strategy and custom data
rag.merge_entities(
    source_entities=["Microsoft Corp", "Microsoft Corporation", "MSFT"],
    target_entity="Microsoft",
    merge_strategy={
        "description": "concatenate",
        "source_id": "join_unique"
    },
    target_entity_data={
        "entity_type": "ORGANIZATION",
    }
)
```

エンティティをマージする場合:
- ソースエンティティのすべてのリレーションシップがターゲットエンティティにリダイレクト
- 重複するリレーションシップはインテリジェントにマージ
- 自己リレーション（ループ）を防止
- マージ後にソースエンティティを削除
- リレーションシップの重みと属性を保持


## トラブルシューティング

### 初期化に関する一般的なエラー

1. **`AttributeError: __aenter__`**
   - **原因**: ストレージバックエンドが初期化されていない
   - **解決方法**: LightRAG インスタンスを作成した後に `await rag.initialize_storages()` を呼び出す

2. **`KeyError: 'history_messages'`**
   - **原因**: パイプラインのステータスが初期化されていない
   - **解決方法**: LightRAG インスタンスを作成した後に `await rag.initialize_storages()` を呼び出す

3. **両方のエラーが連続して発生する場合**
   - **解決方法**: 常に以下のパターンに従ってください:
   ```python
   rag = LightRAG(...)
   await rag.initialize_storages()
   ```

### モデル切り替えの問題

異なる Embedding モデルに切り替える場合、エラーを回避するためにデータディレクトリをクリアする必要があります。LLM キャッシュを保持したい場合に保存しておくべきファイルは `kv_store_llm_response_cache.json` のみです。
