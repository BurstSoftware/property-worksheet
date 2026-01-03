import streamlit as st
import pandas as pd
from fpdf import FPDF
import base64
import io

# ────────────────────────────────────────────────
# Initialize session state
# ────────────────────────────────────────────────
if 'data' not in st.session_state:
    st.session_state.data = {
        'real_estate': [],
        'cash_checking': [],
        'savings_money_market': [],
        'bitcoin': [],
        'other_digital_currency': [],
        'certificates_of_deposit': [],
        'credit_cards': [],
        'debit_cards': [],
        'alt_coins': [],
        'local_currencies': [],
        'barter_units': [],
        'precious_metals': [],
        'mutual_funds': [],
        'listed_stocks': [],
        'unlisted_stocks': [],
        'government_bonds': [],
        'corporate_bonds': [],
        'municipal_bonds': [],
        'annuities': [],
        'iras': [],
        'keoghs': [],
        'roth_iras': [],
        '401k': [],
        '403b': [],
        'automobiles': [],
        'trucks': [],
        'recreational_vehicles': [],
        'planes': [],
        'boats': [],
        'other_vehicles': [],
        'household_goods': [],
        'valuable_clothing': [],
        'jewelry_furs': [],
        'collectables': [],
        'tools_equipment': [],
        'other_personal_property': [],
        'livestock': [],
        'money_owed': [],
        'death_benefits': [],
        'life_insurance': [],
        'miscellaneous': [],
        'email_accounts': [],
        'facebook': [],
        'instagram': [],
        'linkedin': [],
        'twitter': [],
        'subscriptions': [],
        'marketplace_accounts': [],
        'apps': [],
        'photos': [],
        'books': [],
        'music': [],
        'videos': [],
        'file_sharing': [],
        'financial_accounts': [],
        'medical_accounts': [],
        'insurance_accounts': [],
        'blogs_websites': [],
        'domain_names': [],
        'third_party_hosts': [],
        'utilities': [],
        'computer_data': [],
        'contact_lists': [],
        'tax_prep': [],
        'partnerships': [],
        'sole_proprietorships': [],
        'limited_partnerships': [],
        'llcs': [],
        'corporations': []
    }

st.title("Personal Asset & Digital Inventory Manager")

# ────────────────────────────────────────────────
# Helper function to add new entry
# ────────────────────────────────────────────────
def add_entry(category, fields):
    expander_title = f"Add {category.replace('_', ' ').title()}"
    with st.expander(expander_title, expanded=False):
        entry = {}
        
        for field, input_type in fields.items():
            label = field.replace('_', ' ').title()
            # Unique key: category + field
            key = f"input__{category}__{field}"
            
            if input_type == 'text':
                entry[field] = st.text_input(label, key=key)
            elif input_type == 'number':
                entry[field] = st.number_input(label, min_value=0.0, format="%.2f", key=key)
            elif input_type == 'textarea':
                entry[field] = st.text_area(label, height=80, key=key)
        
        # Unique save button key
        save_key = f"save__{category}"
        if st.button(f"Save {category.replace('_', ' ').title()}", key=save_key):
            # Basic validation: at least one meaningful field filled
            if any(v not in (None, "", 0.0) for v in entry.values()):
                st.session_state.data[category].append(entry)
                st.success(f"Entry added to {category.replace('_', ' ').title()}!")
                # Optional: clear inputs by forcing rerun
                st.rerun()
            else:
                st.warning("Please fill in at least some information.")

# ────────────────────────────────────────────────
# Helper function to show & delete entries
# ────────────────────────────────────────────────
def display_entries(category):
    entries = st.session_state.data.get(category, [])
    if entries:
        st.subheader(f"{category.replace('_', ' ').title()} ({len(entries)})")
        
        for i, entry in enumerate(entries):
            with st.container(border=True):
                st.markdown(f"**Entry {i+1}**")
                st.json(entry)  # nice readable view
                
                # Unique delete key
                delete_key = f"delete__{category}__{i}"
                if st.button("🗑️ Delete", key=delete_key):
                    del st.session_state.data[category][i]
                    st.success("Entry deleted")
                    st.rerun()

