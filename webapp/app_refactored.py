import streamlit as st
import pandas as pd
from sdv.sequential import PARSynthesizer
from sdv.sampling import Condition
from io import BytesIO

# Configurations
CONFIG = {
    "bias_options": ["None", "Sex", "Age Range", "Study Title"],
    "defaults": {
        "Sex": {"Male": 50, "Female": 50},
        "Age Range": {
            "< 20 years": 8,
            "20-25 years": 27,
            "26-30 years": 46,
            "31-35 years": 9,
            "36-40 years": 4,
            "40-45 years": 2,
            "> 45 years": 4,
        },
        "Study Title": {
            "Middle school diploma": 0,
            "High school graduation": 4,
            "Three-year degree": 39,
            "Five-year degree": 53,
            "master's degree": 2,
            "Doctorate": 1,
            "Professional qualification": 1,
        },
    },
}

# Generalized functions
def generate_bias_inputs(category_names, default_values):
    percentages = {}
    for category, default_value in zip(category_names, default_values):
        percentages[category] = st.number_input(
            f"Percentage {category}", value=default_value, placeholder="Type a number..."
        )
    return percentages


@st.cache_data
def create_context(column_name, category_percentages, num_rows):
    rows = []
    for category, percentage in category_percentages.items():
        rows.extend([category] * int((percentage / 100) * num_rows))
    return pd.DataFrame({column_name: rows})


@st.cache_data
def generate_data_generalized(_synthesizer, column_name, category_percentages, num_sequences, is_sequential=False):
    if is_sequential:
        context_df = create_context(column_name, category_percentages, num_sequences)
        generated_data = _synthesizer.sample_sequential_columns(context_columns=context_df)
    else:
        conditions = [
            Condition(
                num_rows=int((percentage / 100) * num_sequences),
                column_values={column_name: category},
            )
            for category, percentage in category_percentages.items()
        ]
        generated_data = _synthesizer.sample_from_conditions(conditions=conditions)
    return generated_data


@st.cache_data
def generate_data_no_bias(_synthesizer, num_sequences, is_sequential=False):
    if is_sequential:
        return _synthesizer.sample(num_sequences=num_sequences)
    return _synthesizer.sample(num_rows=num_sequences)


def get_dataset_size_input(label, default_value=150):
    return st.number_input(label, value=default_value, placeholder="Type a number...")


def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine="xlsxwriter")
    df.to_excel(writer, index=False)
    writer.close()
    processed_data = output.getvalue()
    return processed_data


# Load the synthesizers
synthesizer_sin = PARSynthesizer.load(filepath="webapp/synthesizer_sin.pkl")
synthesizer_seq = PARSynthesizer.load(filepath="webapp/synthesizer_seq_1000_nocuda.pkl")

# Streamlit UI
st.title("Synthetic Data Generator")
st.write(
    "Select a type of model, the variable to create a bias for (optional), "
    "pick a number of candidates or rows to be generated, and get an Excel file at the press of a button."
)

st.subheader("Model Selection")
model = st.selectbox(
    "Select the type of data synthesizer",
    ["Single (only candidates)", "Sequential (candidates and events)"],
)

is_sequential = model == "Sequential (candidates and events)"
synthesizer = synthesizer_seq if is_sequential else synthesizer_sin

st.subheader("Bias Selection (optional)")
biascat = st.selectbox("Select the variable you want to introduce bias for", CONFIG["bias_options"])

if biascat == "None":
    num_sequences = get_dataset_size_input("Enter the number of rows to generate")
    if st.button("Generate Data"):
        st.write("Generating unbiased data...")
        df = generate_data_no_bias(synthesizer, num_sequences, is_sequential)
        df_xlsx = to_excel(df)
        st.download_button(
            label="Download data as Excel file",
            data=df_xlsx,
            file_name="synthetic_data.xlsx",
            mime="application/vnd.ms-excel",
        )
else:
    category_percentages = generate_bias_inputs(
        category_names=list(CONFIG["defaults"][biascat].keys()),
        default_values=list(CONFIG["defaults"][biascat].values()),
    )
    if sum(category_percentages.values()) != 100:
        st.write(f"The percentages add up to {sum(category_percentages.values())}%. Make sure they add up to 100% to continue.")
    else:
        num_sequences = get_dataset_size_input("Enter the number of rows to generate")
        if st.button("Generate Data"):
            st.write(f"Generating biased data for {biascat}...")
            df = generate_data_generalized(
                synthesizer,
                column_name=biascat,
                category_percentages=category_percentages,
                num_sequences=num_sequences,
                is_sequential=is_sequential,
            )
            df_xlsx = to_excel(df)
            st.download_button(
                label="Download data as Excel file",
                data=df_xlsx,
                file_name="synthetic_data.xlsx",
                mime="application/vnd.ms-excel",
            )
