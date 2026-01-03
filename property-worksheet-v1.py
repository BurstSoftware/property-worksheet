import streamlit as st
import pandas as pd
from fpdf import FPDF
import base64
import io

# ────────────────────────────────
# Session state
# ────────────────────────────────
if 'assets' not in st.session_state:
    st.session_state.assets = {}

# List of categories you want (add/remove as needed)
CATEGORIES = [
    'real_estate',
    'cash_checking',
    'bitcoin',
    'stocks',
    'retirement',
    'vehicles',
    'jewelry_collectibles',
    'digital_accounts',
    'business'
]

# Initialize empty lists
for cat in CATEGORIES:
    if cat not in st.session_state.assets:
        st.session_state.assets[cat] = []

st.title("Simple Asset Inventory")

# ────────────────────────────────
# Very simple field definition per category
# You can expand later
# ────────────────────────────────
def get_fields(category):
    common = {
        'description': 'text',
        'value_usd': 'number',
        'notes': 'textarea'
    }

    specifics = {
        'real_estate': {'address': 'text'},
        'cash_checking': {'bank': 'text', 'account_last4': 'text'},
        'bitcoin': {'wallet': 'text', 'amount_btc': 'number'},
        'stocks': {'ticker': 'text', 'shares': 'number'},
        'vehicles': {'make_model': 'text', 'year': 'number'},
    }

    return {**common, **specifics.get(category, {})}

# ────────────────────────────────
# Add entry form - EVERY widget has unique key
# ────────────────────────────────
def add_form(cat):
    fields = get_fields(cat)

    with st.expander(f"Add {cat.replace('_', ' ').title()}", expanded=False):
        values = {}

        for fname, ftype in fields.items():
            label = fname.replace('_', ' ').title()
            key_prefix = f"{cat}__{fname}"

            if ftype == 'text':
                values[fname] = st.text_input(label, key=f"{key_prefix}__txt")
            elif ftype == 'number':
                values[fname] = st.number_input(label, min_value=0.0, key=f"{key_prefix}__num")
            elif ftype == 'textarea':
                values[fname] = st.text_area(label, key=f"{key_prefix}__txta")

        if st.button("Save", key=f"{cat}__save"):
            if any(v for v in values.values() if v):  # at least something filled
                st.session_state.assets[cat].append(values)
                st.success("Saved", icon="✅")
                st.rerun()
            else:
                st.warning("Fill something", icon="⚠️")

# ────────────────────────────────
# Show & delete entries
# ────────────────────────────────
def show_entries(cat):
    items = st.session_state.assets[cat]
    if not items:
        return

    st.subheader(f"{cat.replace('_', ' ').title()} ({len(items)})")

    for i, item in enumerate(items):
        with st.container(border=True):
            st.json(item)
            if st.button("Delete", key=f"{cat}__del__{i}"):
                del st.session_state.assets[cat][i]
                st.rerun()

# ────────────────────────────────
# Main layout
# ────────────────────────────────
cols = st.columns(3)
for i, cat in enumerate(CATEGORIES):
    with cols[i % 3]:
        add_form(cat)
        show_entries(cat)

# ────────────────────────────────
# Export
# ────────────────────────────────
st.divider()
if any(st.session_state.assets.values()):
    flat = []
    for cat, records in st.session_state.assets.items():
        for r in records:
            row = r.copy()
            row['Category'] = cat
            flat.append(row)

    df = pd.DataFrame(flat)

    st.download_button(
        "Download CSV",
        df.to_csv(index=False).encode('utf-8'),
        "assets.csv",
        "text/csv"
    )

    # Very basic PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Asset Inventory", ln=1, align='C')

    for cat, group in df.groupby('Category'):
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 8, cat, ln=True)
        pdf.set_font("Arial", size=10)
        pdf.multi_cell(0, 6, group.drop('Category', axis=1).to_string(index=False))

    pdf_bytes = pdf.output(dest='S').encode('latin-1')
    b64 = base64.b64encode(pdf_bytes).decode()
    st.markdown(f'<a href="data:application/pdf;base64,{b64}" download="assets.pdf">Download PDF</a>', unsafe_allow_html=True)

else:
    st.info("No assets yet")
