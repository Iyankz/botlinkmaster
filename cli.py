#!/usr/bin/env python3
"""
BotLinkMaster v4.0 - CLI Tool
Command-line interface for managing devices and testing connections

Author: Yayang Ardiansyah
License: MIT
"""

import click
from rich.console import Console
from rich.table import Table
from rich import print as rprint
from rich.panel import Panel
from botlinkmaster import BotLinkMaster, ConnectionConfig, Protocol
from database import DatabaseManager
import sys

console = Console()
db = DatabaseManager()


@click.group()
@click.version_option(version='4.0', prog_name='BotLinkMaster')
def cli():
    """
    BotLinkMaster CLI - Network Device Management Tool
    
    Manage and monitor network devices via SSH/Telnet
    """
    pass


@cli.command()
def list():
    """List all registered devices"""
    devices = db.get_all_devices()
    
    if not devices:
        console.print("[yellow]No devices registered yet.[/yellow]")
        console.print("\nUse [cyan]botlinkmaster add[/cyan] to register a device.")
        return
    
    table = Table(title="Registered Devices", show_header=True)
    table.add_column("Name", style="cyan")
    table.add_column("Host", style="green")
    table.add_column("Protocol", style="magenta")
    table.add_column("Port")
    table.add_column("Description")
    
    for device in devices:
        port_str = str(device.port) if device.port else "-"
        desc = device.description[:40] + "..." if device.description and len(device.description) > 40 else (device.description or "-")
        table.add_row(
            device.name,
            device.host,
            device.protocol.upper(),
            port_str,
            desc
        )
    
    console.print(table)
    console.print(f"\n[bold]Total devices:[/bold] {len(devices)}")


@cli.command()
@click.argument('name')
@click.argument('host')
@click.argument('username')
@click.argument('password')
@click.option('--protocol', type=click.Choice(['ssh', 'telnet']), default='ssh', help='Connection protocol')
@click.option('--port', type=int, help='Custom port (default: SSH=22, Telnet=23)')
@click.option('--description', help='Device description')
@click.option('--location', help='Device location')
def add(name, host, username, password, protocol, port, description, location):
    """Add a new device"""
    device = db.add_device(
        name=name,
        host=host,
        username=username,
        password=password,
        protocol=protocol,
        port=port,
        description=description,
        location=location
    )
    
    if device:
        console.print(f"[green]✓[/green] Device '[cyan]{name}[/cyan]' added successfully!")
        
        info = f"""
[bold]Device Information:[/bold]
• Name: {device.name}
• Host: {device.host}
• Protocol: {device.protocol.upper()}
• Port: {device.port or 'default'}
"""
        if description:
            info += f"• Description: {description}\n"
        if location:
            info += f"• Location: {location}\n"
        
        console.print(Panel(info.strip(), title="Added Device", border_style="green"))
    else:
        console.print("[red]✗[/red] Failed to add device. Name might already exist.")
        sys.exit(1)


@cli.command()
@click.argument('name')
def delete(name):
    """Delete a device"""
    device = db.get_device(name)
    
    if not device:
        console.print(f"[red]✗[/red] Device '[cyan]{name}[/cyan]' not found.")
        sys.exit(1)
    
    # Confirm deletion
    if click.confirm(f"Delete device '{name}'?", default=False):
        if db.delete_device(name):
            console.print(f"[green]✓[/green] Device '[cyan]{name}[/cyan]' deleted successfully.")
        else:
            console.print(f"[red]✗[/red] Failed to delete device.")
            sys.exit(1)
    else:
        console.print("Deletion cancelled.")


