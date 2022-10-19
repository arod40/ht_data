import streamlit as st
import os
import requests

st.title("Posts Similarity Tagger!!")

backend_base = os.getenv("BACKEND_SERVER")
print(backend_base)


# def request(endpoint, method, payload, headers):

#     url = f"{backend_base}/{endpoint}"
#     response = requests.request(method, url, headers=headers, data=payload)

#     return response


# # GET ANNOTATORS

annotators = requests.request("GET", f"{backend_base}/annotator")
print(annotators.json())
