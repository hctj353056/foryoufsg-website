import json
import re
import os

def clean_date(date_str):
    """清理日期字符串，提取年月日部分"""
    date_str = date_str.strip()
    
    match = re.match(r'(\d{4})[年.](\d{1,2})[月.](\d{1,2})', date_str)
    if match:
        year = match.group(1).zfill(4)
        month = match.group(2).zfill(2)
        day = match.group(3).zfill(2)
        return f"{year}{month}{day}"
    
    return ""

def parse_txt_to_json(txt_path, json_path):
    """解析 txt 文件并生成 JSON"""
    with open(txt_path, 'r', encoding='utf-8') as f:
        content = f.read()
      
    entries = []
    blocks = re.split(r'\n\n+', content.strip())
    
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        
        match = re.match(r'《(.+?)》\s*时间[：:]\s*(.+?)\n', block)
        if match:
            title = match.group(1)
            date = match.group(2).strip()
            content_text = block[match.end():].strip()
            
            clean_date_str = clean_date(date)
            image_name = f"{title}{clean_date_str}.jpg"
            
            entry = {
                "title": title,
                "date": date,
                "content": content_text,
                "image": f"images/{image_name}"
            }
            
            entries.append(entry)
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)
        
    print(f"转换完成：{len(entries)} 条 → {json_path}")

BASE = os.path.dirname(os.path.abspath(__file__))
parse_txt_to_json(
    os.path.join(BASE, "poetry", "原创古诗词.txt"),
    os.path.join(BASE, "poetry", "诗词.json")
)
parse_txt_to_json(
    os.path.join(BASE, "articles", "原创散文.txt"),
    os.path.join(BASE, "articles", "散文.json")
)