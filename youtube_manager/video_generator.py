import os

from gtts import gTTS
from moviepy import AudioFileClip, ImageSequenceClip
from PIL import Image, ImageDraw, ImageFont


def generate_voiceover(text, filename="temp_voice.mp3"):
    """
    Generates a TTS voiceover file from text using gTTS.
    """
    tts = gTTS(text=text, lang="en")
    tts.save(filename)
    return filename


def create_image_frame(
    title,
    text_lines,
    width=1080,
    height=1920,
    bg_color=(34, 49, 63),
    text_color=(255, 255, 255),
):
    """
    Generates a single vertical frame image using PIL.
    """
    # Create blank vertical image
    image = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(image)

    # Try to load a default font, or fallback
    try:
        title_font = ImageFont.truetype("arial.ttf", 64)
        body_font = ImageFont.truetype("arial.ttf", 48)
    except OSError:
        # Fallback to default small font if arial is not found
        title_font = ImageFont.load_default()
        body_font = ImageFont.load_default()

    # Draw Title
    draw.text(
        (width // 2, 300), title, font=title_font, fill=(241, 196, 15), anchor="mm"
    )

    # Draw lines of text
    y_offset = 600
    for line in text_lines:
        draw.text(
            (width // 2, y_offset), line, font=body_font, fill=text_color, anchor="mm"
        )
        y_offset += 100

    return image


def wrap_text(text, font, max_width=900):
    """
    Wraps text to fit within a given pixel width.
    """
    words = text.split()
    lines = []
    current_line = []

    # Simple bounding box approximation
    for word in words:
        test_line = " ".join([*current_line, word])
        # Use simple character counting fallback if custom font is not loaded
        if len(test_line) * 20 > max_width:
            lines.append(" ".join(current_line))
            current_line = [word]
        else:
            current_line.append(word)
    if current_line:
        lines.append(" ".join(current_line))
    return lines


def build_kids_video(title, script_paragraphs, output_filename="shorts_output.mp4"):
    """
    Assembles a vertical educational short video with slides and a voiceover.
    """
    print(f"Creating video: {title}")

    # Combine script paragraphs for TTS
    full_text = " ".join(script_paragraphs)
    voice_file = generate_voiceover(full_text)

    # Get audio duration
    audio_clip = AudioFileClip(voice_file)
    duration = float(audio_clip.duration or 10.0)

    # Calculate how many frames we need (e.g. at 1 frame per second)
    fps = 1
    total_frames = int(duration * fps) + 1

    # Split paragraphs into frames/slides
    # If we have 3 paragraphs, we distribute them over the total duration
    paragraphs_per_frame = max(1, len(script_paragraphs))
    duration_per_para = duration / paragraphs_per_frame

    # Generate temporary image files
    temp_images = []
    for i in range(total_frames):
        current_time = i / fps
        para_idx = min(
            int(current_time / duration_per_para), len(script_paragraphs) - 1
        )
        current_text = script_paragraphs[para_idx]

        # Wrapped text
        wrapped = wrap_text(current_text, None, max_width=900)

        img = create_image_frame(title, wrapped)
        img_path = f"temp_frame_{i}.png"
        img.save(img_path)
        temp_images.append(img_path)

    # Compile into video using MoviePy
    video_clip = ImageSequenceClip(temp_images, fps=fps)
    video_clip = video_clip.with_audio(audio_clip)
    video_clip = video_clip.with_duration(duration)

    # Write final video file
    video_clip.write_videofile(
        output_filename, fps=24, codec="libx264", audio_codec="aac", logger=None
    )

    # Clean up temp files
    audio_clip.close()
    video_clip.close()
    if os.path.exists(voice_file):
        os.remove(voice_file)
    for img_path in temp_images:
        if os.path.exists(img_path):
            os.remove(img_path)

    print(f"Successfully generated vertical video: {output_filename}")
    return output_filename


if __name__ == "__main__":
    # Test generation
    title = "Why do Giraffes have long necks?"
    paragraphs = [
        "Giraffes have very long necks to reach high up into acacia trees.",
        "This helps them eat the most delicious green leaves that other animals cannot reach.",
        "It also lets them spot predators like lions coming from far away!",
    ]
    build_kids_video(title, paragraphs, "test_giraffe.mp4")
