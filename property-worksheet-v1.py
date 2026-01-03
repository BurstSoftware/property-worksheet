import streamlit as st
import pandas as pd
from fpdf import FPDF
import base64
import io

# Initialize session state for data storage
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

st.title("Asset Management Application")

# Function to add entry to a category
def add_entry(category, fields):
    with st.expander(f"Add {category.replace('_', ' ').title()}"):
        entry = {}
        for field, input_type in fields.items():
            if input_type == 'text':
                entry[field] = st.text_input(field.replace('_', ' ').title())
            elif input_type == 'number':
                entry[field] = st.number_input(field.replace('_', ' ').title(), min_value=0.0)
            elif input_type == 'textarea':
                entry[field] = st.text_area(field.replace('_', ' ').title())
        if st.button(f"Save {category.replace('_', ' ').title()}"):
            if all(entry.values()):  # Simple validation: all fields filled
                st.session_state.data[category].append(entry)
                st.success(f"Added to {category.replace('_', ' ').title()}")

# Function to display and edit entries
def display_entries(category):
    if st.session_state.data[category]:
        st.subheader(category.replace('_', ' ').title())
        for i, entry in enumerate(st.session_state.data[category]):
            st.write(f"Entry {i+1}: {entry}")
            if st.button(f"Delete Entry {i+1}", key=f"del_{category}_{i}"):
                del st.session_state.data[category][i]
                st.rerun()

# Define fields for each category (simplified; adjust as needed)
categories = {
    'real_estate': {'address': 'text', 'value': 'number', 'description': 'textarea'},
    'cash_checking': {'account_number': 'text', 'balance': 'number', 'bank': 'text'},
    'savings_money_market': {'account_number': 'text', 'balance': 'number', 'bank': 'text'},
    'bitcoin': {'wallet_address': 'text', 'amount': 'number', 'value': 'number'},
    'other_digital_currency': {'currency_type': 'text', 'wallet_address': 'text', 'amount': 'number'},
    'certificates_of_deposit': {'issuer': 'text', 'amount': 'number', 'maturity_date': 'text'},
    'credit_cards': {'card_number': 'text', 'issuer': 'text', 'balance': 'number'},
    'debit_cards': {'card_number': 'text', 'issuer': 'text', 'linked_account': 'text'},
    'alt_coins': {'coin_type': 'text', 'amount': 'number', 'wallet': 'text'},
    'local_currencies': {'currency_type': 'text', 'amount': 'number', 'description': 'text'},
    'barter_units': {'unit_type': 'text', 'quantity': 'number', 'description': 'textarea'},
    'precious_metals': {'metal_type': 'text', 'quantity': 'number', 'value': 'number'},
    'mutual_funds': {'fund_name': 'text', 'shares': 'number', 'value': 'number'},
    'listed_stocks': {'stock_symbol': 'text', 'shares': 'number', 'value': 'number'},
    'unlisted_stocks': {'company_name': 'text', 'shares': 'number', 'value': 'number'},
    'government_bonds': {'bond_type': 'text', 'amount': 'number', 'maturity': 'text'},
    'corporate_bonds': {'issuer': 'text', 'amount': 'number', 'maturity': 'text'},
    'municipal_bonds': {'issuer': 'text', 'amount': 'number', 'maturity': 'text'},
    'annuities': {'provider': 'text', 'amount': 'number', 'type': 'text'},
    'iras': {'account_number': 'text', 'balance': 'number', 'provider': 'text'},
    'keoghs': {'account_number': 'text', 'balance': 'number', 'provider': 'text'},
    'roth_iras': {'account_number': 'text', 'balance': 'number', 'provider': 'text'},
    '401k': {'account_number': 'text', 'balance': 'number', 'employer': 'text'},
    '403b': {'account_number': 'text', 'balance': 'number', 'employer': 'text'},
    'automobiles': {'make_model': 'text', 'year': 'number', 'value': 'number'},
    'trucks': {'make_model': 'text', 'year': 'number', 'value': 'number'},
    'recreational_vehicles': {'type': 'text', 'make_model': 'text', 'value': 'number'},
    'planes': {'make_model': 'text', 'registration': 'text', 'value': 'number'},
    'boats': {'make_model': 'text', 'registration': 'text', 'value': 'number'},
    'other_vehicles': {'type': 'text', 'description': 'textarea', 'value': 'number'},
    'household_goods': {'description': 'textarea', 'value': 'number'},
    'valuable_clothing': {'description': 'textarea', 'value': 'number'},
    'jewelry_furs': {'description': 'textarea', 'value': 'number'},
    'collectables': {'type': 'text', 'description': 'textarea', 'value': 'number'},
    'tools_equipment': {'description': 'textarea', 'value': 'number'},
    'other_personal_property': {'description': 'textarea', 'value': 'number'},
    'livestock': {'type': 'text', 'quantity': 'number', 'value': 'number'},
    'money_owed': {'debtor': 'text', 'amount': 'number', 'description': 'textarea'},
    'death_benefits': {'policy': 'text', 'amount': 'number', 'beneficiary': 'text'},
    'life_insurance': {'policy_number': 'text', 'provider': 'text', 'value': 'number'},
    'miscellaneous': {'description': 'textarea', 'value': 'number'},
    'email_accounts': {'email': 'text', 'provider': 'text'},
    'facebook': {'username': 'text', 'notes': 'textarea'},
    'instagram': {'username': 'text', 'notes': 'textarea'},
    'linkedin': {'username': 'text', 'notes': 'textarea'},
    'twitter': {'username': 'text', 'notes': 'textarea'},
    'subscriptions': {'service': 'text', 'account': 'text', 'notes': 'textarea'},
    'marketplace_accounts': {'platform': 'text', 'username': 'text', 'notes': 'textarea'},
    'apps': {'app_name': 'text', 'account': 'text', 'notes': 'textarea'},
    'photos': {'storage': 'text', 'notes': 'textarea'},
    'books': {'storage': 'text', 'notes': 'textarea'},
    'music': {'storage': 'text', 'notes': 'textarea'},
    'videos': {'storage': 'text', 'notes': 'textarea'},
    'file_sharing': {'service': 'text', 'account': 'text', 'notes': 'textarea'},
    'financial_accounts': {'type': 'text', 'provider': 'text', 'account': 'text'},
    'medical_accounts': {'provider': 'text', 'account': 'text', 'notes': 'textarea'},
    'insurance_accounts': {'type': 'text', 'provider': 'text', 'policy': 'text'},
    'blogs_websites': {'url': 'text', 'notes': 'textarea'},
    'domain_names': {'domain': 'text', 'registrar': 'text'},
    'third_party_hosts': {'host': 'text', 'account': 'text'},
    'utilities': {'utility': 'text', 'account': 'text'},
    'computer_data': {'description': 'textarea', 'location': 'text'},
    'contact_lists': {'location': 'text', 'notes': 'textarea'},
    'tax_prep': {'software': 'text', 'account': 'text'},
    'partnerships': {'name': 'text', 'details': 'textarea'},
    'sole_proprietorships': {'name': 'text', 'details': 'textarea'},
    'limited_partnerships': {'name': 'text', 'details': 'textarea'},
    'llcs': {'name': 'text', 'details': 'textarea'},
    'corporations': {'name': 'text', 'details': 'textarea'}
}

