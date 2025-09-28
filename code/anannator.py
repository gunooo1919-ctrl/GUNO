# code/annotator.py
import re
import json
from html import escape

# Pemetaan frasa ke konsep finansial (atur sendiri)
PHRASE_RULES = {
    r"sedikit demi sedikit": {
        "concept": "menabung bertahap",
        "explain": "Menabung sedikit tiap periode akan menumpuk jadi jumlah besar.",
        "example_template": "Jika menabung {unit} per minggu selama {periods} minggu, total = {unit} × {periods} = {total}."
    },
    r"cadangan": {
        "concept": "cadangan/pemulihan risiko",
        "explain": "Cadangan digunakan saat terjadi kekurangan (paceklik, kerusakan).",
        "example_template": "Contoh: simpan minimal 10% dari hasil sebagai cadangan."
    },
}

# Regex untuk angka (contoh: 5.000 atau 5000)
NUMBER_RE = re.compile(r"(\d{1,3}(?:[.,]\d{3})*|\d+)(?:\s*(rupiah|Rp|IDR)?)?", flags=re.IGNORECASE)

def parse_number_str(s):
    """Convert extracted number string to int (assume rupiah-like format)."""
    s = s.replace(".", "").replace(",", "")
    try:
        return int(s)
    except:
        try:
            return int(float(s))
        except:
            return None

def extract_annotations(text):
    """
    Scan text and return a list of annotations:
    [{'start':i,'end':j,'span':text,'type':'number'/'phrase','meta':{...}}]
    """
    annotations = []
    # numbers
    for m in NUMBER_RE.finditer(text):
        num = parse_number_str(m.group(1))
        if num is not None:
            annotations.append({
                "start": m.start(),
                "end": m.end(),
                "span": m.group(0),
                "type": "number",
                "meta": {"value": num}
            })
    # phrases
    for pattern, info in PHRASE_RULES.items():
        for m in re.finditer(pattern, text, flags=re.IGNORECASE):
            annotations.append({
                "start": m.start(),
                "end": m.end(),
                "span": m.group(0),
                "type": "phrase",
                "meta": {
                    "concept": info["concept"],
                    "explain": info["explain"],
                    "example_template": info["example_template"]
                }
            })
    # sort by start index
    annotations = sorted(annotations, key=lambda x: x["start"])
    return annotations

def annotate_text_to_html(text, annotations, link_to_simulator="#"):
    """
    Produce HTML string where annotated spans are wrapped with <span class='annot' title='...'>
    and clickable link to simulator is provided for number annotations with example.
    """
    out = []
    last = 0
    for ann in annotations:
        out.append(escape(text[last:ann['start']]))
        span = escape(ann['span'])
        if ann['type'] == 'number':
            meta = ann['meta']
            title = f"Nilai: {meta['value']}"
            # create link to simulator with parameters (you can encode details)
            html = f"<span class='annot number' title='{escape(title)}' data-val='{meta['value']}' style='background:#fffbcc;border-bottom:1px dashed #d4a017;cursor:pointer'>{span}</span>"
        else:  # phrase
            meta = ann['meta']
            title = f"{meta['concept']}: {meta['explain']}"
            # example: provide template but not computed
            html = f"<span class='annot phrase' title='{escape(title)}' style='background:#d2f0d2;border-bottom:1px dashed #2f9a2f;cursor:help'>{span}</span>"
        out.append(html)
        last = ann['end']
    out.append(escape(text[last:]))
    # add small JS to allow click on number spans to open simulator (if you later host a simulator)
    js = f"""
    <script>
      document.querySelectorAll('.annot.number').forEach(function(el){{
         el.addEventListener('click', function(){{
            var v = el.getAttribute('data-val');
            var url = "{link_to_simulator}" + "?value=" + encodeURIComponent(v);
            window.open(url, '_blank');
         }});
      }});
    </script>
    """
    style = """
    <style>
      .annot {{ padding:2px 4px; border-radius:3px; }}
      .annot.phrase:hover {{ box-shadow: 0 0 5px rgba(0,0,0,0.2); }}
      .annot.number:hover {{ box-shadow: 0 0 5px rgba(0,0,0,0.2); }}
    </style>
    """
    return "<div class='annotated-text'>"+ "".join(out) + "</div>" + style + js

def save_annotations_json(annotations, out_path):
    with open(out_path, "w", encoding="utf8") as f:
        json.dump(annotations, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    # quick test
    txt = open("../assets/manuscripts/NL001_sedikit.txt","r",encoding="utf8").read()
    anns = extract_annotations(txt)
    print(anns)
    html = annotate_text_to_html(txt, anns)
    with open("../data/sample_annotations.html","w",encoding="utf8") as f:
        f.write(html)
