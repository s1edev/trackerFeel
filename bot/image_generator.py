import io
import platform
from typing import Tuple

from PIL import Image, ImageDraw, ImageFont


def get_fonts() -> Tuple[ImageFont.FreeTypeFont, ...]:
    system = platform.system()

    if system == "Darwin":
        font_paths = [
            "/System/Library/Fonts/Helvetica.ttc",
            "/Library/Fonts/Arial.ttf",
            "/System/Library/Fonts/Supplemental/Arial.ttf",
        ]
    elif system == "Linux":
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/TTF/DejaVuSans.ttf",
            "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
        ]
    else:
        font_paths = ["C:\\Windows\\Fonts\\arial.ttf"]

    title_font = None
    subtitle_font = None
    text_font = None
    quote_font = None

    for path in font_paths:
        try:
            title_font = ImageFont.truetype(path, 56)
            subtitle_font = ImageFont.truetype(path, 36)
            text_font = ImageFont.truetype(path, 28)
            quote_font = ImageFont.truetype(path, 32)
            break
        except (IOError, OSError):
            continue

    if title_font is None:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
        quote_font = ImageFont.load_default()

    return title_font, subtitle_font, text_font, quote_font


def wrap_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont,
    max_width: int
) -> list:
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        test_line = f"{current_line} {word}".strip()
        bbox = draw.textbbox((0, 0), test_line, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return lines


def generate_mood_image(
    mood: str,
    trend: str,
    quote: str
) -> io.BytesIO:
    width, height = 1080, 1350

    colors = {
        "😄": ("#FFF9E6", "#F57F17", "#FFD54F", "#FFF3E0"),
        "🙂": ("#E8F5E9", "#2E7D32", "#81C784", "#C8E6C9"),
        "😐": ("#ECEFF1", "#455A64", "#90A4AE", "#CFD8DC"),
        "😔": ("#E3F2FD", "#1565C0", "#64B5F6", "#BBDEFB"),
        "😢": ("#EDE7F6", "#512DA8", "#9575CD", "#D1C4E9"),
    }

    bg_color, accent_color, secondary_color, card_bg = colors.get(
        mood.split()[0], ("#FAFAFA", "#616161", "#9E9E9E", "#EEEEEE")
    )

    image = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(image)

    title_font, subtitle_font, text_font, quote_font = get_fonts()

    padding = 80
    card_padding = 50
    content_width = width - (padding * 2)
    card_width = width - (card_padding * 2)

    y_position = padding

    mood_emoji = mood.split()[0]
    draw.text((width / 2, y_position), mood_emoji, font=title_font,
              fill=accent_color, anchor="mt")
    y_position += 90

    draw.text((width / 2, y_position), mood, font=subtitle_font,
              fill=accent_color, anchor="mt")
    y_position += 80

    card_y_start = y_position
    card_y = y_position + card_padding

    draw.rounded_rectangle(
        [(card_padding, card_y_start), (width - card_padding, height - padding)],
        radius=24,
        fill=card_bg,
    )

    trend_label = "ТЕНДЕНЦИЯ"
    draw.text((card_padding + card_padding, card_y), trend_label,
              font=text_font, fill=secondary_color)
    card_y += 45

    trend_lines = wrap_text(draw, trend, text_font, content_width - 40)
    for line in trend_lines:
        bbox = draw.textbbox((0, 0), line, font=text_font)
        line_height = bbox[3] - bbox[1]
        draw.text((card_padding + card_padding, card_y), line,
                  font=text_font, fill="#212121")
        card_y += line_height + 6

    card_y += 30

    divider_y = card_y
    draw.line(
        [(card_padding + card_padding, divider_y),
         (width - card_padding - card_padding, divider_y)],
        fill=secondary_color,
        width=2,
    )
    card_y += 40

    quote_label = "ЦИТАТА ДНЯ"
    draw.text((card_padding + card_padding, card_y), quote_label,
              font=text_font, fill=secondary_color)
    card_y += 45

    quote_lines = wrap_text(draw, f'"{quote}"', quote_font, content_width - 40)
    for line in quote_lines:
        bbox = draw.textbbox((0, 0), line, font=quote_font)
        line_height = bbox[3] - bbox[1]
        draw.text((card_padding + card_padding, card_y), line,
                  font=quote_font, fill="#424242")
        card_y += line_height + 8

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)

    return buffer
