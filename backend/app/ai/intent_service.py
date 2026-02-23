import os
import requests
import json
import re
from datetime import datetime
from app.ai.intent_schema import IntentModel
from app.ai.prompts import INTENT_EXTRACTION_PROMPT

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


class IntentService:

    def extract_intent(self, user_query: str) -> IntentModel:

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            # Recommended by OpenRouter
            "HTTP-Referer": "http://localhost",
            "X-Title": "AI Insights Assistant"
        }

        payload = {
            "model": "mistralai/mistral-7b-instruct",
            "messages": [
                {"role": "system", "content": INTENT_EXTRACTION_PROMPT},
                {"role": "user", "content": user_query}
            ],
            "temperature": 0
        }

        response = requests.post(OPENROUTER_URL, headers=headers, json=payload)

        if response.status_code != 200:
            raise Exception(f"OpenRouter error: {response.text}")

        data = response.json()

        if "choices" not in data:
            raise Exception(f"Unexpected OpenRouter response: {data}")

        content = data["choices"][0]["message"]["content"]

        # Extract JSON safely
        json_match = re.search(r"\{.*\}", content, re.DOTALL)
        if not json_match:
            raise ValueError(f"No valid JSON found in model response: {content}")

        json_str = json_match.group(0)
        intent_dict = json.loads(json_str)

        # -----------------------------
        # STEP 2 — Clean ISO String Date Normalization
        # -----------------------------
        dr = intent_dict.get("date_range")

        if isinstance(dr, str):
            if dr.lower() == "today":
                today = datetime.utcnow().date().isoformat()
                intent_dict["date_range"] = {
                    "start": today,
                    "end": today
                }
            else:
                intent_dict["date_range"] = None

        return IntentModel(**intent_dict)
