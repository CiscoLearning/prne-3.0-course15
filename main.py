import os
import re

import requests
from dotenv import load_dotenv

from connection_tool import send_config, get_conn_info
from inventory_tool import read_inventory, get_device_data

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

def confirm_action(message):
    response = input(f"{message} (y/n): ").strip().lower()
    return response in {"y", "yes"}

def main():
    try:
        inventory = read_inventory("inventory.csv")
    except FileNotFoundError:
        print("Error: inventory.csv file not found.")
        return
    except Exception as e:
        print(f"Error reading inventory: {e}")
        return

    device_name = input("Enter the device name: ").strip()
    device_data = get_device_data(inventory, device_name)

    if not device_data:
        print("Device not found in inventory.")
        return
    try:
        conn_info = get_conn_info(device_data)
    except Exception as e:
        print(f"Error getting connection info: {e}")
        return

    user_prompt = input("Enter your configuration request: ").strip()

    print("Generating configuration...")

    load_dotenv
    ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
    config = clean_config_output(get_config_from_ollama(user_prompt, ollama_url))

    if config.startswith("Error:"):
        print(config)
        return

    print("\nGenerated Configuration:")
    print("-" * 50)
    print(config)
    print("-" * 50)

    if not confirm_action("Do you want to apply this configuration?"):
        print("Configuration not applied.")
        return

    print("Applying configuration...")
    try:
        result = send_config(conn_info, config.splitlines())
        print("\nConfiguration Applied:")
        print("-" * 50)
        print(result)
        print("-" * 50)
    except Exception as e:
        print(f"Error applying configuration: {e}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