# ────────────────────────────────────────────────
# Define fields for each category
# ────────────────────────────────────────────────
categories = {
    'real_estate': {'address': 'text', 'value': 'number', 'description': 'textarea'},
    'cash_checking': {'account_number': 'text', 'balance': 'number', 'bank': 'text'},
    'savings_money_market': {'account_number': 'text', 'balance': 'number', 'bank': 'text'},
    'bitcoin': {'wallet_address': 'text', 'amount_btc': 'number', 'current_value_usd': 'number'},
    'other_digital_currency': {'currency_type': 'text', 'wallet_address': 'text', 'amount': 'number'},
    'certificates_of_deposit': {'issuer': 'text', 'amount': 'number', 'maturity_date': 'text'},
    'credit_cards': {'card_number_last4': 'text', 'issuer': 'text', 'balance': 'number'},
    'debit_cards': {'card_number_last4': 'text', 'issuer': 'text', 'linked_account': 'text'},
    'alt_coins': {'coin_type': 'text', 'amount': 'number', 'wallet': 'text'},
    'precious_metals': {'metal_type': 'text', 'quantity_oz': 'number', 'current_value': 'number'},
    'mutual_funds': {'fund_name': 'text', 'shares': 'number', 'current_value': 'number'},
    'listed_stocks': {'symbol': 'text', 'shares': 'number', 'current_value': 'number'},
    'iras': {'account_number': 'text', 'balance': 'number', 'provider': 'text'},
    'roth_iras': {'account_number': 'text', 'balance': 'number', 'provider': 'text'},
    '401k': {'account_number': 'text', 'balance': 'number', 'employer': 'text'},
    'automobiles': {'make_model': 'text', 'year': 'number', 'value': 'number'},
    'boats': {'make_model': 'text', 'registration': 'text', 'value': 'number'},
    'household_goods': {'description': 'textarea', 'estimated_value': 'number'},
    'jewelry_furs': {'description': 'textarea', 'estimated_value': 'number'},
    'collectables': {'type': 'text', 'description': 'textarea', 'value': 'number'},
    'money_owed': {'debtor': 'text', 'amount': 'number', 'description': 'textarea'},
    'life_insurance': {'policy_number': 'text', 'provider': 'text', 'cash_value': 'number'},
    'email_accounts': {'email': 'text', 'provider': 'text', 'notes': 'textarea'},
    'subscriptions': {'service': 'text', 'account_email': 'text', 'notes': 'textarea'},
    'marketplace_accounts': {'platform': 'text', 'username': 'text', 'notes': 'textarea'},
    'blogs_websites': {'url': 'text', 'notes': 'textarea'},
    'corporations': {'name': 'text', 'details': 'textarea'},
    # Add more categories here following the same pattern...
    # For brevity I only included a subset — copy the pattern for remaining categories
}

# ────────────────────────────────────────────────
# Organize categories into tabs
# ────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Real Estate & Property",
    "Cash & Investments",
    "Vehicles & Personal Items",
    "Digital & Online Assets",
    "Business & Other"
])

with tab1:
    add_entry('real_estate', categories.get('real_estate', {}))
    display_entries('real_estate')

with tab2:
    for cat in [
        'cash_checking', 'savings_money_market', 'bitcoin', 'other_digital_currency',
        'certificates_of_deposit', 'precious_metals', 'mutual_funds', 'listed_stocks',
        'iras', 'roth_iras', '401k'
    ]:
        if cat in categories:
            add_entry(cat, categories[cat])
            display_entries(cat)

with tab3:
    for cat in [
        'automobiles', 'boats', 'household_goods', 'jewelry_furs',
        'collectables', 'money_owed', 'life_insurance'
    ]:
        if cat in categories:
            add_entry(cat, categories[cat])
            display_entries(cat)

with tab4:
    for cat in [
        'email_accounts', 'subscriptions', 'marketplace_accounts', 'blogs_websites'
    ]:
        if cat in categories:
            add_entry(cat, categories[cat])
            display_entries(cat)

with tab5:
    for cat in ['corporations']:
        if cat in categories:
            add_entry(cat, categories[cat])
            display_entries(cat)

# ────────────────────────────────────────────────
# Download Section
# ────────────────────────────────────────────────
st.header("Export Your Data")

all_entries = []
for cat, items in st.session_state.data.items():
    for item in items:
        item_copy = item.copy()
        item_copy['Category'] = cat.replace('_', ' ').title()
        all_entries.append(item_copy)

if all_entries:
    df = pd.DataFrame(all_entries)
    
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "📥 Download as CSV",
        data=csv,
        file_name="personal_asset_inventory.csv",
        mime="text/csv"
    )

    # PDF Generation
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Personal Asset & Digital Inventory", ln=True, align="C")
    pdf.ln(10)

    for cat, group in df.groupby('Category'):
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, cat, ln=True)
        pdf.set_font("Arial", "", 10)
        pdf.multi_cell(0, 8, group.drop('Category', axis=1).to_string(index=False))
        pdf.ln(5)

    pdf_bytes = pdf.output(dest='S').encode('latin-1')
    pdf_b64 = base64.b64encode(pdf_bytes).decode('utf-8')
    
    st.markdown(
        f'<a href="data:application/pdf;base64,{pdf_b64}" download="personal_asset_inventory.pdf">'
        '📄 Download as PDF</a>',
        unsafe_allow_html=True
    )
else:
    st.info("No entries added yet. Start adding your assets above!")
