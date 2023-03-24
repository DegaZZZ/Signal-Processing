import streamlit as st
import pandas as pd
import numpy as np
import soundfile as sf
import scipy.signal
import io
import plotly.graph_objs as go

st.title('Basic Sound Prcocessing')

uploaded_file = st.file_uploader("Upload an audio file", type="wav", help = "Upload an audio file in .wav format that you want to process", label_visibility = "collapsed")

show_positive_only = st.checkbox("Show only positive part of the signal", value=True)

# Variables
analytical_signal = None
instantaneous_frequency = None
modulation_frequency = None
sample_rate = None


if uploaded_file is not None:
    file_contents = uploaded_file.read()
    st.audio(file_contents, format='audio/wav')
    audio_data, sample_rate = sf.read(io.BytesIO(file_contents))
    
    # compute analytic signal
    analytic_signal = scipy.signal.hilbert(audio_data)

    # compute instantaneous frequency
    instantaneous_frequency = np.diff(np.unwrap(np.angle(analytic_signal))) / (2.0*np.pi) * sample_rate

    # compute modulation frequency
    envelope, _ = scipy.signal.find_peaks(np.abs(instantaneous_frequency))
    modulation_frequency = len(envelope) / (len(audio_data) / sample_rate)

    duration = len(audio_data) / sample_rate
    time_axis = [i / sample_rate for i in range(len(audio_data))]

    # Create a Plotly figure of the audio signal
    max_value = max(audio_data)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=time_axis, y=audio_data))
    fig.update_layout(title="Audio Signal", xaxis_title="Time (s)", yaxis_title="Amplitude",
                      yaxis_range=[0, max_value] if show_positive_only else [-max_value, max_value])
    st.plotly_chart(fig)


col1, col2, col3, col4 = st.columns(4)
col1.metric("Minimum", f"{0 if modulation_frequency == None else round(np.min(instantaneous_frequency) / 1000, 2)} kHz")
col2.metric("Maximum", f"{0 if modulation_frequency == None else round(np.max(instantaneous_frequency) / 1000, 2)} kHz")
col3.metric("Modulation", f"{0 if modulation_frequency == None else round(modulation_frequency / 1000, 2)} kHz")
col4.metric("Sample Rate", f"{0 if sample_rate == None else round(sample_rate / 1000, 2)} kHz")