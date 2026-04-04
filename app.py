import streamlit as st
import json
import re
from datetime import datetime

# ---------------- DATA ----------------
version_float = 1.3

# only .json is supported for loading — CSV/TXT are export-only formats
allowed_ext = {".json"}

# frozenset — required fields for a valid record
required_fields = frozenset({"name", "surname", "dob", "student_id"})

# regex: letters only, min 2 chars, no digits
NAME_PATTERN = re.compile(r"^[A-Za-zА-Яа-яЁё\s'\-]{2,}$")

# valid score range: 0..64 inclusive
valid_score_range = range(0, 65)

questions = [
    {"q": "How often do you plan your daily tasks in advance?",
     "opts": [("Always",0),("Often",1),("Sometimes",2),("Rarely",3),("Never",4)]},
    {"q": "How frequently do you prioritise tasks before starting your work?",
     "opts": [("Always",0),("Often",1),("Sometimes",2),("Rarely",3),("Never",4)]},
    {"q": "How often do you complete tasks within the planned time?",
     "opts": [("Always",0),("Often",1),("Sometimes",2),("Rarely",3),("Never",4)]},
    {"q": "How often do you feel in control of your time?",
     "opts": [("Always",0),("Often",1),("Sometimes",2),("Rarely",3),("Never",4)]},
    {"q": "How often do you divide your day into time blocks?",
     "opts": [("Always",0),("Often",1),("Sometimes",2),("Rarely",3),("Never",4)]},
    {"q": "How clearly do you define tasks within each time block?",
     "opts": [("Very clearly",0),("Clearly",1),("Moderately",2),("Slightly",3),("Not at all",4)]},
    {"q": "How often do you follow your planned time blocks?",
     "opts": [("Always",0),("Often",1),("Sometimes",2),("Rarely",3),("Never",4)]},
    {"q": "How often do you switch between tasks while studying?",
     "opts": [("Never",0),("Rarely",1),("Sometimes",2),("Often",3),("Always",4)]},
    {"q": "How often are you distracted (e.g., phone use) during study?",
     "opts": [("Never",0),("Rarely",1),("Sometimes",2),("Often",3),("Always",4)]},
    {"q": "How difficult is it to refocus after distraction?",
     "opts": [("Not difficult",0),("Slightly difficult",1),("Moderately difficult",2),("Difficult",3),("Very difficult",4)]},
    {"q": "How engaged are you in academic activities?",
     "opts": [("Highly engaged",0),("Engaged",1),("Moderately engaged",2),("Slightly engaged",3),("Not engaged",4)]},
    {"q": "How often do you procrastinate on academic tasks?",
     "opts": [("Never",0),("Rarely",1),("Sometimes",2),("Often",3),("Always",4)]},
    {"q": "How confident are you in managing your academic workload?",
     "opts": [("Very confident",0),("Confident",1),("Moderately confident",2),("Slightly confident",3),("Not confident",4)]},
    {"q": "How effective is your schedule for completing tasks?",
     "opts": [("Very effective",0),("Effective",1),("Moderately effective",2),("Slightly effective",3),("Not effective",4)]},
    {"q": "How much does time blocking reduce distractions?",
     "opts": [("Very significantly",0),("Significantly",1),("Moderately",2),("Slightly",3),("Not at all",4)]},
    {"q": "How effective is time blocking in helping you meet deadlines?",
     "opts": [("Very effective",0),("Effective",1),("Moderately effective",2),("Slightly effective",3),("Not effective",4)]},
]

# 6 scoring states — total range 0–64
states = {
    "Excellent Control":      (0,  10),
    "Strong Performance":     (11, 20),
    "Moderate Effectiveness": (21, 32),
    "Low Effectiveness":      (33, 44),
    "Poor Time Management":   (45, 54),
    "Critical Level":         (55, 64),
}

icons = {
    "Excellent Control":      "🏆",
    "Strong Performance":     "✅",
    "Moderate Effectiveness": "👍",
    "Low Effectiveness":      "⚠️",
    "Poor Time Management":   "📌",
    "Critical Level":         "🚨",
}

# ---------------- VALIDATION ----------------

def validate_name(name: str) -> bool:
    # regex check — letters only, min 2 chars
    name = name.strip()
    if not NAME_PATTERN.match(name):
        return False
    # while loop — extra guard: no digits allowed
    i, is_valid = 0, True              # bool
    while i < len(name):               # while loop
        if name[i].isdigit():
            is_valid = False
            break
        i += 1
    return is_valid

