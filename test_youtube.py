
import os
import json
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("YOUTUBE_API_KEY")

if not api_key:
    raise SystemExit("ERROR: YOUTUBE_API_KEY not found in .env")

url = "https://www.googleapis.com/youtube/v3/search"
params = {
    "part": "snippet",
    "q": "cybersecurity",
    "type": "video",
    "maxResults": 3,
    "key": api_key
}

request = Request(url + "?" + urlencode(params))

try:
    with urlopen(request, timeout=20) as response:
        data = json.load(response)

    print("SUCCESS: Connected to YouTube Data API")
    print("Videos returned:", len(data.get("items", [])))

    for item in data.get("items", []):
        print("Title:", item["snippet"]["title"])
        print("Published:", item["snippet"]["publishedAt"])
        print("Video ID:", item["id"]["videoId"])
        print("---")

except HTTPError as error:
    print("YouTube API returned HTTP error:", error.code)
    print("Google's explanation:")
    print(error.read().decode("utf-8"))
except URLError:
    print("Network error: Could not reach YouTube API.")
