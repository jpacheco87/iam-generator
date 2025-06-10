"""
CLI interface for the IAM Generator tool.

This module provides a command-line interface for analyzing AWS CLI commands
and generating IAM permissions and roles.
"""

import json
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich.tree import Tree

from .analyzer import IAMPermissionAnalyzer
from .role_generator import IAMRoleGenerator
from .doc_scraper import AWSCLIDocumentationScraper


console = Console()


@click.group()
@click.version_option(version="1.0.0")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.pass_context
def cli(ctx: click.Context, verbose: bool) -> None:
    """
    AWS CLI IAM Permissions Analyzer
    
    Analyze AWS CLI commands and generate the required IAM permissions
    and roles to execute them securely.
    """
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose


@cli.command()
@click.argument("command", nargs=-1, required=True)
@click.option("--output", "-o", type=click.Choice(["table", "json", "yaml"]), 
              default="table", help="Output format")
@click.option("--save", "-s", type=click.Path(), help="Save output to file")
@click.option("--debug", "-d", is_flag=True, help="Enable debug mode to show fallback warnings")
@click.pass_context
def analyze(ctx: click.Context, command: tuple, output: str, save: Optional[str], debug: bool) -> None:
    """
    Analyze an AWS CLI command and show required IAM permissions.
    
    COMMAND: The AWS CLI command to analyze (without 'aws' prefix)
    
    Examples:
      iam-generator analyze s3 ls s3://my-bucket
      iam-generator analyze ec2 describe-instances --region us-west-2
      iam-generator analyze lambda invoke --function-name my-function
    """
    aws_command = " ".join(command)
    full_command = f"aws {aws_command}"
    
    if ctx.obj["verbose"]:
        console.print(f"[blue]Analyzing command:[/blue] {full_command}")
    
    try:
        analyzer = IAMPermissionAnalyzer(debug_mode=debug)
        result = analyzer.analyze_command(full_command)
        
        if output == "table":
            _display_table_output(result)
        elif output == "json":
            _display_json_output(result)
        elif output == "yaml":
            _display_yaml_output(result)
        
        if save:
            _save_output(result, save, output)
            console.print(f"[green]Output saved to:[/green] {save}")
            
    except Exception as e:
        console.print(f"[red]Error analyzing command:[/red] {str(e)}")
        if ctx.obj["verbose"]:
            import traceback
            console.print(traceback.format_exc())
        sys.exit(1)


@cli.command()
@click.argument("command", nargs=-1, required=True)
@click.option("--role-name", "-n", default="GeneratedRole", help="IAM role name")
@click.option("--trust-policy", "-t", 
              type=click.Choice(["ec2", "lambda", "ecs", "cross-account"]),
              default="ec2", help="Trust policy type")
@click.option("--account-id", help="Account ID for cross-account trust policy")
@click.option("--output-format", "-f", 
              type=click.Choice(["terraform", "cloudformation", "aws-cli", "json"]),
              default="json", help="Output format for role configuration")
