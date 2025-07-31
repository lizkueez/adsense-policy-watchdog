import streamlit as st
import pandas as pd
import openai
import os

# Set page config
st.set_page_config(
    page_title="AdSense Policy Watchdog — GPT-4o Compliance Scanner",
    layout="wide"
)

# Title
st.title("🎯 AdSense Policy Watchdog — GPT-4o Compliance Scanner")
st.markdown("Upload your ad CSV. We'll analyze each headline + message using GPT-4o and Google AdSense rules.")

# Upload file
uploaded_file = st.file_uploader("📁 Upload your ad CSV file", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()

    # Show detected columns
    with st.expander("🧪 Detected Columns"):
        st.code(df.columns.tolist())

    required_columns = ["Ad Creative Headline", "Ad CreativeMessage", "Search ROI"]
    missing = [col for col in required_columns if col not in df.columns]

    if missing:
        st.error(f"❌ Your CSV must include: {', '.join(required_columns)}")
        st.stop()

    st.success("✅ CSV looks good! Scanning for violations...")

    openai.api_key = os.getenv("OPENAI_API_KEY")

    def check_policy_compliance(headline, message):
        prompt = f"""You're an AdSense compliance expert. Analyze this ad content based on Google's AdSense policies.
Headline: {headline}
Message: {message}
Does this violate any AdSense content policies? Respond clearly with 'Compliant' or 'Violation: <reason>'."""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error: {str(e)}"

    results = []
    for _, row in df.iterrows():
        result = check_policy_compliance(row["Ad Creative Headline"], row["Ad CreativeMessage"])
        results.append(result)

    df["GPT Result"] = results

    # Display results
    st.subheader("📋 Compliance Results")
    st.dataframe(df[["Ad Creative Headline", "Ad CreativeMessage", "GPT Result"]], use_container_width=True)

    # Download results
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download Results CSV", csv, "compliance_results.csv", "text/csv")
