import click
from netmiko import ConnectHandler
from jinja2 import Template
from inventory_tool import read_inventory, get_device_data

def connect_device(device):
    try:
        conn = ConnectHandler(**device)
        conn.enable()
        return conn
    except Exception as e:
        click.echo(f"Error connecting to device {device.get('host')}: {e}")
        return None

def get_conn_info(dev_data):
    return {
        "device_type": "cisco_ios",
        "host": dev_data["Management IP"],
        "username": dev_data["Username"],
        "password": dev_data["Password"],
        "secret": dev_data["Password"],
    }

def send_config(device, commands):
    conn = connect_device(device)
    if not conn:
        return "Connection failed; configuration not sent."
    try:
        output = conn.send_config_set(commands)
    except Exception as e:
        output = f"Error sending configuration: {e}"
    finally:
        conn.disconnect()
    return output

# Wrapper functions for task solution compatibility
def establish_connection(device_data):
    """
    Wrapper for connect_device with inventory data format.

    Args:
        device_data (dict): Device information from inventory

    Returns:
        ConnectHandler: Netmiko connection object or None if failed
    """
    conn_info = get_conn_info(device_data)
    return connect_device(conn_info)

def send_commands(connection, commands):
    """
    Send configuration commands via active connection.

    Args:
        connection: Active Netmiko connection
        commands (list): Configuration commands to send

    Returns:
        dict: Result with success status and output/error
    """
    if not connection:
        return {"success": False, "error": "No active connection"}

    try:
        output = connection.send_config_set(commands)
        return {"success": True, "output": output}
    except Exception as e:
        return {"success": False, "error": str(e)}

def render_interface_config(action, interface, ip_address, subnet_mask):
    if action == "create":
        config_vars = {
            "interface": interface,
            "ip_address": ip_address,
            "subnet": subnet_mask
        }
        template_string = """
        interface {{ interface }}
            ip address {{ ip_address }} {{ subnet }}
            no shutdown
        """
    else:
        config_vars = {"interface": interface}
        template_string = """
        interface {{ interface }}
            no ip address
            shutdown
        """
    rendered_config = Template(template_string).render(**config_vars)
    commands = [line.strip() for line in rendered_config.splitlines() if line.strip()]

    return commands

def get_interface_brief(device):
    conn = connect_device(device)
    if not conn:
        return "Connection failed; cannot retrieve interface brief."
    try:
        output = conn.send_command("show ip interface brief")
    except Exception as e:
        output = f"Error retrieving interface brief: {e}"
    finally:
        conn.disconnect()
    return output

@click.group()
def cli():
    pass

@cli.command(name="configure")
@click.option('--inventory', default='inventory.csv', help='Inventory file')
@click.option('--device', prompt='Device name', help='Device name in inventory')
@click.option('--action', type=click.Choice(['create', 'delete']), prompt="Action")
@click.option('--interface', prompt='Interface name', default='GigabitEthernet2', help='Interface to configure')
def configure(inventory, device, action, interface):
    inv_data = read_inventory(inventory)
    dev_data = get_device_data(inv_data, device)
    if not dev_data:
        click.echo(f"Device {device} not found in inventory.")
        return
    conn_info = get_conn_info(dev_data)
    if action == "create":
        ip = click.prompt("IP address")
        subnet = click.prompt("Subnet mask", default="255.255.255.0")
        cfg = {"interface": interface, "ip_address": ip, "subnet": subnet}
        tmpl = """
        interface {{ interface }}
         ip address {{ ip_address }} {{ subnet }}
         no shutdown
        """
    else:
        cfg = {"interface": interface}
        tmpl = """
        interface {{ interface }}
         no ip address
         shutdown
        """
    rendered = Template(tmpl).render(cfg)
    cmds = [line.strip() for line in rendered.splitlines() if line.strip()]
    click.echo(f"\nSending configuration to {device}:")
    click.echo("\n".join(cmds))
    try:
        output = send_config(conn_info, cmds)
        click.echo(f"Output from {device}:\n{output}")
    except Exception as e:
        click.echo(f"Error on {device}: {e}")

@cli.command(name="list_devices")
@click.option('--inventory', default='inventory.csv', help='Inventory file')
def list_devices(inventory):
    try:
        devices = read_inventory(inventory)
        for device in devices:
            click.echo(device)
    except Exception as e:
        click.echo(f"Error reading inventory: {e}")

if __name__ == "__main__":
    cli()