# Tabs for organization
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Property & Real Estate", "Cash & Investments", "Vehicles & Personal Property", "Digital Assets", "Business & Misc"])

with tab1:
    add_entry('real_estate', categories['real_estate'])
    display_entries('real_estate')

with tab2:
    for cat in ['cash_checking', 'savings_money_market', 'bitcoin', 'other_digital_currency', 'certificates_of_deposit', 'credit_cards', 'debit_cards', 'alt_coins', 'local_currencies', 'barter_units', 'precious_metals', 'mutual_funds', 'listed_stocks', 'unlisted_stocks', 'government_bonds', 'corporate_bonds', 'municipal_bonds', 'annuities', 'iras', 'keoghs', 'roth_iras', '401k', '403b']:
        add_entry(cat, categories[cat])
        display_entries(cat)

with tab3:
    for cat in ['automobiles', 'trucks', 'recreational_vehicles', 'planes', 'boats', 'other_vehicles', 'household_goods', 'valuable_clothing', 'jewelry_furs', 'collectables', 'tools_equipment', 'other_personal_property', 'livestock', 'money_owed', 'death_benefits', 'life_insurance', 'miscellaneous']:
        add_entry(cat, categories[cat])
        display_entries(cat)

with tab4:
    for cat in ['email_accounts', 'facebook', 'instagram', 'linkedin', 'twitter', 'subscriptions', 'marketplace_accounts', 'apps', 'photos', 'books', 'music', 'videos', 'file_sharing', 'financial_accounts', 'medical_accounts', 'insurance_accounts', 'blogs_websites', 'domain_names', 'third_party_hosts', 'utilities', 'computer_data', 'contact_lists', 'tax_prep']:
        add_entry(cat, categories[cat])
        display_entries(cat)

with tab5:
    for cat in ['partnerships', 'sole_proprietorships', 'limited_partnerships', 'llcs', 'corporations']:
        add_entry(cat, categories[cat])
        display_entries(cat)

# Download section
st.header("Download Data")

# Collect all data into a flat list for CSV/PDF
all_data = []
for category, entries in st.session_state.data.items():
    for entry in entries:
        entry['category'] = category
        all_data.append(entry)

if all_data:
    df = pd.DataFrame(all_data)

    # CSV Download
    csv = df.to_csv(index=False)
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="assets.csv",
        mime="text/csv"
    )

    # PDF Download
    class PDF(FPDF):
        def header(self):
            self.set_font('Arial', 'B', 12)
            self.cell(0, 10, 'Asset Report', 0, 1, 'C')

        def chapter_title(self, title):
            self.set_font('Arial', 'B', 12)
            self.cell(0, 10, title, 0, 1, 'L')
            self.ln(2)

        def chapter_body(self, body):
            self.set_font('Arial', '', 12)
            self.multi_cell(0, 10, body)
            self.ln()

    pdf = PDF()
    pdf.add_page()
    for category, group in df.groupby('category'):
        pdf.chapter_title(category.replace('_', ' ').title())
        body = group.drop('category', axis=1).to_string(index=False)
        pdf.chapter_body(body)

    pdf_output = io.BytesIO()
    pdf_output.write(pdf.output(dest='S').encode('latin1'))
    pdf_output.seek(0)
    b64 = base64.b64encode(pdf_output.read()).decode()
    href = f'<a href="data:application/pdf;base64,{b64}" download="assets.pdf">Download PDF</a>'
    st.markdown(href, unsafe_allow_html=True)
else:
    st.info("No data to download yet.")
