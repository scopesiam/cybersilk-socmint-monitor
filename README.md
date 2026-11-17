
# Cybersilk SOCMINT Intelligence Monitor

A Python-based Social Media Intelligence (SOCMINT) prototype developed for the Cybersilk technical assessment.

The application collects real YouTube video metadata through the YouTube Data API v3 and provides a separate synthetic dataset for demonstrating potential coordinated posting behaviour.

## Core Capabilities

- Live YouTube Data API v3 collection using topic and date filters.
- Synthetic Telegram and YouTube demonstration data.
- Rule-based narrative classification and volume analysis.
- Daily narrative trends and per-platform comparisons.
- Earliest observed posts and chronological narrative propagation timeline.
- Potential coordinated activity detection using RapidFuzz text similarity and posting-time proximity.
- Connected account grouping with detection reasons, similarity scores and time gaps.
- Rule-based claim verification indicators for financial distress, service disruptions and cyber incidents.
- Evidence records containing account IDs, timestamps, engagement metrics, post IDs and source URLs.
- CSV and JSON exports for further investigation.
- Interactive Streamlit dashboard with adjustable detection thresholds.


**Data integrity:** Live YouTube records and synthetic demonstration posts are clearly distinguished. Synthetic data must not be presented as evidence of real-world activity.



## Setup

### Requirements
- Python 3.10 or newer
- A YouTube Data API v3 key
- Internet access for live YouTube searches

### Installation

1. Clone or download this repository.
2. Open a terminal in the project folder.
3. Create a virtual environment:

   python -m venv .venv

4. Activate the environment on Windows PowerShell:

   .\.venv\Scripts\Activate.ps1

5. Install dependencies:

   python -m pip install -r requirements.txt


6. Create a `.env` file in the project folder (`cybersilk_skeleton`) and add:

   YOUTUBE_API_KEY=your_youtube_api_key_here

   Replace `your_youtube_api_key_here` with your own Google Cloud YouTube Data API v3 key.
.

7. Start the dashboard:

   python -m streamlit run app.py

8. Open the local Streamlit URL displayed in the terminal.

### Using the Dashboard

- Select Live YouTube or Synthetic Demo.
- Enter a topic and date range.
- Select the relevant platforms.
- Click Search to collect or load results.
- Review narrative trends, coordination findings and evidence exports.

### API Security

Never commit the `.env` file, API credentials or Telegram session files to GitHub. Keep `.env` excluded using `.gitignore`.


## What works

- Live YouTube video metadata collection using the YouTube Data API v3.
- Topic and UTC date-range filtering.
- Synthetic Telegram and YouTube records for controlled demonstrations.
- Rule-based narrative classification.
- Narrative volume by platform and daily trends.
- Earliest observed posts within the collected sample.
- Potential coordinated posting detection using text similarity and time proximity.
- Coordination evidence including account IDs, post IDs, similarity scores, time gaps and source URLs.
- CSV and JSON evidence exports.
- Streamlit dashboard with a Search button and session-based result storage.

The coordination detector identifies candidate patterns for analyst review. It does not establish malicious intent or prove coordination.


## What is not implemented yet

- **Live Telegram collection:** Telethon is installed, but Telegram API access and integration are not yet complete.
- **Additional live platforms:** YouTube is currently the only operational live data source. Telegram records in the demo are synthetic.
- **Full platform coverage:** YouTube API searches return a limited sample, not every relevant video.
- **Cross-platform propagation tracking:** The prototype cannot reliably establish how narratives spread between platforms.
- **Media analysis:** Video and image content is not downloaded or analysed. Classification uses available text metadata.
- **Advanced narrative classification:** Keyword-based categories can produce false positives and misclassifications.
- **Coordination attribution:** Similar content posted close together does not establish deliberate coordination.
- **Production reliability:** API quota management, retry handling, persistent storage and automated testing require further development.
- **Detection accuracy:** Precision and recall have not been evaluated against a labelled real-world dataset.

## Detection caveats
Matching text and posting times alone do not prove coordination. Unverified claims must not be labelled false without external evidence. Synthetic examples are not a valid estimate of real-world detection precision or recall.
