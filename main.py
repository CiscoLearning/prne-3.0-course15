# step2.py
import os
import re
import requests
from dotenv import load_dotenv

def get_config_from_ollama(prompt, url):
    payload = {
        "model": "codellama:7b",
        "prompt": prompt,
        "system": (
            "You are a network automation assistant. Generate only valid Cisco IOS XE CLI commands. "
            "Ensure the output is a full multi-line CLI configuration without explanations, comments, "
            "Markdown formatting, or any extra text. Only return raw Cisco IOS commands."
        ),
        "stream": False
    }
    
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=600)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "Error: Unexpected API response format.")
    except requests.exceptions.Timeout:
        return "Error: The request timed out. Please try again later."
    except requests.exceptions.ConnectionError:
        return "Error: Could not connect to the API. Please check your network connection."
    except requests.exceptions.HTTPError as e:
        return f"Error: HTTP error occurred: {e}"
    except ValueError:
        return "Error: Received an invalid JSON response."
    except requests.exceptions.RequestException as e:
        return f"Error: A request error occurred: {e}"
    except Exception as e:
        return f"Error: An unexpected error occurred: {e}"

def clean_config_output(raw_output):
    if not isinstance(raw_output, str) or raw_output.startswith("Error:"):
        return raw_output
        
    raw_output = raw_output.strip()
    raw_output = re.sub(r"```[\w]*\n?|^\S+\(config[^)]*\)#\s*", "", raw_output, flags=re.MULTILINE)
    
    lines = raw_output.split("\n")
    cleaned_lines = [line.strip() for line in lines if line.strip()]
    
    return "\n".join(cleaned_lines)

def main():
    load_dotenv()
    ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
    user_prompt = input("Enter your configuration request: ").strip()

    print("Generating configuration...")
    raw_config = get_config_from_ollama(user_prompt, ollama_url)
    
    config = clean_config_output(raw_config)
    
    print("\nGenerated Configuration:")
    print("-" * 50)
    print(config)
    print("-" * 50)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
