#!/bin/bash

# Start the News Agent in the background
uvicorn news_agent.main:app --host 0.0.0.0 --port 9000 &

# Start the Streamlit app
streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0
