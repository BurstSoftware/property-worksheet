import streamlit as st
import pandas as pd
from fpdf import FPDF
import base64
import io
from datetime import datetime

# ────────────────────────────────────────────────
# Session state
# ────────────────────────────────────────────────
if 'inventory' not in st.session_state:
    st.session_state.inventory = []

st.set_page_config(page_title="Asset Inventory", layout="wide")
st.title("Personal Asset & Digital Inventory")
st.caption("2026 edition — single-form approach • no duplicate widget errors")

# ────────────────────────────────────────────────
# Category → fields mapping
# ────────────────────────────────────────────────
CATEGORY_FIELDS = {
    "Real Estate": [
        ("address", "text", "Full address"),
        ("city_state_zip", "text", "City, State ZIP"),
        ("estimated_value", "number", "Current estimated value $"),
        ("mortgage_balance", "number", "Remaining mortgage $ (0 if none)"),
        ("notes", "textarea", "Notes / condition / liens")
    ],
    "Bank Accounts / Cash": [
        ("institution", "text", "Bank / Credit Union"),
        ("account_type", "text", "Checking / Savings / MM / CD"),
        ("last_4", "text", "Last 4 digits"),
        ("balance", "number", "Current balance $")
    ],
    "Cryptocurrency": [
        ("coin", "text", "BTC / ETH / SOL / etc"),
        ("wallet_exchange", "text", "Wallet or Exchange name"),
        ("address_key", "text", "Address / Public key"),
        ("amount", "number", "Amount held"),
        ("approx_value_usd", "number", "Approximate current value $")
    ],
    "Stocks & Investments": [
        ("ticker_symbol", "text", "Ticker (or fund name)"),
        ("shares_quantity", "number", "Shares / Units"),
        ("current_value", "number", "Total current value $")
    ],
    "Retirement Accounts": [
        ("provider", "text", "Fidelity / Vanguard / etc"),
        ("account_type", "text", "IRA / Roth IRA / 401k / 403b"),
        ("balance", "number", "Current balance $")
    ],
    "Vehicles": [
        ("make_model_year", "text", "Make Model Year"),
        ("mileage", "number", "Current mileage"),
        ("estimated_value", "number", "Estimated private sale value $")
    ],
    "Precious Metals / Collectibles / Jewelry": [
        ("type", "text", "Gold / Silver / Coins / Art / Watches..."),
        ("description", "textarea", "Description / weight / carats"),
        ("estimated_value", "number", "Current estimated value $")
    ],
    "Digital / Online Assets": [
        ("service_platform", "text", "Google / Apple / Facebook / Domain / Email..."),
        ("username", "text", "Username / Email"),
        ("notes", "textarea", "Recovery info / importance / 2FA")
    ],
    "Other / Business / Miscellaneous": [
        ("item_name", "text", "Name / Description"),
        ("estimated_value", "number", "Estimated value $"),
        ("notes", "textarea", "Additional information")
    ]
}

# ────────────────────────────────────────────────
# Single dynamic form
# ────────────────────────────────────────────────
st.subheader("Add New Item")

category = st.selectbox("Category", options=list(CATEGORY_FIELDS.keys()), index=0)

entry = {"category": category, "added": datetime.now().strftime("%Y-%m-%d %H:%M")}

fields = CATEGORY_FIELDS[category]

cols = st.columns([3, 2])

with cols[0]:
    for field_name, ftype, label in fields:
        key = f"new_entry__{category}__{field_name}"

        if ftype == "text":
            entry[field_name] = st.text_input(label, key=key)
        elif ftype == "number":
            entry[field_name] = st.number_input(
                label, min_value=0.0, step=100.0, format="%.2f", key=key
            )
        elif ftype == "textarea":
            entry[field_name] = st.text_area(label, height=85, key=key)

with cols[1]:
    st.markdown(" ")
    st.markdown(" ")
    if st.button("➕ Save Item", type="primary", use_container_width=True):
        # Minimal validation - at least something meaningful filled
        meaningful = False
        for v in entry.values():
            if isinstance(v, (int, float)) and v > 0:
                meaningful = True
            elif isinstance(v, str) and v.strip():
                meaningful = True
        if meaningful:
            st.session_state.inventory.append(entry)
            st.success("Item saved", icon="✅")
            st.rerun()
        else:
            st.error("Please fill in at least one meaningful field")

# ────────────────────────────────────────────────
# Show existing items
# ────────────────────────────────────────────────
st.divider()

if st.session_state.inventory:
    st.subheader(f"Stored Items  ({len(st.session_state.inventory)})")

    for i, item in enumerate(st.session_state.inventory):
        cat = item["category"]
        value_field = next((k for k in item if "value" in k.lower() or "balance" in k.lower()), None)
        title_value = f"${item.get(value_field, 0):,.0f}" if value_field else ""

        with st.expander(f"{cat} – {title_value}", expanded=False):
            st.json(item)

            col_left, col_right = st.columns([8, 2])
            with col_right:
                if st.button("Delete", key=f"del_{i}", type="secondary"):
                    st.session_state.inventory.pop(i)
                    st.rerun()

# ────────────────────────────────────────────────
# Export
# ────────────────────────────────────────────────
st.divider()
st.subheader("Export")

if st.session_state.inventory:
    df = pd.DataFrame(st.session_state.inventory)

    st.download_button(
        label="Download as CSV",
        data=df.to_csv(index=False).encode('utf-8'),
        file_name="asset_inventory.csv",
        mime="text/csv"
    )

    # Simple PDF export
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Asset Inventory - " + datetime.now().strftime("%Y-%m-%d"), ln=True, align="C")

    for item in st.session_state.inventory:
        pdf.ln(6)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, item["category"], ln=True)
        pdf.set_font("Arial", "", 10)

        for k, v in item.items():
            if k not in ["category", "added"]:
                pdf.multi_cell(0, 6, f"{k.replace('_',' ').title()}: {v}")

    pdf_bytes = pdf.output(dest='S').encode('latin-1')
    pdf_b64 = base64.b64encode(pdf_bytes).decode()

    st.markdown(
        f'<a href="data:application/pdf;base64,{pdf_b64}" download="asset_inventory.pdf">'
        'Download PDF</a>',
        unsafe_allow_html=True
    )
else:
    st.info("No items added yet")
