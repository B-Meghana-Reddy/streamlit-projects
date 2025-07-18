import streamlit as st
from bs4 import BeautifulSoup
import requests
from youtube_transcript_api import YouTubeTranscriptApi
from rake_nltk import Rake
import re

st.set_page_config(page_title="YouTube Keyword Extractor", layout="centered")
st.title("🎥 YouTube Keyword Extractor Web App")

def extract_video_id(url):
    match = re.search(r"(?:v=|youtu\.be/)([^&\n]+)", url)
    return match.group(1) if match else None

def get_meta_keywords(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        page = requests.get(url, headers=headers)
        soup = BeautifulSoup(page.content, "html.parser")

        title = soup.find("title").text if soup.find("title") else "No title found"
        meta_tag = soup.find("meta", attrs={"name": "keywords"})
        
        # strict check: return None if keywords tag is missing or empty
        if not meta_tag or not meta_tag.get("content").strip():
            return title, None
        return title, meta_tag["content"]
    
    except Exception as e:
        return None, None

def get_transcript_text(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([item['text'] for item in transcript])
    except:
        return None

def extract_keywords_from_text(text):
    rake = Rake()
    rake.extract_keywords_from_text(text)
    return rake.get_ranked_phrases_with_scores()

# --- Streamlit UI ---
url = st.text_input("📺 Enter a YouTube Video URL")

if url:
    with st.spinner("🔍 Analyzing..."):
        video_id = extract_video_id(url)
        title, meta_keywords = get_meta_keywords(url)

        if title:
            st.subheader("📌 Video Title")
            st.write(title)

        if meta_keywords:
            st.subheader("🔖 Meta Tags Found")
            st.success(meta_keywords)
        else:
            st.warning("⚠️ No meta tags found. Trying transcript-based keyword extraction...")

            if video_id:
                transcript_text = get_transcript_text(video_id)
                if transcript_text:
                    st.subheader("📝 Transcript Preview")
                    st.write(transcript_text[:700] + "..." if len(transcript_text) > 700 else transcript_text)

                    st.subheader("🔑 Top Keywords from Transcript")
                    keywords = extract_keywords_from_text(transcript_text)
                    for score, phrase in keywords[:15]:  # Top 15
                        st.markdown(f"- **{phrase}** _(Score: {score})_")
                else:
                    st.error("❌ Transcript not available for this video.")
            else:
                st.error("❌ Invalid YouTube video URL or ID.")
