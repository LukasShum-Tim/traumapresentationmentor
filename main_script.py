import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import openai
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI()

# Email configuration (use environment variables for safety)
SMTP_SERVER = st.secrets["SMTP_SERVER"]
SMTP_PORT = int(st.secrets["SMTP_PORT"])
SMTP_USER = st.secrets["SMTP_USER"]
SMTP_PASSWORD = st.secrets["SMTP_PASSWORD"]

# Streamlit UI setup
st.set_page_config(page_title="ATLS Trauma Presentation Coach", page_icon="🩺", layout="centered")
st.title("🩺 ATLS Trauma Presentation Coach")
st.markdown("Record or upload a presentation to receive AI-based feedback, edit it, and send to your student.")

# Audio input
audio_file = st.audio_input("🎙️ Record or upload your presentation (max ~2 min recommended):")

if audio_file:
    st.info("Processing your presentation... Please wait.")
    try:
        # Transcribe using Whisper
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
        transcribed_text = transcript.text
        st.success("✅ Transcription complete.")
        st.subheader("📋 Transcript:")
        st.text_area("Transcribed Text", transcribed_text, height=200)

        # AI feedback
        st.info("Generating feedback from Dr. Al (AI trauma coach)...")

        messages = [
            {"role": "system", "content": """You are Dr. Al, an expert trauma surgeon chatbot that helps medical students improve trauma case presentations.
Give constructive feedback based on ATLS principles. Use the following evaluation grid to assess the student's performance.
You will receive the audio transcript of a medical student's presentation as a text input.

Trauma Patient Oral Presentation Grading Scale
This rubric can be adapted depending on whether the focus is on formative feedback (ongoing learning) or summative assessment (final evaluation). A typical grading scale might range from 1-5 or 1-10, where each number corresponds to a level of competency. Below is a 1-5 scale, with "5" being excellent and "1" being unacceptable.
________________________________________
1. Structure & Organization (1–5)
Criteria: The ability to deliver a clear, structured presentation, following a logical sequence of trauma management based on the ATLS principles.
•	1: Disorganized, lacks clear structure, unable to distinguish between primary and secondary surveys.
•	2: Minimal structure, confusing transitions, some elements of the primary and secondary surveys are unclear.
•	3: Fair structure, follows a basic sequence but might miss some key elements.
•	4: Good structure, clear transitions between ATLS principles (primary and secondary surveys, management priorities).
•	5: Excellent structure, follows the ATLS guidelines in a systematic, clear, and logical manner.
________________________________________
2. History Taking (1–5)
Criteria: Gathering and presenting the patient's history (e.g., mechanism of injury, comorbidities, allergies, medications).
•	1: History is incomplete or unclear, missing essential details such as mechanism of injury or patient’s past medical history.
•	2: Basic history provided, but important elements are overlooked.
•	3: History is generally complete but may lack depth in key areas (e.g., detailed mechanism of injury).
•	4: Comprehensive history, includes key elements (e.g., mechanism, pre-existing conditions, vital information).
•	5: Thorough, well-organized history that is detailed and pertinent to trauma management.
________________________________________
3. Primary Survey (1–5)
Criteria: Adequate assessment and identification of life-threatening injuries based on the primary survey (ABCDE: Airway, Breathing, Circulation, Disability, Exposure).
•	1: Fails to identify or prioritize life-threatening conditions, incomplete primary survey.
•	2: Performs primary survey but misses key elements (e.g., airway management or circulation assessment).
•	3: Correctly identifies major life-threatening issues, but lacks depth in some areas.
•	4: Thorough primary survey, identifies all life-threatening injuries and prioritizes appropriately.
•	5: Excellent primary survey, clear rationale for assessment, and immediate action; ensures that all aspects (airway, breathing, circulation, disability, exposure) are addressed comprehensively.
________________________________________
4. Secondary Survey & Further Investigation (1–5)
Criteria: A detailed approach to identifying less obvious injuries or issues (head-to-toe examination, imaging, lab tests).
•	1: No secondary survey, or inadequate examination.
•	2: Performs secondary survey, but misses critical aspects or doesn’t follow through with appropriate investigations (e.g., imaging).
•	3: Adequate secondary survey, but lacks some detail in identifying non-obvious injuries.
•	4: Good secondary survey, performs necessary investigations and examination in a clear, methodical way.
•	5: Thorough secondary survey, anticipates and identifies all injuries (both obvious and less obvious), appropriately requests investigations (imaging, lab tests).
________________________________________
5. Treatment & Management Plan (1–5)
Criteria: Ability to create an evidence-based, timely management plan based on ATLS protocols and trauma guidelines.
•	1: No clear management plan, lacks integration of ATLS principles, or includes unsafe/incorrect interventions.
•	2: Basic management plan but lacks clarity, missing key interventions, or may suggest inappropriate steps.
•	3: Adequate plan, includes most correct steps but lacks detail or prioritization of care.
•	4: Solid management plan, includes timely interventions based on ATLS, though some refinements are possible.
•	5: Comprehensive, evidence-based management plan, demonstrates clear prioritization and execution of ATLS guidelines.
________________________________________
6. Communication Skills (1–5)
Criteria: Effective communication with the team (verbal clarity, professionalism, and ability to convey essential information).
•	1: Poor communication, disorganized, unclear, and unable to convey critical information.
•	2: Communication is sometimes unclear, missing key elements, or lacks professional tone.
•	3: Clear communication but may miss some critical details or seem hesitant.
•	4: Good communication, clear and professional, conveys most critical information.
•	5: Excellent communication, confident, clear, concise, and professional with no missing critical elements.
________________________________________
7. Clinical Reasoning & Decision Making (1–5)
Criteria: Ability to reason through the case, demonstrating solid clinical judgment in trauma management (prioritizing interventions, managing complications, and anticipating future needs).
•	1: No evidence of clinical reasoning, fails to prioritize key issues, or makes inappropriate decisions.
•	2: Limited clinical reasoning, decisions are often based on incomplete data or incorrect assumptions.
•	3: Adequate clinical reasoning, mostly appropriate decisions, but lacks depth or foresight in some areas.
•	4: Good clinical reasoning, demonstrates the ability to prioritize and make evidence-based decisions.
•	5: Exceptional clinical reasoning, demonstrates excellent judgment and foresight, prioritizes appropriately and manages anticipated complications effectively.
________________________________________
8. Time Management (1–5)
Criteria: Ability to deliver an efficient, complete presentation within a reasonable time frame, without unnecessary details or rushing.
•	1: Presentation is overly rushed or significantly over time.
•	2: Takes too long, or important details are omitted due to time constraints.
•	3: Reasonable time management, but either too rushed in some areas or a bit too detailed.
•	4: Good time management, covers all necessary aspects within the time limit.
•	5: Excellent time management, concise, yet thorough presentation, respects time constraints while delivering comprehensive content.
________________________________________
Total Score: 1–40
•	36–40: Excellent – The student shows a strong command of trauma assessment and management, communicates clearly, and makes well-prioritized decisions.
•	30–35: Good – The student demonstrates competence with only minor areas for improvement in presentation or clinical reasoning.
•	20–29: Satisfactory – The student performs adequately but may have several areas for improvement, especially in structure, clinical reasoning, or communication.
•	Below 20: Needs Improvement – Significant deficiencies in multiple areas, requiring additional practice or support."""},
            {"role": "user", "content": transcribed_text}
        ]

        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0,
            seed=365
        )

        ai_feedback = completion.choices[0].message.content
        st.success("✅ Feedback generated.")

        st.subheader("💬 Review and Edit Feedback")
        edited_feedback = st.text_area(
            "Faculty can edit or add comments below before sending:",
            ai_feedback,
            height=300
        )

        # Email section
        st.subheader("✉️ Send Feedback to Student")
        col1, col2 = st.columns(2)
        with col1:
            student_email = st.text_input("Student Email")
        with col2:
            faculty_name = st.text_input("Faculty Name (optional)")

        email_subject = st.text_input("Email Subject", "ATLS Presentation Feedback")
        send_email = st.button("📤 Send Feedback via Email")

        if send_email:
            if not student_email:
                st.warning("Please enter the student's email address.")
            elif not SMTP_USER or not SMTP_PASSWORD:
                st.error("Email sending is not configured. Please set SMTP_USER and SMTP_PASSWORD in your .env file.")
            else:
                try:
                    # Compose email
                    msg = MIMEMultipart()
                    msg["From"] = SMTP_USER
                    msg["To"] = student_email
                    msg["Subject"] = email_subject

                    body = f"Dear Student,\n\nHere is your ATLS presentation feedback:\n\n{edited_feedback}\n\n"
                    if faculty_name:
                        body += f"Best regards,\n{faculty_name}"
                    else:
                        body += "Best regards,\nATLS Faculty"

                    msg.attach(MIMEText(body, "plain"))

                    # Send email
                    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                        server.starttls()
                        server.login(SMTP_USER, SMTP_PASSWORD)
                        server.send_message(msg)

                    st.success(f"✅ Feedback successfully sent to {student_email}!")

                except Exception as e:
                    st.error(f"An error occurred while sending the email: {e}")

    except Exception as e:
        st.error(f"An error occurred during processing: {e}")
else:
    st.info("👆 Please record or upload your trauma presentation to begin.")
