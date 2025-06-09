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
@click.pass_context
def analyze(ctx: click.Context, command: tuple, output: str, save: Optional[str]) -> None:
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
        analyzer = IAMPermissionAnalyzer()
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
@click.pass_context
def generate_role(ctx: click.Context, command: tuple, role_name: str, 
                 trust_policy: str, account_id: Optional[str],
                 output_format: str, save: Optional[str]) -> None:
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
        analyzer = IAMPermissionAnalyzer()
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
@click.pass_context
def batch_analyze(ctx: click.Context, commands_file: str, output_dir: str, format: str) -> None:
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
        
        analyzer = IAMPermissionAnalyzer()
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
def list_services() -> None:
    """List all supported AWS services and their available actions."""
    analyzer = IAMPermissionAnalyzer()
    services = analyzer.permissions_db.get_supported_services()
    
    tree = Tree("[bold blue]Supported AWS Services[/bold blue]")
    
    for service in sorted(services):
        service_node = tree.add(f"[green]{service}[/green]")
        actions = analyzer.permissions_db.get_service_actions(service)
        for action in sorted(actions):
            service_node.add(f"[yellow]{action}[/yellow]")
    
    console.print(tree)


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
