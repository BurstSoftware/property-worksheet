import streamlit as st
import pandas as pd
from fpdf import FPDF
import base64
import io

# ───────────────────────────────────────────────────────────────
# Initialize session state
# ───────────────────────────────────────────────────────────────
if 'data' not in st.session_state:
    st.session_state.data = {}

# All possible categories (you can use all or subset)
ALL_CATEGORIES = [
    'real_estate', 'cash_checking', 'savings_money_market', 'bitcoin',
    'other_digital_currency', 'certificates_deposit', 'credit_cards',
    'precious_metals', 'listed_stocks', 'unlisted_stocks', 'mutual_funds',
    'iras', 'roth_iras', '401k_403b', 'automobiles', 'boats',
    'household_goods', 'jewelry_furs', 'collectibles', 'life_insurance',
    'email_accounts', 'social_media_accounts', 'subscriptions',
    'marketplace_accounts', 'domain_names_websites', 'business_entities'
]

# Initialize empty lists for categories that don't exist yet
for cat in ALL_CATEGORIES:
    if cat not in st.session_state.data:
        st.session_state.data[cat] = []

st.title("Asset & Digital Inventory Manager")
st.caption("Track property, financial accounts, digital assets and more")

# ───────────────────────────────────────────────────────────────
# Define field schemas (expand as needed)
# ───────────────────────────────────────────────────────────────
field_definitions = {
    'real_estate': [
        ('address', 'text'),
        ('city_state_zip', 'text'),
        ('estimated_value_usd', 'number'),
        ('mortgage_balance', 'number'),
        ('notes', 'textarea')
    ],
    'cash_checking': [
        ('bank_name', 'text'),
        ('account_type', 'text'),
        ('last_4_digits', 'text'),
        ('balance', 'number')
    ],
    'bitcoin': [
        ('wallet_type', 'text'),
        ('address', 'text'),
        ('amount_btc', 'number'),
        ('approx_usd_value', 'number')
    ],
    'listed_stocks': [
        ('ticker_symbol', 'text'),
        ('number_of_shares', 'number'),
        ('current_value_usd', 'number')
    ],
    'iras': [
        ('provider', 'text'),
        ('account_type', 'text'),
        ('balance', 'number')
    ],
    'automobiles': [
        ('make_model_year', 'text'),
        ('estimated_value', 'number'),
        ('vin_last6', 'text')
    ],
    # Add other categories following the same pattern...
    # Example placeholder for others:
    'default': [
        ('description', 'textarea'),
        ('value_usd', 'number'),
        ('notes', 'textarea')
    ]
}

# ───────────────────────────────────────────────────────────────
# Add entry form with 100% unique keys
# ───────────────────────────────────────────────────────────────
def add_entry_form(category: str):
    fields = field_definitions.get(category, field_definitions['default'])

    with st.expander(f"➕ Add {category.replace('_', ' ').title()}", expanded=False):
        entry = {}

        for field_name, field_type in fields:
            label = field_name.replace('_', ' ').title()

            # ── UNIQUE KEYS ──────────────────────────────────────
            input_key = f"input_{field_type}__{category}__{field_name}"

            if field_type == 'text':
                entry[field_name] = st.text_input(label, key=input_key)
            elif field_type == 'number':
                entry[field_name] = st.number_input(
                    label,
                    min_value=0.0,
                    step=100.0,
                    format="%.2f",
                    key=input_key
                )
            elif field_type == 'textarea':
                entry[field_name] = st.text_area(
                    label,
                    height=90,
                    key=input_key
                )

        # Save button - unique per category
        save_key = f"btn_save__{category}"

        if st.button("Save Entry", key=save_key, type="primary", use_container_width=True):
            # Very basic validation: at least one non-empty/non-zero field
            if any(value for value in entry.values() if value not in (None, "", 0, 0.0)):
                st.session_state.data[category].append(entry)
                st.success(f"Added to {category.replace('_', ' ').title()}")
                # Force refresh to clear form
                st.rerun()
            else:
                st.warning("Please fill at least one field")

# ───────────────────────────────────────────────────────────────
# Display existing entries with delete buttons
# ───────────────────────────────────────────────────────────────
def display_entries(category: str):
    entries = st.session_state.data.get(category, [])
    if not entries:
        return

    st.subheader(f"{category.replace('_', ' ').title()} ({len(entries)})")

    for i, entry in enumerate(entries):
        with st.container(border=True):
            cols = st.columns([5, 1])
            with cols[0]:
                st.json(entry)
            with cols[1]:
                delete_key = f"btn_delete__{category}__{i}"
                if st.button("🗑", key=delete_key, help="Delete this entry"):
                    del st.session_state.data[category][i]
                    st.rerun()

# ───────────────────────────────────────────────────────────────
# Main UI - Organized in tabs
# ───────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "Property & Vehicles",
    "Banking & Crypto",
    "Investments & Retirement",
    "Digital & Other"
])

with tab1:
    for cat in ['real_estate', 'automobiles']:
        add_entry_form(cat)
        display_entries(cat)

with tab2:
    for cat in ['cash_checking', 'bitcoin']:
        add_entry_form(cat)
        display_entries(cat)

with tab3:
    for cat in ['listed_stocks', 'iras']:
        add_entry_form(cat)
        display_entries(cat)

with tab4:
    # Placeholder for many digital/other categories
    add_entry_form('default')  # fallback form
    st.info("Add more specific categories as needed")

# ───────────────────────────────────────────────────────────────
# Export section
# ───────────────────────────────────────────────────────────────
st.divider()
st.subheader("Export Data")

all_records = []
for category, items in st.session_state.data.items():
    for item in items:
        record = item.copy()
        record['Category'] = category.replace('_', ' ').title()
        all_records.append(record)

if all_records:
    df = pd.DataFrame(all_records)

    # CSV
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "📥 Download CSV",
        csv,
        "asset_inventory.csv",
        "text/csv",
        use_container_width=True
    )

    # Simple PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Asset Inventory", ln=True, align="C")
    pdf.ln(10)

    for cat, group in df.groupby("Category"):
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, cat, ln=True)
        pdf.set_font("Arial", "", 10)
        pdf.multi_cell(0, 6, group.drop(columns="Category").to_string(index=False))
        pdf.ln(5)

    pdf_output = pdf.output(dest='S').encode('latin-1')
    pdf_b64 = base64.b64encode(pdf_output).decode('utf-8')

    st.markdown(
        f'<a href="data:application/pdf;base64,{pdf_b64}" download="asset_inventory.pdf">'
        '📄 Download PDF</a> ',
        unsafe_allow_html=True
    )
else:
    st.info("No entries yet. Start adding above.")

st.caption("Tip: Use unique keys for every widget = no more duplicate ID errors")
