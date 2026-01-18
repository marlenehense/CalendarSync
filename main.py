
import requests
from bs4 import BeautifulSoup
from ics import Calendar, Event
from dateutil import parser
from datetime import timedelta
from urllib.parse import urljoin
import hashlib
import json 
from zoneinfo import ZoneInfo  # Python 3.9+


BASE_URL = "https://10026.webseminare.biz/index.php"  # iframe-URL / Basis für relative Links
FILTERED_URL = "https://10026.webseminare.biz/index.php?view=sidebar&VeID=&ThID=&volltextsuche=&filter1=&filter2=&filter3=26V1"
TZ = ZoneInfo("Europe/Berlin")


cal = Calendar()
all_events = []  # For JSON export

# 1️⃣ Sidebar-Page abrufen
response = requests.get(FILTERED_URL)
response.raise_for_status()
soup = BeautifulSoup(response.text, "html.parser")

# 2️⃣ Alle Event-Divs finden
for div in soup.select("div.sidebar_zeile"):
    
    # Titel & relative Link
    title_tag = div.select_one("div.sidebar_titel a")
    if not title_tag:
        continue
    relative_link = title_tag.get("href")
    detail_url = urljoin(BASE_URL, relative_link)
    
    # 3️⃣ Detailseite abrufen
    resp_detail = requests.get(detail_url)
    resp_detail.raise_for_status()
    soup_detail = BeautifulSoup(resp_detail.text, "html.parser")
    
    # 4️⃣ Detailinformationen parsen
    def get_field(label):
        lbl_div = soup_detail.find("div", text=label)
        if lbl_div:
            val_div = lbl_div.find_next_sibling("div")
            if val_div:
                return val_div.get_text(separator=" ", strip=True)
        return ""
    
    title = get_field("Seminar")
    term_text = get_field("Termin")  # z.B. '09.01.2026,  15:00 - 18:15 Uhr'
    location = get_field("Ort")
    trainer = get_field("Dozent(in)")
    
    # 5️⃣ Datum und Zeit parsen
    try:
        date_str, time_str = [t.strip() for t in term_text.split(",")]
        start_str, end_str = [t.strip().replace("Uhr","") for t in time_str.split("-")]
        dt_start = parser.parse(f"{date_str} {start_str}", dayfirst=True).replace(tzinfo=TZ)
        dt_end = parser.parse(f"{date_str} {end_str}", dayfirst=True).replace(tzinfo=TZ)
    except Exception:
        print(f"Could not parse date/time for {title}")
        continue
    
    # 6️⃣ Event erstellen
    event = Event()
    event.name = title
    event.begin = dt_start
    event.end = dt_end
    event.location = location
    event.description = f"Trainer: {trainer}\nLink: {detail_url}"
    
    # 7️⃣ Stabile UID für Google Kalender
    uid = hashlib.md5(f"{title}{dt_start}{location}".encode()).hexdigest()
    event.uid = uid
    
    cal.events.add(event)
   # 6️⃣ Append to JSON list
    all_events.append({
        "title": title,
        "start": dt_start.isoformat(),
        "end": dt_end.isoformat(),
        "location": location,
        "trainer": trainer,
        "link": detail_url
    })

    #print(f"Added event: {title} ({dt_start} - {dt_end})")

# 8️⃣ ICS-Datei speichern
with open("termine.ics", "w", encoding="utf-8") as f:
    f.writelines(cal)

print("ICS-Datei erstellt: termine.ics ✅") 

with open("termine.json", "w", encoding="utf-8") as f:
    json.dump(all_events, f, indent=2, ensure_ascii=False)
print("JSON-Datei erstellt: termine.json ✅")