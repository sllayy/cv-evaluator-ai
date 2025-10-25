from utils.file_reader import read_cv
from utils.scoring import load_requirements, calculate_score, generate_comment
import os
import json
import random
import re
import fitz

# PDF’ten LinkedIn çıkar
def extract_linkedin_from_pdf(file_path):
    try:
        with fitz.open(file_path) as doc:
            for page in doc:
                text = page.get_text()
                linkedin_match = re.search(r'https?://(www\.)?linkedin\.com/[^\s)]+', text)
                if linkedin_match:
                    return linkedin_match.group(0).strip()
                links = page.get_links()
                for link in links:
                    if "uri" in link and "linkedin.com" in link["uri"]:
                        return link["uri"]
    except:
        pass
    return ""

# Kısa yorum üret
def generate_short_comment(score_detail):
    eksikler = []

    if score_detail.get("Deneyim", 0) < 10:
        eksikler.append("deneyim")
    if score_detail.get("Dil", 0) < 5:
        eksikler.append("yabancı dil")
    if score_detail.get("Sertifikalar", 0) < 5:
        eksikler.append("sertifikalar")
    if score_detail.get("LinkedIn", 0) < 2.5:
        eksikler.append("LinkedIn profili")
    if score_detail.get("Proje", 0) < 2.5:
        eksikler.append("proje tecrübesi")

    random.shuffle(eksikler)
    templates = {
        1: [
            "Adayın {eksik} konusunda eksikleri var gibi görünüyor.",
            "{eksik} yönü geliştirilirse aday çok daha uygun olabilir.",
        ],
        2: [
            "{eksik1} ve {eksik2} eksikliği dikkat çekiyor.",
            "Adayın {eksik1} ve {eksik2} açısından geliştirmesi gerekiyor.",
        ],
        3: [
            "{eksik1}, {eksik2} ve {eksik3} alanlarında yetersizlik gözlemleniyor.",
        ],
        "tam": [
            "Tüm kriterlerde yüksek uyum gösteriyor, güçlü bir aday.",
            "Kriterlerin tamamını karşılayan etkileyici bir profil.",
        ]
    }

    eksik_sayisi = len(eksikler)
    if eksik_sayisi == 0:
        return random.choice(templates["tam"])
    elif eksik_sayisi == 1:
        return random.choice(templates[1]).format(eksik=eksikler[0])
    elif eksik_sayisi == 2:
        return random.choice(templates[2]).format(eksik1=eksikler[0], eksik2=eksikler[1])
    else:
        return random.choice(templates[3]).format(
            eksik1=eksikler[0], eksik2=eksikler[1], eksik3=eksikler[2]
        )

# Etiket
def label_for_score(score):
    return "Uygundur" if score >= 65 else "Uygun değildir"

# Ekstra bilgi çek
def extract_additional_info(text, file_path=None):
    linkedin = ""
    diller = [] #no need for now
    beceriler = []
    egitim = ""

    if file_path and file_path.lower().endswith(".pdf"):
        linkedin = extract_linkedin_from_pdf(file_path)

    if not linkedin:
        linkedin_match = re.search(r'https?://(www\.)?linkedin\.com/[^\s)]+', text)
        if linkedin_match:
            linkedin = linkedin_match.group(0).strip()

    teknik_kelimeler = ["Python", "Java", "C#", "Flutter", "React", "Django", "PostgreSQL", "TensorFlow", "Keras"]
    for kelime in teknik_kelimeler:
        if kelime.lower() in text.lower():
            beceriler.append(kelime)

        # Eğitim bilgisi (Üniversite adı)
    egitim = ""
    uni_matches = re.findall(r'([A-ZÇĞİÖŞÜa-zçğıöşü\s&]{2,40}(?:Üniversitesi|University))', text, flags=re.IGNORECASE)
    if uni_matches:
        egitim = uni_matches[0].strip().title()
    return {
        "linkedin": linkedin,
        #"Diller": ""
        "beceriler": ", ".join(beceriler),
        "egitim": egitim
    }



# ----------------------------- ANALİZ -----------------------------
cv_folder = "inputs/cvs"
output_path = "outputs/scored_results.json"
results = []

requirements = load_requirements()

for filename in os.listdir(cv_folder):
    file_path = os.path.join(cv_folder, filename)
    print(f"\n--- {filename} ---")
    text = read_cv(file_path)
    score, score_detail = calculate_score(text, requirements)
    kisa_yorum = generate_short_comment(score_detail)
    uygunluk = label_for_score(score)
    extra_info = extract_additional_info(text, file_path)

    print(f"✅ {filename} skoru: {score}")
    print("💬 Yorum:", kisa_yorum)

    results.append({
        "filename": filename,
        "score": score,
        "Uygunluk Durumu": uygunluk,
        "Kısa Yorum": kisa_yorum,
        "Linkedin": extra_info["linkedin"],
        #"Diller": extra_info["diller"],
        "Beceriler": extra_info["beceriler"],
        "Eğitim": extra_info["egitim"]
    })

sorted_results = sorted(results, key=lambda x: x["score"], reverse=True)
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(sorted_results, f, indent=4, ensure_ascii=False)

print(f"\n📁 Tüm sonuçlar şuraya kaydedildi: {output_path}")
