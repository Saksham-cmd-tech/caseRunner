"""
headless.py — Headless CLI executor for CaseCraft.
"""

import asyncio
from pathlib import Path

from rich.console import Console, Group
from rich.table import Table
from rich.panel import Panel
from rich.progress import (
    Progress, 
    SpinnerColumn, 
    TextColumn, 
    BarColumn, 
    TaskProgressColumn, 
    TimeElapsedColumn
)
from rich import box

from casecraft.models import TestCase, Verdict
from casecraft.runner import run_all_test_cases_async

console = Console()

VERDICT_STYLES = {
    Verdict.ACCEPTED: ("[bold green]✓ AC[/bold green]", "green"),
    Verdict.WRONG_ANSWER: ("[bold red]✗ WA[/bold red]", "red"),
    Verdict.TIME_LIMIT_EXCEEDED: ("[bold yellow]⏱ TLE[/bold yellow]", "yellow"),
    Verdict.RUNTIME_ERROR: ("[bold magenta]⚠️ RE[/bold magenta]", "magenta"),
    Verdict.COMPILATION_ERROR: ("[bold red]⚒ CE[/bold red]", "red"),
}

async def run_headless_async(file_path: str, test_cases: list[TestCase]):
    file_name = Path(file_path).name
    
    # 1. Print Header
    console.print()
    console.print(Panel(
        f"[bold blue]CaseCraft[/bold blue] ⚡ Running [bold cyan]{file_name}[/bold cyan]",
        box=box.ROUNDED,
        border_style="blue",
        padding=(0, 2)
    ))
    console.print()
    
    # 2. Dynamic Progress Bar
    results = []
    with Progress(
        SpinnerColumn(spinner_name="dots2", style="cyan"),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=40, complete_style="green", finished_style="blue"),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task_id = progress.add_task(f"[cyan]Executing {len(test_cases)} tests...", total=len(test_cases))
        
        def on_test_complete(res):
            progress.advance(task_id, 1)
            
        results = await run_all_test_cases_async(
            file_path=file_path, 
            test_cases=test_cases, 
            progress_callback=on_test_complete
        )

    # 3. Execution Summary Table
    passed_count = sum(1 for r in results if r.verdict == Verdict.ACCEPTED)
    total_count = len(results)
    total_time = sum(r.runtime_ms for r in results)
    
    table = Table(
        show_header=True, 
        header_style="bold bright_white",
        box=box.SIMPLE_HEAVY,
        expand=True,
        border_style="bright_black"
    )
    
    table.add_column("Test Case", justify="left")
    table.add_column("Verdict", justify="center", width=12)
    table.add_column("Runtime", justify="right", width=12)
    
    for i, res in enumerate(results):
        label = res.test_case.label if res.test_case.label else f"Case #{i + 1}"
        verdict_str, row_style = VERDICT_STYLES.get(res.verdict, ("[bold white]?[/]", "white"))
        
        # Dim the row if it passed to highlight failures, or keep it bright
        style = "dim" if res.verdict == Verdict.ACCEPTED else "bold"
        
        table.add_row(
            f"[{style}]{label}[/{style}]", 
            verdict_str, 
            f"[{style}]{res.runtime_ms:.1f} ms[/{style}]"
        )
        
    # 4. Final Summary Panel
    success = passed_count == total_count
    summary_color = "green" if success else "red"
    summary_text = f"[{summary_color} bold]{passed_count}/{total_count} Passed[/{summary_color} bold]"
    if success:
        summary_text += " ✨ All tests cleared!"
    else:
        summary_text += f" ❌ {total_count - passed_count} failed."
        
    summary_group = Group(
        table,
        "",
        f"{summary_text}  |  [dim]Total Time: {total_time:.1f} ms[/dim]"
    )
    
    console.print(Panel(
        summary_group,
        title="[bold]Execution Summary[/bold]",
        title_align="left",
        border_style="bright_black",
        padding=(1, 2)
    ))
    console.print()
    
    # 5. Detail Panels for Failures
    for i, res in enumerate(results):
        if res.verdict != Verdict.ACCEPTED:
            err_msg = res.error if res.error else "Output mismatch."
            label = res.test_case.label if res.test_case.label else f"Case #{i + 1}"
            verdict_str, v_color = VERDICT_STYLES.get(res.verdict, ("Error", "red"))
            
            detail_table = Table.grid(padding=(0, 2), expand=True)
            detail_table.add_column("Expected", style="green", ratio=1)
            detail_table.add_column("Actual", style="red", ratio=1)
            
            # Truncate strings to prevent massive blowouts in the terminal
            exp_str = res.test_case.expected_output[:1000] + ("..." if len(res.test_case.expected_output) > 1000 else "")
            act_str = res.actual_output[:1000] + ("..." if len(res.actual_output) > 1000 else "")
            
            detail_table.add_row("[bold]Expected Output:[/bold]", "[bold]Actual Output:[/bold]")
            detail_table.add_row(
                Panel(exp_str, border_style="green", box=box.MINIMAL), 
                Panel(act_str, border_style="red", box=box.MINIMAL)
            )
            
            details_group = Group(
                detail_table,
                "",
                f"[bold {v_color}]Details / Stderr:[/bold {v_color}]\n[dim]{err_msg}[/dim]"
            )
            
            console.print(Panel(
                details_group,
                title=f"[bold {v_color}]Failed: {label} ({verdict_str})[/bold {v_color}]",
                border_style=v_color,
                box=box.HEAVY
            ))
            console.print()

def run_headless(file_path: str, test_cases: list[TestCase]):
    asyncio.run(run_headless_async(file_path, test_cases))