@click.option("--save", "-s", type=click.Path(), help="Save role configuration to file")
@click.option("--debug", "-d", is_flag=True, help="Enable debug mode to show fallback warnings")
@click.pass_context
def generate_role(ctx: click.Context, command: tuple, role_name: str, 
                 trust_policy: str, account_id: Optional[str],
                 output_format: str, save: Optional[str], debug: bool) -> None:
    """
    Generate an IAM role with permissions for the given AWS CLI command.
    
    COMMAND: The AWS CLI command to analyze (without 'aws' prefix)
    
    Examples:
      iam-generator generate-role s3 ls s3://my-bucket --role-name S3ReadRole
      iam-generator generate-role lambda invoke --function-name my-function -f terraform
    """
    aws_command = " ".join(command)
    full_command = f"aws {aws_command}"
    
    if ctx.obj["verbose"]:
        console.print(f"[blue]Generating role for command:[/blue] {full_command}")
    
    try:
        analyzer = IAMPermissionAnalyzer(debug_mode=debug)
        analysis_result = analyzer.analyze_command(full_command)
        
        role_generator = IAMRoleGenerator()
        
        # Validate cross-account parameters
        if trust_policy == "cross-account" and not account_id:
            console.print("[red]Error:[/red] --account-id is required for cross-account trust policy")
            sys.exit(1)
        
        role_config = role_generator.generate_role(
            analysis_result=analysis_result,
            role_name=role_name,
            trust_policy_type=trust_policy,
            cross_account_id=account_id
        )
        
        if output_format == "terraform":
            output_content = role_config["terraform"]
        elif output_format == "cloudformation":
            output_content = role_config["cloudformation"]
        elif output_format == "aws-cli":
            output_content = role_config["aws_cli"]
        else:  # json
            output_content = json.dumps(role_config["json"], indent=2)
        
        if save:
            with open(save, "w") as f:
                f.write(output_content)
            console.print(f"[green]Role configuration saved to:[/green] {save}")
        else:
            if output_format in ["terraform", "cloudformation", "aws-cli"]:
                syntax = Syntax(output_content, "hcl" if output_format == "terraform" else "yaml")
                console.print(syntax)
            else:
                syntax = Syntax(output_content, "json")
                console.print(syntax)
        
    except Exception as e:
        console.print(f"[red]Error generating role:[/red] {str(e)}")
        if ctx.obj["verbose"]:
            import traceback
            console.print(traceback.format_exc())
        sys.exit(1)


@cli.command()
@click.argument("commands_file", type=click.Path(exists=True))
@click.option("--output-dir", "-o", type=click.Path(), default="./iam-analysis",
              help="Output directory for analysis results")
@click.option("--format", "-f", type=click.Choice(["json", "yaml"]), 
              default="json", help="Output format")
@click.option("--debug", "-d", is_flag=True, help="Enable debug mode to show fallback warnings")
@click.pass_context
def batch_analyze(ctx: click.Context, commands_file: str, output_dir: str, format: str, debug: bool) -> None:
    """
    Analyze multiple AWS CLI commands from a file.
    
    COMMANDS_FILE: File containing AWS CLI commands (one per line)
    """
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    try:
        with open(commands_file, "r") as f:
            commands = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        
        console.print(f"[blue]Analyzing {len(commands)} commands...[/blue]")
        
        analyzer = IAMPermissionAnalyzer(debug_mode=debug)
        results = {}
        
        for i, command in enumerate(commands, 1):
            if not command.startswith("aws "):
                command = f"aws {command}"
            
            console.print(f"[yellow]({i}/{len(commands)})[/yellow] {command}")
            
            try:
                result = analyzer.analyze_command(command)
                results[command] = result
            except Exception as e:
                console.print(f"[red]  Error:[/red] {str(e)}")
                results[command] = {"error": str(e)}
        
        # Save results
        output_file = output_path / f"batch_analysis.{format}"
        with open(output_file, "w") as f:
            if format == "json":
                json.dump(results, f, indent=2)
            else:  # yaml
                import yaml
                yaml.dump(results, f, default_flow_style=False)
        
        console.print(f"[green]Batch analysis complete. Results saved to:[/green] {output_file}")
        
    except Exception as e:
        console.print(f"[red]Error in batch analysis:[/red] {str(e)}")
        if ctx.obj["verbose"]:
            import traceback
            console.print(traceback.format_exc())
        sys.exit(1)


