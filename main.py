
import requests
import argparse
from bs4 import BeautifulSoup
from ics import Calendar, Event
from dateutil import parser
from datetime import timedelta
from urllib.parse import urljoin
import hashlib
import json 
from zoneinfo import ZoneInfo  # Python 3.9+

BASE_URL = "https://10026.webseminare.biz/index.php"  

def parse_args():
    parser = argparse.ArgumentParser(
        description="Scrape calendar and generate ICS file"
    )

    # OPTIONAL URL parameter
    parser.add_argument(
        "--view",
        help="Optional view parameter appended to base URL (e.g. VeDetails)",
        default=None
    )

    return parser.parse_args()

def get_main_calendar(view):
    #https://10026.webseminare.biz/index.php?filter3=26V1
    if view:
        filtered_url = f"{BASE_URL}?filter3={view}"
    else:
        filtered_url = BASE_URL
    print(filtered_url)
    response = requests.get(filtered_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    return soup

def get_detail_calendar(soup):

    TZ = ZoneInfo("Europe/Berlin")
    cal = Calendar()
    all_events = []  # For JSON export


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
    
    return cal, all_events

def write_ics_file(cal, view):
    # 8️⃣ ICS-Datei speichern
    if view:
        filename = f"termine_{view}.ics"
    else:
        filename = "termine.ics"

    with open(filename, "w", encoding="utf-8") as f:
        f.writelines(cal)
    print(f"ICS-Datei erstellt: {filename}✅") 

def write_json_file(all_events, view):

    if view:
        filename = f"termine_{view}.json"
    else:
        filename = "termine.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(all_events, f, indent=2, ensure_ascii=False)
    print(f"JSON-Datei erstellt: {filename} ✅")

def main():
    # minimal high-level flow
    args = parse_args()
    soup = get_main_calendar(args.view)
    cal, all_events = get_detail_calendar(soup)
    write_ics_file(cal, args.view)
    write_json_file(all_events, args.view)

if __name__ == "__main__":
    main()
