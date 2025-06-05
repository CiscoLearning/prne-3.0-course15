import requests

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

if __name__ == "__main__":
    prompt = "Set the interface of GigabitEthernet2 to 192.168.1.1/24"
    ollama_url = "http://localhost:11434/api/generate"  # Example URL
    print("Generating configuration, please wait.")
    config = get_config_from_ollama(prompt, ollama_url)
    print("Generated configuration:")
    print(config)
