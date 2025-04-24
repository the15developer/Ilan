import requests
from bs4 import BeautifulSoup
import re
import os
import json
from datetime import datetime
from reminder.email_reminder import send_reminder_email


def extract_deadline_from_linkedin(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print("Sayfa alınamadı:", response.status_code)
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    full_text = soup.get_text(separator=" ", strip=True)

    # İlan başlığı: <title> etiketinden al
    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else "Başlık bulunamadı"

    # 1. Adım: "Son başvuru tarihi" geçen tüm cümleleri bul
    sentences = re.findall(r'son başvuru [^!?,\n]*[!?,]', full_text, flags=re.IGNORECASE)
    print(len(sentences))
    print(sentences)

    # 2. Adım: Her cümlede çeşitli tarih formatlarını dene
    for sentence in sentences:
        # Türkçe tarih: 28 Nisan 2025
        match1 = re.search(r'(\d{1,2}\s(?:Ocak|Şubat|Mart|Nisan|Mayıs|Haziran|Temmuz|Ağustos|Eylül|Ekim|Kasım|Aralık)\s\d{4})', sentence, flags=re.IGNORECASE)
        if match1:
            print("match1 !")
            return title, match1.group(1)

        # Noktalı: 28.04.2025
        match2 = re.search(r'(\d{1,2}\.\d{1,2}\.\d{4})', sentence)
        if match2:
            print("match2 !")
            return title, match2.group(1)

        # Eğik çizgili: 28/04/2025
        match3 = re.search(r'(\d{1,2}/\d{1,2}/\d{4})', sentence)
        if match3:
            print("match3 !")
            return title, match3.group(1)

        # ISO: 2025-04-28
        match4 = re.search(r'(\d{4}-\d{1,2}-\d{1,2})', sentence)
        if match4:
            print("match4 !")
            return title, match4.group(1)

    return title, "Son başvuru tarihi bulunamadı."


def save_to_json(title, date, url, filepath="database/deadlines.json"):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    # Dosya varsa oku, yoksa boş liste başlat
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []

    # Yeni ID'yi belirle
    new_id = max([entry.get("id", 0) for entry in data], default=0) + 1

    # Zaman damgası
    timestamp = datetime.now().isoformat()

    # Yeni kaydı oluştur
    new_entry = {
        "id": new_id,
        "url": url,
        "title": title,
        "deadline": date,
        "category": "staj",
        "timestamp": timestamp
    }

    # Aynı URL varsa güncelle, yoksa ekle
    for entry in data:
        if entry["url"] == url:
            entry.update(new_entry)
            break
    else:
        data.append(new_entry)

    # Güncellenmiş veriyi kaydet
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# Test et
url = "https://www.youthall.com/tr/Youthall/yazilim-stajyeri_138/"
baslik, tarih= extract_deadline_from_linkedin(url)

print(baslik)
print(tarih)

save_to_json(baslik, tarih, url)




send_reminder_email(baslik, url, tarih)