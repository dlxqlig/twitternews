import dashscope
from http import HTTPStatus
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("QWEN_API_KEY")
print(f"API Key found: {api_key[:5]}...{api_key[-5:] if api_key else 'None'}")

dashscope.api_key = api_key

def test_qwen():
    prompt = "Hello, are you working?"
    try:
        response = dashscope.Generation.call(
            model="qwen-turbo",
            messages=[{'role': 'user', 'content': prompt}],
            result_format='message',
        )
        
        if response.status_code == HTTPStatus.OK:
            print("Success!")
            print(response.output.choices[0]['message']['content'])
        else:
            print(f"Failed: {response.code} - {response.message}")
            print(response)
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_qwen()
