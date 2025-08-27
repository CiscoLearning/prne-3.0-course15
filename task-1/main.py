"""
Containerized Network Automation Tool
A Python application designed to run with Ollama for AI-powered network configuration generation

This tool allows you to:
- Generate network configurations from natural language prompts
- Apply configurations to network devices using containerized AI services
- Manage network automation workflows using Docker orchestration
- Scale automation tasks across containerized infrastructure
"""

import os
import json
import requests
import time
from connection_tool import establish_connection, send_commands
from inventory_tool import read_inventory, get_device_data

# OLLAMA API INTEGRATION


def query_ollama(prompt: str, model: str = "codellama") -> str:
    """
    Send a prompt to Ollama and return the generated response.

    Args:
        prompt (str): Natural language prompt for AI configuration generation
        model (str, optional): Ollama model to use for generation (default: codellama)

    Returns:
        str: Generated configuration text or error message if request fails
    """
    url = "http://localhost:11434/api/generate"

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1,
            "top_p": 0.9,
            "max_tokens": 2000
        }
    }

    try:
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        return result.get('response', 'No response generated')
    except Exception as e:
        return f"Error communicating with Ollama: {str(e)}"

# TASK 2: CONFIGURATION GENERATION

# Uncomment by removing the ''' markers
'''
def generate_device_config(device_info: dict, requirements: str) -> str:
    """
    Generate device configuration using AI based on requirements.

    Args:
        device_info (dict): Device information from inventory
        requirements (str): Natural language configuration requirements

    Returns:
        str: Generated Cisco IOS XE configuration
    """
    # Create context-aware prompt for network configuration
    prompt = f"""
    Generate a Cisco IOS XE configuration for the following device and requirements:

    Device Information:
    - Name: {device_info.get('Name', 'Unknown')}
    - Type: Router
    - Management IP: {device_info.get('Management IP', 'Unknown')}
    - Location: {device_info.get('Description', 'Unknown')}

    Requirements:
    {requirements}

    Please provide only the Cisco IOS XE configuration commands, without explanations or comments.
    Start with the interface configuration and include all necessary commands.
    """

    print(f"Generating configuration for {device_info.get('Name', 'device')}...")
    print("This may take a few moments...")

    generated_config = query_ollama(prompt)

    if generated_config.startswith("Error"):
        print(f"Configuration generation failed: {generated_config}")
        return None

    print("Configuration generated successfully!")
    return generated_config
'''

# Uncomment by removing the ''' markers
'''
def process_generated_config(config: str) -> list:
    """
    Process and validate generated configuration for device deployment.

    Args:
        config (str): Raw configuration from AI generation

    Returns:
        list: List of configuration commands ready for deployment
    """
    if not config:
        return []

    # Clean and format the configuration
    lines = config.strip().split('\n')
    commands = []

    for line in lines:
        line = line.strip()
        # Skip empty lines and comments
        if line and not line.startswith('#') and not line.startswith('!'):
            # Remove common prefixes that might be added by the AI
            if line.startswith('Router(config)#'):
                line = line.replace('Router(config)#', '').strip()
            elif line.startswith('(config)#'):
                line = line.replace('(config)#', '').strip()
            elif line.startswith('R1(config)#'):
                line = line.replace('R1(config)#', '').strip()

            if line:
                commands.append(line)

    return commands
'''

# TASK 3: DEVICE DEPLOYMENT

# Uncomment by removing the ''' markers
'''
def deploy_configuration(device_data: dict, config_commands: list) -> bool:
    """
    Deploy generated configuration to network device.

    Args:
        device_data (dict): Device information from inventory
        config_commands (list): Configuration commands to deploy

    Returns:
        bool: True if deployment successful, False otherwise
    """
    # Establish connection to device
    connection = establish_connection(device_data)

    if not connection:
        print("Failed to establish device connection")
        return False

    # Deploy configuration commands
    result = send_commands(connection, config_commands)

    if result["success"]:
        print("Configuration deployment completed successfully")
        if result.get("output"):
            print("Device response:")
            print(result["output"])
        return True
    else:
        print(f"Configuration deployment failed: {result.get('error', 'Unknown error')}")
        return False
'''


def main():
    """
    Main entry point for containerized network automation with AI.
    """
    print("Welcome to the AI-powered Network Automation Tool!")
    print("This tool will be enhanced throughout the lab tasks.")
    print("\nCurrent status: Starter code loaded successfully")


if __name__ == "__main__":
    main()
