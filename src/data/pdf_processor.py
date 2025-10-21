import pdfplumber
import re

class PDFProcessor:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.raw_text = ""
        
    def extract_text(self) -> str:
        """Trích xuất toàn bộ văn bản từ PDF"""
        print("🔄 Đang trích xuất văn bản từ PDF...")
        
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text()
                    if text:
                        self.raw_text += f"\n--- Trang {page_num} ---\n{text}"
                        print(f"✅ Đã xử lý trang {page_num}")
            
            print(f"✅ Hoàn thành! Tổng số ký tự: {len(self.raw_text)}")
            return self.raw_text
            
        except Exception as e:
            print(f"❌ Lỗi khi trích xuất PDF: {e}")
            return ""
    
    def clean_text(self) -> str:
        """Làm sạch văn bản"""
        print("🔄 Đang làm sạch văn bản...")
        
        cleaned = self.raw_text
        
        # Xóa các phần header/footer và số trang
        patterns_to_remove = [
            r'--- Page \d+ ---',  # --- Page 12 ---
            r'CÔNG BÁO/Số \d+ \+ \d+/Ngày \d+-\d+-\d+ \d+',  # CÔNG BÁO/Số 1215 + 1216/Ngày 27-11-2023 69
            r'CÔNG BÁO/Số \d+ \+ \d+/Ngày \d+-\d+-\d+',  # CÔNG BÁO/Số 1215 + 1216/Ngày 27-11-2023
            r'\d+ CÔNG BÁO/Số \d+ \+ \d+/Ngày \d+-\d+-\d+',  # 58 CÔNG BÁO/Số 1215 + 1216/Ngày 27-11-2023
            r'--- Trang \d+ ---',  # --- Trang 1 ---
        ]
        
        for pattern in patterns_to_remove:
            cleaned = re.sub(pattern, '', cleaned)
        
        # Xóa các số đứng riêng lẻ (thường là số trang)
        cleaned = re.sub(r'^\d+$', '', cleaned, flags=re.MULTILINE)
        
        # Xóa các dòng chỉ chứa khoảng trắng và số
        cleaned = re.sub(r'^\s*\d+\s*$', '', cleaned, flags=re.MULTILINE)
        
        # Chuẩn hóa khoảng trắng
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        # Xóa khoảng trắng thừa ở đầu và cuối
        cleaned = cleaned.strip()
        
        print("✅ Đã làm sạch văn bản")
        return cleaned

    def smart_merge(self):
        # Gộp các dòng chưa kết thúc câu
        self.raw_text = re.sub(r'(\w+)\n(\w+)', r'\1 \2', self.raw_text)
        
        # Giữ nguyên các đoạn được đánh số a, b, c...
        self.raw_text = re.sub(r'([a-z]\.)\s*\n', r'\1 ', self.raw_text)
    
        return self.raw_text

    def save_raw_text(self, output_path: str = "raw_text.txt"):
        """Lưu văn bản thô ra file để kiểm tra"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(self.raw_text)
        print(f"💾 Đã lưu văn bản thô vào: {output_path}")

# Sử dụng
if __name__ == "__main__":
    processor = PDFProcessor("data/raw/2008 Transport Law.pdf")
    raw_text = processor.extract_text()
    raw_text = processor.clean_text()
    processor.smart_merge()
    processor.save_raw_text("data/raw/pdf_raw_text.txt")