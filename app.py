import streamlit as st
import pandas as pd
import random
import re
from collections import Counter
from itertools import combinations
from io import BytesIO

from PIL import Image

try:
    from rapidocr_onnxruntime import RapidOCR
except ImportError:
    RapidOCR = None


# ==========================================
# BEASTMODE DAILY LOTTO AI
# ==========================================

st.set_page_config(
    page_title="BEASTMODE DAILY LOTTO AI",
    page_icon="👑",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background-color: #101010;
    color: white;
}
h1, h2, h3 {
    color: #D4AF37 !important;
}
section[data-testid="stSidebar"] {
    background-color: #1B1B1B;
}
section[data-testid="stSidebar"] * {
    color: white;
}
.stButton > button {
    background-color: #D4AF37;
    color: #101010;
    border-radius: 10px;
    font-weight: bold;
    width: 100%;
}
.stButton > button:hover {
    background-color: #F5D76E;
    color: black;
}
div[data-testid="stMetric"] {
    background-color: #202020;
    border: 1px solid #D4AF37;
    padding: 12px;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)


# ==========================================
# SESSION DATA
# ==========================================

if "lotto_data" not in st.session_state:
    st.session_state.lotto_data = None

if "saved_combos" not in st.session_state:
    st.session_state.saved_combos = []

if "generated_combo" not in st.session_state:
    st.session_state.generated_combo = []

if "detected_draws" not in st.session_state:
    st.session_state.detected_draws = []

if "ocr_text" not in st.session_state:
    st.session_state.ocr_text = ""


# ==========================================
# HEADER
# ==========================================

st.markdown("""
<div style="
    text-align:center;
    padding:20px;
    background:linear-gradient(135deg,#171717,#292929);
    border:2px solid #D4AF37;
    border-radius:18px;">
    <h1>👑 BEASTMODE</h1>
    <h2>DAILY LOTTO AI</h2>
    <p>NUMBER GENERATOR • IMAGE READER • HISTORICAL ANALYSIS</p>
</div>
""", unsafe_allow_html=True)

st.info(
    "Lottery draws are random. BEASTMODE analyses historical results "
    "and generates possible combinations. It cannot guarantee or "
    "predict winning numbers."
)


# ==========================================
# MENU
# ==========================================

st.sidebar.title("👑 BEASTMODE MENU")

page = st.sidebar.radio(
    "Choose a section",
    [
        "🏠 Home",
        "🎯 Number Generator",
        "📸 Upload Results",
        "📊 Historical Analysis",
        "🔥 Hot & Overdue Numbers",
        "🔗 Number Pairs",
        "💾 Saved Combinations"
    ],
    key="main_menu"
)


# ==========================================
# HELPER FUNCTIONS
# ==========================================

def get_numbers(value, maximum=36):
    """Extract valid lottery numbers from text or numeric cells."""
    if isinstance(value, (int, float)):
        try:
            number = int(value)
            if float(value) == number and 1 <= number <= maximum:
                return [number]
        except (ValueError, TypeError, OverflowError):
            return []
        return []

    if isinstance(value, (list, tuple)):
        raw = value
    else:
        raw = re.findall(r"\d+", str(value))

    numbers = []

    for item in raw:
        try:
            number = int(item)
            if 1 <= number <= maximum:
                numbers.append(number)
        except (ValueError, TypeError):
            continue

    return numbers


def make_combination():
    return sorted(random.sample(range(1, 37), 5))


def get_frequency(draws):
    frequency = Counter()

    for draw in draws:
        frequency.update(draw)

    return frequency


def load_draws(data):
    if data is None or data.empty:
        return []

    draws = []

    for _, row in data.iterrows():
        numbers = []

        for value in row.tolist():
            numbers.extend(get_numbers(value))

        if len(numbers) == 5 and len(set(numbers)) == 5:
            if all(1 <= n <= 36 for n in numbers):
                draws.append(sorted(numbers))

    return draws


def recognise_image(image):
    """Read text from an uploaded picture using RapidOCR."""
    if RapidOCR is None:
        raise RuntimeError(
            "The image-reading package is not installed. "
            "Please update requirements.txt and redeploy the app."
        )

    engine = RapidOCR()
    results, _ = engine(image)

    if not results:
        return []

    return results


