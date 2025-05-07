# app.py

import streamlit as st
from openai import OpenAI
import base64
from pathlib import Path
import os

# Set your OpenAI API Key securely via Streamlit secrets or environment variable
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"] if "OPENAI_API_KEY" in st.secrets else os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

JSON_FORMAT_TEMPLATE = """
{
  "invoice_no": "string",
  "status": "yes/no",
  "supplier": "string",
  "invoice_date": "MM/dd/yyyy",
  "payment_terms": "string",
  "payment_due_date": "MM/dd/yyyy",
  "delivery_receipt_no": "string",
  "delivery_receipt_date": "MM/dd/yyyy",
  "eta": "MM/dd/yyyy",
  "currency": "string",
  "shipping_detail": "string",
  "remarks": "string",
  "items": [
    {
      "po_number": "string",
      "material": "string",
      "price": float,
      "discount": float,
      "qty_ordered": int,
      "qty_invoiced": int,
      "qty_delivered": int,
      "amount": float
    }
  ]
}
"""

SYSTEM_PROMPT = (
    "You are an AI that extracts structured data from invoice forms. "
    "Given an image of an invoice and a template with data types, return the populated JSON. "
    "If some field values are unfulfilled leave them blank."
)

# --- Streamlit UI ---
st.title("Cody ERP OCR Invoice to JSON POC")

uploaded_file = st.file_uploader("Upload an invoice image", type=["png", "jpg", "jpeg", "webp"])

if uploaded_file:
    st.image(uploaded_file, caption="Uploaded Invoice", use_column_width=True)

    # Read file and encode in base64
    image_bytes = uploaded_file.read()
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    with st.spinner("Extracting invoice data..."):
        response = client.chat.completions.create(
            model="gpt-4o",  # Or use "gpt-4o-mini"
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Here is the template with data types:\n{JSON_FORMAT_TEMPLATE}"},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{image_b64}"}
                        }
                    ]
                }
            ],
            temperature=0.2,
        )

        extracted_json = response.choices[0].message.content
        st.success("✅ Data Extracted")
        st.code(extracted_json, language="json")
