import streamlit as st
import pandas as pd
from sdv.sequential import PARSynthesizer
from sdv.single_table import GaussianCopulaSynthesizer
from io import BytesIO
from sdv.sampling import Condition


 #Functions used in webapp for:
 #1) Calculating the number of sequences the synthesizer needs to generate per variable;
 #2) Synthetic data generation (one per variable);
 #3) Converting the df to an Excel file suitable for downloading through the Streamlit UI.
 

@st.cache_data
def sequencefraq(var, sequences):
    if var == 0:
        return 0
    return int((var/100)*sequences)

@st.cache_data
def generate_data_no_bias(sequences=150):
    synthetic_data = synthesizer_seq.sample(num_sequences=sequences,sequence_length=None)
    return synthetic_data

@st.cache_data
def generate_data_sex(model, male=50, female=50, sequences=150):
    maleseq = sequencefraq(male, sequences)
    femaleseq = sequencefraq(female, sequences)
    scenario_context = pd.DataFrame(data={
    'Sex': ['Male']*maleseq + ['Female']*femaleseq})
    biased_sample = synthesizer_seq.sample_sequential_columns(context_columns=scenario_context)    
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
    biased_sample = synthesizer_seq.sample_sequential_columns(context_columns=scenario_context)    
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
    biased_sample = synthesizer_seq.sample_sequential_columns(context_columns=scenario_context)    
    return biased_sample

@st.cache_data
def generate_data_single(custom_synthesizer, column_name, category_percentages, num_rows):
    """
    Generate simulated synthetic data based on user-defined column, percentages, and number of rows.
    
    Parameters:
    - custom_synthesizer: A trained SDV synthesizer object.
    - column_name (str): The name of the column to condition the data on.
    - category_percentages (dict): Dictionary where keys are category names and values are percentages (0-100).
    - num_rows (int): Total number of rows to generate.
    
    Returns:
    - pandas.DataFrame: The simulated synthetic data.
    """
    
    # Calculate rows per category
    category_conditions = []
    for category, percentage in category_percentages.items():
        rows_for_category = int((percentage / 100) * num_rows)
        category_conditions.append(Condition(
            num_rows=rows_for_category,
            column_values={column_name: category}
        ))
    
    # Generate synthetic data using the conditions
    simulated_synthetic_data = custom_synthesizer.sample_from_conditions(conditions=category_conditions)
    
    return simulated_synthetic_data

@st.cache_data
def generate_unbiased_single(num_rows=150):
    return synthesizer_sin.sample(num_rows=num_rows)

def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False)
    writer.close()
    processed_data = output.getvalue()
    return processed_data



#Load the SDV synthesizer (single table)
synthesizer_sin = PARSynthesizer.load(
    filepath='webapp/synthesizer_sin.pkl'
)

#Load the SDV synthesizer (sequential)
synthesizer_seq = PARSynthesizer.load(
    filepath='webapp/synthesizer_seq_1000_nocuda.pkl'
)

#Start of interface

st.title("Synthetic Data Generator")
st.write("Select a type of model, the variable to create a bias for (optional), pick a number of candidates or rows to be generated and get an Excel file at the press of a button.")

st.subheader("Model Selection")
model  = st.pills("Select the type of data synthesizer", ["Single (only candidates)", "Sequential (candidates and events)"], selection_mode="single")

# Dynamic part of interface based on selected variables
if model == "Single (only candidates)":
    st.subheader("Bias Selection (optional)")

    biascat = st.selectbox(
        "**Select the variable you want to introduce bias for**",
        ("None", "Sex", "Age Range", "Study Title"),
)
    if biascat == "None":
        st.subheader("Dataset Size Selection")
        num_rows = st.number_input(
        "**Enter the number of rows you want in the file**", value=150, placeholder="Type a number..."
        )
        if st.button("Generate Data"):
            st.write("Data is being Generated")
            df = generate_unbiased_single(num_rows)
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
            num_rows = st.number_input(
            "**Enter the number of rows you want in the file**", value=150, placeholder="Type a number..."
            )
            if st.button("Generate Data"):
                column_name = 'Sex'
                category_percentages = {'Male': male, 'Female': female}
                st.write("Data is being Generated")
                df = generate_data_single(synthesizer_sin, column_name, category_percentages, num_rows)
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
            num_rows = st.number_input(
            "**Enter the number of rows you want in the file**", value=150, placeholder="Type a number..."
            )
            if st.button("Generate Data"):
                column_name = 'Age Range'
                category_percentages = {'< 20 years': age1, '20 - 25 years': age2,'26 - 30 years': age3, '31 - 35 years': age4,'36 - 40 years': age5, '40 - 45 years': age6,'> 45 years':age7}
                st.write("Data is being Generated")
                df = generate_data_single(synthesizer_sin, column_name, category_percentages, num_rows)
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
            num_rows = st.number_input(
            "**Enter the number of rows you want in the file**", value=150, placeholder="Type a number..."
            )
            if st.button("Generate Data"):
                column_name = 'Study Title'
                category_percentages = {'Middle school diploma': study1, 'High school graduation': study2,'Three-year degree': study3, 'Five-year degree': study4,"master's degree": study5, 'Doctorate': study6,'Professional qualification':study7}
                st.write("Data is being Generated")
                df = generate_data_single(synthesizer_sin, column_name, category_percentages, num_rows)
                df_xlsx = to_excel(df)
                st.download_button(
                label="Download data as Excel file",
                data=df_xlsx,
                file_name='synthetic_data.xlsx',
                mime="application/vnd.ms-excel",
                )

if model == "Sequential (candidates and events)":
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





