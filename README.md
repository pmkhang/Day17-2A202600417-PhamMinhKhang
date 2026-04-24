# Lab #17 — Multi-Memory Agent với LangGraph

## Reflection: Privacy & Limitations

### 1. Memory nào giúp agent nhất?

**Long-term profile** giúp nhiều nhất — lưu thông tin cá nhân (tên, nghề, dị ứng) và inject vào mọi turn, giúp agent cá nhân hóa câu trả lời xuyên suốt session.

### 2. Rủi ro PII/Privacy

**Long-term profile** là memory nhạy cảm nhất vì lưu thông tin cá nhân dạng plaintext trong `data/profile.json`:
- Tên, địa chỉ, dị ứng, nghề nghiệp — đây là PII trực tiếp.
- Nếu file bị leak hoặc truy cập trái phép, toàn bộ profile bị lộ.
- **Episodic memory** cũng rủi ro nếu user chia sẻ thông tin nhạy cảm trong conversation (mật khẩu, số tài khoản).

### 3. Nếu user yêu cầu xóa memory

| Memory | Cách xóa |
|--------|----------|
| Short-term | `short_term.clear()` — xóa ngay trong RAM |
| Long-term profile | Xóa key trong `data/profile.json` hoặc xóa file |
| Episodic | Xóa entry trong `data/episodes.json` theo index/timestamp |
| Semantic | `collection.delete(ids=[doc_id])` trong ChromaDB |

Hiện tại chưa có API xóa — cần implement `delete()` cho từng backend.

### 4. Consent & TTL

- Chưa có cơ chế **consent** — agent lưu profile facts mà không hỏi user.
- Chưa có **TTL** — data tồn tại vĩnh viễn, không tự expire.
- Cần thêm: timestamp khi lưu, TTL config, và confirmation trước khi persist PII.

### 5. Risk của retrieval sai

- **Semantic retrieval** có thể trả về chunk không liên quan nếu query quá ngắn hoặc embedding model yếu.
- **Episodic recall** lấy n episodes gần nhất — không filter theo relevance, có thể inject noise vào prompt.
- **Conflict handling** dựa vào LLM extract JSON — nếu LLM parse sai, fact cũ bị ghi đè nhầm.

### 6. Limitations kỹ thuật

1. **Token counting thô** — dùng `len(chars)` thay vì tokenizer thật, có thể cắt giữa câu.
2. **LLM extraction không ổn định** — JSON parse từ LLM có thể fail nếu model trả về format lạ (đã có try/except nhưng silent fail).
3. **ChromaDB local** — không scale multi-user, mỗi user cần collection riêng.
4. **Không có auth** — bất kỳ ai có access filesystem đều đọc được `data/profile.json`.
5. **Episodic save dựa vào keyword** — heuristic đơn giản, dễ miss hoặc false positive.
