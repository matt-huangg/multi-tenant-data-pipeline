"""Processing service for text and image jobs."""

from openai import OpenAI

from app.config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)


class ProcessingService:
    """Process AI content jobs."""

    def process_job(self, job: dict):
        """Process a persisted job and return a JSON-serializable result."""
        payload = job.get("payload") or {}

        if job["type"] == "text":
            return self.prompt_ai(payload["text"])

        if job["type"] == "image":
            return self.prompt_image(payload["image_url"])

        raise ValueError(f"Unsupported job type: {job['type']}")

    def prompt_ai(self, prompt: str):
        response = client.responses.create(
            model="gpt-5.4-mini",
            input=prompt,
            store=True,
        )
        return {"output_text": response.output_text}

    def prompt_image(self, image_url: str):
        response = client.responses.create(
            model="gpt-5.4-mini",
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": "Describe this image."},
                        {"type": "input_image", "image_url": image_url},
                    ],
                }
            ],
            store=True,
        )
        return {"output_text": response.output_text}


processing_service = ProcessingService()
