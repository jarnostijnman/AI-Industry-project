import streamlit as st
import pandas as pd
from sdv.sequential import PARSynthesizer
from io import BytesIO

@st.cache_data
def sequencefraq(var, sequences):
    if var == 0:
        return 0
    return int((var/100)*sequences)

@st.cache_data
def generate_data_no_bias(sequences=150):
    synthetic_data = synthesizer.sample(num_sequences=sequences,sequence_length=None)
    return synthetic_data

@st.cache_data
def generate_data_sex(male=50, female=50, sequences=150):
    maleseq = sequencefraq(male, sequences)
    femaleseq = sequencefraq(female, sequences)
    scenario_context = pd.DataFrame(data={
    'Sex': ['Male']*maleseq + ['Female']*femaleseq})
    biased_sample = synthesizer.sample_sequential_columns(context_columns=scenario_context)    
    return biased_sample

@st.cache_data
def generate_data_age_range(age1=9, age2=20, age3=46, age4=12, age5=5, age6=3, age7=5, sequences=150):
    age1seq = sequencefraq(age1, sequences)
    age2seq = sequencefraq(age2, sequences) 
    age3seq = sequencefraq(age3, sequences)
    age4seq = sequencefraq(age4, sequences)
    age5seq = sequencefraq(age5, sequences)
    age6seq = sequencefraq(age6, sequences)
    age7seq = sequencefraq(age7, sequences)
    scenario_context = pd.DataFrame(data={
    'Age Range':    ['< 20 years']    * age1seq + 
                    ['20 - 25 years'] * age2seq +
                    ['26 - 30 years'] * age3seq +
                    ['31 - 35 years'] * age4seq +
                    ['36 - 40 years'] * age5seq +
                    ['40 - 45 years'] * age6seq +
                    ['> 45 years']    * age7seq
                    })
    biased_sample = synthesizer.sample_sequential_columns(context_columns=scenario_context)    
    return biased_sample

@st.cache_data
def generate_data_study_title(study1=0, study2=4, study3=39, study4=53, study5=2, study6=1, study7=1, sequences=150):
    study1seq = sequencefraq(study1, sequences)
    study2seq = sequencefraq(study2, sequences) 
    study3seq = sequencefraq(study3, sequences)
    study4seq = sequencefraq(study4, sequences)
    study5seq = sequencefraq(study5, sequences)
    study6seq = sequencefraq(study6, sequences)
    study7seq = sequencefraq(study7, sequences)
    scenario_context = pd.DataFrame(data={
    'Study Title':    ['Middle school diploma']    * study1seq + 
                    ['High school graduation']   * study2seq +
                    ['Three-year degree']        * study3seq +
                    ['Five-year degree']         * study4seq +
                    ["master's degree"]          * study5seq +
                    ['Doctorate']                * study6seq +
                    ['Professional qualification']    * study7seq
                    })
    biased_sample = synthesizer.sample_sequential_columns(context_columns=scenario_context)    
    return biased_sample

def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False)
    # workbook = writer.book
    # worksheet = writer.sheets['Sheet1']
    # format1 = workbook.add_format({'num_format': '0.00'}) 
    # worksheet.set_column('A:A', None, format1)  
    writer.close()
    processed_data = output.getvalue()
    return processed_data

#Load the SDV synthesizer
synthesizer = PARSynthesizer.load(
    filepath='webapp/synthesizer_1000_nocuda.pkl'
)

#Start of Webpage
st.title("Synthetic Data Generator")
st.write("Select a variable to create a bias (optional), pick a number of candidates to be generated and get an Excel file at the press of a button.")
st.subheader("Bias Selection (optional)")

biascat = st.selectbox(
    "**Select the variable you want to introduce bias for**",
    ("None", "Sex", "Age Range", "Study Title"),
)

if biascat == "None":
    st.subheader("Dataset Size Selection")
    sequences = st.number_input(
    "**Enter the number of candidates you want to include in the file**", value=150, placeholder="Type a number..."
    )
    if st.button("Generate Data"):
        st.write("Data is being Generated")
        df = generate_data_no_bias(sequences)
        df_xlsx = to_excel(df)
        st.download_button(
        label="Download data as Excel file",
        data=df_xlsx,
        file_name='synthetic_data.xlsx',
        mime="application/vnd.ms-excel",
        )

