import json
import os

import requests
import streamlit as st

backend_base = os.getenv("BACKEND_SERVER")
print(f"Connected to server: {backend_base}")

st.set_page_config(layout="wide")

state = st.session_state

st.markdown(
    """
<style>
p {
    font-size:20px !important;
}
</style>
""",
    unsafe_allow_html=True,
)


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
    if state.access_code_input in state.access_code2id:
        if "error" in state:
            del state.error
        state.access_code = state.access_code_input
        state.annotations = sorted(
            requests.request(
                "GET",
                f"{backend_base}/annotator/{state.access_code2id[state.access_code]}/annotations",
            ).json(),
            key=lambda x: x["left_post"]["body"],
        )
        state.submitted = {
            idx: state.annotations[idx].get("value") is not None
            for idx in range(len(state.annotations))
        }
        notyet = [idx for idx, isdone in state.submitted.items() if not isdone]
        state.current_annotation_idx = min(notyet) if len(notyet) > 0 else 0
        state.total_submitted = sum(state.submitted.values())
        state.init_annotator = True
        print("Logged in sucessfully")
    else:
        state.error = "Access code not found. Please, try again. If problem persists, contact supervisor."


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
        f":warning: <span style='color:red'>Warning! The text you are about to read contains explicit language. Viewer discretion advised.</span>",
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

        if "error" in state:
            st.markdown(
                f":warning: <span style='color:red'>{state.error}</span>",
                unsafe_allow_html=True,
            )
# Annotation logic
else:
    idx = state.current_annotation_idx
    annotation = state.annotations[idx]
    submitted = state.submitted[idx]
    total_submitted = state.total_submitted
    total_annotations = len(state.annotations)

    if total_submitted == total_annotations:
        st.markdown(
            f":warning: <span style='color:green;text-align:center'> The coding activity is complete.</span>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<p style='text-align:center'>Please take a few minutes to provide us with some feedback on your experience.<br/>This link will take you out of the coding application to an online survey with five questions.<br/>Your experience will help us to improve the research protocols:<br/><a href=https://www.surveymonkey.com/r/AI_Tagfeedback><span style='color:blue'>https://www.surveymonkey.com/r/AI_Tagfeedback</span></a></p>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<p style='text-align:center'>Thank you for helping to develop an AI to detect human trafficking.</p>",
            unsafe_allow_html=True,
        )
    else:
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
            label="How would you rate these two posts?",
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
