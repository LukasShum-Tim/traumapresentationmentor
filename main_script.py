import os
import openai
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI()

# Streamlit UI setup
st.set_page_config(page_title="ATLS Trauma Presentation Coach", page_icon="🩺", layout="centered")
st.title("🩺 ATLS Trauma Presentation Coach")
st.markdown("Record your trauma case presentation and receive AI-powered feedback based on **ATLS principles**.")

# Audio recording widget
audio_file = st.audio_input("🎙️ Record or upload your presentation (max ~2 min recommended):")

if audio_file:
    st.info("Processing your presentation... Please wait.")
    try:
        # Send to Whisper transcription
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
        transcribed_text = transcript.text
        st.success("✅ Transcription complete.")
        st.subheader("📋 Transcript:")
        st.text_area("Transcribed Text", transcribed_text, height=200)

        # Generate AI feedback
        st.info("Generating feedback from Dr. Al (AI trauma coach)...")

        messages = [
            {"role": "system", "content": """You are Dr. Al, a chatbot that helps medical students improve trauma case presentations.
Give constructive feedback based on ATLS principles. Highlight a maximum of 3 strengths and 3 areas for improvement. You will receive the audio transcript of a medical student's presentation as a text input."""},
            {"role": "user", "content": transcribed_text}
        ]

        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0,
            seed=365
        )

        feedback = completion.choices[0].message.content

        st.subheader("💬 AI Feedback:")
        st.write(feedback)

    except Exception as e:
        st.error(f"An error occurred during processing: {e}")
else:
    st.info("👆 Please record or upload your trauma presentation to begin.")
