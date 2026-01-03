import streamlit as st
import pandas as pd
from fpdf import FPDF
import base64
import io

# ────────────────────────────────
# Session state
# ────────────────────────────────
if 'data' not in st.session_state:
    st.session_state.data = {}

# Minimal set of categories (expand as needed)
CATEGORIES = [
    'real_estate',
    'cash_checking',
    'bitcoin',
    'stocks',
    'retirement_accounts',
    'vehicles',
    'personal_property',
    'digital_assets'
]

for cat in CATEGORIES:
    if cat not in st.session_state.data:
        st.session_state.data[cat] = []

st.title("Asset Inventory – Fixed Version")

# ────────────────────────────────
# Field definition per category
# ────────────────────────────────
def get_fields(cat):
    base = {
        'description': 'text',
        'value': 'number',
        'notes': 'textarea'
    }
    extras = {
        'real_estate':     {'address': 'text'},
        'cash_checking':   {'bank': 'text', 'account': 'text'},
        'bitcoin':         {'wallet': 'text', 'amount': 'number'},
        'stocks':          {'ticker': 'text', 'shares': 'number'},
        'vehicles':        {'make_model': 'text', 'year': 'number'}
    }
    return {**base, **extras.get(cat, {})}

# ────────────────────────────────
# Add form – every single widget has UNIQUE key
# ────────────────────────────────
def add_form(category):
    fields = get_fields(category)

    with st.expander(f"Add → {category.replace('_', ' ').title()}", expanded=False):
        entry = {}

        for fname, ftype in fields.items():
            label = fname.replace('_', ' ').title()
            key_base = f"{category}__{fname}"

            if ftype == 'text':
                entry[fname] = st.text_input(
                    label,
                    key=f"txt__{key_base}"
                )
            elif ftype == 'number':
                entry[fname] = st.number_input(
                    label,
                    min_value=0.0,
                    step=0.01,
                    key=f"num__{key_base}"
                )
            elif ftype == 'textarea':
                entry[fname] = st.text_area(
                    label,
                    height=68,
                    key=f"area__{key_base}"
                )

        # Save button – unique per category
        if st.button("Save entry", key=f"save__{category}", type="primary"):
            # Very minimal validation
            if any(v for v in entry.values() if v not in (None, "", 0.0)):
                st.session_state.data[category].append(entry)
                st.success("Saved ✓")
                st.rerun()
            else:
                st.error("Fill at least one field")

# ────────────────────────────────
# Show & delete entries
# ────────────────────────────────
def show_entries(category):
    items = st.session_state.data.get(category, [])
    if not items:
        return

    st.markdown(f"**{category.replace('_', ' ').title()}** ({len(items)})")

    for idx, item in enumerate(items):
        with st.container(border=True):
            col1, col2 = st.columns([8,2])
            with col1:
                st.json(item)
            with col2:
                if st.button("×", key=f"del__{category}__{idx}", help="Delete"):
                    del st.session_state.data[category][idx]
                    st.rerun()

# ────────────────────────────────
# Layout – simple columns (you can change to tabs)
# ────────────────────────────────
st.write("Add your assets in any category:")

cols = st.columns(3)
for i, category in enumerate(CATEGORIES):
    with cols[i % 3]:
        add_form(category)
        show_entries(category)

# ────────────────────────────────
# Export
# ────────────────────────────────
st.divider()

all_rows = []
for cat, entries in st.session_state.data.items():
    for entry in entries:
        row = entry.copy()
        row['category'] = cat
        all_rows.append(row)

if all_rows:
    df = pd.DataFrame(all_rows)

    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV", csv, "inventory.csv", "text/csv")

    # Very minimal PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, "Asset Inventory", ln=True, align="C")

    for cat, group in df.groupby("category"):
        pdf.ln(5)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, cat.replace('_', ' ').title(), ln=True)
        pdf.set_font("Arial", size=10)
        pdf.multi_cell(0, 6, group.drop("category", axis=1).to_string(index=False))

    pdf_bytes = pdf.output(dest='S').encode('latin-1')
    b64 = base64.b64encode(pdf_bytes).decode()
    st.markdown(
        f'<a href="data:application/pdf;base64,{b64}" download="inventory.pdf">Download PDF</a>',
        unsafe_allow_html=True
    )
else:
    st.info("No data yet")
