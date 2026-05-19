import requests
import sys

OLLAMA_MODELS = {
    "llama3.1", 
    "phi3",
    "deepseek-r1:1.5b"
}

def prompt_model(model: str, prompt: str) -> str :
    """
    Prompt the model with the input prompt and return a text response. 
    It will select the model based on the input model. 
    """
    if model not in OLLAMA_MODELS:
        return f"[Error] Unavailable model: {model}"

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",      # Ollama’s inference endpoint
            json={
                "model": model,
                "prompt": prompt,
                "stream": False     # streaming not needed
            },
            timeout=120     # avoid freezing if model takes too long to respond
        )

        response.raise_for_status()     # check if the request was successful (status code 200-299), if not throws exception

        data = response.json()  # convert response to JSON format

        return data.get("response", "[Error] No response returned.")    # extract the "response" field from the JSON, if not present return error message

    except requests.exceptions.ConnectionError:     # if the connection to the Ollama server not running, or wrong port, or any other connection issue
        return "[Error] Cannot connect to Ollama server."

    except requests.exceptions.Timeout:
        return "[Error] Request timed out."

    except Exception as e:  # any other unexpected error 
        return f"[Error] {str(e)}"

def main():
    if len(sys.argv) < 3:
        print('Usage: uv run prompt_model.py <model> "<prompt>"')
        return

    model = sys.argv[1]
    prompt = sys.argv[2]

    print("\n--- RESPONSE ---\n")
    print(prompt_model(model, prompt))

if __name__ == "__main__":
    main()
