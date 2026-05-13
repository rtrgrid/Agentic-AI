import vertexai
from vertexai.generative_models import GenerativeModel

vertexai.init(
    project="gd-gcp-internship-ds",
    location="us-central1"
)

model = GenerativeModel("gemini-2.0-flash")

response = model.generate_content(
    "Explain what a RAG agent is in simple words"
)

print(response.text)