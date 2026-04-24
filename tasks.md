# Tasks — Lab #17: Build Multi-Memory Agent với LangGraph

## 1. Full memory stack (25 điểm)

- [x] Implement short-term memory (list/sliding window/conversation buffer)
- [x] Implement long-term profile memory (dict/JSON/KV store)
- [x] Implement episodic memory (JSON list/file/log store)
- [x] Implement semantic memory (Chroma/FAISS/vector search)
- [x] Đảm bảo mỗi memory type có interface lưu/retrieve riêng biệt

## 2. LangGraph state/router + prompt injection (30 điểm)

- [x] Định nghĩa `MemoryState` (TypedDict với messages, user_profile, episodes, semantic_hits, memory_budget)
- [x] Implement node `retrieve_memory(state)` gom memory từ các backends
- [x] Router inject memory vào state
- [x] Xây dựng prompt có 4 section rõ: profile, episodic, semantic, recent conversation
- [x] Implement trim/token budget cơ bản

## 3. Save/update memory + conflict handling (15 điểm)

- [x] Update ít nhất 2 profile facts
- [x] Ghi episodic memory khi task hoàn tất / có outcome rõ
- [x] Xử lý conflict: fact mới ghi đè fact cũ (test case: dị ứng sữa bò → dị ứng đậu nành)
- [x] Không append bừa gây mâu thuẫn profile

## 4. Benchmark 10 multi-turn conversations (20 điểm)

- [x] Tạo file `BENCHMARK.md`
- [x] Viết đủ 10 multi-turn conversations (mỗi conversation nhiều turn)
- [x] So sánh no-memory vs with-memory cho từng scenario
- [x] Bao phủ đủ 5 nhóm test:
  - [x] Profile recall
  - [x] Conflict update
  - [x] Episodic recall
  - [x] Semantic retrieval
  - [x] Trim/token budget

## 5. Reflection privacy/limitations (10 điểm)

- [x] Nhận diện ít nhất 1 rủi ro PII/privacy
- [x] Nêu memory nào nhạy cảm nhất
- [x] Đề cập deletion, TTL, consent hoặc risk của retrieval sai
- [x] Nêu ít nhất 1 limitation kỹ thuật của solution hiện tại

## Bonus (tùy chọn)

- [x] Redis thật chạy ổn (+2)
- [x] Chroma/FAISS thật chạy ổn (+2)
- [x] LLM-based extraction có parse/error handling (+2)
- [x] Token counting tốt hơn word count (+2)
- [x] Graph flow demo rõ, dễ explain (+2)
