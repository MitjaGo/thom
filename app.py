import streamlit as st
import pandas as pd

st.title("🎸 Squier Affinity Telecaster Dashboard")

try:
    reg = pd.read_csv("data_regular.csv")
except:
    reg = pd.DataFrame()

try:
    bst = pd.read_csv("data_bstock.csv")
except:
    bst = pd.DataFrame()

st.header("🟢 Regular Stock")
if reg.empty:
    st.write("No models found.")
else:
    st.dataframe(reg)

st.header("🟡 B-Stock")
if bst.empty:
    st.write("No B-Stock found.")
else:
    st.dataframe(bst)


    
