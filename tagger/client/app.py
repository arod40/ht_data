import os

import requests
import streamlit as st


def handle_go_prev():
    state.current_annotation_idx = (state.current_annotation_idx - 1) % len(
        state.annotations
    )


def handle_go_next():
    state.current_annotation_idx = (state.current_annotation_idx + 1) % len(
        state.annotations
    )


def handle_submit():
    pass


def handle_change_annotator():
    if state.annotator_name == "select one...":
        del state.annotations
        del state.current_annotation_idx
        del state.submitted
        del state.init_annotator
    else:
        state.annotations = requests.request(
            "GET",
            f"{backend_base}/annotator/{state.name2id[state.annotator_name]}/annotations",
        ).json()
        state.current_annotation_idx = 0
        state.submitted = {
            idx: state.annotations[idx].get("value") is not None
            for idx in range(len(state.annotations))
        }
        state.init_annotator = True


st.title("Posts Similarity Tagger!!")

# backend_base = os.getenv("BACKEND_SERVER")
backend_base = "http://localhost:8080"
print(f"Connected to server: {backend_base}")

state = st.session_state

# GET ANNOTATOR CREDENTIALS

if "init_app" not in state:
    state.annotators = requests.request("GET", f"{backend_base}/annotator").json()
    state.name2id = {ann["name"]: ann["id"] for ann in state.annotators}
    state.init_app = True

st.selectbox(
    label="What is your name?",
    options=["select one..."] + [ann["name"] for ann in state.annotators],
    key="annotator_name",
    on_change=handle_change_annotator,
)

# Annotation logic
if "init_annotator" in state:

    st.title(f"Welcome, {state.annotator_name}")

    col1, col2 = st.columns(2)

    idx = state.current_annotation_idx
    st.text(idx)
    annotation = state.annotations[idx]
    submitted = state.submitted[idx]

    with col1:
        st.header("Post 1")
        st.text(annotation["left_post"]["body"])

    with col2:
        st.header("Post 2")
        st.text(annotation["right_post"]["body"])

    butt1, butt2, butt3 = st.columns(3)
    with butt1:
        st.button(
            "Previous",
            on_click=handle_go_prev,
            disabled=state.current_annotation_idx == 0,
        )
    with butt2:
        st.button("Submit", on_click=handle_submit)
    with butt3:
        st.button(
            "Next",
            on_click=handle_go_next,
            disabled=state.current_annotation_idx == len(state.annotations) - 1,
        )
