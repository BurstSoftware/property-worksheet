import streamlit as st
import pandas as pd
from fpdf import FPDF
import base64
import io

# ────────────────────────────────
# Session state initialization
# ────────────────────────────────
if 'assets' not in st.session_state:
    st.session_state.assets = {}

# Main categories (add more as needed)
CATEGORIES = [
    "real_estate",
    "cash_checking",
    "savings",
    "bitcoin",
    "other_crypto",
    "stocks",
    "retirement",
    "vehicles",
    "precious_metals",
    "jewelry_collectibles",
    "digital_accounts",
    "business_entities"
]

for cat in CATEGORIES:
    if cat not in st.session_state.assets:
        st.session_state.assets[cat] = []

st.title("Asset Inventory")

# ────────────────────────────────
# Field definitions per category
# ────────────────────────────────
def get_fields(category):
    base_fields = {
        "description": "text",
        "value_usd": "number",
        "notes": "textarea"
    }
    
    specific = {
        "real_estate": {"address": "text", "city": "text"},
        "cash_checking": {"bank": "text", "account_last4": "text"},
        "bitcoin": {"wallet_type": "text", "address": "text", "amount_btc": "number"},
        "stocks": {"ticker": "text", "shares": "number"},
        "vehicles": {"make_model": "text", "year": "number"},
        "precious_metals": {"type": "text", "quantity_oz": "number"},
    }
    
    return {**base_fields, **specific.get(category, {})}

# ────────────────────────────────
# Create input form – EVERY widget MUST have unique key
# ────────────────────────────────
def create_add_form(category: str):
    fields = get_fields(category)

    with st.expander(f"➕ Add {category.replace('_', ' ').title()}", expanded=False):
        entry = {}

        for field_name, field_type in fields.items():
            label = field_name.replace('_', ' ').title()
            
            # ── CRITICAL: unique key for every input ────────────────
            unique_key = f"input__{category}__{field_name}__{field_type}"

            if field_type == "text":
                entry[field_name] = st.text_input(
                    label,
                    key=unique_key,
                    placeholder=f"Enter {label.lower()}"
                )
            elif field_type == "number":
                entry[field_name] = st.number_input(
                    label,
                    min_value=0.0,
                    step=0.01,
                    format="%.2f",
                    key=unique_key
                )
            elif field_type == "textarea":
                entry[field_name] = st.text_area(
                    label,
                    height=80,
                    key=unique_key
                )

        # Save button - also unique
        if st.button("Save", key=f"save__{category}", type="primary", use_container_width=True):
            if any(value for value in entry.values() if value):
                st.session_state.assets[category].append(entry)
                st.success("Entry saved", icon="✅")
                st.rerun()
            else:
                st.warning("Please fill at least one field", icon="⚠️")

# ────────────────────────────────
# Display saved entries + delete
# ────────────────────────────────
def display_entries(category: str):
    items = st.session_state.assets[category]
    if not items:
        return

    st.markdown(f"**{category.replace('_', ' ').title()}** ({len(items)} entries)")

    for idx, entry in enumerate(items):
        with st.container(border=True):
            col1, col2 = st.columns([7, 1])
            with col1:
                st.json(entry)
            with col2:
                if st.button("🗑", key=f"delete__{category}__{idx}", help="Remove entry"):
                    del st.session_state.assets[category][idx]
                    st.rerun()

# ────────────────────────────────
# Layout - simple columns (you can change to tabs)
# ────────────────────────────────
st.write("Add your assets below:")

columns = st.columns(3)
for i, cat in enumerate(CATEGORIES):
    with columns[i % 3]:
        create_add_form(cat)
        display_entries(cat)

# ────────────────────────────────
# Export section
# ────────────────────────────────
st.divider()

all_data = []
for cat, records in st.session_state.assets.items():
    for record in records:
        flat = record.copy()
        flat["category"] = cat
        all_data.append(flat)

if all_data:
    df = pd.DataFrame(all_data)

    st.download_button(
        label="Download CSV",
        data=df.to_csv(index=False).encode('utf-8'),
        file_name="assets_inventory.csv",
        mime="text/csv"
    )

    # Simple PDF export
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Asset Inventory", ln=True, align="C")

    for cat, group in df.groupby("category"):
        pdf.ln(8)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, cat.replace('_', ' ').title(), ln=True)
        pdf.set_font("Arial", size=10)
        pdf.multi_cell(0, 6, group.drop("category", axis=1).to_string(index=False))

    pdf_output = pdf.output(dest='S').encode('latin-1')
    pdf_base64 = base64.b64encode(pdf_output).decode('utf-8')
    
    st.markdown(
        f'<a href="data:application/pdf;base64,{pdf_base64}" download="assets_inventory.pdf">'
        'Download PDF</a>',
        unsafe_allow_html=True
    )
