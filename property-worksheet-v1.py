import streamlit as st
import pandas as pd
from fpdf import FPDF
import base64
import io
import datetime

# ────────────────────────────────────────────────
# Session state
# ────────────────────────────────────────────────
if 'assets' not in st.session_state:
    st.session_state.assets = []

st.title("Asset & Digital Inventory")
st.caption("Single-form entry • No duplicate widget errors")

# ────────────────────────────────────────────────
# Category definitions + fields
# ────────────────────────────────────────────────
CATEGORIES = {
    "Real Estate": {
        "address": ("text", "Street address"),
        "city_state_zip": ("text", "City, State ZIP"),
        "estimated_value": ("number", "Estimated current value $"),
        "mortgage_balance": ("number", "Outstanding mortgage $"),
        "notes": ("textarea", "Notes / description")
    },
    "Bank / Checking / Savings": {
        "bank_name": ("text", "Bank / Institution"),
        "account_type": ("text", "Account type"),
        "last_4": ("text", "Last 4 digits"),
        "balance": ("number", "Current balance $")
    },
    "Cryptocurrency": {
        "coin": ("text", "Coin / Token"),
        "wallet_type": ("text", "Wallet / exchange"),
        "address": ("text", "Address / public key"),
        "amount": ("number", "Amount held"),
        "current_value_usd": ("number", "Approx. current value $")
    },
    "Stocks / ETFs": {
        "ticker": ("text", "Ticker symbol"),
        "shares": ("number", "Number of shares"),
        "current_value": ("number", "Current total value $")
    },
    "Retirement Accounts": {
        "provider": ("text", "Provider / Custodian"),
        "account_type": ("text", "IRA / Roth / 401k / etc"),
        "balance": ("number", "Current balance $")
    },
    "Vehicles": {
        "make_model_year": ("text", "Make, Model, Year"),
        "vin_last6": ("text", "VIN last 6 digits"),
        "mileage": ("number", "Current mileage"),
        "estimated_value": ("number", "Estimated value $")
    },
    "Precious Metals / Collectibles": {
        "type": ("text", "Type (gold / art / coins / etc)"),
        "quantity_description": ("text", "Quantity / description"),
        "estimated_value": ("number", "Estimated current value $")
    },
    "Digital Assets / Accounts": {
        "service_platform": ("text", "Service / Platform"),
        "username_email": ("text", "Username / Email"),
        "notes": ("textarea", "Notes / 2FA info / recovery")
    },
    "Other / Miscellaneous": {
        "description": ("textarea", "Description of asset"),
        "estimated_value": ("number", "Estimated value $"),
        "notes": ("textarea", "Additional notes")
    }
}

# ────────────────────────────────────────────────
# Main entry form — ONLY ONE set of widgets at a time
# ────────────────────────────────────────────────
st.subheader("Add New Asset")

col1, col2 = st.columns([3,1])

with col1:
    selected_category = st.selectbox(
        "Category",
        options=list(CATEGORIES.keys()),
        key="category_selector"
    )

current_fields = CATEGORIES[selected_category]

entry = {}

# Create only the fields for the currently selected category
for field_key, (ftype, label) in current_fields.items():
    # Unique keys using field_key + timestamp to be extra safe
    safe_key = f"entry_{field_key}_{int(datetime.datetime.now().timestamp() * 1000)}"

    if ftype == "text":
        entry[field_key] = st.text_input(label, key=safe_key)
    elif ftype == "number":
        entry[field_key] = st.number_input(
            label,
            min_value=0.0,
            step=100.0,
            format="%.2f",
            key=safe_key
        )
    elif ftype == "textarea":
        entry[field_key] = st.text_area(label, height=90, key=safe_key)

# Category is saved with the entry
entry["category"] = selected_category
entry["added"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

if st.button("Save Asset", type="primary", use_container_width=True):
    has_content = any(v for v in entry.values() if v not in (None, "", 0.0))
    if has_content:
        st.session_state.assets.append(entry)
        st.success("Asset saved", icon="✅")
        # Clear form by forcing rerun (Streamlit will reset inputs)
        st.rerun()
    else:
        st.warning("Please fill in at least one field")

# ────────────────────────────────────────────────
# Display existing entries
# ────────────────────────────────────────────────
st.divider()

if st.session_state.assets:
    st.subheader(f"Stored Assets ({len(st.session_state.assets)})")

    for i, asset in enumerate(st.session_state.assets):
        with st.expander(
            f"{asset['category']} – {asset.get('description', asset.get('address', 'Item'))} "
            f"(${asset.get('estimated_value', asset.get('current_value', asset.get('balance', 0))):,.0f})"
        ):
            st.json(asset)

            if st.button("Delete this entry", key=f"delete_asset_{i}"):
                st.session_state.assets.pop(i)
                st.rerun()

# ────────────────────────────────────────────────
# Export
# ────────────────────────────────────────────────
st.divider()
st.subheader("Export")

if st.session_state.assets:
    df = pd.DataFrame(st.session_state.assets)

    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "Download CSV",
        csv,
        "assets_inventory.csv",
        "text/csv",
        use_container_width=True
    )

    # Simple PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 12, "Asset Inventory Report", ln=True, align="C")
    pdf.ln(10)

    for asset in st.session_state.assets:
        cat = asset["category"]
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, cat, ln=True)
        pdf.set_font("Arial", size=10)
        for k, v in asset.items():
            if k not in ["category", "added"]:
                pdf.cell(0, 6, f"{k.replace('_', ' ').title()}: {v}", ln=True)
        pdf.ln(5)

    pdf_bytes = pdf.output(dest='S').encode('latin-1')
    pdf_b64 = base64.b64encode(pdf_bytes).decode('utf-8')

    st.markdown(
        f'<a href="data:application/pdf;base64,{pdf_b64}" download="assets_inventory.pdf">'
        'Download PDF Report</a>',
        unsafe_allow_html=True
    )
else:
    st.info("No assets recorded yet.")
