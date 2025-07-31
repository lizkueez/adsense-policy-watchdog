import streamlit as st
import pandas as pd
import openai
import os

# Load API key from secrets.toml
openai.api_key = st.secrets["OPENAI_API_KEY"]

st.title("🧠 Ad Compliance Checker")

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

def check_violation(headline, message):
    prompt = f"""
You are an ad compliance assistant. Your job is to determine whether the following headline and message violate advertising policies.

Headline: {headline}
Message: {message}

Respond with one of the following:
- OK if there’s nothing wrong
- WARNING if something might be questionable
- VIOLATION if it clearly violates ad policies

Provide a 1-sentence reason after your verdict.
"""

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {str(e)}"

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.success("CSV looks good! Scanning for violations...")

    results = []
    for i, row in df.iterrows():
        headline = row.get("Ad Creative Headline", "")
        message = row.get("Ad CreativeMessage", "")
        st.write(f"🔍 Scanning row {i+1}: {headline[:40]}...")
        result = check_violation(headline, message)
        results.append(result)

    df["GPT Result"] = results
    st.subheader("📋 Compliance Results")
    st.dataframe(df[["Ad Creative Headline", "Ad CreativeMessage", "GPT Result"]])

    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Results", data=csv, file_name="compliance_results.csv", mime="text/csv")
