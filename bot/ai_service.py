import json
import logging
from typing import Optional

from mistralai import Mistral

from config import MISTRAL_API_KEY

logger = logging.getLogger(__name__)


def get_mistral_client() -> Mistral:
    return Mistral(api_key=MISTRAL_API_KEY)


async def analyze_mood(
    mood: str,
    text: str,
    recent_entries: list
) -> Optional[dict]:
    client = get_mistral_client()

    entries_context = ""
    if recent_entries:
        entries_context = "\n".join(
            [f"- {entry.created_at.strftime('%Y-%m-%d')}: {entry.mood} — {entry.text[:100]}"
             for entry in recent_entries]
        )

    logger.info(f"Analyzing mood: {mood} for user with {len(recent_entries)} recent entries")

    prompt = f"""
User's current mood: {mood}
User's day description: {text}

Last 7 mood entries:
{entries_context if entries_context else "No previous entries."}

Analyze the user's mood and provide a JSON response with:
- trend: brief analysis (1-2 sentences, max 150 characters) - identify patterns, note improvements or declines
- quote: a REAL motivational quote from a known author (max 100 characters)

Use ONLY real quotes from famous people like:
- Steve Jobs, Maya Angelou, Nelson Mandela, Mahatma Gandhi
- Albert Einstein, Mark Twain, Oscar Wilde, Winston Churchill
- Dalai Lama, Martin Luther King Jr., Eleanor Roosevelt, Theodore Roosevelt
- Or other well-known motivational speakers/authors

Return ONLY valid JSON in this exact format:
{{
  "trend": "brief analysis",
  "quote": "Quote text — Author Name"
}}

Keep responses concise, warm, and varied. Use different wording each time.
The quote must be REAL and ATTRIBUTED to a specific person.
Make the trend analysis personal and insightful based on the user's input.
"""

    try:
        response = client.chat.complete(
            model="mistral-large-latest",
            messages=[
                {
                    "role": "system",
                    "content": "You are a supportive mood tracking assistant. Always respond with valid JSON only. Use REAL quotes from famous people."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.8,
        )

        content = response.choices[0].message.content
        json_str = content.strip()

        if json_str.startswith("```json"):
            json_str = json_str[7:]
        if json_str.startswith("```"):
            json_str = json_str[3:]
        if json_str.endswith("```"):
            json_str = json_str[:-3]

        result = json.loads(json_str.strip())

        logger.info(f"Successfully received analysis: trend='{result.get('trend', '')[:50]}...'")

        return {
            "trend": result.get("trend", "No trend analysis available"),
            "quote": result.get("quote", "The only way to do great work is to love what you do — Steve Jobs")
        }

    except Exception as e:
        logger.error(f"Mistral API error: {e}")
        return {
            "trend": "Analysis temporarily unavailable",
            "quote": "Believe you can and you're halfway there — Theodore Roosevelt"
        }
