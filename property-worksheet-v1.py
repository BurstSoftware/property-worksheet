import streamlit as st
import pandas as pd
from fpdf import FPDF
import base64
import io

# ───────────────────────────────────────────────────────────────
# Session state initialization
# ───────────────────────────────────────────────────────────────
if 'assets' not in st.session_state:
    st.session_state.assets = {
        'real_estate': [],
        'cash_checking': [],
        'savings_mm': [],
        'bitcoin': [],
        'other_crypto': [],
        'cds': [],
        'credit_cards': [],
        'precious_metals': [],
        'stocks_listed': [],
        'stocks_unlisted': [],
        'mutual_funds': [],
        'bonds_gov': [],
        'bonds_corp': [],
        'bonds_muni': [],
        'iras': [],
        'roth_iras': [],
        '401k_403b': [],
        'vehicles': [],
        'boats_planes': [],
        'jewelry_collectibles': [],
        'household_valuables': [],
        'life_insurance': [],
        'notes_receivable': [],
        'digital_accounts': [],
        'social_media': [],
        'subscriptions': [],
        'domains_websites': [],
        'business_entities': []
    }

st.title("Personal & Family Asset Inventory")
st.caption("Securely track assets — export CSV/PDF")

# ───────────────────────────────────────────────────────────────
# Helper: Add new entry form
# ───────────────────────────────────────────────────────────────
def add_asset_form(category: str, fields: dict):
    """Create input form with UNIQUE keys for every widget"""
    with st.expander(f"➕ Add to {category.replace('_', ' ').title()}", expanded=False):
        entry = {}

        for field_name, field_type in fields.items():
            label = field_name.replace('_', ' ').title()
            # ── VERY IMPORTANT: unique key pattern ───────────────────────
            base_key = f"{category}__{field_name}"

            if field_type == 'text':
                entry[field_name] = st.text_input(
                    label,
                    key=f"{base_key}__text",
                    placeholder=f"Enter {label.lower()}"
                )
            elif field_type == 'number':
                entry[field_name] = st.number_input(
                    label,
                    min_value=0.0,
                    step=100.0,
                    format="%.2f",
                    key=f"{base_key}__num"
                )
            elif field_type == 'textarea':
                entry[field_name] = st.text_area(
                    label,
                    height=88,
                    key=f"{base_key}__area"
                )

        # Save button — also needs unique key
        if st.button("💾 Save Entry", key=f"{category}__SAVE", use_container_width=True):
            # Minimal validation — at least something filled
            if any(v for v in entry.values() if v not in (None, "", 0.0, 0)):
                st.session_state.assets[category].append(entry)
                st.success("Entry saved!", icon="✅")
                st.rerun()
            else:
                st.warning("Please fill at least one field", icon="⚠️")

# ───────────────────────────────────────────────────────────────
# Helper: Display & delete entries
# ───────────────────────────────────────────────────────────────
def show_entries(category: str):
    items = st.session_state.assets.get(category, [])
    if not items:
        return

    st.subheader(f"{category.replace('_', ' ').title()}  ({len(items)})")

    for idx, record in enumerate(items):
        with st.container(border=True):
            col1, col2 = st.columns([5,1])
            with col1:
                st.json(record)
            with col2:
                if st.button("🗑", key=f"{category}__DEL__{idx}", help="Delete this entry"):
                    del st.session_state.assets[category][idx]
                    st.rerun()

# ───────────────────────────────────────────────────────────────
# Field definitions (you can expand this a lot more)
# ───────────────────────────────────────────────────────────────
field_sets = {
    'real_estate': {
        'address': 'text',
        'city_state_zip': 'text',
        'estimated_value': 'number',
        'mortgage_balance': 'number',
        'notes': 'textarea'
    },
    'cash_checking': {
        'bank': 'text',
        'account_type': 'text',
        'account_last4': 'text',
        'balance': 'number'
    },
    'bitcoin': {
        'wallet_type': 'text',
        'address': 'text',
        'amount_btc': 'number',
        'current_value_usd': 'number'
    },
    'precious_metals': {
        'type': 'text',
        'quantity_oz': 'number',
        'purchase_price': 'number',
        'current_value': 'number'
    },
    'stocks_listed': {
        'ticker': 'text',
        'shares': 'number',
        'current_value': 'number'
    },
    'iras': {
        'provider': 'text',
        'account_type': 'text',
        'balance': 'number'
    },
    'vehicles': {
        'make_model_year': 'text',
        'vin_last6': 'text',
        'mileage': 'number',
        'estimated_value': 'number'
    },
    'life_insurance': {
        'company': 'text',
        'policy_number': 'text',
        'face_amount': 'number',
        'cash_value': 'number'
    },
    'digital_accounts': {
        'service': 'text',
        'username_email': 'text',
        'notes_2fa': 'textarea'
    },
    'business_entities': {
        'entity_name': 'text',
        'type': 'text',
        'ownership_percentage': 'number',
        'estimated_value': 'number'
    }
    # Add many more categories following the same pattern...
}

# ───────────────────────────────────────────────────────────────
# Main layout — Tabs
# ───────────────────────────────────────────────────────────────
tab_names = ["Property", "Banking & Crypto", "Investments", "Vehicles & Valuables", "Digital & Other"]

tabs = st.tabs(tab_names)

with tabs[0]:
    add_asset_form('real_estate', field_sets.get('real_estate', {}))
    show_entries('real_estate')

with tabs[1]:
    for cat in ['cash_checking', 'bitcoin']:
        if cat in field_sets:
            add_asset_form(cat, field_sets[cat])
            show_entries(cat)

with tabs[2]:
    for cat in ['precious_metals', 'stocks_listed', 'iras']:
        if cat in field_sets:
            add_asset_form(cat, field_sets[cat])
            show_entries(cat)

with tabs[3]:
    for cat in ['vehicles', 'life_insurance']:
        if cat in field_sets:
            add_asset_form(cat, field_sets[cat])
            show_entries(cat)

with tabs[4]:
    for cat in ['digital_accounts', 'business_entities']:
        if cat in field_sets:
            add_asset_form(cat, field_sets[cat])
            show_entries(cat)

# ───────────────────────────────────────────────────────────────
# Export
# ───────────────────────────────────────────────────────────────
st.divider()
st.subheader("Export Inventory")

flat_data = []
for cat, records in st.session_state.assets.items():
    for rec in records:
        row = rec.copy()
        row['Category'] = cat.replace('_', ' ').title()
        flat_data.append(row)

if flat_data:
    df = pd.DataFrame(flat_data)

    # CSV
    csv_data = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download CSV",
        data=csv_data,
        file_name="asset_inventory.csv",
        mime="text/csv",
        use_container_width=True
    )

    # PDF (very simple version)
    if st.button("Generate PDF Report", use_container_width=True):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 12, "Asset Inventory Report", ln=1, align="C")
        pdf.ln(8)

        for category, group in df.groupby("Category"):
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, category, ln=1)
            pdf.set_font("Arial", "", 10)
            pdf.multi_cell(0, 7, group.drop(columns="Category").to_string(index=False))
            pdf.ln(6)

        pdf_bytes = pdf.output(dest='S').encode('latin-1')
        b64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')

        st.markdown(
            f'<a href="data:application/pdf;base64,{b64_pdf}" download="asset_inventory.pdf">'
            '📄 Download PDF Report</a>',
            unsafe_allow_html=True
        )
else:
    st.info("No assets recorded yet.")
