import re
import json
import os

BASE_DIR = r"d:\works\Almedicus\histology-exam\js"
OUT_FILE = r"d:\works\Almedicus\histology-bot\bot_data.json"

def clean_html(text):
    if not text:
        return ""
    t = text.replace("<br>", "\n").replace("<br/>", "\n").replace("<br />", "\n")
    t = re.sub(r'</?(?:p|div|h[1-6]|ul|ol|li)[^>]*>', '\n', t)
    def keep_tg(m):
        tag = m.group(1).lower()
        full = m.group(0)
        if tag in ('b', 'strong', 'i', 'em', 'code', 'pre', 'u', 's', 'strike'):
            return full
        return ''
    t = re.sub(r'<(/?)(\w+)[^>]*>', keep_tg, t)
    t = t.replace('<strong>', '<b>').replace('</strong>', '</b>')
    t = t.replace('<em>', '<i>').replace('</em>', '</i>')
    lines = [line.strip() for line in t.split('\n')]
    lines = [l for l in lines if l]
    return '\n'.join(lines)

def parse_objects(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    objects = []
    i = 0
    n = len(content)
    while i < n:
        start = content.find('{', i)
        if start == -1:
            break
        header = content[start:start+40]
        if not re.search(r'\{\s*id\s*:', header):
            i = start + 1
            continue

        depth = 0
        in_str = False
        str_char = None
        j = start
        while j < n:
            c = content[j]
            if in_str:
                if c == '\\':
                    j += 2
                    continue
                elif c == str_char:
                    in_str = False
            else:
                if c in ('"', "'", '`'):
                    in_str = True
                    str_char = c
                elif c == '{':
                    depth += 1
                elif c == '}':
                    depth -= 1
                    if depth == 0:
                        obj_str = content[start:j+1]
                        objects.append(obj_str)
                        i = j + 1
                        break
            j += 1
        else:
            break
    return objects

def extract_field(obj_str, field_name):
    pattern = r'\b' + field_name + r'\s*:\s*(`[\s\S]*?`|"[\s\S]*?"|\'[\s\S]*?\'|\[[\s\S]*?\]|\d+)'
    m = re.search(pattern, obj_str)
    if not m:
        return None
    val = m.group(1).strip()
    if val.startswith('`') and val.endswith('`'):
        return val[1:-1].strip()
    elif val.startswith('"') and val.endswith('"'):
        return val[1:-1].strip()
    elif val.startswith("'") and val.endswith("'"):
        return val[1:-1].strip()
    elif val.isdigit():
        return int(val)
    elif val.startswith('[') and val.endswith(']'):
        items = re.findall(r'["\'](.*?)["\']', val)
        return items
    return val

print("1. Parsing questions...")
questions = []
for p in range(1, 5):
    fname = os.path.join(BASE_DIR, f"data_questions_part{p}.js")
    for obj_str in parse_objects(fname):
        qid = extract_field(obj_str, "id")
        q = {
            "id": qid,
            "category": extract_field(obj_str, "category") or "",
            "question": extract_field(obj_str, "question") or "",
            "question_uz": extract_field(obj_str, "question_uz") or "",
            "keywords": extract_field(obj_str, "keywords") or "",
            "answer_clean": clean_html(extract_field(obj_str, "answer") or "")
        }
        questions.append(q)
print(f"Total Questions: {len(questions)}")

print("2. Parsing cases...")
cases = []
for p in range(1, 4):
    fname = os.path.join(BASE_DIR, f"data_cases_part{p}.js")
    for obj_str in parse_objects(fname):
        cid = extract_field(obj_str, "id")
        sub_q = extract_field(obj_str, "sub_questions") or []
        c = {
            "id": cid,
            "title": extract_field(obj_str, "title") or "",
            "title_uz": extract_field(obj_str, "title_uz") or "",
            "case_text": extract_field(obj_str, "case_text") or "",
            "case_text_uz": extract_field(obj_str, "case_text_uz") or "",
            "sub_questions": sub_q,
            "solution_clean": clean_html(extract_field(obj_str, "solution") or "")
        }
        cases.append(c)
print(f"Total Cases: {len(cases)}")

print("3. Parsing preparations and atlas data...")
# Read atlas data
atlas_data = {}
with open(os.path.join(BASE_DIR, "data_atlas_info.js"), 'r', encoding='utf-8') as f:
    atlas_raw = f.read()

# match atlas blocks: \s*(\d+):\s*\{([^}]+)\}
for m in re.finditer(r'(\d+)\s*:\s*\{([^}]+)\}', atlas_raw):
    pid = int(m.group(1))
    block = m.group(2)
    def get_at_f(k):
        fm = re.search(r'\b' + k + r'\s*:\s*["\'](.*?)["\']', block)
        return fm.group(1) if fm else ""
    atlas_data[pid] = {
        "fig": get_at_f("fig"),
        "stain": get_at_f("stain"),
        "pointers": get_at_f("pointers"),
        "desc": get_at_f("desc")
    }

preparations = []
for p in range(1, 3):
    fname = os.path.join(BASE_DIR, f"data_prep_part{p}.js")
    for obj_str in parse_objects(fname):
        pid = extract_field(obj_str, "id")
        at = atlas_data.get(pid, {})
        prep = {
            "id": pid,
            "name": extract_field(obj_str, "name") or "",
            "name_lat": extract_field(obj_str, "name_lat") or "",
            "staining": at.get("stain") or extract_field(obj_str, "staining") or "",
            "diagnostic_key": extract_field(obj_str, "diagnostic_key") or "",
            "layers": clean_html(extract_field(obj_str, "layers_and_structure") or ""),
            "exam_questions": clean_html(extract_field(obj_str, "exam_questions") or ""),
            "atlas_fig": at.get("fig", ""),
            "atlas_pointers": at.get("pointers", ""),
            "atlas_desc": at.get("desc", ""),
            "micro_image": f"images/slides/slide_{pid}.jpg",
            "atlas_image": f"images/atlas/atlas_{pid}.png"
        }
        preparations.append(prep)
print(f"Total Preparations: {len(preparations)}")

print("4. Parsing schemes...")
schemes = []
with open(os.path.join(BASE_DIR, "data_schemes.js"), 'r', encoding='utf-8') as f:
    s_raw = f.read()

start = s_raw.find('[')
end = s_raw.rfind(']')
raw_json = s_raw[start:end+1]
parsed_schemes = json.loads(raw_json)

for s in parsed_schemes:
    sid = s.get("id")
    schemes.append({
        "id": sid,
        "title": s.get("title", ""),
        "title_uz": s.get("title_uz", ""),
        "title_cyr": s.get("title_cyr", ""),
        "title_ru": s.get("title_ru", ""),
        "category": s.get("category", ""),
        "question": s.get("question", ""),
        "question_uz": s.get("question_uz", ""),
        "question_cyr": s.get("question_cyr", ""),
        "question_ru": s.get("question_ru", ""),
        "answer_clean": clean_html(s.get("answer_uz") or s.get("answer_cyr") or s.get("answer_ru") or ""),
        "answer_uz_clean": clean_html(s.get("answer_uz", "")),
        "answer_cyr_clean": clean_html(s.get("answer_cyr", "")),
        "answer_ru_clean": clean_html(s.get("answer_ru", "")),
        "image": s.get("image", f"images/schemes/image{sid}.png")
    })
print(f"Total Schemes: {len(schemes)}")

data = {
    "questions": questions,
    "cases": cases,
    "preparations": preparations,
    "schemes": schemes
}

with open(OUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"SUCCESS: {len(questions)} savol, {len(cases)} masala, {len(preparations)} preparat, {len(schemes)} sxema bot_data.json ga yozildi!")
