# Dự án Chatbot RAG Luật Giao thông (Transport Law RAG Chatbot)

Dự án này nhằm xây dựng một chatbot sử dụng kiến trúc RAG (Retrieval-Augmented Generation) để trả lời các câu hỏi liên quan đến Luật Giao thông Đường bộ Việt Nam.

## 🚀 Tiến độ Dự án

**Ngày 1 (21/10/2025): Xử lý và Phân mảnh Dữ liệu (Data Processing & Chunking)**

Mục tiêu của ngày hôm nay là chuyển đổi file `.pdf` Luật Giao thông 2008 thô thành các file `.json` có cấu trúc, sẵn sàng cho việc embedding và nạp vào cơ sở dữ liệu vector (Vector Database).

---

## ⚙️ Luồng Xử lý Dữ liệu (Data Pipeline)

Quy trình xử lý dữ liệu được chia thành các bước, thực thi bởi các script trong `src/data/`.

### Bước 1: Trích xuất Văn bản từ PDF (Tùy chọn)

Script này đọc file PDF gốc và trích xuất toàn bộ nội dung văn bản ra một file `.txt` thô.

```bash
python src/data/pdf_processor.py
```

Kết quả: Tạo file `pdf_raw_text.txt` trong `data/raw/` từ file `2008_Transport_Law.pdf`.

### Bước 2: Xử lý Thủ công hoặc Sử dụng File Sẵn có

- Xử lý thủ công file `pdf_raw_text.txt` để tạo file `raw_text.txt` trong `data/raw/`.
- Hoặc sử dụng trực tiếp file `raw_text.txt` đã xử lý sẵn nếu muốn bỏ qua bước thủ công.

### Bước 3: Phân mảnh Dữ liệu (Chunking)

Chạy script sau để phân mảnh dữ liệu từ file `raw_text.txt` thành các đoạn có cấu trúc:

```bash
python src/data/law_parser.py
```

Kết quả: Tạo hai file `.json` trong `data/processed/`:
- `law_chunks.json`
- `law_structure.json`

---
