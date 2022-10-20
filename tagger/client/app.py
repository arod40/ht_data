import json
import os

import requests
import streamlit as st

backend_base = os.getenv("BACKEND_SERVER")
print(f"Connected to server: {backend_base}")

state = st.session_state


def handle_go_prev():
    state.current_annotation_idx = (state.current_annotation_idx - 1) % len(
        state.annotations
    )
    state.selected_value = ""


def handle_go_next():
    state.current_annotation_idx = (state.current_annotation_idx + 1) % len(
        state.annotations
    )
    state.selected_value = ""


def handle_submit():
    idx = state.current_annotation_idx
    annotation = state.annotations[idx]
    submitted = state.submitted[idx]
    left_post_id = annotation["left_post"]["id"]
    right_post_id = annotation["right_post"]["id"]
    annotator_id = annotation["annotator"]["id"]
    if not submitted or state.selected_value != annotation["value"]:
        response = requests.request(
            "PUT",
            f"{backend_base}/annotation/{left_post_id}/{right_post_id}/{annotator_id}",
            data=json.dumps({"value": state.selected_value}),
            headers={"Content-Type": "application/json"},
        )
        if response.status_code == 200:
            state.submitted[idx] = True
            annotation["value"] = state.selected_value


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


def get_color(annotation):
    return "red" if annotation == "dissimilar" else "green"


st.title("Posts Similarity Tagger!!")

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
    annotation = state.annotations[idx]
    submitted = state.submitted[idx]

    with col1:
        st.header("Post 1")
        st.text(annotation["left_post"]["body"])

    with col2:
        st.header("Post 2")
        st.text(annotation["right_post"]["body"])

    st.selectbox(
        label="How do you consider these two posts are?",
        options=["", "similar", "dissimilar"],
        key="selected_value",
    )

    if not submitted:
        st.markdown(":x: Not submitted yet")
    else:
        st.markdown(
            f"Current annotation: <span style='color:{get_color(annotation['value'])}'>{annotation['value']}</span>",
            unsafe_allow_html=True,
        )

    butt1, butt2, butt3 = st.columns(3)
    with butt1:
        st.button(
            "Previous",
            on_click=handle_go_prev,
            disabled=state.current_annotation_idx == 0,
        )
    with butt2:
        st.button(
            "Submit",
            on_click=handle_submit,
            disabled=state.selected_value == ""
            or state.selected_value == annotation["value"],
        )
    with butt3:
        st.button(
            "Next",
            on_click=handle_go_next,
            disabled=state.current_annotation_idx == len(state.annotations) - 1,
        )

    if submitted and state.selected_value != annotation["value"]:
        if state.selected_value != "":
            st.markdown(
                f":warning: Selected value <span style='color:{get_color(state.selected_value)}'>{state.selected_value}</span> is different from current annotated value <span style='color:{get_color(annotation['value'])}'>{annotation['value']}</span>. You need to submit if you want to persist the change.",
                unsafe_allow_html=True,
            )
