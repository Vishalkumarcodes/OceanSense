import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import os
import matplotlib.pyplot as plt
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL') or 'postgresql://postgres:vishal2002@localhost:5432/oceandatabase'
engine = create_engine(DATABASE_URL)

st.set_page_config(page_title='OceanSense Analytics', layout='wide')
st.title('OceanSense — Analytics')

@st.cache_data
def load_issues():
    try:
        return pd.read_sql('select id,title,severity,status,created_at from issues order by created_at desc', engine)
    except Exception as e:
        st.error('Could not load issues: '+str(e))
        return pd.DataFrame()

df = load_issues()
st.dataframe(df)

if not df.empty:
    counts = df['severity'].value_counts()
    fig, ax = plt.subplots()
    counts.plot(kind='bar', ax=ax)
    ax.set_xlabel('Severity')
    ax.set_ylabel('Count')
    st.pyplot(fig)

    df['created_at'] = pd.to_datetime(df['created_at'])
    ts = df.set_index('created_at').resample('D').size()
    fig2, ax2 = plt.subplots()
    ts.plot(ax=ax2)
    ax2.set_title('Reports per day')
    st.pyplot(fig2)