def numbers_from_ocr(results):
    """
    Collect possible five-number rows from OCR results.
    The user must verify the results before loading them.
    """
    entries = []

    for result in results:
        try:
            box, text, score = result
            text = str(text).strip()

            if not text:
                continue

            y_center = sum(point[1] for point in box) / len(box)
            x_center = sum(point[0] for point in box) / len(box)

            entries.append({
                "text": text,
                "x": x_center,
                "y": y_center
            })

        except (ValueError, TypeError, IndexError):
            continue

    if not entries:
        return [], ""

    entries.sort(key=lambda item: item["y"])

    rows = []

    for entry in entries:
        placed = False

        for row in rows:
            if abs(entry["y"] - row["y"]) < 25:
                row["items"].append(entry)
                row["y"] = sum(
                    item["y"] for item in row["items"]
                ) / len(row["items"])
                placed = True
                break

        if not placed:
            rows.append({
                "y": entry["y"],
                "items": [entry]
            })

    detected_draws = []
    full_text = []

    for row in rows:
        row["items"].sort(key=lambda item: item["x"])
        row_text = " ".join(item["text"] for item in row["items"])
        full_text.append(row_text)

        numbers = []

        for item in row["items"]:
            numbers.extend(get_numbers(item["text"]))

        # A row must contain exactly five distinct valid numbers.
        if len(numbers) == 5 and len(set(numbers)) == 5:
            detected_draws.append(sorted(numbers))

    return detected_draws, "\n".join(full_text)


# ==========================================
# HOME
# ==========================================

if page == "🏠 Home":

    st.subheader("📊 Your Dashboard")

    draws = load_draws(st.session_state.lotto_data)

    col1, col2, col3 = st.columns(3)

    col1.metric("Historical Draws", len(draws))
    col2.metric("Numbers Per Draw", 5)
    col3.metric("Possible Combinations", "376,992")

    st.markdown("### 👑 Welcome to BEASTMODE")

    st.write(
        "Upload a picture of historical results, explore previous "
        "draws, and generate possible number combinations."
    )

    if draws:
        st.success(
            f"{len(draws)} historical draws are ready for analysis."
        )
    else:
        st.warning(
            "No historical results loaded yet. Open Upload Results "
            "to add a screenshot or CSV file."
        )

    st.markdown("### 🎯 Quick Number Generator")

    if st.button("Generate a Combination", key="home_generate"):
        st.session_state.generated_combo = make_combination()

    if st.session_state.generated_combo:
        st.markdown(
            "## " + "  •  ".join(
                str(n) for n in st.session_state.generated_combo
            )
        )


# ==========================================
# NUMBER GENERATOR
# ==========================================

elif page == "🎯 Number Generator":

    st.subheader("🎯 Daily Lotto Number Generator")

    st.write("Generate five different numbers between 1 and 36.")

    if st.button("Generate Numbers", key="generator_button"):
        st.session_state.generated_combo = make_combination()

    if st.session_state.generated_combo:

        st.markdown("### Your Combination")

        cols = st.columns(5)

        for index, number in enumerate(
            st.session_state.generated_combo
        ):
            cols[index].markdown(
                f"""
                <div style="
                    text-align:center;
                    background:#D4AF37;
                    color:#101010;
                    padding:18px 5px;
                    border-radius:50%;
                    font-size:24px;
                    font-weight:bold;">
                    {number}
                </div>
                """,
                unsafe_allow_html=True
            )

        combination_text = ",".join(
            str(n) for n in st.session_state.generated_combo
        )

        st.download_button(
            "Download Combination",
            data=combination_text,
            file_name="beastmode_combination.csv",
            mime="text/csv"
        )

        if st.button("Save This Combination", key="save_generator"):

            if st.session_state.generated_combo not in (
                st.session_state.saved_combos
            ):
                st.session_state.saved_combos.append(
                    st.session_state.generated_combo.copy()
                )
                st.success("Combination saved!")

            else:
                st.info("This combination is already saved.")

    st.caption(
        "Every valid combination has the same chance in a fair draw. "
        "Generated numbers are possibilities, not predictions."
    )


# ==========================================
# UPLOAD RESULTS: IMAGE OR CSV
# ==========================================

