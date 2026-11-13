import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
from rapidfuzz.fuzz import ratio 
from youtube_collector import search_youtube


st.set_page_config(page_title="SOCMINT Intelligence Monitor", layout="wide")
st.title("SOCMINT Intelligence Monitor")

BASE = datetime(2026, 11, 5, 10, 0, tzinfo=timezone.utc)
EXAMPLES = [
    ("telegram", "alpha", 0, "Acme Bank is collapsing! Withdraw your money now!", "https://example.com/demo/t1", 90),
    ("telegram", "beta", 2, "Acme Bank is collapsing. Withdraw your money now!", "https://example.com/demo/t2", 70),
    ("youtube", "gamma", 4, "Acme Bank is collapsing - withdraw your money now!", "https://example.com/demo/y1", 130),
    ("telegram", "delta", 12, "Customers report they cannot withdraw money from Acme Bank", "https://example.com/demo/t3", 25),
    ("youtube", "epsilon", 45, "Are Acme Bank withdrawals restricted? Let's examine the evidence", "https://example.com/demo/y2", 40),
    ("telegram", "zeta", 70, "Rumours claim Acme Bank suffered a cyberattack", "https://example.com/demo/t4", 15),
    ("youtube", "eta", 180, "Acme Bank cybersecurity rumour explained", "https://example.com/demo/y3", 19),
    ("telegram", "theta", 185, "Acme Bank is collapsing! Withdraw your money now!", "https://example.com/demo/t5", 5),
]


def demo_posts(topic):
    # Synthetic examples intentionally replace the bank name with the demo topic.
    return pd.DataFrame([
        {
            "post_id": f"demo-{i+1}", "platform": platform, "account_id": account,
            "text":text,
            "published_at": BASE + timedelta(minutes=minute),
            "collected_at": datetime.now(timezone.utc), "url": url,
            "media_urls": [], "engagement": engagement, "synthetic": True,
        }
        for i, (platform, account, minute, text, url, engagement) in enumerate(EXAMPLES)
    ])


def narrative(text):
    t = text.lower()
    if any(x in t for x in ("collaps", "withdraw your money")):
        return "Insolvency rumour"
    if any(x in t for x in ("withdrawal", "cannot withdraw", "withdrawals")):
        return "Withdrawal restrictions"
    if any(x in t for x in ("cyberattack", "cybersecurity", "hack")):
        return "Cyberattack rumour"
    return "Other"


def youtube_narrative(text):
    """Classify YouTube content using simple keyword rules."""

    t = str(text).lower()

    if any(word in t for word in (
        "ransomware", "data breach", "cyberattack",
        "hacked", "dark web", "stolen data"
    )):
        return "Cyber incidents and breaches"

    if any(word in t for word in (
        "phishing", "scam", "fraud", "social engineering"
    )):
        return "Cybercrime and fraud"

    if any(word in t for word in (
        "pentesting", "ethical hacking", "security tools",
        "vulnerability", "malware"
    )):
        return "Security tools and techniques"

    if any(word in t for word in (
        "career", "jobs", "salary", "certification",
        "training", "learning"
    )):
        return "Cybersecurity careers and education"

    return "General cybersecurity discussion"


def find_pairs(df, threshold=90, window=5):
    matches = []
    records = df.sort_values("published_at").to_dict("records")
    for i, a in enumerate(records):
        for b in records[i+1:]:
            if a["account_id"] == b["account_id"]:
                continue
            gap = abs((b["published_at"] - a["published_at"]).total_seconds()) / 60
            if gap > window:continue
            similarity = ratio(a["text"].lower(), b["text"].lower())
            if gap <= window and similarity >= threshold:
                matches.append({"account_1": a["account_id"], 
                                "account_2": b["account_id"],
                                "similarity_pct": round(similarity, 1), 
                                "gap_minutes": round(gap, 1),
                                "post_1": a["post_id"],
                                "post_2": b["post_id"],
                                "url_1": a.get("url", ""),
                                "url_2": b.get("url", ""),
            })
    return pd.DataFrame(matches, columns=[
    "account_1", "account_2", "similarity_pct",
    "gap_minutes", "post_1", "post_2",
    "url_1", "url_2"])



with st.sidebar:
    st.header("Search")

data_source = st.selectbox(
    "Select Data Source",
    ["Synthetic Demo", "Live YouTube"],
    index=1,
    help="Choose between demonstration data and real YouTube API results."
)
if data_source == "Live YouTube":
    st.caption("Cybersilk technical challenge | LIVE YOUTUBE DATA")
else:
    st.caption("Cybersilk technical challenge | SYNTHETIC DEMO DATA")
