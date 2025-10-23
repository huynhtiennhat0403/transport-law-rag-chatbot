import re
import json

def parse_law_document(text):
    """
    Parse văn bản luật giao thông thành cấu trúc phân cấp
    
    Returns:
        list: Danh sách các chương, mỗi chương chứa các điều, khoản, điểm
    """
    lines = text.strip().split('\n')
    
    structure = []
    current_chapter = None
    current_article = None
    current_clause = None
    current_point = None
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip empty lines
        if not line:
            i += 1
            continue
        
        # Pattern: Chương [số La Mã] [TIÊU ĐỀ IN HOA]
        chapter_match = re.match(r'^Chương\s+([IVXLCDM]+)\s+(.+)$', line)
        if chapter_match:
            current_chapter = {
                'type': 'chapter',
                'number': chapter_match.group(1),
                'title': chapter_match.group(2).strip(),
                'articles': []
            }
            structure.append(current_chapter)
            current_article = None
            current_clause = None
            i += 1
            continue
        
        # Pattern: Điều [số]. [Tiêu đề]
        article_match = re.match(r'^Điều\s+(\d+[a-z]?)\.\s+(.+)$', line)
        if article_match:
            current_article = {
                'type': 'article',
                'number': article_match.group(1),
                'title': article_match.group(2).strip(),
                'content': '',
                'clauses': []
            }
            if current_chapter:
                current_chapter['articles'].append(current_article)
            current_clause = None
            i += 1
            continue
        
        # Pattern: [số]. [Nội dung] (khoản)
        clause_match = re.match(r'^(\d+)\.\s+(.+)$', line)
        if clause_match and current_article:
            clause_num = clause_match.group(1)
            clause_content = clause_match.group(2).strip()
            
            current_clause = {
                'type': 'clause',
                'number': clause_num,
                'content': clause_content,
                'points': []
            }
            current_article['clauses'].append(current_clause)
            i += 1
            continue
        
        # Pattern: [chữ]. [Nội dung] (điểm)
        point_match = re.match(r'^([a-zđ])\.\s+(.+)$', line)
        if point_match and current_clause:
            point_letter = point_match.group(1)
            point_content = point_match.group(2).strip()
            
            current_point = {
                'type': 'point',
                'letter': point_letter,
                'content': point_content
            }
            current_clause['points'].append(current_point)
            i += 1
            continue
        
        # Nội dung thuộc về Điều (không có khoản con)
        if current_article and not current_clause:
            if current_article['content']:
                current_article['content'] += ' ' + line
            else:
                current_article['content'] = line
        # Nội dung tiếp theo của khoản
        elif current_clause and not point_match:
            current_clause['content'] += ' ' + line
        # Nội dung tiếp theo của điểm
        elif current_point:
            current_point['content'] += ' ' + line
        
        i += 1
    
    return structure

def flatten_to_chunks(structure):
    """
    Chuyển cấu trúc phân cấp thành list của chunks với metadata đầy đủ
    
    Returns:
        list: Danh sách các chunk, mỗi chunk có content và metadata
    """
    chunks = []
    
    for chapter in structure:
        chapter_num = chapter['number']
        chapter_title = chapter['title']
        
        for article in chapter['articles']:
            article_num = article['number']
            article_title = article['title']
            
            # Nếu Điều có nội dung trực tiếp (không có khoản)
            if article['content'] and not article['clauses']:
                chunks.append({
                    'content': article['content'],
                    'metadata': {
                        'chapter_number': chapter_num,
                        'chapter_title': chapter_title,
                        'article_number': article_num,
                        'article_title': article_title,
                        'full_reference': f"Chương {chapter_num}, Điều {article_num}"
                    }
                })
            
            # Nếu Điều có các khoản
            for clause in article['clauses']:
                clause_num = clause['number']
                
                # Nếu khoản không có điểm con
                if not clause['points']:
                    chunks.append({
                        'content': clause['content'],
                        'metadata': {
                            'chapter_number': chapter_num,
                            'chapter_title': chapter_title,
                            'article_number': article_num,
                            'article_title': article_title,
                            'clause_number': clause_num,
                            'full_reference': f"Chương {chapter_num}, Điều {article_num}, Khoản {clause_num}"
                        }
                    })
                else:
                    # Nếu khoản có các điểm con
                    # Option 1: Mỗi điểm là 1 chunk riêng
                    for point in clause['points']:
                        chunks.append({
                            'content': point['content'],
                            'metadata': {
                                'chapter_number': chapter_num,
                                'chapter_title': chapter_title,
                                'article_number': article_num,
                                'article_title': article_title,
                                'clause_number': clause_num,
                                'point_letter': point['letter'],
                                'full_reference': f"Chương {chapter_num}, Điều {article_num}, Khoản {clause_num}, Điểm {point['letter']}"
                            }
                        })
    
    return chunks

def save_structure_to_json(structure, output_file='../data/processed/law_structure.json'):
    """Lưu cấu trúc ra file JSON"""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(structure, f, ensure_ascii=False, indent=2)
    print(f"✓ Đã lưu cấu trúc vào {output_file}")


def save_chunks_to_json(chunks, output_file='../data/processed/law_chunks.json'):
    """Lưu chunks ra file JSON"""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)
    print(f"✓ Đã lưu {len(chunks)} chunks vào {output_file}")

# ===== MAIN EXECUTION =====
if __name__ == "__main__":
    # Đọc file văn bản
    with open('../data/raw/raw_text.txt', 'r', encoding='utf-8') as f:
        text = f.read()
    
    print("🔍 Bắt đầu parse văn bản luật...")
    
    # Parse thành cấu trúc
    structure = parse_law_document(text)
    
    # Hiển thị thống kê
    total_articles = sum(len(ch['articles']) for ch in structure)
    print(f"\n📊 Thống kê:")
    print(f"  - Số chương: {len(structure)}")
    print(f"  - Số điều: {total_articles}")
    
    # Lưu cấu trúc phân cấp
    save_structure_to_json(structure)
    
    # Chuyển thành chunks
    chunks = flatten_to_chunks(structure)
    save_chunks_to_json(chunks)
    
    # Hiển thị ví dụ
    print(f"\n📝 Ví dụ chunk đầu tiên:")
    print(json.dumps(chunks[0], ensure_ascii=False, indent=2))
    
    print(f"\n✅ Hoàn thành!")
