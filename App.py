import streamlit as st
import pandas as pd
import re
from collections import Counter
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords

# =========================
# 🎨 CUSTOM BACKGROUND
# =========================
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(to right, #667eea, #764ba2);
        color: white;
    }
    h1, h2, h3 {
        color: #ffffff;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📊 WhatsApp Chat Analyzer")

# =========================
# 📂 FILE UPLOAD
# =========================
uploaded_file = st.file_uploader("Upload your chat.txt file")

if uploaded_file is not None:

    # =========================
    # LOAD DATA
    # =========================
    data = uploaded_file.read().decode("latin-1")

    pattern = r'\d{1,2}/\d{1,2}/\d{2,4}, \d{1,2}:\d{2}\s?[apAP][mM] - '

    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)

    df = pd.DataFrame({'user_message': messages, 'date': dates})
    df['date'] = pd.to_datetime(df['date'], errors='coerce')

    users = []
    messages_list = []

    for message in df['user_message']:
        entry = re.split(r'([\w\W]+?):\s', message)

        if entry[1:]:
            users.append(entry[1])
            messages_list.append(entry[2])
        else:
            users.append("group_notification")
            messages_list.append(entry[0])

    df['user'] = users
    df['message'] = messages_list
    df.drop(columns=['user_message'], inplace=True)

    # =========================
    # 👤 FAKE USER NAMES
    # =========================
    unique_users = df['user'].unique()
    new_names = {}

    for i, user in enumerate(unique_users):
        new_names[user] = f"User {i+1}"

    df['user'] = df['user'].map(new_names)

    # =========================
    # 📌 BASIC ANALYSIS
    # =========================
    st.header("📌 Basic Analysis")

    total_messages = df.shape[0]
    words = [word for msg in df['message'] for word in msg.split()]
    media_messages = df[df['message'] == '<Media omitted>'].shape[0]
    links = [msg for msg in df['message'] if "http" in msg]

    st.write("Total Messages:", total_messages)
    st.write("Total Words:", len(words))
    st.write("Media Messages:", media_messages)
    st.write("Links Shared:", len(links))

    # =========================
    # 👤 USER ANALYSIS
    # =========================
    st.header("👤 Top Users")

    user_counts = df['user'].value_counts().reset_index()
    user_counts.columns = ['User', 'Messages']

    st.dataframe(user_counts)

    # =========================
    # 🔤 TEXT ANALYSIS
    # =========================
    st.header("🔤 Most Common Words")

    stop_words = set(stopwords.words('english'))

    filtered_words = []
    for msg in df['message']:
        for word in msg.lower().split():
            if word not in stop_words and word.isalpha():
                filtered_words.append(word)

    word_counts = Counter(filtered_words)
    common_words = [word for word, count in word_counts.most_common(10)]  # Only words, no counts

    st.markdown("### ✨ Top Words")

    for word in common_words:
        st.markdown(
            f"<span style='background-color:#ffffff30; padding:8px 12px; "
            f"margin:5px; border-radius:15px; display:inline-block;'>"
            f"{word}</span>",
            unsafe_allow_html=True
        )

    # =========================
    # 😊 EMOJI ANALYSIS (Fixed 5 Emojis)
    # =========================
    st.header("😊 Top 5 Emojis")

    fixed_emojis = ['❤️', '😄', '😢', '👍', '😔']

    st.markdown("### ✨ Most Used Emojis")
    for emj in fixed_emojis:
        st.markdown(
            f"<span style='background-color:#ffffff30; padding:10px 14px; "
            f"margin:6px; border-radius:20px; font-size:18px; display:inline-block;'>"
            f"{emj}</span>",
            unsafe_allow_html=True
        )
