import streamlit as st
import os
from urllib.parse import urlparse, parse_qs
import re
import traceback
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

GROQ_API_KEY = os.getenv('GROQ_API_KEY') or os.getenv('API_KEY')
GROQ_MODEL = os.getenv('GROQ_MODEL', 'llama-3.1-8b-instant')
GROQ_API_URL = os.getenv('GROQ_API_URL', 'https://api.groq.com/openai/v1')

# --- YOUR YOUTUBEPROCESSOR CLASS (No changes needed here) ---

class YouTubeProcessor:
    def __init__(self, model_name=None):
        self.educational_keywords = [
            'tutorial', 'learn', 'education', 'course', 'lecture',
            'lesson', 'training', 'guide', 'how to', 'explained',
            'introduction to', 'basics of', 'educational', 'study',
            'learning', 'academy', 'university', 'college', 'school',
            'teaching', 'instructor', 'professor', 'classroom',
            'compiler', 'compiler design', 'algorithm', 'data structure',
            'computer science', 'programming', 'coding', 'software engineering',
            'mathematics', 'engineering', 'exam', 'gate', 'gatehub',
            'three address code', 'triples', 'indirect triples', 'representation'
        ]
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.api_key = GROQ_API_KEY
        self.model_name = model_name or GROQ_MODEL
        self.api_base = GROQ_API_URL

    def extract_video_id(self, url):
        """Extract video ID from various YouTube URL formats."""
        youtube_regex = r'(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})'
        match = re.search(youtube_regex, url)
        
        if match:
            return match.group(1)
            
        parsed_url = urlparse(url)
        if parsed_url.netloc == 'youtu.be':
            return parsed_url.path[1:]
        elif parsed_url.netloc in ('www.youtube.com', 'youtube.com'):
            if parsed_url.path == '/watch':
                return parse_qs(parsed_url.query)['v'][0]
            elif parsed_url.path[:7] == '/embed/':
                return parsed_url.path.split('/')[2]
            elif parsed_url.path[:3] == '/v/':
                return parsed_url.path.split('/')[2]
        
        return None

    def is_valid_youtube_url(self, url):
        """Validate if the URL is a valid YouTube URL."""
        try:
            video_id = self.extract_video_id(url)
            return video_id is not None
        except Exception:
            return False

    def get_video_info(self, video_id):
        """Get video information using YouTube oEmbed, with an HTML fallback."""
        video_url = f'https://www.youtube.com/watch?v={video_id}'
        oembed_url = f'https://www.youtube.com/oembed?url={video_url}&format=json'

        try:
            oembed_response = requests.get(oembed_url, headers=self.headers, timeout=30)
            oembed_response.raise_for_status()
            oembed_data = oembed_response.json()

            title = oembed_data.get('title', '')
            channel = oembed_data.get('author_name', 'Unknown Channel')
            description = oembed_data.get('author_url', '')

            return {
                'title': title,
                'description': description,
                'channel': channel,
                'url': video_url
            }
        except Exception as oembed_error:
            print(f"oEmbed failed, falling back to scraping: {oembed_error}")

        try:
            response = requests.get(video_url, headers=self.headers, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            
            title_tag = soup.find('meta', property='og:title')
            description_tag = soup.find('meta', property='og:description')
            channel_tag = soup.find('link', itemprop='name')

            title = title_tag['content'] if title_tag and title_tag.has_attr('content') else ''
            description = description_tag['content'] if description_tag and description_tag.has_attr('content') else ''
            channel = channel_tag['content'] if channel_tag and channel_tag.has_attr('content') else 'Unknown Channel'

            return {
                'title': title,
                'description': description,
                'channel': channel,
                'url': video_url
            }
        except Exception as scrape_error:
            print(f"Error getting video info: {scrape_error}")
            return None

    def is_educational_content(self, video_info):
        """Check if the video content is educational."""
        if not video_info:
            return False

        try:
            title = str(video_info.get('title') or '').lower()
            description = str(video_info.get('description') or '').lower()
            channel = str(video_info.get('channel') or '').lower()
            
            # Print statements will show in your terminal, not in Streamlit
            print("\nAnalyzing video metadata:")
            print(f"Title: {video_info.get('title', 'N/A')}")
            print(f"Channel: {video_info.get('channel', 'N/A')}")
            
            for keyword in self.educational_keywords:
                if keyword in title or keyword in description or keyword in channel:
                    print(f"\nFound educational keyword '{keyword}'")
                    return True

            print("\nNo clear educational indicators found")
            return False

        except Exception as e:
            print(f"\nError checking educational content: {str(e)}")
            return False

    def generate_notes_and_flashcards(self, video_info):
        """Generate study notes and flashcards using Groq."""
        if not self.api_key:
            return "Error generating notes and flashcards: GROQ_API_KEY is not configured."

        prompt = f"""
            Based on this YouTube video information, please:
            1. Generate concise study notes highlighting key concepts
            2. Create 5-10 flashcards in Q&A format
            
            Video Information:
            Title: {video_info['title']}
            Channel: {video_info['channel']}
            Description: {video_info['description']}
            
            Format the output as:
            NOTES:
            - Key point 1
            - Key point 2
            ...
            
            FLASHCARDS:
            Q1: [Question]
            A1: [Answer]
            ...
            """

        try:
            return self._call_groq(prompt)
        except Exception as e:
            print(f"Groq generation error: {traceback.format_exc()}")
            return f"Error generating notes and flashcards: {str(e)}"

    def _call_groq(self, prompt):
        url = f"{self.api_base}/chat/completions"
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        payload = {
            'model': self.model_name,
            'messages': [{"role": "user", "content": prompt}],
            'temperature': 0.7,
            'max_tokens': 1024
        }

        response = requests.post(url, json=payload, headers=headers, timeout=90)
        try:
            data = response.json()
        except ValueError:
            raise RuntimeError(f'Groq returned a non-JSON response: {response.text}')

        if response.status_code != 200:
            error_message = data.get('error', {}).get('message') or response.text
            raise RuntimeError(f'Groq API error {response.status_code}: {error_message}')

        return data['choices'][0]['message']['content'].strip()

    def process_youtube_url(self, url):
        """Main function to process YouTube URL and generate educational content."""
        try:
            if not self.is_valid_youtube_url(url):
                return {"error": "Invalid YouTube URL"}

            video_id = self.extract_video_id(url)
            if not video_id:
                return {"error": "Could not extract video ID"}
            
            print(f"\nProcessing video ID: {video_id}")
            
            video_info = self.get_video_info(video_id)
            if not video_info:
                return {"error": "Could not fetch video information"}

            educational = self.is_educational_content(video_info)
            if not educational:
                return {
                    "error": "This video does not appear educational based on the keyword filter. Please provide an educational video URL."
                }

            content = self.generate_notes_and_flashcards(video_info)
            
            # Check if content itself is an error message
            if "Error generating notes" in content:
                 return {"error": content}
            
            return {
                "success": True,
                "video_id": video_id,
                "title": video_info['title'],
                "educational": educational,
                "content": content
            }

        except Exception as e:
            print("Error details:", traceback.format_exc())
            return {"error": str(e)}

# --- NEW STREAMLIT APP CODE ---

# Set the page title and layout
st.set_page_config(page_title="FastFlicker - YouTube Video Note & Flashcard Generator 📼🧠", layout="wide")
st.title("FastFlicker - YouTube Video Note & Flashcard Generator 📼🧠")

# Check if the API key is available
if not GROQ_API_KEY:
    st.error("GROQ_API_KEY not found! Please add it to your .env file.")
else:
    available_models = [
        'llama-3.1-8b-instant',              # ✅ Fast, 14,400 req/day free
        'llama-3.3-70b-versatile',           # ✅ High quality, 1,000 req/day free
        'meta-llama/llama-4-scout-17b-16e-instruct',  # ✅ Newest Llama 4
        'gemma2-9b-it',                      # ✅ Google Gemma, free
    ]
    if GROQ_MODEL not in available_models:
        available_models.insert(0, GROQ_MODEL)

    selected_model = st.sidebar.selectbox(
        "Select model to use",
        available_models,
        index=available_models.index(GROQ_MODEL) if GROQ_MODEL in available_models else 0,
        help="Choose the Groq model your key is authorized to use. If one model fails, try another."
    )

    st.caption(f"Using Groq model: {selected_model}")
    st.caption("Default model: llama-3.1-8b-instant (free, fast). Switch to llama-3.3-70b-versatile for higher quality output. Check Groq console for rate limits.")

    # Use st.cache_resource to initialize the processor only once per selected model
    @st.cache_resource
    def init_processor(model_name):
        return YouTubeProcessor(model_name)
        
    processor = init_processor(selected_model)

    # --- Sidebar for Inputs ---
    st.sidebar.header("Controls")
    url = st.sidebar.text_input("Enter YouTube URL:", placeholder="https://youtu.be/..." )

    if st.sidebar.button("Generate Notes", type="primary"):
        if not url:
            st.sidebar.warning("Please enter a URL first.")
        else:
            # --- Main Content Area for Output ---
            with st.spinner("Processing video... This might take a moment. ⏳"):
                try:
                    # Run the processing
                    result = processor.process_youtube_url(url)
                    
                    if "error" in result:
                        st.error(f"Error: {result['error']}")
                    else:
                        st.subheader(f"Video Title: {result['title']}")
                        # Embed the YouTube video
                        st.video(url)
                        
                        st.markdown("---")
                        st.header("Generated Content 🚀")
                        # Use markdown to render the notes and flashcards
                        st.markdown(result['content']) 
                        
                except Exception as e:
                    st.error("An unexpected error occurred:")
                    st.exception(e) # Display the full exception