@cli.command()
@click.option("--services", "-s", multiple=True, help="Specific services to scrape (default: all)")
@click.option("--output", "-o", default="generated_permissions_db.py", help="Output file for generated database")
@click.option("--format", "-f", type=click.Choice(["python", "json"]), default="python", help="Output format")
@click.option("--compare", is_flag=True, help="Compare with existing database and show differences")
@click.option("--update-existing", is_flag=True, help="Update existing database with missing commands")
@click.pass_context
def scrape_docs(ctx: click.Context, services: tuple, output: str, format: str, compare: bool, update_existing: bool) -> None:
    """
    Scrape AWS CLI documentation to build comprehensive permissions database.
    
    This command automatically discovers AWS services and commands, then generates
    IAM permission mappings using intelligent heuristics and patterns.
    
    Examples:
    
        # Scrape all AWS services
        iam-generator scrape-docs
        
        # Scrape specific services only
        iam-generator scrape-docs --services ec2 --services s3 --services rds
        
        # Compare with existing database
        iam-generator scrape-docs --compare
        
        # Update existing database with missing commands
        iam-generator scrape-docs --update-existing
    """
    import logging
    
    if ctx.obj.get("verbose"):
        logging.basicConfig(level=logging.INFO)
    
    scraper = AWSCLIDocumentationScraper()
    
    try:
        if compare:
            # Compare with existing database
            console.print("[bold blue]Comparing with existing database...[/bold blue]")
            
            try:
                try:
                    from .permissions_db import IAMPermissionsDatabase
                except ImportError:
                    from iam_generator.permissions_db import IAMPermissionsDatabase
                existing_db_instance = IAMPermissionsDatabase()
                existing_db = existing_db_instance._permissions_map
                comparison = scraper.compare_with_existing(existing_db, list(services) if services else None)
                
                # Display comparison results
                console.print("\n[bold green]Database Comparison Results:[/bold green]")
                
                if comparison["missing_services"]:
                    console.print(f"\n[yellow]Missing Services ({len(comparison['missing_services'])}):[/yellow]")
                    for service in comparison["missing_services"]:
                        console.print(f"  • {service}")
                
                if comparison["missing_commands"]:
                    console.print(f"\n[yellow]Missing Commands ({len(comparison['missing_commands'])}):[/yellow]")
                    for command in comparison["missing_commands"]:
                        console.print(f"  • {command}")
                
                if comparison["new_services"]:
                    console.print(f"\n[green]Manual Services ({len(comparison['new_services'])}):[/green]")
                    for service in comparison["new_services"]:
                        console.print(f"  • {service}")
                
                if comparison["new_commands"]:
                    console.print(f"\n[green]Manual Commands ({len(comparison['new_commands'])}):[/green]")
                    for command in comparison["new_commands"]:
                        console.print(f"  • {command}")
                
                if not any(comparison.values()):
                    console.print("[green]✓ Databases are in sync![/green]")
                
            except ImportError:
                console.print("[red]Error: Could not import existing database for comparison[/red]")
                return
        
        elif update_existing:
            # Update existing database with missing commands
            console.print("[bold blue]Updating existing database...[/bold blue]")
            
            try:
                try:
                    from .permissions_db import IAMPermissionsDatabase
                except ImportError:
                    from iam_generator.permissions_db import IAMPermissionsDatabase
                existing_db_instance = IAMPermissionsDatabase()
                existing_db = existing_db_instance._permissions_map
                comparison = scraper.compare_with_existing(existing_db, list(services) if services else None)
                
                if comparison["missing_commands"]:
                    console.print(f"Found {len(comparison['missing_commands'])} missing commands")
                    
                    # Generate permissions for missing commands only
                    missing_services = set()
                    for cmd in comparison["missing_commands"]:
                        service, command = cmd.split(":", 1)
                        missing_services.add(service)
                    
                    # Scrape only the services with missing commands
                    generated_db = scraper.generate_permissions_database(list(missing_services))
                    
                    # Create update entries
                    update_content = "\n# Missing commands found by doc_scraper:\n"
                    for cmd in comparison["missing_commands"]:
                        service, command = cmd.split(":", 1)
                        if service in generated_db and command in generated_db[service]:
                            command_perms = generated_db[service][command]
                            update_content += f'    # {service}:{command}\n'
                            update_content += f'    "{command}": CommandPermissions(\n'
                            update_content += f'        service="{command_perms.service}",\n'
                            update_content += f'        action="{command_perms.action}",\n'
                            update_content += f'        permissions=[\n'
                            
                            for perm in command_perms.permissions:
                                update_content += f'            IAMPermission(action="{perm.action}", resource="{perm.resource}"),\n'
                            
                            update_content += f'        ],\n'
                            update_content += f'        description="{command_perms.description}",\n'
                            update_content += f'        resource_patterns={command_perms.resource_patterns}\n'
                            update_content += f'    ),\n'
                    
                    # Save update as separate file
                    update_file = "missing_commands_update.py"
                    with open(update_file, 'w') as f:
                        f.write(update_content)
                    
                    console.print(f"[green]✓ Missing commands saved to {update_file}[/green]")
                    console.print("[yellow]You can manually add these to your permissions_db.py[/yellow]")
                
                else:
                    console.print("[green]✓ No missing commands found![/green]")
                    
            except ImportError:
                console.print("[red]Error: Could not import existing database[/red]")
                return
        
        else:
            # Generate complete new database
            console.print("[bold blue]Scraping AWS CLI documentation...[/bold blue]")
            
            services_list = list(services) if services else None
            database = scraper.generate_permissions_database(services_list)
            
            if format == "python":
                scraper.save_database_to_file(database, output)
                console.print(f"[green]✓ Generated database saved to {output}[/green]")
            else:  # json format
                import json
                json_data = {}
                for service, commands in database.items():
                    json_data[service] = {}
                    for cmd_name, cmd_perms in commands.items():
                        json_data[service][cmd_name] = {
                            "service": cmd_perms.service,
                            "action": cmd_perms.action,
                            "permissions": [{"action": p.action, "resource": p.resource} for p in cmd_perms.permissions],
                            "description": cmd_perms.description,
                            "resource_patterns": cmd_perms.resource_patterns
                        }
                
                with open(output, 'w') as f:
                    json.dump(json_data, f, indent=2)
                console.print(f"[green]✓ Generated database saved to {output}[/green]")
            
            # Show statistics
            total_commands = sum(len(commands) for commands in database.values())
            console.print(f"\n[bold green]Statistics:[/bold green]")
            console.print(f"  Services: {len(database)}")
            console.print(f"  Commands: {total_commands}")
    
    except Exception as e:
        console.print(f"[red]Error during scraping: {e}[/red]")
        if ctx.obj.get("verbose"):
            import traceback
            console.print(traceback.format_exc())
        sys.exit(1)


