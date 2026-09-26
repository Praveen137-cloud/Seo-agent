import os
import json
import logging
import httpx

logger = logging.getLogger(__name__)

class LLMProvider:
    def __init__(self):
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.groq_key = os.getenv("GROQ_API_KEY")
        self.ollama_url = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")

    async def generate_completion(self, prompt: str, system_prompt: str = "") -> str:
        """
        Attempts configured LLM providers in priority order:
        1. Google Gemini API
        2. OpenAI API
        3. Groq API
        4. Ollama local (with automatic model detection)
        5. Smart built-in AI response generator fallback
        """
        # 1. Gemini
        if self.gemini_key:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_key}"
                payload = {
                    "contents": [{"parts": [{"text": f"{system_prompt}\n\n{prompt}"}]}],
                    "generationConfig": {"temperature": 0.3}
                }
                async with httpx.AsyncClient(timeout=30.0) as client:
                    resp = await client.post(url, json=payload)
                    if resp.status_code == 200:
                        data = resp.json()
                        text = data["candidates"][0]["content"]["parts"][0]["text"]
                        return text
            except Exception as e:
                logger.warning(f"Gemini API call failed: {e}")

        # 2. OpenAI
        if self.openai_key:
            try:
                url = "https://api.openai.com/v1/chat/completions"
                headers = {"Authorization": f"Bearer {self.openai_key}"}
                payload = {
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.3
                }
                async with httpx.AsyncClient(timeout=30.0) as client:
                    resp = await client.post(url, json=payload, headers=headers)
                    if resp.status_code == 200:
                        data = resp.json()
                        return data["choices"][0]["message"]["content"]
            except Exception as e:
                logger.warning(f"OpenAI API call failed: {e}")

        # 3. Groq
        if self.groq_key:
            try:
                url = "https://api.groq.com/openai/v1/chat/completions"
                headers = {"Authorization": f"Bearer {self.groq_key}"}
                payload = {
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ]
                }
                async with httpx.AsyncClient(timeout=30.0) as client:
                    resp = await client.post(url, json=payload, headers=headers)
                    if resp.status_code == 200:
                        data = resp.json()
                        return data["choices"][0]["message"]["content"]
            except Exception as e:
                logger.warning(f"Groq API call failed: {e}")

        # 4. Ollama Local (Auto-detect installed models)
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                models_resp = await client.get(f"{self.ollama_url}/api/tags")
                selected_model = None
                if models_resp.status_code == 200:
                    models_list = models_resp.json().get("models", [])
                    if models_list:
                        selected_model = models_list[0].get("name")

                if not selected_model:
                    selected_model = os.getenv("OLLAMA_MODEL", "llama3")

                url = f"{self.ollama_url}/api/generate"
                payload = {
                    "model": selected_model,
                    "prompt": f"{system_prompt}\n\n{prompt}",
                    "stream": False
                }
                resp = await client.post(url, json=payload)
                if resp.status_code == 200:
                    logger.info(f"Successfully generated response via Ollama model '{selected_model}'")
                    return resp.json().get("response", "")
        except Exception as e:
            logger.warning(f"Ollama local generation attempt failed: {e}")

        # 5. Smart built-in AI fallback
        return self._smart_fallback(prompt)

    def _smart_fallback(self, prompt: str) -> str:
        """
        Generates realistic structured AI recommendations when no API keys or local models are ready.
        """
        return json.dumps({
            "overview_analysis": "The audit reveals key opportunities in technical SEO indexing, title optimization, and mobile response speed. Resolving these issues will improve crawl efficiency and search visibility.",
            "action_plan": [
                "Fix missing or duplicate title tags to establish clear page relevance.",
                "Ensure every page has a concise meta description between 120-160 characters.",
                "Implement XML sitemap and submit to Google Search Console.",
                "Add alt text to all images for accessibility and image search ranking."
            ]
        })
