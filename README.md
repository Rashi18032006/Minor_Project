# YouTube Video Note & Flashcard Generator

Streamlit app that takes a YouTube URL, checks whether the video appears educational, and generates study notes and flashcards using the Groq API.

## Features

- Paste a YouTube URL in the sidebar
- Validates the video against an educational keyword filter
- Fetches YouTube metadata (title, description, channel)
- Generates notes and flashcards only for educational videos
- Displays the embedded video and generated content in Streamlit

## Requirements

- Python 3.10+
- `pip` installed
- A valid `GROQ_API_KEY`

## Setup

Open a terminal in the `FastFlicker` project folder:

```powershell
cd "c:\Users\lenovo\OneDrive\Desktop\minor project\FastFlicker"
```

Create and activate the virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Install the dependencies:

```powershell
pip install -r requirements.txt
```

## Configure Groq

Create a `.env` file in the project root with your API key:

```env
GROQ_API_KEY=your_api_key_here
GROQ_API_URL=https://api.groq.com/openai/v1
```

Optional: set a specific model override if you want to use a different Groq model.

```env
GROQ_MODEL=llama-3.1-8b-instant
```

## Run the app

Start Streamlit:

```powershell
streamlit run app.py
```

Then open the local URL shown in the terminal, usually:

```text
http://localhost:8501
```

## Usage

- Enter a YouTube video URL in the sidebar.
- The app will verify whether the video appears educational.
- If the video is educational, it will generate notes and flashcards.
- If the video is not educational, the app will return an error and will not generate content.

## Notes

- The project uses the Groq `/chat/completions` endpoint.
- Default model is `llama-3.1-8b-instant`.
- Non-educational videos are blocked to prevent unwanted content generation.
- If you encounter API failures, verify your `GROQ_API_KEY` and `GROQ_API_URL` settings.

## Troubleshooting

If the virtual environment fails to activate in PowerShell, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

If dependencies are missing, ensure the virtual environment is active before running `streamlit run app.py`.
