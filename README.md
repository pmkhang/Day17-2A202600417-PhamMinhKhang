# Lab #17 — Multi-Memory Agent with LangGraph

Agent hội thoại đa bộ nhớ sử dụng LangGraph, gồm short-term, long-term, episodic, semantic memory; có cơ chế retrieve/inject vào prompt, cập nhật memory sau mỗi turn, và xử lý conflict theo nguyên tắc fact mới ghi đè fact cũ.

## 1. Mục tiêu

- Xây dựng full memory stack cho conversational agent.
- Dùng LangGraph để điều phối luồng `retrieve_memory -> call_llm -> save_memory`.
- Đảm bảo agent có thể:
  - Recall profile dài hạn.
  - Lưu và recall episodic outcomes.
  - Query semantic knowledge bằng vector retrieval.
  - Trim prompt theo token budget.

## 2. Kiến trúc hệ thống

### 2.1 Memory stack

- `ShortTermMemory`:
  - In-memory buffer.
  - Sliding window theo turns.
  - `max_turns=10` tương đương tối đa 20 messages (user/assistant pairs).

- `LongTermMemory`:
  - JSON key-value store (`data/profile.json`).
  - API: `save`, `retrieve`, `all`.

- `RedisLongTermMemory`:
  - Ưu tiên Redis nếu có `REDIS_URL`.
  - Tự fallback về JSON (`LongTermMemory`) khi Redis unavailable.

- `EpisodicMemory`:
  - Lưu danh sách episodes vào `data/episodes.json`.
  - API: `save`, `retrieve(n)`.

- `SemanticMemory`:
  - ChromaDB PersistentClient (`data/chroma_db`).
  - API: `save`, `retrieve(query, n_results)`.

### 2.2 Graph flow (LangGraph)

- Node 1: `retrieve_memory(state)`
  - Load `user_profile`, `episodes`, `semantic_hits`.
- Node 2: `call_llm(state)`
  - Build system prompt với 4 sections:
    - Profile
    - Episodic Memory
    - Semantic Knowledge
    - Recent Conversation
- Node 3: `save_memory(state)`
  - Extract profile facts từ user message (LLM JSON extraction + parse handling).
  - Save episodic khi có outcome keywords.
  - Auto-ingest assistant reply vào semantic store.

Luồng chạy: `START -> retrieve_memory -> call_llm -> save_memory -> END`.

## 3. Cấu trúc thư mục

```text
.
├── data/
│   ├── profile.json
│   ├── episodes.json
│   └── chroma_db/
├── src/
│   ├── agent.py
│   ├── providers.py
│   ├── tokens.py
│   └── memory/
│       ├── short_term.py
│       ├── long_term.py
│       ├── redis_long_term.py
│       ├── episodic.py
│       └── semantic.py
├── BENCHMARK.md
├── tasks.md
└── Makefile
```

## 4. Yêu cầu môi trường

- Python `>=3.12`
- `uv` để quản lý dependencies

Dependencies chính:
- `langgraph`
- `openai`
- `chromadb`
- `redis`
- `python-dotenv`
- `tiktoken`

## 5. Cài đặt và chạy

### 5.1 Cài dependencies

```bash
make setup
```

### 5.2 Chạy toàn bộ checklist task

```bash
make check
```

### 5.3 Chạy từng nhóm check

```bash
make check-memory
make check-graph
make check-conflict
make check-benchmark
make check-reflection
make check-bonus
```

### 5.4 Demo graph flow

```bash
make graph-demo
```

### 5.5 Compile check

```bash
make compile
```

## 6. Cấu hình biến môi trường

Ứng dụng hỗ trợ 2 provider:

- `AI_PROVIDER=openai`
  - `OPENAI_API_KEY`
  - `OPENAI_MODEL` (default: `gpt-4o-mini`)

- `AI_PROVIDER=9router` (default)
  - `NINEROUTER_BASE_URL` (default: `http://localhost:20128/v1`)
  - `NINEROUTER_API_KEY`
  - `NINEROUTER_MODEL` (default: `cx/gpt-5.2`)

Optional:
- `REDIS_URL` để bật Redis long-term storage.

## 7. Token budget và trimming

- Budget hiện tại: `MEMORY_BUDGET = 500` tokens.
- Đếm token bằng `tiktoken (cl100k_base)`.
- Nếu không có `tiktoken`, fallback sang heuristic `word_count * 1.3`.
- Prompt được trim dần theo từng dòng cho tới khi `count_tokens(system) <= memory_budget`.

## 8. Benchmark

File benchmark: `BENCHMARK.md`

- 10 multi-turn conversations.
- So sánh `No-memory` vs `With-memory`.
- Bao phủ đủ 5 nhóm:
  - Profile recall
  - Conflict update
  - Episodic recall
  - Semantic retrieval
  - Trim/token budget

## 9. Reflection: Privacy, Safety, Limitations

### 9.1 Memory nào giúp agent nhiều nhất

`Long-term profile memory` hữu ích nhất cho personalization vì cung cấp facts ổn định xuyên suốt nhiều turn/session.

### 9.2 Rủi ro PII/Privacy

- Memory nhạy cảm nhất: `long-term profile` (PII trực tiếp như tên, nghề, dị ứng).
- `episodic memory` cũng có rủi ro nếu hội thoại chứa thông tin nhạy cảm.
- Dữ liệu hiện được lưu local, chưa có encryption-at-rest hoặc access control.

### 9.3 Deletion / TTL / Consent

- Hiện chưa có API delete thống nhất cho mọi backend.
- Chưa có TTL để tự động hết hạn dữ liệu.
- Chưa có consent flow rõ ràng trước khi persist dữ liệu cá nhân.

### 9.4 Risk khi retrieval sai

- Semantic retrieval có thể trả về thông tin không liên quan.
- Episodic retrieval đang ưu tiên recent items, chưa rerank theo relevance.
- LLM extraction có thể parse sai schema và gây lưu sai fact.

### 9.5 Hạn chế kỹ thuật hiện tại

1. Chưa có test tự động end-to-end cho các luồng hội thoại dài.
2. Episodic save vẫn dựa vào keyword heuristic (có thể false positive/false negative).
3. ChromaDB local chưa tối ưu cho multi-tenant production scale.
4. Chưa có auth/authorization layer cho truy cập memory stores.

## 10. Hướng cải tiến

1. Thêm `delete()` và `ttl()` cho từng memory backend.
2. Thêm consent policy trước khi lưu PII.
3. Nâng semantic retrieval bằng metadata filtering + reranking.
4. Viết test tự động cho conflict update, prompt trimming, và episodic trigger.
5. Bổ sung observability (logging/tracing) cho memory pipeline.
