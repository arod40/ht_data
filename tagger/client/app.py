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
            state.submitted[idx] = True
            annotation["value"] = state.selected_value


def handle_login():
    # TODO: check credentials
    state.username = state.username_input
    state.password = state.password_input

    state.annotations = requests.request(
        "GET",
        f"{backend_base}/annotator/{state.name2id[state.username]}/annotations",
    ).json()
    state.current_annotation_idx = 0
    state.submitted = {
        idx: state.annotations[idx].get("value") is not None
        for idx in range(len(state.annotations))
    }
    state.init_annotator = True


def handle_logout():
    del state.annotations
    del state.current_annotation_idx
    del state.submitted
    del state.init_annotator
    del state.username
    del state.password


def get_color(annotation):
    return "red" if annotation == "dissimilar" else "green"


if "init_app" not in state:
    state.annotators = requests.request("GET", f"{backend_base}/annotator").json()
    state.name2id = {ann["name"]: ann["id"] for ann in state.annotators}
    state.init_app = True

if "init_annotator" not in state:
    st.title("Posts Similarity Tagger!!")
    with st.sidebar:
        st.text_input(
            label="Username",
            key="username_input",
        )

        st.text_input(label="Password", key="password_input", type="password")

        st.button(
            label="Login",
            on_click=handle_login,
        )
# Annotation logic
else:
    col1, col2 = st.columns(2)

    idx = state.current_annotation_idx
    annotation = state.annotations[idx]
    submitted = state.submitted[idx]

    with col1:
        st.header("Post 1")
        components.html(
            f"<pre style='color:white;'>{annotation['left_post']['body']}</pre>",
            height=500,
            scrolling=True,
        )

    with col2:
        st.header("Post 2")
        components.html(
            f"<pre style='color:white;'>{annotation['right_post']['body']}</pre>",
            height=500,
            scrolling=True,
        )

    with st.sidebar:
        st.title(f"Welcome, {state.username}")
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
