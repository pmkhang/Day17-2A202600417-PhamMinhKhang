# BENCHMARK — Lab #17: Multi-Memory Agent

**Setup:** 10 multi-turn conversations, mỗi conversation ≥ 3 turns.  
**So sánh:** No-memory (stateless LLM) vs With-memory (full memory stack).  
**Token ước lượng:** tiktoken (`cl100k_base`); fallback word count × 1.3 nếu không cài tiktoken

---

## Summary Table

| # | Scenario | Group | No-memory | With-memory | Pass? |
|---|----------|-------|-----------|-------------|-------|
| 1 | Recall tên sau 6 turns | Profile recall | Không biết | Khang | ✅ |
| 2 | Recall nghề nghiệp | Profile recall | Không biết | Lập trình viên backend | ✅ |
| 3 | Conflict: dị ứng update | Conflict update | Sữa bò | Đậu nành | ✅ |
| 4 | Conflict: thành phố update | Conflict update | Hà Nội | TP.HCM | ✅ |
| 5 | Recall bài debug Docker | Episodic recall | Không biết | Dùng service name | ✅ |
| 6 | Recall task deploy | Episodic recall | Không biết | GitHub Actions thành công | ✅ |
| 7 | Tìm FAQ về Redis | Semantic retrieval | Chung chung | Redis cần flush khi test | ✅ |
| 8 | Tìm kiến thức Docker networking | Semantic retrieval | Chung chung | Dùng service name thay localhost | ✅ |
| 9 | Trim khi history dài | Trim/token budget | Không kiểm soát | Sliding window max_turns=10 | ✅ |
| 10 | Budget limit system prompt | Trim/token budget | Không kiểm soát | Cắt tại 2000 chars | ✅ |

---

## Conversation 1 — Profile Recall: Tên sau 6 turns

**Group:** Profile recall

| Turn | User | No-memory AI | With-memory AI |
|------|------|-------------|----------------|
| 1 | Tôi tên là Khang | Xin chào Khang! | Xin chào Khang! Đã lưu tên. |
| 2 | Tôi đang học AI | Thú vị! | Hay đấy Khang, AI rất rộng. |
| 3 | Hôm nay tôi mệt | Bạn nên nghỉ ngơi. | Khang nên nghỉ ngơi nhé. |
| 4 | Cho tôi gợi ý học | Bạn có thể học... | Khang đang học AI, gợi ý: LangChain... |
| 5 | Tôi thích Python | OK! | Khang thích Python — phù hợp với AI. |
| 6 | Bạn nhớ tên tôi không? | **Không, tôi không lưu tên.** | **Tên bạn là Khang.** |

**Result:** No-memory ❌ — With-memory ✅  
**Token ước lượng:** ~180 words × 1.3 ≈ 234 tokens

---

## Conversation 2 — Profile Recall: Nghề nghiệp

**Group:** Profile recall

| Turn | User | No-memory AI | With-memory AI |
|------|------|-------------|----------------|
| 1 | Tôi là lập trình viên backend | Thú vị! | Đã lưu: nghề = lập trình viên backend. |
| 2 | Tôi hay dùng Python và FastAPI | OK! | Noted: Python + FastAPI. |
| 3 | Gợi ý tool monitoring cho tôi | Prometheus, Grafana... | Với backend Python/FastAPI: Prometheus + Grafana. |
| 4 | Bạn biết nghề tôi là gì không? | **Tôi không biết.** | **Bạn là lập trình viên backend.** |

**Result:** No-memory ❌ — With-memory ✅  
**Token ước lượng:** ~120 words × 1.3 ≈ 156 tokens

---

## Conversation 3 — Conflict Update: Dị ứng

**Group:** Conflict update

| Turn | User | No-memory AI | With-memory AI |
|------|------|-------------|----------------|
| 1 | Tôi dị ứng sữa bò | Tránh sữa bò nhé. | Đã lưu: allergy = sữa bò. |
| 2 | Gợi ý bữa sáng cho tôi | Bánh mì, trứng... | Tránh sữa bò: bánh mì, trứng, yến mạch nước. |
| 3 | À nhầm, tôi dị ứng đậu nành chứ không phải sữa bò | OK! | Đã cập nhật: allergy = đậu nành (ghi đè sữa bò). |
| 4 | Tôi dị ứng gì vậy? | **Tôi không biết.** | **Bạn dị ứng đậu nành.** |

**Profile sau:** `allergy = đậu nành` ✅ (không còn sữa bò)  
**Result:** No-memory ❌ — With-memory ✅  
**Token ước lượng:** ~130 words × 1.3 ≈ 169 tokens

---

## Conversation 4 — Conflict Update: Thành phố

**Group:** Conflict update

| Turn | User | No-memory AI | With-memory AI |
|------|------|-------------|----------------|
| 1 | Tôi sống ở Hà Nội | Hà Nội đẹp! | Đã lưu: city = Hà Nội. |
| 2 | Gợi ý quán cà phê | Cộng, Giảng... | Ở Hà Nội: Cộng Cà Phê, Giảng. |
| 3 | Tôi vừa chuyển vào TP.HCM rồi | OK! | Đã cập nhật: city = TP.HCM. |
| 4 | Bạn biết tôi ở đâu không? | **Không biết.** | **Bạn ở TP.HCM.** |

**Profile sau:** `city = TP.HCM` ✅  
**Result:** No-memory ❌ — With-memory ✅  
**Token ước lượng:** ~120 words × 1.3 ≈ 156 tokens

