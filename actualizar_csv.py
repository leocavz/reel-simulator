#!/usr/bin/env python3
"""Actualiza leo_cavz_reels.csv con nuevos reels e insights desde Instagram Graph API."""

import csv
import json
import os
import time
import urllib.request
from pathlib import Path

IG_TOKEN = os.environ["IG_TOKEN"]
IG_ID = "17841447249535082"
CSV_FILE = Path(__file__).parent / "leo_cavz_reels.csv"

FIELDNAMES = [
    "fecha", "shortCode", "url", "views", "plays", "likes",
    "comentarios", "duracion_seg", "caption",
    "saves", "shares", "reach", "avg_watch_ms", "total_watch_ms",
]


def api(url):
    try:
        with urllib.request.urlopen(url, timeout=15) as r:
            return json.loads(r.read())
    except Exception as e:
        return {"error": str(e)}


def shortcode_from_url(url):
    return url.rstrip("/").split("/")[-1]


def get_all_media():
    media = []
    url = (
        f"https://graph.facebook.com/v19.0/{IG_ID}/media"
        f"?fields=id,timestamp,permalink,caption,like_count,comments_count"
        f"&limit=100&access_token={IG_TOKEN}"
    )
    while url:
        data = api(url)
        if "error" in data:
            print(f"Error fetching media: {data['error']}")
            break
        media.extend(data.get("data", []))
        url = data.get("paging", {}).get("next")
        time.sleep(0.3)
    return media


def get_insights(media_id):
    metrics = "plays,saved,shares,reach,ig_reels_avg_watch_time,ig_reels_video_view_total_time"
    url = (
        f"https://graph.facebook.com/v19.0/{media_id}/insights"
        f"?metric={metrics}&access_token={IG_TOKEN}"
    )
    data = api(url)
    result = {}
    for item in data.get("data", []):
        val = item.get("values", [{}])[0].get("value", 0)
        result[item["name"]] = val
    return result


def main():
    existing = {}
    if CSV_FILE.exists():
        with open(CSV_FILE, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                existing[row["shortCode"]] = row
    print(f"Reels en CSV: {len(existing)}")

    print("Obteniendo media de Instagram Graph API...")
    media_list = get_all_media()
    print(f"  {len(media_list)} posts en la cuenta")

    new_count = 0
    for m in media_list:
        code = shortcode_from_url(m.get("permalink", ""))
        if not code or code in existing:
            continue
        ts = m.get("timestamp", "")
        existing[code] = {
            "fecha": ts[:10] if ts else "",
            "shortCode": code,
            "url": m.get("permalink", ""),
            "views": "",
            "plays": "",
            "likes": m.get("like_count", ""),
            "comentarios": m.get("comments_count", ""),
            "duracion_seg": "",
            "caption": m.get("caption", ""),
            "saves": "", "shares": "", "reach": "", "avg_watch_ms": "", "total_watch_ms": "",
        }
        new_count += 1
        print(f"  + {code} ({ts[:10]})")

    print(f"Nuevos reels: {new_count}")

    print("\nActualizando insights...")
    media_by_code = {shortcode_from_url(m.get("permalink", "")): m["id"] for m in media_list}

    ok = 0
    for code, row in existing.items():
        media_id = media_by_code.get(code)
        if not media_id:
            continue
        ins = get_insights(media_id)
        if ins:
            row["plays"] = ins.get("plays", row.get("plays", ""))
            row["reach"] = ins.get("reach", "")
            row["saves"] = ins.get("saved", "")
            row["shares"] = ins.get("shares", "")
            row["avg_watch_ms"] = ins.get("ig_reels_avg_watch_time", "")
            row["total_watch_ms"] = ins.get("ig_reels_video_view_total_time", "")
            if not row.get("views"):
                row["views"] = ins.get("reach", "")
            ok += 1
        time.sleep(0.4)

    print(f"Insights actualizados: {ok}/{len(existing)}")

    rows = sorted(existing.values(), key=lambda r: r.get("fecha", ""), reverse=True)
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nListo — {CSV_FILE.name} actualizado con {len(rows)} reels")


if __name__ == "__main__":
    main()
