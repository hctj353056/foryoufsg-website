import json
import re
import os

def parse_txt_to_json(txt_path, json_path):
    """解析 txt 文件并生成 JSON"""
    existing_images = {}
    
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            try:
                existing_data = json.load(f)
                for item in existing_data:
                    if 'image' in item:
                        existing_images[item['title']] = item['image']
            except:
                pass
    
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
            
            entry = {
                "title": title,
                "date": date,
                "content": content_text
            }
            
            if title in existing_images:
                entry["image"] = existing_images[title]
            
            entries.append(entry)
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)
    
    print(f"转换完成：{len(entries)} 条 → {json_path}")

# 执行
BASE = os.path.dirname(os.path.abspath(__file__))
parse_txt_to_json(
    os.path.join(BASE, "poetry", "原创古诗词.txt"),
    os.path.join(BASE, "poetry", "诗词.json")
)
parse_txt_to_json(
    os.path.join(BASE, "articles", "原创散文.txt"),
    os.path.join(BASE, "articles", "散文.json")
)