---

## Conversation 5 — Episodic Recall: Debug Docker

**Group:** Episodic recall

| Turn | User | No-memory AI | With-memory AI |
|------|------|-------------|----------------|
| 1 | Tôi đang bị lỗi connect DB trong Docker | Kiểm tra connection string... | Bạn dùng `localhost` hay service name? |
| 2 | Tôi dùng localhost | Thử 127.0.0.1 | Trong Docker, dùng service name thay `localhost`. |
| 3 | Đổi sang service name là xong rồi! | Tốt! | Đã lưu episode: debug Docker → dùng service name. |
| 4 | (session mới) Hôm trước tôi fix Docker bằng cách nào? | **Không biết.** | **Bạn đã dùng Docker service name thay localhost.** |

**Result:** No-memory ❌ — With-memory ✅  
**Token ước lượng:** ~150 words × 1.3 ≈ 195 tokens

---

## Conversation 6 — Episodic Recall: Deploy

**Group:** Episodic recall

| Turn | User | No-memory AI | With-memory AI |
|------|------|-------------|----------------|
| 1 | Tôi cần deploy app lên server | Dùng rsync hoặc CI/CD... | Bạn muốn deploy thủ công hay CI/CD? |
| 2 | Dùng GitHub Actions | Tạo workflow .yml... | Tạo `.github/workflows/deploy.yml`... |
| 3 | Deploy thành công rồi, cảm ơn! | Tốt! | Đã lưu: deploy GitHub Actions → thành công. |
| 4 | (session mới) Tôi đã deploy bằng gì? | **Không biết.** | **Bạn đã deploy thành công bằng GitHub Actions.** |

**Result:** No-memory ❌ — With-memory ✅  
**Token ước lượng:** ~140 words × 1.3 ≈ 182 tokens

---

## Conversation 7 — Semantic Retrieval: Redis FAQ

**Group:** Semantic retrieval

| Turn | User | No-memory AI | With-memory AI |
|------|------|-------------|----------------|
| 1 | (pre-load) FAQ: "Redis cần flush khi test để tránh data cũ" | — | Đã lưu vào semantic store. |
| 2 | Test Redis hay bị fail do data cũ, tại sao? | Có thể do cache... | **Redis cần flush khi test để tránh data cũ.** |
| 3 | Cách flush? | `FLUSHALL` hoặc `FLUSHDB` | Dùng `FLUSHDB` trước mỗi test suite. |

**Result:** No-memory ❌ — With-memory ✅  
**Token ước lượng:** ~110 words × 1.3 ≈ 143 tokens

---

## Conversation 8 — Semantic Retrieval: Docker Networking

**Group:** Semantic retrieval

| Turn | User | No-memory AI | With-memory AI |
|------|------|-------------|----------------|
| 1 | (pre-load) FAQ: "Trong Docker Compose, dùng service name thay localhost" | — | Đã lưu vào semantic store. |
| 2 | Tại sao container không connect được nhau? | Kiểm tra network... | **Trong Docker Compose, dùng service name thay localhost.** |
| 3 | Ví dụ cụ thể? | `host.docker.internal`... | `db:5432` thay vì `localhost:5432`. |

**Result:** No-memory ❌ — With-memory ✅  
**Token ước lượng:** ~100 words × 1.3 ≈ 130 tokens

---

## Conversation 9 — Trim/Token Budget: History dài

**Group:** Trim/token budget

| Turn | User | No-memory AI | With-memory AI |
|------|------|-------------|----------------|
| 1–10 | (10 turns liên tiếp) | Trả lời bình thường | Trả lời bình thường |
| 11 | Thêm 1 turn nữa | **Context tăng không kiểm soát** | **Trim còn 10 turns gần nhất** |
| 12 | Bạn nhớ turn 1 không? | Có thể nhớ (context đầy) | Không nhớ turn 1 (đã trim) — đúng hành vi |

**Result:** No-memory ❌ — With-memory ✅ (`ShortTermMemory(max_turns=10)`)  
**Token ước lượng:** 10 turns × ~20 words × 1.3 ≈ 260 tokens

---

## Conversation 10 — Trim/Token Budget: System prompt budget

**Group:** Trim/token budget

| Turn | User | No-memory AI | With-memory AI |
|------|------|-------------|----------------|
| 1 | (profile 20 facts + 10 episodes + 5 semantic hits) | — | — |
| 2 | Hỏi bất kỳ | Prompt không có memory | System prompt inject đầy đủ |
| 3 | Kiểm tra độ dài prompt | Không kiểm soát | System prompt trim đến ≤ 500 tokens ✅ |

**Result:** No-memory ❌ — With-memory ✅ (token-budget loop `count_tokens(system) <= 500`)  
**Token ước lượng:** budget 500 tokens (system) + ~100 tokens (user) ≈ 600 tokens/turn

---

## Notes

- Token counting: tiktoken (`cl100k_base`); fallback word count × 1.3 nếu không cài tiktoken.
- Conflict handling: `long_term.save(key, value)` ghi đè — không append.
- Sliding window: `ShortTermMemory(max_turns=10)` giữ 10 turns = 20 messages.
- Budget: token-budget loop `count_tokens(system) <= MEMORY_BUDGET` (500 tokens).
- Semantic test: data được auto-ingest từ assistant reply sau mỗi turn; không cần pre-load tay.
