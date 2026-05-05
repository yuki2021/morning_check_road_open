import json
import os
import sys
import requests
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
ROUTES_API_URL = "https://routes.googleapis.com/directions/v2:computeRoutes"

HOME = os.getenv("HOME_ADDRESS")
WORK = os.getenv("WORK_ADDRESS")

def load_routes():
    routes = []
    i = 1
    while True:
        raw = os.getenv(f"ROUTE{i}")
        if not raw:
            break
        data = json.loads(raw)
        routes.append({
            "name": data["name"],
            "waypoints": [HOME] + data["waypoints"] + [WORK],
        })
        i += 1
    return routes


def fetch_route(name, waypoints):
    origin = waypoints[0]
    destination = waypoints[-1]
    intermediates = waypoints[1:-1]

    body = {
        "origin": {"address": origin},
        "destination": {"address": destination},
        "travelMode": "DRIVE",
        "routingPreference": "TRAFFIC_AWARE",
    }
    if intermediates:
        body["intermediates"] = [{"address": wp} for wp in intermediates]

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": API_KEY,
        "X-Goog-FieldMask": "routes.duration,routes.distanceMeters",
    }

    try:
        res = requests.post(ROUTES_API_URL, json=body, headers=headers, timeout=10)
        if not res.ok:
            return {"name": name, "error": f"{res.status_code}: {res.text}"}
        data = res.json()
    except requests.RequestException as e:
        return {"name": name, "error": str(e)}

    if "routes" not in data or not data["routes"]:
        return {"name": name, "error": "ルートが見つかりませんでした"}

    route = data["routes"][0]
    duration_sec = int(route["duration"].rstrip("s"))
    distance_m = route["distanceMeters"]

    return {
        "name": name,
        "duration_min": duration_sec // 60,
        "duration_sec": duration_sec % 60,
        "distance_km": distance_m / 1000,
    }


def notify_slack(message):
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    if not webhook_url:
        return
    requests.post(webhook_url, json={"text": message}, timeout=10)


def build_slack_message(now, valid, fastest):
    lines = [f"*朝の通勤ルートチェック ({now})*\n"]
    for r in valid:
        marker = " :star: 最速！" if r["name"] == fastest["name"] else ""
        lines.append(f"{r['name']}{marker}")
        lines.append(f"　所要時間: {r['duration_min']}分{r['duration_sec']:02d}秒　距離: {r['distance_km']:.1f} km")
    return "\n".join(lines)


def main():
    if not API_KEY:
        print("エラー: GOOGLE_MAPS_API_KEY が設定されていません（.env を確認してください）")
        sys.exit(1)
    if not HOME or not WORK:
        print("エラー: HOME_ADDRESS または WORK_ADDRESS が設定されていません（.env を確認してください）")
        sys.exit(1)

    JST = timezone(timedelta(hours=9))
    now = datetime.now(JST).strftime("%Y-%m-%d %H:%M")
    print(f"\n== 朝の通勤ルートチェック ({now}) ==\n")

    results = []
    for route in load_routes():
        print(f"  取得中: {route['name']} ...", end="", flush=True)
        result = fetch_route(route["name"], route["waypoints"])
        results.append(result)
        if "error" in result:
            print(f" エラー: {result['error']}")
        else:
            print(f" {result['duration_min']}分")

    valid = [r for r in results if "error" not in r]
    if not valid:
        print("\n全ルートの取得に失敗しました。")
        sys.exit(1)

    fastest = min(valid, key=lambda r: r["duration_min"] * 60 + r["duration_sec"])

    print("\n" + "=" * 50)
    print("ルート比較結果")
    print("=" * 50)
    for r in valid:
        marker = " ★ 最速！" if r["name"] == fastest["name"] else ""
        print(f"  {r['name']}")
        print(f"    所要時間: {r['duration_min']}分{r['duration_sec']:02d}秒   距離: {r['distance_km']:.1f} km{marker}")
    print("=" * 50)

    for r in results:
        if "error" in r:
            print(f"  ※ {r['name']}: {r['error']}")

    print()
    notify_slack(build_slack_message(now, valid, fastest))


if __name__ == "__main__":
    main()
