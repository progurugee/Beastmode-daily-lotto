import streamlit as st
import pandas as pd
import random
import ast
from collections import Counter
from itertools import combinations
from io import StringIO

st.set_page_config(
    page_title="BEASTMODE DAILY LOTTO AI",
    page_icon="🎯",
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
p, label, .stMarkdown {
    color: #EEEEEE;
}
div.stButton > button {
    background-color: #D4AF37;
    color: #101010;
    font-weight: bold;
    border-radius: 10px;
    border: none;
    min-height: 45px;
}
div.stButton > button:hover {
    background-color: #F5D76E;
    color: black;
}
div[data-testid="stMetric"] {
    background: #202020;
    border: 1px solid #D4AF37;
    padding: 15px;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center;padding:20px;
background:linear-gradient(135deg,#171717,#29220D);
border:2px solid #D4AF37;border-radius:18px;">
<h1>👑 BEASTMODE</h1>
<h2>DAILY LOTTO AI</h2>
<p>HISTORICAL ANALYSIS • NUMBER GENERATOR • STATISTICS</p>
</div>
""", unsafe_allow_html=True)

st.write("")

st.info(
    "Daily Lotto is random. Historical statistics describe "
    "past draws and cannot predict winning numbers."
)

if "saved_combos" not in st.session_state:
    st.session_state.saved_combos = []

st.sidebar.title("👑 BEASTMODE MENU")
page = st.sidebar.radio(
    "Choose a section",
    [
        "🏠 Home",
        "🎯 Number Generator",
        "📊 Historical Analysis",
        "📂 Upload Results",
        "💾 Saved Combinations"
    ]
)

if "lotto_data" not in st.session_state:
    st.session_state.lotto_data = None


def parse_numbers(value):
    try:
        if isinstance(value, (list, tuple)):
            nums = list(value)
        else:
            text = str(value).strip()
            try:
                nums = ast.literal_eval(text)
                if not isinstance(nums, (list, tuple)):
                    nums = text.replace(",", " ").split()
            except (ValueError, SyntaxError):
                nums = text.replace(",", " ").split()

        nums = [int(n) for n in nums]
        nums = sorted(set(nums))

        if len(nums) == 5 and all(1 <= n <= 36 for n in nums):
            return nums
    except (ValueError, TypeError):
        pass

    return None


def get_history(df):
    if df is None or df.empty:
        return [], None

    cols = {str(c).strip().lower(): c for c in df.columns}

    number_col = None
    for name in ["numbers", "drawn_numbers", "winning_numbers"]:
        if name in cols:
            number_col = cols[name]
            break

    if number_col is not None:
        rows = []
        for value in df[number_col]:
            nums = parse_numbers(value)
            if nums:
                rows.append(nums)

        date_col = cols.get("date")
        latest_date = None
        if date_col:
            dates = pd.to_datetime(
                df[date_col], errors="coerce"
            ).dropna()
            if not dates.empty:
                latest_date = dates.max().date()

        return rows, latest_date

    # Also support CSVs with five separate number columns.
    for group in [
        ["n1", "n2", "n3", "n4", "n5"],
        ["number1", "number2", "number3", "number4", "number5"],
        ["ball1", "ball2", "ball3", "ball4", "ball5"]
    ]:
        if all(name in cols for name in group):
            rows = []
            for _, row in df.iterrows():
                nums = parse_numbers(
                    [row[cols[name]] for name in group]
                )
                if nums:
                    rows.append(nums)
            return rows, None

    return [], None


def analyse_draws(draws):
    freq = Counter(n for draw in draws for n in draw)
    pairs = Counter(
        pair
        for draw in draws
        for pair in combinations(sorted(draw), 2)
    )

    overdue = {}
    for n in range(1, 37):
        overdue[n] = next(
            (
                i for i, draw in enumerate(draws)
                if n in draw
            ),
            len(draws)
        )

    return freq, pairs, overdue


if page == "🏠 Home":
    st.subheader("📊 Your Dashboard")

    draws, latest_date = get_history(
        st.session_state.lotto_data
    )

    c1, c2, c3 = st.columns(3)

    c1.metric("Historical Draws", len(draws))
    c2.metric("Numbers Per Draw", 5)
    c3.metric("Possible Combinations", "376,992")

    st.markdown("### 🎯 Welcome to BEASTMODE")

    st.write(
        "Generate combinations, explore historical results, "
        "and study number frequencies and pairs."
    )

    st.markdown("### ⚡ Quick Start")

    st.write("1. Open Number Generator to create combinations.")
    st.write("2. Upload a CSV to analyse historical results.")
    st.write("3. Open Historical Analysis to view statistics.")
    st.write("4. Save combinations you want to keep.")

    if latest_date:
        st.caption(f"Latest date found in uploaded data: {latest_date}")

    st.warning(
        "This tool is for analysis and entertainment. "
        "It does not increase your chance of winning."
    )


elif page == "🎯 Number Generator":
    st.subheader("🎯 BEASTMODE Number Generator")

    quantity = st.selectbox(
        "How many combinations?",
        [5, 10, 20, 50]
    )

    mode = st.selectbox(
        "Generation mode",
        [
            "Random combinations",
            "Rank by historical score"
        ]
    )

    draws, _ = get_history(st.session_state.lotto_data)
    freq, pairs, overdue = analyse_draws(draws)

    if st.button("🔥 GENERATE COMBINATIONS"):
        all_combos = set()

        if mode == "Rank by historical score" and draws:
            pool = set()

            # Generate random candidates and rank them.
            for _ in range(4000):
                combo = tuple(sorted(
                    random.sample(range(1, 37), 5)
                ))
                pool.add(combo)

            def score(combo):
                frequency_score = sum(
                    freq[n] for n in combo
                )
                pair_score = sum(
                    pairs[tuple(sorted(pair))]
                    for pair in combinations(combo, 2)
                )
                overdue_score = sum(
                    min(overdue[n], 20) for n in combo
                )
                return (
                    frequency_score
                    + 0.5 * pair_score
                    + 0.25 * overdue_score
                )

            all_combos = sorted(
                pool,
                key=score,
                reverse=True
            )[:quantity]

        else:
            while len(all_combos) < quantity:
                all_combos.add(tuple(sorted(
                    random.sample(range(1, 37), 5)
                )))

            all_combos = list(all_combos)

        if not isinstance(all_combos, list):
            all_combos = list(all_combos)

        st.session_state.current_combos = all_combos
        st.session_state.current_mode = mode

    combos = st.session_state.get("current_combos", [])

    if combos:
        st.markdown("### 🏆 Your Combinations")

        output = []

        for i, combo in enumerate(combos, 1):
            st.markdown(
                f"**Combination {i}**"
            )

            circles = "".join(
                f"""<span style="
                display:inline-flex;
                align-items:center;
                justify-content:center;
                background:#D4AF37;
                color:#111;
                width:43px;
                height:43px;
                border-radius:50%;
                margin:4px;
                font-weight:bold;
                font-size:16px;
                ">{n:02d}</span>"""
                for n in combo
            )

            st.markdown(
                circles,
                unsafe_allow_html=True
            )

            output
