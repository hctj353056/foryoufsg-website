import json
import re
import os

def parse_txt_to_json(txt_path, json_path):
    """解析 txt 文件并生成 JSON"""
    with open(txt_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 分割每首诗/散文
    entries = []
    blocks = re.split(r'\n\n+', content.strip())
    
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        
        # 提取标题和时间
        match = re.match(r'《(.+?)》\s*时间[：:]\s*(.+?)\n', block)
        if match:
            title = match.group(1)
            date = match.group(2).strip()
            
            # 提取内容（去除标题行）
            content_text = block[match.end():].strip()
            
            entries.append({
                "title": title,
                "date": date,
                "content": content_text
            })
    
    # 写入 JSON
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)
    
    print(f"转换完成：{len(entries)} 条 → {json_path}")

# 执行
base = "knowledge-base/original-works"
#base = '/storage/emulated/0/用户自建/GitHub/foryoufsg-website/knowledge-base/original-works/'
parse_txt_to_json(
    f"{base}/poetry/原创古诗词.txt",
    f"{base}/poetry/诗词.json"
)
parse_txt_to_json(
    f"{base}/articles/原创散文.txt",
    f"{base}/articles/散文.json"
)