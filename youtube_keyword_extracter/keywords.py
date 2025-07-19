import streamlit as st
from bs4 import BeautifulSoup
import requests
from youtube_transcript_api import YouTubeTranscriptApi
from rake_nltk import Rake
import re

st.set_page_config(page_title="YouTube Keyword Extractor", layout="centered")
st.title("🎥 YouTube Keyword Extractor & Density Checker")

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

def compute_keyword_density(text, keyword_phrases):
    text = re.sub(r"[^\w\s]", "", text.lower())
    words = text.split()
    total_words = len(words)

    density_data = []
    for score, phrase in keyword_phrases:
        phrase_clean = phrase.lower()
        phrase_count = text.count(phrase_clean)
        phrase_density = (phrase_count / total_words) * 100 if total_words > 0 else 0
        density_data.append((phrase, phrase_count, phrase_density))
    return density_data

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

            st.subheader("📊 Meta Tag Keyword Density (based on video title)")
            
            meta_keywords_list = [kw.strip().lower() for kw in meta_keywords.split(",")]
            base_text = title.lower()

            total_words = len(base_text.split())
            col1, col2, col3 = st.columns(3)
            col1.markdown("**🔤 Keyword**")
            col2.markdown("**🔢 Count**")
            col3.markdown("**📈 Density (%)**")

            for kw in meta_keywords_list:
                count = base_text.count(kw)
                density = (count / total_words) * 100 if total_words > 0 else 0
                col1.markdown(f"{kw}")
                col2.markdown(f"{count}")
                col3.markdown(f"{density:.2f}%")

        else:
            st.warning("⚠️ No meta tags found. Trying transcript-based keyword extraction...")

        if video_id:
            transcript_text = get_transcript_text(video_id)
            if transcript_text:
                st.subheader("📝 Transcript Preview")
                st.write(transcript_text[:700] + "..." if len(transcript_text) > 700 else transcript_text)

                st.subheader("🔑 Extracted Keywords from Transcript")
                keyword_phrases = extract_keywords_from_text(transcript_text)
                for score, phrase in keyword_phrases[:15]:
                    st.markdown(f"- **{phrase}** _(Score: {score})_")

                st.subheader("📊 Transcript Keyword Density")
                density_result = compute_keyword_density(transcript_text, keyword_phrases[:15])
                
                col1, col2, col3 = st.columns(3)
                col1.markdown("**🔤 Keyword**")
                col2.markdown("**🔢 Count**")
                col3.markdown("**📈 Density (%)**")

                for phrase, count, density in density_result:
                    col1.markdown(f"{phrase}")
                    col2.markdown(f"{count}")
                    col3.markdown(f"{density:.2f}%")
            else:
                st.error("❌ Transcript not available for this video.")
        else:
            st.error("❌ Invalid YouTube video URL or ID.")