@cli.command()
@click.option("--missing-only", is_flag=True, help="Show only commands that are missing from database")
@click.pass_context 
def list_services(ctx: click.Context, missing_only: bool) -> None:
    """
    List all available AWS services and their command coverage.
    
    This command shows which AWS services are available and how many
    commands are currently supported in the permissions database.
    """
    try:
        scraper = AWSCLIDocumentationScraper()
        available_services = scraper.discover_services()
        
        if missing_only:
            # Show only services missing from database
            try:
                try:
                    from .permissions_db import IAMPermissionsDatabase
                except ImportError:
                    from iam_generator.permissions_db import IAMPermissionsDatabase
                existing_db_instance = IAMPermissionsDatabase()
                existing_db = existing_db_instance._permissions_map
                missing_services = [s for s in available_services if s not in existing_db]
                
                console.print(f"[bold yellow]Missing Services ({len(missing_services)}):[/bold yellow]")
                for service in sorted(missing_services):
                    console.print(f"  • {service}")
                    
            except ImportError:
                console.print("[red]Error: Could not import existing database[/red]")
        else:
            # Show all services with coverage information
            try:
                try:
                    from .permissions_db import IAMPermissionsDatabase
                except ImportError:
                    from iam_generator.permissions_db import IAMPermissionsDatabase
                existing_db_instance = IAMPermissionsDatabase()
                existing_db = existing_db_instance._permissions_map
                
                table = Table(title="AWS Services Coverage")
                table.add_column("Service", style="cyan")
                table.add_column("Status", style="green")
                table.add_column("Commands", justify="right")
                
                for service in sorted(available_services):
                    if service in existing_db:
                        command_count = len(existing_db[service])
                        table.add_row(service, "✓ Supported", str(command_count))
                    else:
                        table.add_row(service, "⚠ Missing", "0")
                
                console.print(table)
                
                # Show summary
                supported = len([s for s in available_services if s in existing_db])
                total = len(available_services)
                console.print(f"\n[bold]Summary:[/bold] {supported}/{total} services supported ({supported/total*100:.1f}%)")
                
            except ImportError:
                # Show without coverage information
                console.print("[bold blue]Available AWS Services:[/bold blue]")
                for service in sorted(available_services):
                    console.print(f"  • {service}")
                console.print(f"\nTotal: {len(available_services)} services")
    
    except Exception as e:
        console.print(f"[red]Error listing services: {e}[/red]")
        sys.exit(1)


