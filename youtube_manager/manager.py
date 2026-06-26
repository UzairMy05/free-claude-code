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


def _openrouter_client() -> "OpenAI | None":
    """Return an OpenAI-compatible client pointed at OpenRouter, or None if no key."""
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    if not openrouter_key:
        return None
    from openai import OpenAI

    return OpenAI(
        api_key=openrouter_key,
        base_url="https://openrouter.ai/api/v1",
        default_headers={
            "HTTP-Referer": "https://github.com/UzairMy05/free-claude-code",
            "X-Title": "YouTube Shorts Kids Manager",
        },
    )


def _generate_topic(client: "OpenAI") -> dict | None:
    """
    Agent 1 — Topic Ideator.
    Model: google/gemini-2.5-pro-exp-03-25:free
    Strength: Deep reasoning + broad knowledge for creative, unique topic ideas.
    """
    import json

    prompt = (
        "You are a creative children's education expert. "
        "Generate ONE unique, fun science or nature fact suitable for kids under 12. "
        "Avoid common topics like 'sky is blue' or 'grass is green'. "
        "Output ONLY valid JSON with this exact structure: "
        '{"title": "<max 50 chars>", "topic_summary": "<1 sentence plain description>"}'
    )
    try:
        response = client.chat.completions.create(
            model="google/gemini-2.5-pro-exp-03-25:free",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            max_tokens=200,
        )
        content = response.choices[0].message.content
        if not content:
            raise ValueError("Empty topic response")
        return json.loads(content)
    except Exception as e:
        print(f"[Topic Ideator] Failed: {e}")
        return None


def _generate_script(client: "OpenAI", title: str, topic_summary: str) -> list[str] | None:
    """
    Agent 2 — Script Writer.
    Model: deepseek/deepseek-r1:free
    Strength: Structured, logical writing with step-by-step reasoning for clear explanations.
    """
    import json

    prompt = (
        f"You are a children's science writer. Write a voiceover script for a YouTube Short about: '{title}'.\n"
        f"Context: {topic_summary}\n"
        "Rules:\n"
        "- Write exactly 4 sentences.\n"
        "- Each sentence must be simple, clear, and exciting for kids under 12.\n"
        "- Avoid technical jargon. Use vivid, concrete comparisons.\n"
        "- Each sentence should be 15-25 words.\n"
        'Output ONLY valid JSON: {"paragraphs": ["sentence1", "sentence2", "sentence3", "sentence4"]}'
    )
    try:
        response = client.chat.completions.create(
            model="deepseek/deepseek-r1:free",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            max_tokens=400,
        )
        content = response.choices[0].message.content
        if not content:
            raise ValueError("Empty script response")
        data = json.loads(content)
        return data.get("paragraphs")
    except Exception as e:
        print(f"[Script Writer] Failed: {e}")
        return None


def _generate_tags(client: "OpenAI", title: str, paragraphs: list[str]) -> list[str]:
    """
    Agent 3 — SEO Tag Specialist.
    Model: meta-llama/llama-3.3-70b-instruct:free
    Strength: Fast instruction-following, excellent at classification and keyword extraction.
    """
    import json

    script_text = " ".join(paragraphs)
    prompt = (
        f"You are a YouTube SEO expert for kids' educational content.\n"
        f"Video title: '{title}'\n"
        f"Script: {script_text}\n"
        "Generate exactly 8 high-ranking YouTube tags for this video. "
        "Mix broad tags (e.g. 'kids science') with specific ones (e.g. the topic name). "
        'Output ONLY valid JSON: {"tags": ["tag1", "tag2", ..., "tag8"]}'
    )
    try:
        response = client.chat.completions.create(
            model="meta-llama/llama-3.3-70b-instruct:free",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            max_tokens=200,
        )
        content = response.choices[0].message.content
        if not content:
            raise ValueError("Empty tags response")
        data = json.loads(content)
        return data.get("tags", [])
    except Exception as e:
        print(f"[SEO Tag Specialist] Failed: {e}. Using fallback tags.")
        return ["kids", "educational", "science for kids", "fun facts", "shorts"]


def generate_kids_content() -> dict:
    """
    Orchestrates three specialized free AI agents to create a full YouTube Short brief.

    Pipeline:
      Agent 1 (Gemini 2.5 Pro)     → Topic ideation
      Agent 2 (DeepSeek R1)        → Script writing
      Agent 3 (Llama 3.3 70B)      → SEO tag generation

    Falls back to the built-in KIDS_TOPICS database if OpenRouter is unavailable.
    """
    client = _openrouter_client()
    if client:
        print("🤖 Agent 1 (Gemini 2.5 Pro): Generating topic...")
        topic_data = _generate_topic(client)

        if topic_data:
            title = topic_data.get("title", "")
            topic_summary = topic_data.get("topic_summary", "")

            print(f"   ✅ Topic: {title}")
            print("🤖 Agent 2 (DeepSeek R1): Writing script...")
            paragraphs = _generate_script(client, title, topic_summary)

            if paragraphs:
                print("   ✅ Script ready.")
                print("🤖 Agent 3 (Llama 3.3 70B): Generating SEO tags...")
                tags = _generate_tags(client, title, paragraphs)
                print(f"   ✅ Tags: {', '.join(tags)}")
                return {"title": title, "paragraphs": paragraphs, "tags": tags}

        print("⚠️  One or more agents failed. Falling back to built-in database.")

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
