# Tasks — Lab #17: Build Multi-Memory Agent với LangGraph

## 1. Full memory stack (25 điểm)

- [x] Implement short-term memory (list/sliding window/conversation buffer)
- [x] Implement long-term profile memory (dict/JSON/KV store)
- [x] Implement episodic memory (JSON list/file/log store)
- [x] Implement semantic memory (Chroma/FAISS/vector search)
- [x] Đảm bảo mỗi memory type có interface lưu/retrieve riêng biệt

## 2. LangGraph state/router + prompt injection (30 điểm)

- [ ] Định nghĩa `MemoryState` (TypedDict với messages, user_profile, episodes, semantic_hits, memory_budget)
- [ ] Implement node `retrieve_memory(state)` gom memory từ các backends
- [ ] Router inject memory vào state
- [ ] Xây dựng prompt có 4 section rõ: profile, episodic, semantic, recent conversation
- [ ] Implement trim/token budget cơ bản

## 3. Save/update memory + conflict handling (15 điểm)

- [ ] Update ít nhất 2 profile facts
- [ ] Ghi episodic memory khi task hoàn tất / có outcome rõ
- [ ] Xử lý conflict: fact mới ghi đè fact cũ (test case: dị ứng sữa bò → dị ứng đậu nành)
- [ ] Không append bừa gây mâu thuẫn profile

## 4. Benchmark 10 multi-turn conversations (20 điểm)

- [ ] Tạo file `BENCHMARK.md`
- [ ] Viết đủ 10 multi-turn conversations (mỗi conversation nhiều turn)
- [ ] So sánh no-memory vs with-memory cho từng scenario
- [ ] Bao phủ đủ 5 nhóm test:
  - [ ] Profile recall
  - [ ] Conflict update
  - [ ] Episodic recall
  - [ ] Semantic retrieval
  - [ ] Trim/token budget

## 5. Reflection privacy/limitations (10 điểm)

- [ ] Nhận diện ít nhất 1 rủi ro PII/privacy
- [ ] Nêu memory nào nhạy cảm nhất
- [ ] Đề cập deletion, TTL, consent hoặc risk của retrieval sai
- [ ] Nêu ít nhất 1 limitation kỹ thuật của solution hiện tại

## Bonus (tùy chọn)

- [ ] Redis thật chạy ổn (+2)
- [ ] Chroma/FAISS thật chạy ổn (+2)
- [ ] LLM-based extraction có parse/error handling (+2)
- [ ] Token counting tốt hơn word count (+2)
- [ ] Graph flow demo rõ, dễ explain (+2)
