# Rich Console Reference

**Official Docs:** https://rich.readthedocs.io/  
**GitHub:** https://github.com/Textualize/rich  
**Version:** 14.x

---

## Installation

```bash
pip install rich
```

---

## Quick Start

```python
from rich.console import Console

console = Console()

console.print("Hello, [bold magenta]World[/bold magenta]!")
console.print("[green]Success![/green]")
console.print("[red]Error![/red]")
```

---

## Progress Bars

### Simple Track

```python
from rich.progress import track
import time

for i in track(range(100), description="Processing..."):
    time.sleep(0.1)
```

### Advanced Progress

```python
from rich.progress import (
    Progress, 
    SpinnerColumn, 
    TextColumn, 
    BarColumn,
    TaskProgressColumn,
    TimeElapsedColumn
)

with Progress(
    SpinnerColumn(),
    TextColumn("[progress.description]{task.description}"),
    BarColumn(),
    TaskProgressColumn(),
    TextColumn("[{task.completed}/{task.total}]"),
    TimeElapsedColumn(),
) as progress:
    task1 = progress.add_task("[cyan]Downloading...", total=100)
    task2 = progress.add_task("[green]Processing...", total=100)
    
    while not progress.finished:
        progress.update(task1, advance=0.5)
        progress.update(task2, advance=0.3)
        time.sleep(0.02)
```

---

## Console Output

### Styled Text

```python
console.print("[bold]Bold[/bold]")
console.print("[italic]Italic[/italic]")
console.print("[underline]Underline[/underline]")
console.print("[strike]Strikethrough[/strike]")
console.print("[bold red on white]Red on white[/]")
```

### Colors

- Basic: `red`, `green`, `blue`, `yellow`, `magenta`, `cyan`, `white`
- Modifiers: `bold`, `dim`, `italic`, `underline`
- Backgrounds: `on red`, `on blue`, etc.

### Rules (Dividers)

```python
console.rule("[bold]Section Title[/]")
console.rule(style="dim")
console.rule("[bold green]✓ Complete[/]", style="green")
```

---

## Logging

```python
console.log("Starting process...")
console.log("[green]✓[/] Task completed")
console.log("[yellow]⚠[/] Warning message")
console.log("[red]✗[/] Error occurred")
```

---

## Tables

```python
from rich.table import Table

table = Table(title="Results")
table.add_column("Name", style="cyan")
table.add_column("Status", justify="center")
table.add_column("Count", justify="right")

table.add_row("Task 1", "[green]Complete[/]", "100")
table.add_row("Task 2", "[yellow]Pending[/]", "50")

console.print(table)
```

---

## Panels

```python
from rich.panel import Panel

console.print(Panel("Hello World", title="Welcome"))
console.print(Panel.fit("[bold green]Success![/]", border_style="green"))
```

---

## Status Spinner

```python
with console.status("[bold green]Working...") as status:
    # Do work
    time.sleep(2)
    status.update("[bold blue]Almost done...")
    time.sleep(1)
```

---

## Common Patterns

### CLI Application Header

```python
console.rule("[bold blue]🎬 Content Repurposing Tool[/]", style="blue")
console.print()
console.print("📁 [bold]Output Directories:[/]")
console.print(f"   └─ Content: [cyan]/path/to/output[/]")
```

### Processing Loop with Status

```python
for idx, item in enumerate(items, 1):
    console.print()
    console.rule(f"[bold]Item {idx}/{len(items)}[/]", style="dim")
    console.log(f"🎥 Processing: [bold]{item}[/]")
    
    # Success
    console.log(f"[green]✓[/] Completed successfully")
    
    # Warning
    console.log(f"[yellow]⚠[/] Skipped - no data")
    
    # Error
    console.log(f"[red]✗[/] Failed: {error}")
```

### Summary Output

```python
console.print()
console.rule("[bold green]✓ Processing Complete[/]", style="green")
console.print()
console.print("📊 [bold]Generated Content:[/]")
console.print(f"   🎬 [bold blue]{count}[/] Reel(s)")
console.print(f"   🐦 [bold cyan]{count}[/] Tweet(s)")
console.print(f"   🖼️  [bold magenta]{count}[/] Carousel(s)")
```

---

## Emoji Reference

Common emojis for CLI output:
- ✓ `[green]✓[/]` - Success
- ✗ `[red]✗[/]` - Error  
- ⚠ `[yellow]⚠[/]` - Warning
- 📁 Folder
- 🎥 Video
- 📄 Document
- 💡 Idea/Tip
- ✨ Generated
- 🔍 Search
- ⚙️ Config

---

## Integration with Logging

```python
import logging
from rich.logging import RichHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)]
)

log = logging.getLogger("rich")
log.info("This uses rich formatting")
```

---

## Related Specs

- [Stack Decisions](../specs/stack.md)
