import streamlit as st
import pandas as pd
from openai import OpenAI
import os

st.set_page_config(
    page_title="AdSense Policy Watchdog",
    layout="wide"
)

st.title("🎯 AdSense Policy Watchdog — GPT-4o Compliance Scanner")
st.markdown("Upload your ad CSV. We'll analyze each headline + message using GPT-4o and Google AdSense rules.")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

uploaded_file = st.file_uploader("📄 Upload your ad CSV file", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()

    st.subheader("🧾 Detected Columns")
    st.code(df.columns.tolist())

    required_columns = ["Ad Creative Headline", "Ad CreativeMessage", "Search ROI"]

    if all(col in df.columns for col in required_columns):
        st.success("✅ CSV looks good! Scanning for violations...")

        def check_policy_compliance(headline, message):
            prompt = f"""You're an AdSense compliance expert. Analyze this ad content based on Google's AdSense policies.
Headline: {headline}
Message: {message}
Does this violate any AdSense content policies? Respond clearly with 'Compliant' or 'Violation: <reason>'."""

            try:
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.2,
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                return f"Error: {str(e)}"

        st.subheader("📋 Compliance Results")
        results = []

        for i, row in df.iterrows():
            headline = row["Ad Creative Headline"]
            message = row["Ad CreativeMessage"]
            result = check_policy_compliance(headline, message)
            results.append(result)

        df["GPT Result"] = results
        st.dataframe(df[["Ad Creative Headline", "Ad CreativeMessage", "GPT Result"]])

    else:
        st.error("❌ Your CSV must include: Ad Creative Headline, Ad Creative Message, and Search ROI")