@cli.command()
@click.argument('name')
def show(name):
    """Show device details and cached interfaces"""
    device = db.get_device(name)
    
    if not device:
        console.print(f"[red]✗[/red] Device '[cyan]{name}[/cyan]' not found.")
        sys.exit(1)
    
    # Device info
    info = f"""
[bold cyan]{device.name}[/bold cyan]

[bold]Connection Details:[/bold]
• Host: {device.host}
• Username: {device.username}
• Protocol: {device.protocol.upper()}
• Port: {device.port or 'default'}

[bold]Metadata:[/bold]
• Description: {device.description or 'N/A'}
• Location: {device.location or 'N/A'}
• Created: {device.created_at.strftime('%Y-%m-%d %H:%M:%S')}
• Updated: {device.updated_at.strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    console.print(Panel(info.strip(), title="Device Information", border_style="cyan"))
    
    # Cached interfaces
    interfaces = db.get_device_interfaces(name)
    
    if interfaces:
        table = Table(title="Cached Interfaces", show_header=True)
        table.add_column("Interface", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Description")
        table.add_column("Last Checked")
        
        for iface in interfaces:
            status_style = "green" if iface.status and "up" in iface.status.lower() else "red"
            table.add_row(
                iface.interface_name,
                f"[{status_style}]{iface.status or 'unknown'}[/{status_style}]",
                iface.description or "-",
                iface.last_checked.strftime('%Y-%m-%d %H:%M:%S')
            )
        
        console.print("\n")
        console.print(table)
    else:
        console.print("\n[yellow]No cached interfaces yet.[/yellow]")


@cli.command()
@click.argument('name')
def test(name):
    """Test connection to a device"""
    device = db.get_device(name)
    
    if not device:
        console.print(f"[red]✗[/red] Device '[cyan]{name}[/cyan]' not found.")
        sys.exit(1)
    
    console.print(f"Testing connection to '[cyan]{name}[/cyan]' ({device.host})...")
    
    try:
        config = ConnectionConfig(
            host=device.host,
            username=device.username,
            password=device.password,
            protocol=Protocol.SSH if device.protocol == 'ssh' else Protocol.TELNET,
            port=device.port
        )
        
        with console.status("[bold green]Connecting..."):
            bot = BotLinkMaster(config)
            if bot.connect():
                console.print("[green]✓[/green] Connection successful!")
                
                # Try to get interfaces
                with console.status("[bold green]Getting interfaces..."):
                    interfaces = bot.get_interfaces()
                
                if interfaces:
                    console.print(f"[green]✓[/green] Found {len(interfaces)} interfaces")
                    
                    table = Table(show_header=True)
                    table.add_column("Interface", style="cyan")
                    table.add_column("Status", style="green")
                    table.add_column("Protocol")
                    table.add_column("Description")
                    
                    for iface in interfaces[:10]:  # Show first 10
                        status_style = "green" if iface.get('status') and "up" in iface['status'].lower() else "red"
                        table.add_row(
                            iface.get('name', 'N/A'),
                            f"[{status_style}]{iface.get('status', 'unknown')}[/{status_style}]",
                            iface.get('protocol', 'N/A'),
                            iface.get('description', '-')
                        )
                    
                    console.print("\n")
                    console.print(table)
                    
                    if len(interfaces) > 10:
                        console.print(f"\n[dim]...and {len(interfaces) - 10} more interfaces[/dim]")
                else:
                    console.print("[yellow]⚠[/yellow] Could not retrieve interfaces")
                
                bot.disconnect()
            else:
                console.print("[red]✗[/red] Connection failed!")
                console.print("\nPossible issues:")
                console.print("• Wrong host or port")
                console.print("• Invalid credentials")
                console.print("• Device unreachable")
                console.print("• Firewall blocking connection")
                sys.exit(1)
                
    except Exception as e:
        console.print(f"[red]✗[/red] Error: {str(e)}")
        sys.exit(1)


@cli.command()
@click.argument('device_name')
@click.argument('interface_name')
def check(device_name, interface_name):
    """Check specific interface status"""
    device = db.get_device(device_name)
    
    if not device:
        console.print(f"[red]✗[/red] Device '[cyan]{device_name}[/cyan]' not found.")
        sys.exit(1)
    
    console.print(f"Checking interface '[yellow]{interface_name}[/yellow]' on '[cyan]{device_name}[/cyan]'...")
    
    try:
        config = ConnectionConfig(
            host=device.host,
            username=device.username,
            password=device.password,
            protocol=Protocol.SSH if device.protocol == 'ssh' else Protocol.TELNET,
            port=device.port
        )
        
        with console.status("[bold green]Connecting..."):
            bot = BotLinkMaster(config)
            if not bot.connect():
                console.print("[red]✗[/red] Connection failed!")
                sys.exit(1)
        
        with console.status("[bold green]Getting interface info..."):
            interface_info = bot.get_specific_interface(interface_name)
        
        bot.disconnect()
        
        if not interface_info:
            console.print(f"[red]✗[/red] Interface '[yellow]{interface_name}[/yellow]' not found!")
            sys.exit(1)
        
        # Display interface info
        status = interface_info.get('status', 'unknown')
        status_icon = "[green]●[/green]" if status and "up" in status.lower() else "[red]●[/red]"
        
        info = f"""
{status_icon} [bold]{interface_name}[/bold]

[bold]Status:[/bold] {status.upper()}
"""
        
        if 'description' in interface_info and interface_info['description']:
            info += f"[bold]Description:[/bold] {interface_info['description']}\n"
        
        if 'ip_address' in interface_info:
            info += f"[bold]IP Address:[/bold] {interface_info['ip_address']}\n"
        
        if 'mac_address' in interface_info:
            info += f"[bold]MAC Address:[/bold] {interface_info['mac_address']}\n"
        
        console.print(Panel(info.strip(), title="Interface Information", border_style="green"))
        
        # Cache the interface
        db.cache_interface(
            device_name=device_name,
            interface_name=interface_name,
            status=interface_info.get('status'),
            protocol_status=interface_info.get('status'),
            description=interface_info.get('description')
        )
        console.print("\n[dim]✓ Interface cached in database[/dim]")
        
    except Exception as e:
        console.print(f"[red]✗[/red] Error: {str(e)}")
        sys.exit(1)


@cli.command()
def stats():
    """Show database statistics"""
    stats = db.get_statistics()
    
    info = f"""
[bold]Database Statistics:[/bold]

• Total Devices: {stats['total_devices']}
• Cached Interfaces: {stats['total_cached_interfaces']}
"""
    
    console.print(Panel(info.strip(), title="Statistics", border_style="blue"))


if __name__ == '__main__':
    cli()
