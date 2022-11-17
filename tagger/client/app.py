import json
import os
from turtle import onclick

import requests
import streamlit as st
import streamlit.components.v1 as components

backend_base = os.getenv("BACKEND_SERVER")
print(f"Connected to server: {backend_base}")

st.set_page_config(layout="wide")

state = st.session_state


def handle_go_prev():
    state.current_annotation_idx = (state.current_annotation_idx - 1) % len(
        state.annotations
    )


def handle_go_next():
    state.current_annotation_idx = (state.current_annotation_idx + 1) % len(
        state.annotations
    )


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
            if not submitted:
                state.total_submitted += 1
            state.submitted[idx] = True
            annotation["value"] = response.json()["value"]
            annotation["date"] = response.json()["date"]


def handle_login():
    state.access_code = state.access_code_input
    state.annotations = sorted(
        requests.request(
            "GET",
            f"{backend_base}/annotator/{state.access_code2id[state.access_code]}/annotations",
        ).json(),
        key=lambda x: x["left_post"]["body"],
    )
    state.current_annotation_idx = 0
    state.submitted = {
        idx: state.annotations[idx].get("value") is not None
        for idx in range(len(state.annotations))
    }
    state.total_submitted = sum(state.submitted.values())
    state.init_annotator = True
    print("Logged in sucessfully")


def handle_logout():
    del state.annotations
    del state.current_annotation_idx
    del state.submitted
    del state.init_annotator
    del state.access_code


def get_color(annotation):
    return "red" if annotation == "dissimilar" else "green"


if "init_app" not in state:
    print("Initializing App...")
    state.annotators = requests.request("GET", f"{backend_base}/annotator").json()
    state.access_code2id = {ann["access_code"]: ann["id"] for ann in state.annotators}
    state.init_app = True
    print("App initialized")
    print(state.annotators)

if "init_annotator" not in state:
    print("Need to log in...")
    st.title("Posts Similarity Tagger")
    st.markdown(
        f":warning: <span style='color:red'>Warning! The text you are about to read contains graphic language. Viewer discretion advised.</span>",
        unsafe_allow_html=True,
    )
    st.subheader("")
    with st.sidebar:
        st.text_input(
            label="Access Code",
            key="access_code_input",
        )

        st.button(
            label="Login",
            on_click=handle_login,
        )
# Annotation logic
else:
    idx = state.current_annotation_idx
    annotation = state.annotations[idx]
    submitted = state.submitted[idx]
    total_submitted = state.total_submitted
    total_annotations = len(state.annotations)

    st.text("Progress")
    st.progress(total_submitted / total_annotations)
    st.text(f"{total_submitted}/{total_annotations}")

    col1, col2 = st.columns(2)

    with col1:
        st.header("Post 1")
        st.write(annotation["left_post"]["body"])

    with col2:
        st.header("Post 2")
        st.write(annotation["right_post"]["body"])
    with st.sidebar:
        st.title(f"Welcome!")
        st.button("Logout", on_click=handle_logout)
        if submitted:
            options = ["similar", "dissimilar"]
            index = 0 if annotation["value"] == "similar" else 1
        else:
            options = ["similar", "dissimilar", "not annotated yet"]
            index = 2

        st.radio(
            label="How do you consider these two posts are?",
            options=options,
            index=index,
            key="selected_value",
            on_change=handle_submit,
            horizontal=True,
        )
        butt1, butt2 = st.columns(2)
        with butt1:
            st.button(
                "Previous",
                on_click=handle_go_prev,
                disabled=state.current_annotation_idx == 0,
            )
        with butt2:
            st.button(
                "Next",
                on_click=handle_go_next,
                disabled=state.current_annotation_idx == len(state.annotations) - 1,
            )

        st.text("Last edited:" if submitted else "Created at:")
        st.text(annotation["date"])
        if os.getenv("ENV") == "dev":
            st.text(annotation["leven_sim"])
