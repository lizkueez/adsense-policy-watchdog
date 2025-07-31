import streamlit as st
import pandas as pd
import openai

st.set_page_config(page_title="AdSense Policy Watchdog", page_icon="🎯", layout="wide")

st.title("🎯 AdSense Policy Watchdog — GPT-4o Compliance Scanner")
st.markdown("Upload your ad CSV. We'll analyze each headline + message using GPT-4o and Google AdSense rules.")

openai.api_key = st.secrets["OPENAI_API_KEY"]

uploaded_file = st.file_uploader("📁 Upload your ad CSV file", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()
    st.subheader("🧪 Detected Columns")
    st.write(list(df.columns))

    required_columns = ["Ad Creative Headline", "Ad CreativeMessage", "Search ROI"]
    missing = [col for col in required_columns if col not in df.columns]

    if missing:
        st.error(f"❌ Your CSV must include: {', '.join(required_columns)}")
    else:
        st.success("✅ CSV looks good! Scanning for violations...")
        df = df.sort_values(by="Search ROI", ascending=False)

        results = []
        for _, row in df.iterrows():
            prompt = f"""You're an ad compliance reviewer. Check the ad below for Google AdSense violations (clickbait, misleading, unsupported, sensitive content).
Respond with ✅ or ❌ and explain briefly.

Headline: {row['Ad Creative Headline']}
Message: {row['Ad CreativeMessage']}
"""
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3
                )
                result = response["choices"][0]["message"]["content"]
                results.append({
                    "Headline": row["Ad Creative Headline"],
                    "Message": row["Ad CreativeMessage"],
                    "Result": result
                })
            except Exception as e:
                results.append({
                    "Headline": row["Ad Creative Headline"],
                    "Message": row["Ad CreativeMessage"],
                    "Result": f"❌ Error: {e}"
                })

        st.subheader("📋 Compliance Results")
        st.dataframe(pd.DataFrame(results))
