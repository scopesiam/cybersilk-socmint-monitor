
import os
import json
from datetime import datetime, timezone
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Read the YouTube API key without displaying it
API_KEY = os.getenv("YOUTUBE_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "YOUTUBE_API_KEY was not found. Check your .env file."
    )



def search_youtube(topic, start_date, end_date, max_results=10):
    """Search YouTube videos by topic and UTC publication dates."""

    # Convert the dates into the format YouTube expects
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    if end < start:
        raise ValueError("End date cannot be before start date.")

    # Include the entire final day
    from datetime import timedelta
    end_exclusive = end + timedelta(days=1)

    params = {
        "part": "snippet",
        "q": topic,
        "type": "video",
        "publishedAfter": start.strftime("%Y-%m-%dT00:00:00Z"),
        "publishedBefore": end_exclusive.strftime("%Y-%m-%dT00:00:00Z"),
        "maxResults": max_results,
        "order": "date",
        "key": API_KEY,
    }

    url = "https://www.googleapis.com/youtube/v3/search"
    request = Request(url + "?" + urlencode(params))

    with urlopen(request, timeout=20) as response:
        data = json.load(response)

    videos = []

    for item in data.get("items", []):
        snippet = item["snippet"]
        video_id = item["id"]["videoId"]

        videos.append({
            "platform": "youtube",
            "post_id": video_id,
            "account_id": snippet.get("channelId", ""),
            "account_name": snippet.get("channelTitle", ""),
            "text": snippet.get("title", "") + " " + snippet.get("description", ""),
            "published_at": snippet.get("publishedAt", ""),
            "url": f"https://www.youtube.com/watch?v={video_id}",
            "media_urls": [
                snippet.get("thumbnails", {}).get("high", {}).get("url", "")
            ],
            "synthetic": False,
            "narrative": "Unclassified",
        })

    
    # Retrieve statistics for all collected video IDs
    video_ids = [video["post_id"] for video in videos]

    statistics = get_video_statistics(video_ids)

    # Attach engagement statistics to each video
    for video in videos:
        video["engagement"] = statistics.get(
            video["post_id"],
            {
                "views": None,
                "likes": None,
                "comments": None,
            }
        )

    return videos




def get_video_statistics(video_ids):
    """Retrieve engagement statistics for YouTube videos."""

    if not video_ids:
        return {}

    params = {
        "part": "statistics",
        "id": ",".join(video_ids),
        "key": API_KEY,
    }

    url = "https://www.googleapis.com/youtube/v3/videos"
    request = Request(url + "?" + urlencode(params))

    with urlopen(request, timeout=20) as response:
        data = json.load(response)

    statistics = {}

    for item in data.get("items", []):
        stats = item.get("statistics", {})

        statistics[item["id"]] = {
            "views": int(stats["viewCount"])
            if "viewCount" in stats else None,
            "likes": int(stats["likeCount"])
            if "likeCount" in stats else None,
            "comments": int(stats["commentCount"])
            if "commentCount" in stats else None,
        }

    return statistics

if __name__ == "__main__":
    print("Searching YouTube for cybersecurity videos...")

    results = search_youtube(
        topic="cybersecurity",
        start_date="2026-11-01",
        end_date="2026-11-10",
        max_results=5
    )

    print(f"\nVideos collected: {len(results)}")

    for video in results:
        print("\n--------------------------")
        print("Channel:", video["account_name"])
        print("Published:", video["published_at"])
        print("Video:", video["url"])
        print("Text:", video["text"][:150])
        print("Views:", video["engagement"]["views"])
        print("Likes:", video["engagement"]["likes"])
        print("Comments:", video["engagement"]["comments"])
