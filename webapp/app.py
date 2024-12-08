import streamlit as st
import pandas as pd
from sdv.sequential import PARSynthesizer
from pyxlsb import open_workbook as open_xlsb
from io import BytesIO


# with open('webapp/synthesizer.pkl', 'rb') as f:
#     synthesizer = pickle.load(f)

synthesizer = PARSynthesizer.load(
    filepath='webapp/synthesizer.pkl'
)

@st.cache_data
def generate_data_sex(male=50, female=50, sequences=100):
    maleseq = (male/100)*sequences
    femaleseq = (female/100)*sequences
    maleseq = int(maleseq)
    femaleseq = int(femaleseq)
    scenario_context = pd.DataFrame(data={
    'Sex': ['Male']*maleseq + ['Female']*femaleseq})
    biased_sample = synthesizer.sample_sequential_columns(context_columns=scenario_context)    
    return biased_sample


def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    # workbook = writer.book
    # worksheet = writer.sheets['Sheet1']
    # format1 = workbook.add_format({'num_format': '0.00'}) 
    # worksheet.set_column('A:A', None, format1)  
    writer.close()
    processed_data = output.getvalue()
    return processed_data

biascat = st.selectbox(
    "What variable do you want to create bias in?",
    ("Sex", "Age Range", "Study Title"),
)


if biascat == "Sex":
    male = st.number_input(
    "Percentage Male", value=50, placeholder="Type a number..."
    )
    female = st.number_input(
    "Percentage Female", value=50, placeholder="Type a number..."
    )
    if male+female!=100:
        st.write("Make sure the percentages add up to 100 to continue")
    else:
        sequences = st.number_input(
        "Number of Candidates", value=100, placeholder="Type a number..."
        )
        if st.button("Generate Data"):
            st.write("Data is being Generated")
            df = generate_data_sex(male, female, sequences)
            df_xlsx = to_excel(df)
            st.download_button(
            label="Download data as Excel file",
            data=df_xlsx,
            file_name='synthetic_data.xlsx',
            mime="application/vnd.ms-excel",
            )








