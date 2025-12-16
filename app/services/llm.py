import google.generativeai as genai
import openai
import dashscope
from http import HTTPStatus
from app.config import settings
import logging
import json

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        self.model_name = settings.DEFAULT_LLM_MODEL
        
        if self.provider == "gemini":
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(self.model_name)
        elif self.provider == "openai":
            openai.api_key = settings.OPENAI_API_KEY
        elif self.provider == "qwen":
            dashscope.api_key = settings.QWEN_API_KEY
            # If model name is still gemini default, switch to qwen-turbo
            if "gemini" in self.model_name:
                self.model_name = "qwen-turbo"
            
    def analyze_tweet(self, tweet_text: str, prompt_template: str = None) -> dict:
        if not prompt_template:
            prompt_template = """
            Analyze the following tweet for relevance to tech news, AI, or crypto. 
            Rate it from 0.0 to 1.0.
            Provide a short summary.
            
            Tweet: {tweet_text}
            
            Output format (JSON):
            {{"score": 0.8, "summary": "..."}}
            """
            
        prompt = prompt_template.format(tweet_text=tweet_text)
        
        try:
            if self.provider == "gemini":
                response = self.model.generate_content(prompt)
                text = response.text
                # Simple cleanup to get JSON
                text = text.replace("```json", "").replace("```", "").strip()
                return json.loads(text)
                
            elif self.provider == "openai":
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}]
                )
                text = response.choices[0].message.content
                return json.loads(text)

            elif self.provider == "qwen":
                response = dashscope.Generation.call(
                    model=self.model_name,
                    messages=[{'role': 'user', 'content': prompt}],
                    result_format='message',  # set the result to be "message" format.
                )
                if response.status_code == HTTPStatus.OK:
                    text = response.output.choices[0]['message']['content']
                    print(f"DEBUG: Qwen Raw Response: {text}") # Debug print
                    
                    # Improved JSON extraction
                    try:
                        # Try to find JSON block
                        import re
                        json_match = re.search(r'\{.*\}', text, re.DOTALL)
                        if json_match:
                            text = json_match.group(0)
                        
                        return json.loads(text)
                    except json.JSONDecodeError:
                        logger.error(f"JSON Decode Error. Raw text: {text}")
                        return {"score": 0.0, "summary": "Analysis failed: Invalid JSON from LLM"}
                        
                else:
                    logger.error(f"Qwen API failed: {response.code} - {response.message}")
                    return {"score": 0.0, "summary": f"Qwen Error: {response.message}"}
                
        except Exception as e:
            logger.error(f"LLM Analysis failed: {e}")
            return {"score": 0.0, "summary": "Analysis failed"}

llm_service = LLMService()