elif page == "📸 Upload Results":

    st.subheader("📸 Upload Lotto Results")

    st.write(
        "Take a screenshot of previous lottery results or choose "
        "a picture from your phone gallery."
    )

    upload_type = st.radio(
        "Choose how to upload",
        ["📸 Screenshot or Picture", "📄 CSV File"],
        key="upload_type"
    )

    # --------------------------------------
    # IMAGE UPLOAD
    # --------------------------------------

    if upload_type == "📸 Screenshot or Picture":

        uploaded_image = st.file_uploader(
            "Choose a picture from your phone",
            type=["jpg", "jpeg", "png"],
            key="image_upload"
        )

        if uploaded_image is not None:

            try:
                image = Image.open(uploaded_image).convert("RGB")

                st.markdown("### 👀 Picture Preview")

                st.image(
                    image,
                    caption="Check that the lottery numbers are readable.",
                    use_container_width=True
                )

                if st.button("🔍 Read Numbers From Picture"):

                    with st.spinner(
                        "BEASTMODE is reading the picture..."
                    ):
                        results = recognise_image(image)

                        detected, recognised_text = numbers_from_ocr(
                            results
                        )

                        st.session_state.detected_draws = detected
                        st.session_state.ocr_text = recognised_text

                if st.session_state.ocr_text:

                    st.markdown("### 🔎 Recognised Text")
                    st.text(st.session_state.ocr_text)

                if st.session_state.detected_draws:

                    st.markdown("### ✅ Check Detected Number Rows")

                    st.warning(
                        "Check every number carefully. Only confirm "
                        "official results from a completed draw. "
                        "Your own ticket numbers are not historical "
                        "winning results."
                    )

                    corrected_draws = []

                    for index, draw in enumerate(
                        st.session_state.detected_draws
                    ):
                        st.write(f"Detected row {index + 1}")

                        cols = st.columns(5)
                        corrected = []

                        for j, number in enumerate(draw):
                            corrected_number = cols[j].number_input(
                                f"Number {j + 1}",
                                min_value=1,
                                max_value=36,
                                value=int(number),
                                key=f"image_{index}_{j}"
                            )
                            corrected.append(corrected_number)

                        corrected_draws.append(corrected)

                    if st.button(
                        "✅ Confirm and Load Historical Results"
                    ):

                        valid = all(
                            len(set(draw)) == 5
                            for draw in corrected_draws
                        )

                        if not valid:
                            st.error(
                                "Each row must contain five different numbers."
                            )
                        else:
                            existing = load_draws(
                                st.session_state.lotto_data
                            )

                            combined = existing + [
                                sorted(draw) for draw in corrected_draws
                            ]

                            st.session_state.lotto_data = pd.DataFrame(
                                combined,
                                columns=[
                                    "Number 1",
                                    "Number 2",
                                    "Number 3",
                                    "Number 4",
                                    "Number 5"
                                ]
                            )

                            st.success(
                                f"Loaded {len(corrected_draws)} rows. "
                                "Historical analysis is now updated."
                            )

                            st.session_state.detected_draws = []
                            st.session_state.ocr_text = ""

                elif st.session_state.ocr_text:
                    st.warning(
                        "BEASTMODE could not confidently find rows "
                        "of exactly five numbers. Try a clearer picture "
                        "or use the CSV option."
                    )

            except Exception as error:
                st.error(f"Could not read this picture: {error}")

    # --------------------------------------
    # CSV UPLOAD
    # --------------------------------------

    else:

        st.write(
            "CSV is an optional alternative for users who already "
            "have historical results in a spreadsheet."
        )

        uploaded_file = st.file_uploader(
            "Choose a CSV file",
            type=["csv"],
            key="csv_upload"
        )

        if uploaded_file is not None:

            try:
                uploaded_data = pd.read_csv(uploaded_file)

                st.markdown("### Preview of your file")

                st.dataframe(
                    uploaded_data.head(10),
                    use_container_width=True
                )

                columns = list(uploaded_data.columns)

                selected_columns = st.multiselect(
                    "Choose the five columns containing the drawn numbers",
                    options=columns,
                    default=columns[-5:] if len(columns) >= 5 else columns
                )

                if st.button("Load Historical Results", key="load_csv"):

                    if len(selected_columns) != 5:

                        st.error(
                            "Please select exactly five number columns."
                        )

                    else:

                        valid_rows = []

                        for _, row in uploaded_data[
                            selected_columns
                        ].iterrows():

                            numbers = []

                            for value in row.tolist():
                                numbers.extend(get_numbers(value))

                            if (
                                len(numbers) == 5
                                and len(set(numbers)) == 5
                                and all(1 <= n <= 36 for n in numbers)
                            ):
                                valid_rows.append(sorted(numbers))

                        if valid_rows:

                            existing = load_draws(
                                st.session_state.lotto_data
                            )

                            combined = existing + valid_rows

                            st.session_state.lotto_data = pd.DataFrame(
                                combined,
                                columns=[
                                    "Number 1",
                                    "Number 2",
                                    "Number 3",
                                    "Number 4",
                                    "Number 5"
                                ]
                            )

                            st.success(
                                f"Successfully loaded {len(valid_rows)} "
                                "historical draws!"
                            )

                        else:

                            st.error(
                                "No valid rows were found. Check your "
                                "selected columns and CSV file."
                            )

            except Exception as error:
                st.error(f"Could not read the CSV file: {error}")

    if st.session_state.lotto_data is not None:

        st.info(
            f"{len(st.session_state.lotto_data)} historical rows "
            "are currently loaded in this session."
        )


# ==========================================
# HISTORICAL ANALYSIS
# ==========================================