@cli.command("stats")
@click.option("--format", "-f", type=click.Choice(["table", "json"]), 
              default="table", help="Output format")
@click.option("--save", "-s", type=click.Path(), help="Save stats to file")
@click.pass_context
def show_stats(ctx: click.Context, format: str, save: Optional[str]) -> None:
    """
    Show auto-discovery system statistics.
    
    Display comprehensive statistics about the auto-discovery cache,
    supported services, and system performance.
    """
    if ctx.obj["verbose"]:
        console.print("[blue]Getting auto-discovery statistics...[/blue]")
    
    try:
        analyzer = IAMPermissionAnalyzer(enable_auto_discovery=True)
        stats = analyzer.get_auto_discovery_stats()
        
        if format == "table":
            _display_stats_table(stats)
        else:
            _display_stats_json(stats)
        
        if save:
            _save_stats(stats, save, format)
            console.print(f"[green]Stats saved to {save}[/green]")
            
    except Exception as e:
        console.print(f"[red]Error getting statistics: {e}[/red]")
        sys.exit(1)


def _display_stats_table(stats: Dict[str, Any]) -> None:
    """Display statistics in table format."""
    
    # Main statistics table
    main_table = Table(title="🔍 Auto-Discovery System Statistics")
    main_table.add_column("Metric", style="cyan", no_wrap=True)
    main_table.add_column("Value", style="magenta")
    main_table.add_column("Description", style="white")
    
    # Core stats
    main_table.add_row(
        "Auto-Discovery Status", 
        "✅ Enabled" if stats.get('auto_discovery_enabled', False) else "❌ Disabled",
        "Whether auto-discovery is active"
    )
    
    main_table.add_row(
        "Manual Services", 
        str(stats.get('manual_services', 0)),
        "Services in the manual database"
    )
    
    if stats.get('auto_discovery_enabled', False):
        main_table.add_row(
            "Auto-Discovered Services", 
            str(stats.get('total_cached_services', 0)),
            "Services discovered automatically"
        )
        
        main_table.add_row(
            "Cached Commands", 
            str(stats.get('total_cached_commands', 0)),
            "Commands cached from discovery"
        )
        
        main_table.add_row(
            "High-Confidence Commands", 
            str(stats.get('high_confidence_commands', 0)),
            "Commands with high confidence ratings"
        )
        
        cache_size_kb = stats.get('cache_file_size', 0) / 1024
        main_table.add_row(
            "Cache Size", 
            f"{cache_size_kb:.1f} KB",
            "Size of auto-discovery cache file"
        )
        
        main_table.add_row(
            "Analyzer Cache", 
            str(stats.get('analyzer_cache_size', 0)),
            "Items in analyzer cache"
        )
    
    # System capabilities
    main_table.add_row(
        "Scraper Available", 
        "✅ Yes" if stats.get('scraper_available', False) else "❌ No",
        "Documentation scraper availability"
    )
    
    console.print(main_table)
    
    # Show total supported services
    total_services = stats.get('manual_services', 0) + stats.get('total_cached_services', 0)
    
    console.print(f"\n📊 [bold green]Total Supported Services: {total_services}[/bold green]")
    
    if stats.get('auto_discovery_enabled', False) and stats.get('total_cached_services', 0) > 0:
        console.print(f"   └─ Manual Database: {stats.get('manual_services', 0)} services")
        console.print(f"   └─ Auto-Discovered: {stats.get('total_cached_services', 0)} services")
        
        improvement = (stats.get('total_cached_services', 0) / stats.get('manual_services', 1)) * 100
        console.print(f"   └─ Discovery Improvement: +{improvement:.1f}%")


