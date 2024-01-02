import streamlit as st
import pandas as pd
import numpy as np 
from datetime import datetime
import os
import warnings
warnings.filterwarnings('ignore')


st.set_page_config(page_title="Timesheets Converter", page_icon="bar_chart:", layout="wide")

st.title("Timesheet Converter")
st.markdown('<style>div.block-container{padding-top:1rem}</style>', unsafe_allow_html=True)

f1 = st.file_uploader(":file_folder: Upload a file", type=(["xlsx", "xls"]))

if f1 is not None:
    filename = f1.name
    st.write(filename)
    file = pd.read_excel(f1)

    Code = file.iloc[0,1]
    Employee = file.iloc[0,6]
    df = file[~file.iloc[:,0].isna()]
    df1 = df.iloc[:, [0,5,9,14,16,21]]
    df1.columns = df1.iloc[1,:]

    df1 = df1[df1['Client ']!='Code:']
    df1 = df1[df1['Client ']!="Client "]

    df1 = df1.fillna(0)
    df1.reset_index(drop=True, inplace=True)

    #del df1['index']

    column_to_check = df1.iloc[:, 0]


    condition = ~column_to_check.astype(str).str.contains(r'Printed On', case=False, na=False)
    condition_2 = ~column_to_check.astype(str).str.contains(r"Timesheet for the period", case=False, na=False)


    df1 = df1[condition]
    df1 = df1[condition_2]

    df1 = df1[df1['Hours']!=float]
    df1['Hours'].astype(float)


    df1 = df1[df1['Client ']!="Total For Chargeable Time"]


    ab = pd.DataFrame(columns=['Name', 'Date', 'Client_name', 'Client_code', 'Service', 'Job', 'Task', 'Analysis', 'Hours', 'Description'])


    date = None
    for i in range(len(df1)):
        x = df1.iloc[i,:]
        if (type(x.iloc[0]) == datetime):
            date = x.iloc[0]
            dt_object = datetime.strptime(str(date), '%Y-%m-%d %H:%M:%S')
            date = dt_object.strftime('%d-%m-%Y')
        elif x.iloc[-1]==0:
            ab.loc[i-1,"Client_name"] = x.iloc[0]
            ab.loc[i-1,"Description"] = x.iloc[2]
        else:
            ab.loc[i,"Name"] = Employee
            ab.loc[i, 'Date'] = date
            ab.loc[i, "Client_code"] = x.iloc[0]
            ab.loc[i,"Service"] = x.iloc[1]
            ab.loc[i, "Job"] = x.iloc[2]
            ab.loc[i, "Task"] = x.iloc[3]
            ab.loc[i, "Analysis"] = x.iloc[4]
            ab.loc[i, "Hours"] = x.iloc[5]
            
            


    ab = ab[~ab['Client_name'].isna()]
    ab = ab[~ab["Service"].isna()]

    ab.reset_index(drop=True, inplace=True)
    ab.index +=1

    ab['Job/Tasks'] = ab['Job'].str.cat(ab['Task'].astype(str), sep='/')
    ab['Services/Analysis'] = ab['Service'].str.cat(ab['Analysis'], sep='/')
    ab.drop(['Service', 'Task', 'Analysis', 'Job'], axis=1, inplace=True)


    cols_order = ['Name', 'Date', 'Client_name', 'Client_code', 'Job/Tasks',
        'Services/Analysis', 'Description', 'Hours']

    final_df = ab.reindex(columns=cols_order)
    st.subheader("Top 10 Rows:")
    st.dataframe(final_df.head(10))

# Display the bottom 10 rows
    st.subheader("Bottom 10 Rows:")
    st.dataframe(final_df.tail(10))

    sum = round(final_df['Hours'].sum(),3)

    st.subheader("Total Sums of Hours:")
    styled_sum = f"<span style='font-size: 32px; color: red;'>{sum}</span>"
    st.markdown(styled_sum, unsafe_allow_html=True)

    if st.button("Download Data as Excel"):
        csv = final_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Data", data = csv, file_name = "Data.csv", mime = 'text/csv')