with st.form("socmint_search"):
    topic = st.text_input("Topic", "Acme Bank").strip()
    start = st.date_input("Start date (UTC)", value=BASE.date())
    end = st.date_input("End date (UTC)", value=BASE.date())
    platforms = st.multiselect("Platforms", ["telegram", "youtube"], default=["telegram", "youtube"])
    threshold = st.slider("Similarity threshold (%)", 70, 100, 90)
    window = st.slider("Posting window (minutes)", 1, 30, 5)
    search_clicked = st.form_submit_button("Search", type="primary")
if not search_clicked and "search_results" not in st.session_state:
    st.info("Enter your search criteria and click Search to begin.")
    st.stop()
if not topic:
    st.warning("Enter a topic to continue.")
    st.stop()
if start > end:
    st.error("Start date must not be after end date.")
    st.stop()


if data_source == "Live YouTube":
    if not search_clicked:
        posts = st.session_state.get("search_results", [])
    else:
        with st.spinner("Collecting real YouTube videos..."):
            posts = search_youtube(
                topic=topic,
                start_date=start.isoformat(),
                end_date=end.isoformat(),
                max_results=25
            )
    df = pd.DataFrame(posts)
    st.session_state["search_results"] = posts
    if df.empty:
        st.warning("No YouTube videos found for the selected topic and dates.")
        st.stop()
    
    df["collected_at"] = pd.Timestamp.now(tz="UTC")

else:
    df = demo_posts(topic)


df = df[
    df["text"].str.contains(
        topic,
        case=False,
        regex=False,
        na=False
    )
].copy()



df["published_at"] = pd.to_datetime(df["published_at"], utc=True, errors="coerce")
df = df[df["platform"].isin(platforms) & df["published_at"].dt.date.between(start, end)].copy()
if df.empty:
    st.info("No demo posts match the selected dates and platforms. Try 5 November 2026.")
    st.stop()

if data_source == "Live YouTube":
    df["narrative"] = df["text"].map(youtube_narrative)
else:
    df["narrative"] = df["text"].map(narrative)

df["day"] = df["published_at"].dt.strftime("%Y-%m-%d")
pairs = find_pairs(df, threshold, window)

c1, c2, c3 = st.columns(3)
c1.metric("Posts collected", len(df))
c2.metric("Narratives", df["narrative"].nunique())
c3.metric("Suspicious pairs", len(pairs))

overview, coordination, evidence, methodology = st.tabs(["Narratives", "Coordination", "Evidence & exports", "Methodology"])
with overview:
    st.subheader("Narrative volume by platform")
    counts = df.groupby(["narrative", "platform"]).size().reset_index(name="posts")
    st.plotly_chart(px.bar(counts, x="narrative", y="posts", color="platform", barmode="group"), use_container_width=True)
    st.subheader("Volume over time")
    daily = df.groupby(["day", "narrative"]).size().reset_index(name="posts")
    daily["day"] = pd.to_datetime(daily["day"]).dt.strftime("%d %b %Y")
    st.plotly_chart(px.bar(daily, x="day", y="posts", color="narrative", barmode="group"), use_container_width=True)
    st.subheader("Earliest observed posts (within collected sample)")
    earliest = df.sort_values("published_at").groupby("narrative", as_index=False).first()
    st.dataframe(earliest[["narrative", "platform", "account_id", "published_at", "url"]], hide_index=True)
with coordination:
    st.subheader("Potential coordinated posting pairs")
    st.write("Rule: different accounts, similar text and posts close in time. A match is NOT proof of coordination.")
    st.dataframe(pairs, hide_index=True, use_container_width=True)
    st.warning("Analyst review required: common breaking news can produce false positives.")
with evidence:
    st.dataframe(df[["post_id", "platform", "account_id", "text", "published_at", "engagement", "url", "narrative"]], hide_index=True, use_container_width=True)
    export_df = df.drop(columns=["day"]).copy()
    for col in ("published_at", "collected_at"):
        export_df[col] = export_df[col].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    st.download_button("Download posts CSV", export_df.to_csv(index=False).encode(), "posts.csv", "text/csv")
    st.download_button("Download posts JSON", export_df.to_json(orient="records", indent=2).encode(), "posts.json", "application/json")
    st.download_button("Download coordination CSV", pairs.to_csv(index=False).encode(), "coordination.csv", "text/csv")
with methodology:
    st.markdown("""**Coverage:** synthetic demonstration posts only. No real social media APIs connected yet.\n\n**Narratives:** simple transparent keyword rules; ambiguous wording can be misclassified.\n\n**Coordination:** RapidFuzz text similarity plus posting-time proximity. No account creation dates, profile images, forwards, or verified amplification edges are available in this demo.\n\n**Misinformation:** not automatically determined. Claims are unverified until supported or contradicted by independently sourced evidence.\n\n**Origins:** earliest observed post in this limited dataset, not the true first post online.\n\n**Media:** demo has empty media URL arrays; real collectors will populate media metadata when permitted.\n\n**Privacy:** only collect accessible public data in accordance with platform rules; never commit API credentials.\n""")