def validate_dob(dob: str) -> bool:
    try:
        datetime.strptime(dob, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def validate_sid(sid: str) -> bool:
    if len(sid) < 4:
        return False
    for ch in sid:                     # for loop — digits only
        if not ch.isdigit():
            return False
    return True

def validate_record(record: dict) -> bool:
    # frozenset — check all required fields present
    return required_fields.issubset(frozenset(record.keys()))

def interpret_score(score: int) -> str:
    if score not in valid_score_range:  # range check
        return "Out of Range"
    for state, (lo, hi) in states.items():
        if lo <= score <= hi:
            return state
    return "Unknown"

def get_recommendation(score: int) -> str:
    if score <= 10: return "Highly effective time blocking and productivity."
    if score <= 20: return "Good scheduling with only minor improvements needed."
    if score <= 32: return "Some inconsistency — consider refining your structure."
    if score <= 44: return "Frequent distractions and weak structure need attention."
    if score <= 54: return "High multitasking and low control — start restructuring now."
    return "Severe lack of structure — urgent improvement needed."

# ---------------- STREAMLIT APP ----------------
st.set_page_config(page_title="Time Blocking Survey", page_icon="⏱️")
st.title("⏱️ Time Blocking & Schedule Effectiveness Survey")
st.info("Fill in your details below, then answer all 16 questions honestly.")

# --- User Details ---
name    = st.text_input("Given Name")
surname = st.text_input("Surname")
dob     = st.text_input("Date of Birth (YYYY-MM-DD)")
sid     = st.text_input("Student ID (min 4 digits)")

# --- Start Survey ---
if st.button("Start Survey"):

    # Collect and validate all inputs
    errors = []
    if not validate_name(name):    errors.append("❌ Name: letters only, min 2 characters.")
    if not validate_name(surname): errors.append("❌ Surname: letters only, min 2 characters.")
    if not validate_dob(dob):      errors.append("❌ Date of Birth must be in YYYY-MM-DD format.")
    if not validate_sid(sid):      errors.append("❌ Student ID must be at least 4 digits.")

    if errors:
        for e in errors:
            st.error(e)
    else:
        st.success("✅ Details valid. Answer all questions below.")
        st.divider()

        total_score = 0
        answers = []

        # Display all 16 questions
        for idx, q in enumerate(questions):
            opt_labels = [opt[0] for opt in q["opts"]]
            choice = st.radio(
                f"**Q{idx+1}.** {q['q']}",
                opt_labels,
                key=f"q{idx}",
                index=None,            # forces user to actively choose
                horizontal=False
            )
            if choice is not None:
                score = next(s for label, s in q["opts"] if label == choice)
                total_score += score
                answers.append({
                    "question":        q["q"],
                    "selected_option": choice,
                    "score":           score
                })

        st.divider()

        # Only show results when all questions answered
        if len(answers) == len(questions):

            result         = interpret_score(total_score)
            recommendation = get_recommendation(total_score)

            st.markdown(f"## {icons.get(result, '📊')} Result: {result}")
            st.markdown(f"**Total Score:** {total_score} / 64")
            st.info(recommendation)

            # Score legend — for loop over all 6 states
            st.markdown("### Score Guide")
            for state, (lo, hi) in states.items():
                marker = " ◀ **YOU**" if state == result else ""
                st.markdown(f"{icons[state]} **{lo}–{hi}:** {state}{marker}")

            st.divider()

            # Build full record
            record = {
                "name":           name,
                "surname":        surname,
                "dob":            dob,
                "student_id":     sid,
                "total_score":    total_score,
                "result":         result,
                "recommendation": recommendation,
                "answers":        answers,
                "version":        version_float
            }

            # frozenset check — all required fields must be in the record
            if not validate_record(record):
                st.error("Missing required fields in record.")
            else:
                # JSON preserves full nested structure — best for reloading results later
                json_str = json.dumps(record, indent=2)
                filename = f"{sid}_{name}_{surname}_result.json".replace(" ", "_")

                st.download_button(
                    label="💾 Download Result (JSON)",
                    data=json_str,
                    file_name=filename,
                    mime="application/json"
                )

                # CSV allows easy analysis in Excel/Sheets
                csv_rows = ["name,surname,dob,student_id,total_score,result"]
                csv_rows.append(f"{name},{surname},{dob},{sid},{total_score},{result}")
                csv_rows.append("")
                csv_rows.append("#,question,answer,score")
                for i, a in enumerate(answers, 1):   # for loop — build CSV rows
                    csv_rows.append(f'{i},"{a["question"]}","{a["selected_option"]}",{a["score"]}')
                csv_str = "\n".join(csv_rows)

                st.download_button(
                    label="📊 Download Result (CSV)",
                    data=csv_str,
                    file_name=filename.replace(".json", ".csv"),
                    mime="text/csv"
                )

                # TXT gives a human-readable printable report
                sep  = "=" * 50
                dash = "-" * 50
                txt_lines = [
                    sep, "  TIME BLOCKING SURVEY REPORT", sep,
                    f"  Name  : {name} {surname}",
                    f"  DOB   : {dob}",
                    f"  ID    : {sid}",
                    dash,
                    f"  Score : {total_score} / 64",
                    f"  Result: {result}",
                    f"  Note  : {recommendation}",
                    sep, "  ANSWERS", dash
                ]
                for i, a in enumerate(answers, 1):   # for loop — write each answer
                    txt_lines.append(f"  Q{i:02d}. {a['question']}")
                    txt_lines.append(f"       → {a['selected_option']} (score: {a['score']})")
                txt_lines.append(sep)
                txt_str = "\n".join(txt_lines)

                st.download_button(
                    label="📄 Download Result (TXT)",
                    data=txt_str,
                    file_name=filename.replace(".json", ".txt"),
                    mime="text/plain"
                )

        else:
            st.warning(f"Please answer all {len(questions)} questions to see your result. ({len(answers)}/{len(questions)} answered)")