elif page == "📊 Historical Analysis":

    st.subheader("📊 Historical Number Analysis")

    draws = load_draws(st.session_state.lotto_data)

    if not draws:

        st.warning(
            "No historical results loaded. Upload confirmed results first."
        )

    else:

        frequency = get_frequency(draws)

        analysis = pd.DataFrame({
            "Number": list(range(1, 37)),
            "Times Drawn": [
                frequency.get(n, 0) for n in range(1, 37)
            ]
        })

        analysis["Percentage of Draws"] = (
            analysis["Times Drawn"] / len(draws) * 100
        ).round(2)

        st.metric("Draws Analysed", len(draws))

        st.markdown("### Number Frequencies")

        st.bar_chart(
            analysis.set_index("Number")["Times Drawn"]
        )

        st.dataframe(
            analysis.sort_values(
                "Times Drawn",
                ascending=False
            ),
            use_container_width=True,
            hide_index=True
        )

        st.download_button(
            "Download Frequency Report",
            data=analysis.to_csv(index=False),
            file_name="beastmode_frequency_report.csv",
            mime="text/csv"
        )


# ==========================================
# HOT AND OVERDUE NUMBERS
# ==========================================

elif page == "🔥 Hot & Overdue Numbers":

    st.subheader("🔥 Hot & Overdue Numbers")

    draws = load_draws(st.session_state.lotto_data)

    if not draws:

        st.warning("Upload historical results first.")

    else:

        frequency = get_frequency(draws)

        hot_numbers = sorted(
            range(1, 37),
            key=lambda n: (-frequency.get(n, 0), n)
        )[:10]

        overdue_numbers = []

        for number in range(1, 37):

            last_seen = None

            for index, draw in enumerate(reversed(draws)):

                if number in draw:
                    last_seen = index
                    break

            overdue_numbers.append(
                (
                    number,
                    last_seen if last_seen is not None else len(draws)
                )
            )

        overdue_numbers.sort(
            key=lambda item: (-item[1], item[0])
        )

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 🔥 Frequently Drawn")
            st.write(", ".join(str(n) for n in hot_numbers))

        with col2:
            st.markdown("### ⏳ Longest Since Appearing")
            st.write(
                ", ".join(
                    str(number)
                    for number, _ in overdue_numbers[:10]
                )
            )

        overdue_table = pd.DataFrame(
            overdue_numbers,
            columns=["Number", "Draws Since Last Seen"]
        )

        st.dataframe(
            overdue_table,
            use_container_width=True,
            hide_index=True
        )

        st.caption(
            "These statistics describe previous results. They do not "
            "make a number more likely to appear in the next draw."
        )


# ==========================================
# NUMBER PAIRS
# ==========================================

elif page == "🔗 Number Pairs":

    st.subheader("🔗 Number Pair Analysis")

    draws = load_draws(st.session_state.lotto_data)

    if not draws:

        st.warning("Upload historical results first.")

    else:

        pair_frequency = Counter()

        for draw in draws:
            pair_frequency.update(combinations(sorted(draw), 2))

        top_pairs = pair_frequency.most_common(30)

        pair_table = pd.DataFrame([
            {
                "Number Pair": f"{pair[0]} + {pair[1]}",
                "Times Together": count
            }
            for pair, count in top_pairs
        ])

        st.markdown("### Most Common Historical Pairs")

        st.dataframe(
            pair_table,
            use_container_width=True,
            hide_index=True
        )

        st.download_button(
            "Download Pair Report",
            data=pair_table.to_csv(index=False),
            file_name="beastmode_number_pairs.csv",
            mime="text/csv"
        )

        st.caption(
            "Past pairs do not guarantee future results."
        )


# ==========================================
# SAVED COMBINATIONS
# ==========================================

elif page == "💾 Saved Combinations":

    st.subheader("💾 Saved Combinations")

    saved = st.session_state.saved_combos

    if not saved:

        st.info(
            "No combinations saved yet. Open Number Generator "
            "and tap Save This Combination."
        )

    else:

        st.success(f"You have saved {len(saved)} combination(s).")

        for index, combo in enumerate(saved, start=1):

            st.write(
                f"**Combination {index}:** "
                + "  •  ".join(str(n) for n in combo)
            )

        saved_data = pd.DataFrame(
            saved,
            columns=[
                "Number 1",
                "Number 2",
                "Number 3",
                "Number 4",
                "Number 5"
            ]
        )

        st.download_button(
            "Download Saved Combinations",
            data=saved_data.to_csv(index=False),
            file_name="beastmode_saved_combinations.csv",
            mime="text/csv"
        )

        if st.button("Clear Saved Combinations"):

            st.session_state.saved_combos = []

            st.success("Saved combinations cleared.")

            st.rerun()


# ==========================================
# FOOTER
# ==========================================

st.sidebar.markdown("---")
st.sidebar.caption("👑 BEASTMODE DAILY LOTTO AI")
st.sidebar.caption("Screenshot + CSV Support")
st.sidebar.caption("For analysis and entertainment.")
