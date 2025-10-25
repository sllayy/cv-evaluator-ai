import json
import re

def load_requirements():
    with open("inputs/job_requirements.json", "r", encoding="utf-8") as f:
        return json.load(f)

def calculate_score(cv_text, requirements):
    score = 0
    cv_text_lower = cv_text.lower()
    cv_lines = cv_text_lower.splitlines()

    # Anahtar kelimeler
    education_keywords = ["lisans", "bachelor", "üniversite", "university", "degree"]
    experience_keywords = [r"(\d+)\s*yıl", r"(\d+)\s*years", r"experience\s*of\s*(\d+)"]
    level_keywords = [
        "başlangıç", "orta", "iyi", "ileri",
        "basic", "intermediate", "good", "strong",
        "advanced", "fluent", "proficient", "expert"
    ]

    # 1. Beceriler (30 puan + seviye bonusu)
    skills_required = requirements.get("aranan_beceriler", [])
    found_skills = []
    for skill in skills_required:
        for line in cv_lines:
            if skill.lower() in line:
                if any(level in line for level in level_keywords):
                    found_skills.append((skill, "yüksek"))
                else:
                    found_skills.append((skill, "normal"))
                break
    total_skill = len(skills_required)
    seviye_bonus = sum(1 for _, sev in found_skills if sev == "yüksek") * 2
    skill_score = min(len(found_skills) / total_skill, 1.0) * 30 + seviye_bonus if total_skill else 0
    skill_score = min(skill_score, 30)
    score += skill_score

    # 2. Sertifikalar (10 puan)
    certs_required = requirements.get("sertifikalar", [])
    found_certs = []
    for cert in certs_required:
        if cert and cert.strip():
            keyword = cert.lower().split()[0]
            for line in cv_lines:
                if keyword in line:
                    found_certs.append(cert)
                    break
    cert_score = min(len(found_certs) / len(certs_required), 1.0) * 10 if certs_required else 0
    score += cert_score

    # 3. Eğitim (10 puan) + kurum adı
    education_score = 0
    university_line = ""

    # Üniversite ismini daha iyi tespit eden desen
    uni_match = re.search(r'\b([A-ZÇĞİÖŞÜa-zçğıöşü\s&]+(?:Üniversitesi|University))\b', cv_text, flags=re.IGNORECASE)
    if uni_match:
        university_line = uni_match.group(0).strip().title()
        education_score = 10
    elif any(k in cv_text_lower for k in education_keywords):
        education_score = 10
    score += education_score

    # 4. Dil (10 puan)
    dil_bilgisi = requirements.get("dil", {})
    matched_langs = []
    for lang, required_level in dil_bilgisi.items():
        for line in cv_lines:
            if lang.lower() in line:
                if any(level in line for level in level_keywords):
                    matched_langs.append(lang)
                    break
    dil_score = min(len(matched_langs) * 5, 10)
    score += dil_score

    # 5. Proje & LinkedIn (5 + 5)
    ekstra = requirements.get("ekstra", {})
    proje_keywords = ["proje", "project"]
    linkedin_keywords = ["linkedin"]
    proje_score = 5 if ekstra.get("proje_tecrubesi") and any(k in cv_text_lower for k in proje_keywords) else 0
    linkedin_score = 5 if ekstra.get("linkedin") and any(k in cv_text_lower for k in linkedin_keywords) else 0
    score += proje_score + linkedin_score

    # 6. Deneyim (20 puan)
    min_yil = requirements.get("minimum_deneyim_yili", 0)
    years_found = []
    for pattern in experience_keywords:
        years_found += [int(yil) for yil in re.findall(pattern, cv_text_lower)]

    deneyim_score = 0
    if min_yil > 0 and years_found:
        max_yil = max(years_found)
        if max_yil >= min_yil:
            deneyim_score = 20
    score += deneyim_score

    # Detaylı skor
    score_detail = {
        "Beceriler": round(skill_score, 1),
        "Sertifikalar": round(cert_score, 1),
        "Eğitim": round(education_score, 1),
        "Eğitim Kurumu": university_line or "Belirlenemedi",
        "Dil": round(dil_score, 1),
        "Proje": round(proje_score, 1),
        "LinkedIn": round(linkedin_score, 1),
        "Deneyim": round(deneyim_score, 1)
    }

    return round(score, 2), score_detail

def generate_comment(score, score_detail):
    kisa_yorum = []

    if score >= 90:
        kisa_yorum.append("Pozisyon için oldukça yüksek bir uyum göstermektedir.")
    elif score >= 70:
        kisa_yorum.append("Pozisyona genel olarak uygundur.")
    elif score >= 50:
        kisa_yorum.append("Bazı önemli kriterleri karşılamaktadır fakat belirgin eksiklikler mevcuttur.")
    else:
        kisa_yorum.append("Pozisyonun gerektirdiği temel yeterliliklerin çoğunu karşılamamaktadır.")

    kisa_yorum.append("\n📊 Detaylı Uyum Puanları:")
    for kategori, puan in score_detail.items():
        if isinstance(puan, (int, float)):
            kisa_yorum.append(f" - {kategori}: {puan:.1f} / {get_max_score(kategori)}")

    kisa_yorum.append(f"\n🔚 Genel Uyum Skoru: {score:.1f} / 100")
    return "\n".join(kisa_yorum)

def get_max_score(kategori):
    return {
        "Beceriler": 30,
        "Sertifikalar": 10,
        "Eğitim": 10,
        "Dil": 10,
        "Proje": 5,
        "LinkedIn": 5,
        "Deneyim": 20
    }.get(kategori, 10)
