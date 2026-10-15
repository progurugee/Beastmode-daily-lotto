import streamlit as st
import pandas as pd
import random
import re
from collections import Counter
from itertools import combinations
from io import StringIO

st.set_page_config(
    page_title="BEASTMODE DAILY LOTTO AI",
    page_icon="🎯",
    layout="wide"
)

# ==============================
# BEASTMODE BLACK & GOLD THEME
# ==============================

st.markdown("""
<style>
.stApp {
    background-color: #101010;
    color: #FFFFFF;
}
h1, h2, h3 {
    color: #D4AF37 !important;
}
section[data-testid="stSidebar"] {
    background-color: #1B1B1B;
}
section[data-testid="stSidebar"] * {
    color: #FFFFFF;
}
.stButton > button {
    background-color: #D4AF37;
    color: #101010;
    border-radius: 10px;
    border: none;
    font-weight: bold;
    width: 100%;
}
.stButton > button:hover {
    background-color: #F5D76E;
    color: #000000;
}
div[data-testid="stMetric"] {
    background-color: #202020;
    border: 1px solid #D4AF37;
    padding: 12px;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# ==============================
# SESSION DATA
# ==============================

if "lotto_data" not in st.session_state:
    st.session_state.lotto_data = None

if "saved_combos" not in st.session_state:
    st.session_state.saved_combos = []

if "generated_combo" not in st.session_state:
    st.session_state.generated_combo = []

# ==============================
# HEADER
# ==============================

st.markdown("""
<div style="
    text-align:center;
    padding:20px;
    background:linear-gradient(135deg,#171717,#292929);
    border:2px solid #D4AF37;
    border-radius:18px;">
    <h1>👑 BEASTMODE</h1>
    <h2>DAILY LOTTO AI</h2>
    <p>NUMBER GENERATOR • HISTORICAL ANALYSIS • STATISTICS</p>
</div>
""", unsafe_allow_html=True)

st.info(
    "Lottery draws are random. This app analyses historical results "
    "and generates combinations, but cannot predict winning numbers."
)

# ==============================
# MENU
# ==============================

st.sidebar.title("👑 BEASTMODE MENU")

page = st.sidebar.radio(
    "Choose a section",
    [
        "🏠 Home",
        "🎯 Number Generator",
        "📂 Upload Results",
        "📊 Historical Analysis",
        "🔥 Hot & Overdue Numbers",
        "🔗 Number Pairs",
        "💾 Saved Combinations"
    ],
    key="main_menu"
)

# ==============================
# HELPER FUNCTIONS
# ==============================

def get_numbers(value):
    """Extract valid Daily Lotto numbers from a value."""
    if isinstance(value, (list, tuple)):
        raw = list(value)
    else:
        raw = re.findall(r"\d+", str(value))

    numbers = []

    for item in raw:
        try:
            number = int(item)
            if 1 <= number <= 36:
                numbers.append(number)
        except (TypeError, ValueError):
            continue

    return numbers


def load_draws(data):
    """Convert uploaded data into a list of lottery draws."""
    if data is None or data.empty:
        return []

    draws = []

    for _, row in data.iterrows():
        numbers = []

        for value in row.tolist():
            numbers.extend(get_numbers(value))

        numbers = sorted(set(numbers))

        if len(numbers) == 5:
            draws.append(numbers)

    return draws


def get_frequency(draws):
    """Count how often each number appears."""
    frequency = Counter()

    for draw in draws:
        frequency.update(draw)

    return frequency


def make_combination():
    """Generate five distinct numbers from 1 to 36."""
    return sorted(random.sample(range(1, 37), 5))# ==============================
# HOME DASHBOARD
# ==============================

if page == "🏠 Home":
    st.subheader("📊 Your Dashboard")

    draws = load_draws(st.session_state.lotto_data)

    col1, col2, col3 = st.columns(3)

    col1.metric("Historical Draws", len(draws))
    col2.metric("Numbers Per Draw", 5)
    col3.metric("Possible Combinations", "376,992")

    st.markdown("### 👑 Welcome to BEASTMODE")

    st.write(
        "Use the menu to generate combinations, upload historical "
        "results, and explore statistics from previous draws."
    )

    if draws:
        st.success("Historical results are loaded and ready for analysis.")
    else:
        st.warning(
            "No historical results loaded yet. Open Upload Results "
            "to import a CSV file."
        )

    st.markdown("### 🎯 Quick Number Generator")

    if st.button("Generate a Combination", key="home_generate"):
        combo = make_combination()
        st.session_state.generated_combo = combo

    if st.session_state.generated_combo:
        st.markdown(
            "## " + "  •  ".join(
                str(n) for n in st.session_state.generated_combo
            )
        )


# ==============================
# NUMBER GENERATOR
# ==============================

elif page == "🎯 Number Generator":
    st.subheader("🎯 Daily Lotto Number Generator")

    st.write("Generate five different numbers from 1 to 36.")

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

        st.write("")

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
        "Generated numbers are random and do not have a higher "
        "chance of winning than other valid combinations."
    )


# ==============================
# UPLOAD HISTORICAL RESULTS
# ==============================

elif page == "📂 Upload Results":
    st.subheader("📂 Upload Historical Results")

    st.write(
        "Upload a CSV file containing past Daily Lotto results. "
        "Each row should contain the five numbers from one draw."
    )

    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=["csv"],
        key="lotto_csv_upload"
    )

    if uploaded_file is not None:
        try:
            uploaded_data = pd.read_csv(uploaded_file)

            st.write("### Preview of your file")
            st.dataframe(uploaded_data.head(10), use_container_width=True)

            st.write("### Select the five number columns")

            columns = list(uploaded_data.columns)

            selected_columns = st.multiselect(
                "Choose the columns containing the drawn numbers",
                options=columns,
                default=columns[-5:] if len(columns) >= 5 else columns,
                key="selected_number_columns"
            )

            if st.button("Load Historical Results", key="load_history"):
                if len(selected_columns) != 5:
                    st.error(
                        "Please select exactly five columns containing "
                        "the drawn numbers."
                    )
                else:
                    number_data = uploaded_data[selected_columns].copy()

                    valid_rows = []

                    for _, row in number_data.iterrows():
                        numbers = []

                        for value in row.tolist():
                            numbers.extend(get_numbers(value))

                        if len(numbers) == 5 and len(set(numbers)) == 5:
                            if all(1 <= n <= 36 for n in numbers):
                                valid_rows.append(sorted(numbers))

                    if valid_rows:
                        st.session_state.lotto_data = pd.DataFrame(
                            valid_rows,
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
                            "No valid draws were found. Check that you "
                            "selected the five number columns correctly."
                        )

        except Exception as error:
            st.error(f"Could not read this CSV file: {error}")

    if st.session_state.lotto_data is not None:
        st.info(
            f"{len(st.session_state.lotto_data)} historical draws "
            "are currently loaded in this session."
        )# ==============================
# HISTORICAL ANALYSIS
# ==============================

elif page == "📊 Historical Analysis":
    st.subheader("📊 Historical Number Analysis")

    draws = load_draws(st.session_state.lotto_data)

    if not draws:
        st.warning(
            "No historical results loaded. Open Upload Results "
            "and upload your CSV file first."
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
                "Times Drawn", ascending=False
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


# ==============================
# HOT & OVERDUE NUMBERS
# ==============================

elif page == "🔥 Hot & Overdue Numbers":
    st.subheader("🔥 Hot & Overdue Numbers")

    draws = load_draws(st.session_state.lotto_data)

    if not draws:
        st.warning(
            "Upload historical results first to view number statistics."
        )
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
                (number, last_seen if last_seen is not None else len(draws))
            )

        overdue_numbers.sort(key=lambda item: (-item[1], item[0]))

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 🔥 Most Frequently Drawn")
            st.write(
                ", ".join(str(n) for n in hot_numbers)
            )

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

        st.markdown("### Overdue Statistics")

        st.dataframe(
            overdue_table,
            use_container_width=True,
            hide_index=True
        )

        st.caption(
            "Hot and overdue labels describe past results only. "
            "They do not make a number more or less likely in the next draw."
        )


# ==============================
# NUMBER PAIRS
# ==============================

elif page == "🔗 Number Pairs":
    st.subheader("🔗 Number Pair Analysis")

    draws = load_draws(st.session_state.lotto_data)

    if not draws:
        st.warning(
            "Upload historical results first to analyse number pairs."
        )
    else:
        pair_frequency = Counter()

        for draw in draws:
            pair_frequency.update(combinations(sorted(draw), 2))

        top_pairs = pair_frequency.most_common(30)

        if top_pairs:
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
            "Pairs that appeared together in the past are not guaranteed "
            "to appear together again."
        )


# ==============================
# SAVED COMBINATIONS
# ==============================

elif page == "💾 Saved Combinations":
    st.subheader("💾 Saved Combinations")

    saved = st.session_state.saved_combos

    if not saved:
        st.info(
            "You haven't saved any combinations yet. Open Number Generator "
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

        if st.button("Clear Saved Combinations", key="clear_saved"):
            st.session_state.saved_combos = []
            st.success("Saved combinations cleared.")
            st.rerun()


# ==============================
# FOOTER
# ==============================

st.sidebar.markdown("---")
st.sidebar.caption("BEASTMODE DAILY LOTTO AI")
st.sidebar.caption("Version 2.0")
st.sidebar.caption("For analysis and entertainment.")