def _display_stats_json(stats: Dict[str, Any]) -> None:
    """Display statistics in JSON format."""
    json_output = json.dumps(stats, indent=2)
    syntax = Syntax(json_output, "json", theme="monokai")
    console.print(syntax)


def _save_stats(stats: Dict[str, Any], filepath: str, format: str) -> None:
    """Save statistics to file."""
    with open(filepath, "w") as f:
        if format == "json":
            json.dump(stats, f, indent=2)
        else:  # table format as text
            f.write("Auto-Discovery System Statistics\n")
            f.write("================================\n\n")
            for key, value in stats.items():
                f.write(f"{key}: {value}\n")


def _display_table_output(result: Dict[str, Any]) -> None:
    """Display analysis result in table format."""
    # Command details
    console.print(Panel(
        f"[bold]Service:[/bold] {result['service']}\n"
        f"[bold]Action:[/bold] {result['action']}\n"
        f"[bold]Command:[/bold] {result['original_command']}",
        title="Command Analysis",
        border_style="blue"
    ))
    
    # Required permissions table
    if result['required_permissions']:
        table = Table(title="Required IAM Permissions")
        table.add_column("Permission", style="cyan")
        table.add_column("Resource", style="magenta")
        
        for perm in result['required_permissions']:
            table.add_row(perm['action'], perm.get('resource', '*'))
        
        console.print(table)
    
    # Additional permissions if any
    if result.get('additional_permissions'):
        additional_table = Table(title="Additional Permissions (Optional)")
        additional_table.add_column("Permission", style="yellow")
        additional_table.add_column("Reason", style="green")
        
        for perm in result['additional_permissions']:
            additional_table.add_row(perm['action'], perm.get('reason', ''))
        
        console.print(additional_table)
    
    # Display warnings if any (only in debug mode)
    if result.get('warnings'):
        warning_text = "\n".join(f"⚠️  {warning}" for warning in result['warnings'])
        console.print(Panel(warning_text, title="Debug Warnings", border_style="yellow"))
    
    # Generated policy document
    if result.get('policy_document'):
        policy_json = json.dumps(result['policy_document'], indent=2)
        syntax = Syntax(policy_json, "json", theme="monokai")
        console.print(Panel(syntax, title="Generated IAM Policy", border_style="green"))


def _display_json_output(result: Dict[str, Any]) -> None:
    """Display analysis result in JSON format."""
    json_output = json.dumps(result, indent=2)
    syntax = Syntax(json_output, "json", theme="monokai")
    console.print(syntax)


def _display_yaml_output(result: Dict[str, Any]) -> None:
    """Display analysis result in YAML format."""
    import yaml
    yaml_output = yaml.dump(result, default_flow_style=False)
    syntax = Syntax(yaml_output, "yaml", theme="monokai")
    console.print(syntax)


def _save_output(result: Dict[str, Any], filepath: str, format: str) -> None:
    """Save analysis result to file."""
    with open(filepath, "w") as f:
        if format == "json":
            json.dump(result, f, indent=2)
        elif format == "yaml":
            import yaml
            yaml.dump(result, f, default_flow_style=False)
        else:  # table format as text
            f.write(f"Service: {result['service']}\n")
            f.write(f"Action: {result['action']}\n")
            f.write(f"Command: {result['original_command']}\n\n")
            f.write("Required Permissions:\n")
            for perm in result['required_permissions']:
                f.write(f"  - {perm['action']} on {perm.get('resource', '*')}\n")
            if result.get('policy_document'):
                f.write("\nGenerated Policy:\n")
                f.write(json.dumps(result['policy_document'], indent=2))


if __name__ == "__main__":
    cli()
