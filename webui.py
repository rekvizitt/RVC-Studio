# First
from io import BytesIO
import os
from pathlib import Path
from pytube import YouTube
import streamlit as st
from lib.download_models import BASE_MODELS, BASE_MODELS_DIR, MDX_MODELS, PRETRAINED_MODELS, RVC_DOWNLOAD_LINK, RVC_MODELS, VR_MODELS, download_link_generator, download_model

st.set_page_config("RVC Studio",menu_items={
    # 'Get Help': '',
    # 'Report a bug': "",
    # 'About': ""
})

from web_utils.contexts import ProgressBarContext, SessionStateContext

@st.cache_data(show_spinner=False)
def download_audio_to_buffer(url):
    buffer = BytesIO()
    youtube_video = YouTube(url)
    audio = youtube_video.streams.get_audio_only()
    default_filename = audio.default_filename
    audio.stream_to_buffer(buffer)
    return default_filename, buffer

def render_model_checkboxes(generator):
    not_downloaded = []
    for model_path,link in generator:
        col1, col2 = st.columns(2)
        is_downloaded = os.path.exists(model_path)
        col1.checkbox(os.path.basename(model_path),value=is_downloaded,disabled=True)
        if not is_downloaded: not_downloaded.append((model_path,link))
        if col2.button("Download",disabled=is_downloaded,key=model_path):
            with st.spinner(f"Downloading from {link} to {model_path}"):
                download_model((model_path,link))
                st.experimental_rerun()
    return not_downloaded

if __name__=="__main__":
    with st.container():
        st.title("Download required models")

        with st.expander("Base Models"):
            generator = download_link_generator(RVC_DOWNLOAD_LINK, BASE_MODELS)
            to_download = render_model_checkboxes(generator)
            if st.button("Download All",key="download-all-base-models",disabled=len(to_download)==0):
                with ProgressBarContext(to_download,download_model,"Downloading models") as pb:
                    pb.run()

        st.subheader("Required Models for training")
        with st.expander("Pretrained Models"):
            generator = download_link_generator(RVC_DOWNLOAD_LINK, PRETRAINED_MODELS)
            to_download = render_model_checkboxes(generator)
            if st.button("Download All",key="download-all-pretrained-models",disabled=len(to_download)==0):
                with ProgressBarContext(to_download,download_model,"Downloading models") as pb:
                    pb.run()

        st.subheader("Required Models for inference")
        with st.expander("RVC Models"):
            generator = download_link_generator(RVC_DOWNLOAD_LINK, RVC_MODELS)
            to_download = render_model_checkboxes(generator)
            if st.button("Download All",key="download-all-rvc-models",disabled=len(to_download)==0):
                with ProgressBarContext(to_download,download_model,"Downloading models") as pb:
                    pb.run()
        with st.expander("Vocal Separation Models"):
            generator = download_link_generator(RVC_DOWNLOAD_LINK, VR_MODELS+MDX_MODELS)
            to_download = render_model_checkboxes(generator)
            if st.button("Download All",key="download-all-vr-models",disabled=len(to_download)==0):
                with ProgressBarContext(to_download,download_model,"Downloading models") as pb:
                    pb.run()

    with SessionStateContext("youtube_downloader") as state:
        st.title("Download Audio from Youtube")
        state.url = st.text_input("Insert Youtube URL:",value=state.url)
        if st.button("Fetch",disabled=state.url is None):
            with st.spinner("Downloading Audio Stream from Youtube..."):
                state.downloaded_audio = download_audio_to_buffer(state.url)
            st.subheader("Title")
            st.write(state.downloaded_audio[0])
            title_vid = Path(state.downloaded_audio[0]).with_suffix(".mp3").name
            st.subheader("Listen to Audio")
            st.audio(state.downloaded_audio[1], format='audio/mpeg')
            st.subheader("Download Audio File")
            st.download_button(
                label="Download mp3",
                data=state.downloaded_audio[1],
                file_name=title_vid,
                mime="audio/mpeg")