import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import base64
import io

# ────────────────────────────────────────────────
# Session state
# ────────────────────────────────────────────────
if 'assets' not in st.session_state:
    st.session_state.assets = []

st.set_page_config(page_title="Asset Inventory", layout="wide")
st.title("Asset & Digital Inventory")
st.markdown("Single-form entry — no duplicate widget errors")

# ────────────────────────────────────────────────
# Define categories and their fields
# ────────────────────────────────────────────────
FORM_SCHEMAS = {
    "Real Estate": [
        ("address", "text", "Address"),
        ("city_state_zip", "text", "City, State ZIP"),
        ("value", "number", "Estimated value $"),
        ("notes", "textarea", "Notes")
    ],
    "Bank Accounts / Cash": [
        ("bank", "text", "Bank name"),
        ("account_type", "text", "Type (checking/savings/etc)"),
        ("balance", "number", "Balance $")
    ],
    "Cryptocurrency": [
        ("coin", "text", "Coin"),
        ("wallet", "text", "Wallet/Exchange"),
        ("amount", "number", "Amount"),
        ("value_usd", "number", "Approx value $")
    ],
    "Stocks & Investments": [
        ("symbol", "text", "Ticker/Symbol"),
        ("quantity", "number", "Shares/Units"),
        ("value", "number", "Current value $")
    ],
    "Retirement Accounts": [
        ("provider", "text", "Provider"),
        ("type", "text", "IRA / Roth / 401k / ..."),
        ("balance", "number", "Balance $")
    ],
    "Vehicles & Boats": [
        ("make_model_year", "text", "Make Model Year"),
        ("value", "number", "Estimated value $")
    ],
    "Personal Property": [
        ("description", "textarea", "Description"),
        ("value", "number", "Estimated value $")
    ],
    "Digital Assets / Accounts": [
        ("service", "text", "Platform/Service"),
        ("username", "text", "Username/Email"),
        ("notes", "textarea", "Notes / recovery info")
    ],
    "Other / Business": [
        ("description", "textarea", "Description"),
        ("value", "number", "Value $"),
        ("notes", "textarea", "Notes")
    ]
}

# ────────────────────────────────────────────────
# Single dynamic form
# ────────────────────────────────────────────────
st.subheader("Add new item")

category = st.selectbox("Category", options=list(FORM_SCHEMAS.keys()))

entry = {"category": category, "added": datetime.now().strftime("%Y-%m-%d %H:%M")}

for field_name, field_type, label in FORM_SCHEMAS[category]:
    key = f"new__{category}__{field_name}"

    if field_type == "text":
        entry[field_name] = st.text_input(label, key=key)
    elif field_type == "number":
        entry[field_name] = st.number_input(label, min_value=0.0, key=key)
    elif field_type == "textarea":
        entry[field_name] = st.text_area(label, height=88, key=key)

if st.button("Save item", type="primary"):
    # Minimal validation
    if any(v for v in entry.values() if v not in (None, "", 0.0)):
        st.session_state.assets.append(entry)
        st.success("Item saved")
        st.rerun()
    else:
        st.warning("Please fill at least one field")

# ────────────────────────────────────────────────
# Show existing items
# ────────────────────────────────────────────────
st.divider()

if st.session_state.assets:
    st.subheader(f"Recorded items ({len(st.session_state.assets)})")

    for i, item in enumerate(st.session_state.assets):
        with st.expander(f"{item['category']} • {item.get('value', item.get('balance', '—'))}", expanded=False):
            st.json(item)
            if st.button("Delete", key=f"del__{i}"):
                st.session_state.assets.pop(i)
                st.rerun()

# ────────────────────────────────────────────────
# Export
# ────────────────────────────────────────────────
st.divider()

if st.session_state.assets:
    df = pd.DataFrame(st.session_state.assets)

    st.download_button(
        "Download CSV",
        df.to_csv(index=False).encode('utf-8'),
        "assets.csv",
        "text/csv"
    )

    # Very basic PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Asset Inventory", ln=True, align="C")

    for item in st.session_state.assets:
        pdf.ln(5)
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 8, item["category"], ln=True)
        pdf.set_font("Arial", "", 10)
        for k, v in item.items():
            if k not in ("category", "added"):
                pdf.multi_cell(0, 6, f"{k}: {v}")

    pdf_bytes = pdf.output(dest='S').encode('latin-1')
    pdf_b64 = base64.b64encode(pdf_bytes).decode()
    st.markdown(
        f'<a href="data:application/pdf;base64,{pdf_b64}" download="assets.pdf">Download PDF</a>',
        unsafe_allow_html=True
    )

else:
    st.info("No items added yet")