if biascat == "Sex":
    st.markdown("**Adjust percentages per sex** (default is the estimated source distribution)")
    male = st.number_input(
    "Percentage Male", value=77, placeholder="Type a number..."
    )
    female = st.number_input(
    "Percentage Female", value=23, placeholder="Type a number..."
    )
    sexsum = male+female
    if sexsum!=100:
        st.write(f"The percentages add up to {sexsum}%")
        st.write("Make sure the percentages add up to 100 to continue")
    else:
        st.subheader("Dataset Size Selection")
        sequences = st.number_input(
        "**Enter the number of candidates you want to include in the file**", value=150, placeholder="Type a number..."
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

if biascat == "Age Range":
    st.markdown("**Adjust percentages per age group** (default is the estimated source distribution)")
    age1 = st.number_input(
    "Percentage < 20 years", value=8, placeholder="Type a number..."
    )
    age2 = st.number_input(
    "Percentage 20-25 years", value=27, placeholder="Type a number..."
    )
    age3 = st.number_input(
    "Percentage 26-30 years", value=46, placeholder="Type a number..."
    )
    age4 = st.number_input(
    "Percentage 31-35 years", value=9, placeholder="Type a number..."
    )
    age5 = st.number_input(
    "Percentage 36-40 years", value=4, placeholder="Type a number..."
    )
    age6 = st.number_input(
    "Percentage 40-45 years", value=2, placeholder="Type a number..."
    )
    age7 = st.number_input(
    "Percentage > 45 years", value=4, placeholder="Type a number..."
    )
    agesum = age1+age2+age3+age4+age5+age6+age7
    if agesum!=100:
        st.write(f"The percentages add up to {agesum}%")
        st.write("Make sure the percentages add up to 100% to continue")
    else:
        st.subheader("Dataset Size Selection")
        sequences = st.number_input(
        "**Enter the number of candidates you want to include in the file**", value=150, placeholder="Type a number..."
        )
        if st.button("Generate Data"):
            st.write("Data is being Generated")
            df = generate_data_age_range(age1, age2, age3, age4, age5, age6, age7, sequences)
            df_xlsx = to_excel(df)
            st.download_button(
            label="Download data as Excel file",
            data=df_xlsx,
            file_name='synthetic_data.xlsx',
            mime="application/vnd.ms-excel",
            )

if biascat == "Study Title":
    st.markdown("**Adjust percentages per study title group** (default is the estimated source distribution)")
    study1 = st.number_input(
    "Percentage Middle school ", value=0, placeholder="Type a number..."
    )
    study2 = st.number_input(
    "Percentage High school", value=4, placeholder="Type a number..."
    )
    study3 = st.number_input(
    "Percentage Three-year degree", value=39, placeholder="Type a number..."
    )
    study4 = st.number_input(
    "Percentage Five-year degree", value=53, placeholder="Type a number..."
    )
    study5 = st.number_input(
    "Percentage Master's degree", value=2, placeholder="Type a number..."
    )
    study6 = st.number_input(
    "Percentage Doctorate", value=1, placeholder="Type a number..."
    )
    study7 = st.number_input(
    "Percentage Professional qualification", value=1, placeholder="Type a number..."
    )
    studysum = study1+study2+study3+study4+study5+study6+study7
    if studysum!=100:
        st.write(f"The percentages add up to {studysum}%")
        st.write("Make sure the percentages add up to 100% to continue")
    else:
        st.subheader("Dataset Size Selection")
        sequences = st.number_input(
        "**Enter the number of candidates you want to include in the file**", value=150, placeholder="Type a number..."
        )
        if st.button("Generate Data"):
            st.write("Data is being Generated")
            df = generate_data_study_title(study1, study2, study3, study4, study5, study6, study7, sequences)
            df_xlsx = to_excel(df)
            st.download_button(
            label="Download data as Excel file",
            data=df_xlsx,
            file_name='synthetic_data.xlsx',
            mime="application/vnd.ms-excel",
            )







