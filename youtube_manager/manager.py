import os
import random
import time

from dotenv import load_dotenv

from youtube_manager.video_generator import build_kids_video
from youtube_manager.youtube_uploader import get_youtube_service, upload_short

# Load environment variables (to check for LLM API keys if available)
load_dotenv()

# Built-in educational facts (fallback database)
KIDS_TOPICS = [
    {
        "title": "Why is the Sky Blue?",
        "paragraphs": [
            "Sunlight looks white, but it is actually made of all the colors of the rainbow!",
            "When this light hits the Earth's air, it bounces off the gases and moves in all directions.",
            "Blue light bounces around much more than the other colors because it travels as smaller, shorter waves.",
            "This is called Rayleigh scattering, and it is why we see a beautiful blue sky!",
        ],
        "tags": [
            "science",
            "kids science",
            "why is the sky blue",
            "fun facts",
            "educational",
        ],
    },
    {
        "title": "How do Chameleons Change Color?",
        "paragraphs": [
            "Chameleons don't just change color to blend in with their background.",
            "They actually change color to show how they feel, like being angry or happy!",
            "Under their skin, they have tiny crystals that reflect different kinds of light.",
            "By relaxing or tightening their skin, they change the space between these crystals, creating new colors!",
        ],
        "tags": ["animals", "nature", "chameleons", "science for kids", "educational"],
    },
    {
        "title": "Why do Cats Purr?",
        "paragraphs": [
            "Most people think cats only purr when they are happy, but that is not the whole story!",
            "Cats also purr to calm themselves down when they feel scared or hurt.",
            "The sound of a cat's purr actually has a special vibration frequency.",
            "This vibration can help heal their bones and muscles and keep them healthy!",
        ],
        "tags": ["cats", "pets", "fun facts", "animal science", "kids educational"],
    },
    {
        "title": "Why is Grass Green?",
        "paragraphs": [
            "Grass is green because of a special helper called chlorophyll.",
            "Chlorophyll lives inside the cells of plants and helps them make their own food.",
            "It absorbs red and blue light from the sun, but it rejects green light.",
            "Since the green light bounces back to our eyes, we see the grass as green!",
        ],
        "tags": ["nature", "plants", "kids science", "fun facts", "school"],
    },
    {
        "title": "How do Honeybees Talk?",
        "paragraphs": [
            "Honeybees cannot speak words, but they are amazing communicators!",
            "To tell other bees where to find flowers, they perform a special dance.",
            "This is called the waggle dance, where they run in a figure-eight pattern.",
            "The angle of the dance tells the other bees exactly which way to fly!",
        ],
        "tags": ["insects", "bees", "nature facts", "educational", "for kids"],
    },
]


def generate_kids_content():
    """
    Attempts to generate a kids' educational topic using an LLM if keys exist.
    Otherwise, picks a random one from the built-in database.
    """
    # Placeholder for LLM generation if Gemini/OpenAI API is set up:
    gemini_key = os.getenv("GEMINI_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")

    prompt = (
        "Generate a fun science/educational fact for kids under 12. "
        "Output JSON with 'title' (max 50 chars), 'paragraphs' (a list of 3-4 short, simple sentences suitable for kids voiceover), "
        "and 'tags' (a list of 5 tags)."
    )

    if gemini_key or openai_key:
        try:
            from openai import OpenAI

            if gemini_key:
                client = OpenAI(
                    api_key=gemini_key,
                    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
                )
                model_name = "gemini-1.5-flash"
            else:
                client = OpenAI(api_key=openai_key)
                model_name = "gpt-4o-mini"

            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
            )
            import json

            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response from LLM")
            data = json.loads(content)
            return data
        except Exception as e:
            print(f"LLM generation failed: {e}. Falling back to database.")

    # Fallback to local list
    return random.choice(KIDS_TOPICS)


def run_daily_pipeline(count=5, delay_hours=3):
    """
    Orchestrates creating and uploading the specified number of Shorts.
    """
    try:
        # Initialize YouTube service first to ensure authentication works
        youtube = get_youtube_service(
            client_secrets_path="client_secrets.json", token_path="token.pickle"
        )
    except Exception as e:
        print(f"Failed to authenticate YouTube Service: {e}")
        print("Please ensure client_secrets.json is placed in the project root.")
        return

    print(f"Starting pipeline to post {count} shorts...")

    for i in range(count):
        print(f"\n--- Processing Video {i + 1} of {count} ---")

        # 1. Get content
        topic = generate_kids_content()
        title = topic["title"]
        paragraphs = topic["paragraphs"]
        tags = topic.get("tags", [])

        # 2. Render Video
        video_file = f"short_{i + 1}.mp4"
        try:
            build_kids_video(title, paragraphs, video_file)
        except Exception as e:
            print(f"Failed to generate video: {e}")
            continue

        # 3. Upload Video
        try:
            upload_short(
                youtube=youtube,
                video_path=video_file,
                title=f"{title} 🌟 #shorts #kids #educational",
                description="Fun educational facts for curious kids! Learn something new every day.",
                tags=tags,
            )
            # Remove local file after successful upload
            if os.path.exists(video_file):
                os.remove(video_file)
        except Exception as e:
            print(f"Failed to upload video: {e}")
            continue

        # 4. Wait between uploads (unless it's the last one)
        if i < count - 1:
            print(f"Waiting for {delay_hours} hours before next post...")
            time.sleep(delay_hours * 3600)


if __name__ == "__main__":
    # Configured for automated daily posting: 5 videos, spaced 4 hours apart
    run_daily_pipeline(count=5, delay_hours=4)
