#!/usr/bin/env python3
"""
Log Viewer Terminal UI
A Textual-based terminal UI for viewing and interacting with command output.

Usage: python log_viewer.py <command> [args...]
"""

import sys
import subprocess
import threading
import time
import platform
from typing import List, Optional, Any, TextIO
from dataclasses import dataclass
from enum import Enum

from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Header, Footer, Static, Input
from textual.scroll_view import ScrollView
from textual.binding import Binding
from textual import events


class Mode(Enum):
    NORMAL = "NORMAL"
    INSERT = "INSERT"
    SEARCH = "SEARCH"
    FILTER = "FILTER"


@dataclass
class LogLine:
    content: str
    source: str  # 'stdout' or 'stderr'
    timestamp: float
    line_number: int


class LogViewer(ScrollView):
    """Main log viewing widget with search and filter capabilities."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.lines: List[LogLine] = []
        self.filtered_lines: List[LogLine] = []
        self.search_term: str = ""
        self.filter_term: str = ""
        self.line_counter = 0
        self.auto_scroll = True

    def add_line(self, content: str, source: str = "stdout"):
        """Add a new line to the log."""
        self.line_counter += 1
        line = LogLine(
            content=content.rstrip("\n\r"),
            source=source,
            timestamp=time.time(),
            line_number=self.line_counter,
        )
        self.lines.append(line)
        self.refresh_display()

    def refresh_display(self):
        """Refresh the display based on current filters."""
        self.filtered_lines = self.lines.copy()

        # Apply filter
        if self.filter_term:
            self.filtered_lines = [
                line
                for line in self.filtered_lines
                if self.filter_term.lower() in line.content.lower()
            ]

        # Clear and repopulate
        self.remove_children()

        for line in self.filtered_lines:
            # Highlight search term if present
            if self.search_term and self.search_term.lower() in line.content.lower():
                content = self._highlight_search(line.content, self.search_term)
            else:
                content = line.content

            # Format line number with padding and separator

            # Add appropriate icons based on source
            if line.source == "stderr":
                icon = "❌ "
                style_class = "stderr"
            elif line.source == "system":
                icon = "ℹ️  "
                style_class = "system"
            elif line.source == "input":
                icon = "➤ "
                style_class = "input"
            else:
                icon = ""
                style_class = "stdout"

            formatted_content = f"{icon}{content}"

            line_widget = Static(formatted_content, classes=f"log-line {style_class}")
            self.mount(line_widget)

        if self.auto_scroll:
            self.scroll_end()

    def _highlight_search(self, content: str, search_term: str) -> str:
        """Highlight search term in content using Rich markup."""
        if not search_term:
            return content

        # Case-insensitive highlighting
        import re

        pattern = re.escape(search_term)
        highlighted = re.sub(
            pattern,
            f"[black on yellow]{search_term}[/black on yellow]",
            content,
            flags=re.IGNORECASE,
        )
        return highlighted

    def set_search(self, term: str):
        """Set search term and refresh display."""
        self.search_term = term
        self.refresh_display()

    def set_filter(self, term: str):
        """Set filter term and refresh display."""
        self.filter_term = term
        self.refresh_display()

    def clear_search(self):
        """Clear search term."""
        self.search_term = ""
        self.refresh_display()

    def clear_filter(self):
        """Clear filter term."""
        self.filter_term = ""
        self.refresh_display()


class StatusBar(Static):
    """Status bar showing current mode and other info."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.mode = Mode.NORMAL
        self.command = ""
        self.process_running = False

    def update_status(
        self,
        mode: Mode,
        command: str = "",
        process_running: bool = False,
        line_count: int = 0,
    ):
        """Update the status bar with enhanced formatting."""
        self.mode = mode
        self.command = command
        self.process_running = process_running

        # Mode indicator with color coding
        mode_indicators = {
            Mode.NORMAL: "[bold blue]◉ NORMAL[/bold blue]",
            Mode.INSERT: "[bold green]◉ INSERT[/bold green]",
            Mode.SEARCH: "[bold yellow]◉ SEARCH[/bold yellow]",
            Mode.FILTER: "[bold magenta]◉ FILTER[/bold magenta]",
        }

        mode_text = mode_indicators.get(mode, f"◉ {mode.value}")

        # Process status with icons
        if process_running:
            status_icon = "[green]●[/green] RUNNING"
        else:
            status_icon = "[red]●[/red] STOPPED"

        # Build status text
        status_parts = [mode_text]

        if command:
            # Truncate long commands
            display_command = command if len(command) <= 40 else command[:37] + "..."
            status_parts.append(f"[dim]Command:[/dim] [bold]{display_command}[/bold]")

        status_parts.append(status_icon)

        # Add line count
        if line_count > 0:
            status_parts.append(f"[dim]Lines:[/dim] {line_count}")

        status_text = " [dim]│[/dim] ".join(status_parts)
        self.update(status_text)


class LogViewerApp(App[None]):
    """Main application class."""

    TITLE = "Riveflow"
    SUB_TITLE = "Interactive command output viewer"

    # CSS = """
    # /* Main app styling */
    # App {
    #     background: #0d0d0d;
    # }

    # /* Header styling */
    # Header {
    #     background: #161616;
    #     color: white;
    #     text-style: bold;
    #     border: solid #106ebe;
    # }

    # /* Footer styling */
    # Footer {
    #     background: #161616;
    #     color: #cccccc;
    #     border-top: solid #0078d4;
    #     padding: 0 1;
    # }

    # /* Main container */
    # .main-view {
    #     height: 1fr;
    #     background: #1e1e1e;
    #     border: round #005a9e;
    #     margin: 1;
    # }

    # /* Log viewer styling */
    # LogViewer {
    #     background: #1e1e1e;
    #     border: solid #004578;
    #     scrollbar-background: #161616;
    #     scrollbar-color: #0078d4;
    #     scrollbar-color-hover: #ff6b35;
    #     scrollbar-color-active: #ff8c42;
    # }

    # /* Log line styling */
    # .log-line {
    #     padding: 0 1;
    #     margin: 0;
    #     height: 1;
    #     border-left: solid transparent;
    # }

    # .log-line:hover {
    #     background: #2d2d30;
    #     border-left: solid #ff6b35;
    # }

    # /* Different log line types */
    # .stderr {
    #     background: #e74856 15%;
    #     color: #f48fb1;
    #     border-left: solid #e74856;
    # }

    # .stderr:hover {
    #     background: #e74856 25%;
    # }

    # .stdout {
    #     color: white;
    # }

    # .system {
    #     background: #16c60c 10%;
    #     color: #4caf50;
    #     border-left: solid #16c60c;
    #     text-style: italic;
    # }

    # .system:hover {
    #     background: #16c60c 20%;
    # }

    # .input {
    #     background: #ffb900 10%;
    #     color: white;
    #     border-left: solid #ffb900;
    #     text-style: bold;
    # }

    # .input:hover {
    #     background: #ffb900 20%;
    # }

    # /* Input bar styling */
    # .input-bar {
    #     dock: bottom;
    #     height: 3;
    #     background: #161616;
    #     border: round #005a9e;
    #     margin: 0 1 1 1;
    # }

    # Input {
    #     background: #1e1e1e;
    #     border: solid #005a9e;
    #     color: white;
    #     padding: 0 1;
    # }

    # Input:focus {
    #     border: solid #ff6b35;
    #     background: #2d2d30;
    # }

    # /* Status bar styling */
    # .status-bar {
    #     dock: bottom;
    #     height: 1;
    #     background: #005a9e;
    #     color: white;
    #     text-style: bold;
    #     border-top: solid #106ebe;
    #     padding: 0 1;
    # }

    # /* Search highlighting */
    # .highlight {
    #     background: #ffb900;
    #     color: #1e1e1e;
    #     text-style: bold;
    # }

    # /* Container styling */
    # Container {
    #     background: transparent;
    # }
    # """
    CSS = ""

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit", show=True),
        Binding("i", "insert_mode", "Insert", show=True),
        Binding("escape", "normal_mode", "Normal", show=True),
        Binding("/", "search_mode", "Search", show=True),
        Binding("f", "filter_mode", "Filter", show=True),
        Binding("ctrl+l", "clear_log", "Clear", show=True),
        Binding("ctrl+k", "kill_process", "Kill", show=True),
        Binding("ctrl+r", "restart_process", "Restart", show=True),
        Binding("ctrl+s", "toggle_autoscroll", "Auto-scroll", show=True),
    ]

    def __init__(self, command_args: List[str]):
        super().__init__()
        self.command_args = command_args
        self.mode = Mode.NORMAL
        self.process: Optional[subprocess.Popen[str]] = None
        self.process_thread: Optional[threading.Thread] = None
        self.log_viewer: Optional[LogViewer] = None
        self.status_bar: Optional[StatusBar] = None
        self.input_bar: Optional[Input] = None

    def compose(self) -> ComposeResult:
        """Compose the UI."""
        yield Header()

        with Container(classes="main-view"):
            self.log_viewer = LogViewer()
            yield self.log_viewer

        with Container(classes="input-bar"):
            self.input_bar = Input(placeholder="Insert mode: type to send to process")
            self.input_bar.display = False
            yield self.input_bar

        self.status_bar = StatusBar(classes="status-bar")
        yield self.status_bar

        yield Footer()

    def on_mount(self) -> None:
        """Called when the app is mounted."""
        # Add welcome message
        # if self.log_viewer:
        # self.log_viewer.add_line("🚀 Log Viewer UI Started", "system")
        # self.log_viewer.add_line(
        #     "Press 'i' for insert mode, '/' for search, 'f' for filter", "system"
        # )
        # self.log_viewer.add_line(
        #     "Use Ctrl+C to quit, Ctrl+K to kill process", "system"
        # )
        # self.log_viewer.add_line("─" * 60, "system")

        self.update_status()
        self.start_process()

    def start_process(self) -> None:
        """Start the command process."""
        if self.process and self.process.poll() is None:
            return

        try:
            self.process = subprocess.Popen(
                self.command_args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
            )

            self.process_thread = threading.Thread(target=self._read_process_output)
            self.process_thread.daemon = True
            self.process_thread.start()

            if self.log_viewer:
                self.log_viewer.add_line(
                    f"Started command: {' '.join(self.command_args)}", "system"
                )
            self.update_status()

        except Exception as e:
            if self.log_viewer:
                self.log_viewer.add_line(f"Failed to start command: {e}", "stderr")

    def _read_process_output(self) -> None:
        """Read process output in a separate thread."""
        if not self.process or not self.log_viewer:
            return

        # Use platform-appropriate method to read output
        if platform.system() == "Windows":
            self._read_output_windows()
        else:
            self._read_output_unix()

        self._read_remaining_output()

        return_code = self.process.returncode if self.process else -1
        self.call_from_thread(
            self.log_viewer.add_line,
            f"Process exited with code {return_code}",
            "system",
        )
        self.call_from_thread(self.update_status)

    def _read_output_windows(self) -> None:
        """Read output on Windows using threading."""
        if not self.process or not self.log_viewer:
            return

        # Create separate threads for stdout and stderr
        stdout_thread = None
        stderr_thread = None

        if self.process.stdout:
            stdout_thread = threading.Thread(
                target=self._read_stream_thread, args=(self.process.stdout, "stdout")
            )
            stdout_thread.daemon = True
            stdout_thread.start()

        if self.process.stderr:
            stderr_thread = threading.Thread(
                target=self._read_stream_thread, args=(self.process.stderr, "stderr")
            )
            stderr_thread.daemon = True
            stderr_thread.start()

        # Wait for process to complete
        self.process.wait()

        # Give threads a moment to finish reading
        if stdout_thread:
            stdout_thread.join(timeout=1.0)
        if stderr_thread:
            stderr_thread.join(timeout=1.0)

    def _read_stream_thread(self, stream: TextIO, source: str) -> None:
        """Read from a single stream in a separate thread."""
        if not self.log_viewer:
            return

        try:
            while True:
                line = stream.readline()
                if not line:
                    break
                self.call_from_thread(self.log_viewer.add_line, line, source)
        except Exception as e:
            self.call_from_thread(
                self.log_viewer.add_line, f"Error reading {source}: {e}", "stderr"
            )

    def _read_output_unix(self) -> None:
        """Read output on Unix systems using select."""
        if not self.process or not self.log_viewer:
            return

        try:
            import select
        except ImportError:
            # Fallback to Windows method if select is not available
            self._read_output_windows()
            return

        while self.process.poll() is None:
            try:
                self._process_available_streams_unix(select)
            except Exception as e:
                self.call_from_thread(
                    self.log_viewer.add_line, f"Error reading output: {e}", "stderr"
                )
                break

    def _process_available_streams_unix(self, select_module: Any) -> None:
        """Process available stdout/stderr streams using select (Unix only)."""
        if not self.process or not self.log_viewer:
            return

        stdout = self.process.stdout
        stderr = self.process.stderr

        if not stdout or not stderr:
            return

        ready, _, _ = select_module.select([stdout, stderr], [], [], 0.1)

        for stream in ready:
            line = stream.readline()
            if line:
                source = "stdout" if stream == stdout else "stderr"
                self.call_from_thread(self.log_viewer.add_line, line, source)

    def _read_remaining_output(self) -> None:
        """Read any remaining output after process ends."""
        if not self.process or not self.log_viewer:
            return

        # Read any remaining output
        if self.process.stdout:
            remaining = self.process.stdout.read()
            if remaining:
                self.call_from_thread(self.log_viewer.add_line, remaining, "stdout")

        if self.process.stderr:
            remaining = self.process.stderr.read()
            if remaining:
                self.call_from_thread(self.log_viewer.add_line, remaining, "stderr")

    def update_status(self) -> None:
        """Update the status bar."""
        if self.status_bar:
            running = bool(self.process and self.process.poll() is None)
            line_count = len(self.log_viewer.lines) if self.log_viewer else 0
            self.status_bar.update_status(
                self.mode, " ".join(self.command_args), running, line_count
            )

    def action_insert_mode(self) -> None:
        """Switch to insert mode."""
        if not self.input_bar:
            return
        self.mode = Mode.INSERT
        self.input_bar.display = True
        self.input_bar.focus()
        self.input_bar.placeholder = "Insert mode: type to send to process"
        self.update_status()

    def action_normal_mode(self) -> None:
        """Switch to normal mode."""
        if not self.input_bar or not self.log_viewer:
            return
        self.mode = Mode.NORMAL
        self.input_bar.display = False
        self.log_viewer.focus()
        self.update_status()

    def action_search_mode(self) -> None:
        """Switch to search mode."""
        if not self.input_bar:
            return
        self.mode = Mode.SEARCH
        self.input_bar.display = True
        self.input_bar.focus()
        self.input_bar.placeholder = "Search: enter term to highlight"
        self.input_bar.value = ""
        self.update_status()

    def action_filter_mode(self) -> None:
        """Switch to filter mode."""
        if not self.input_bar:
            return
        self.mode = Mode.FILTER
        self.input_bar.display = True
        self.input_bar.focus()
        self.input_bar.placeholder = "Filter: enter term to filter lines"
        self.input_bar.value = ""
        self.update_status()

    def action_clear_log(self) -> None:
        """Clear the log."""
        if not self.log_viewer:
            return
        self.log_viewer.lines.clear()
        self.log_viewer.filtered_lines.clear()
        self.log_viewer.line_counter = 0
        self.log_viewer.refresh_display()

    def action_kill_process(self) -> None:
        """Kill the running process."""
        if self.process and self.process.poll() is None:
            self.process.terminate()
            if self.log_viewer:
                self.log_viewer.add_line("Process terminated", "system")
            self.update_status()

    def action_restart_process(self) -> None:
        """Restart the running process."""
        if self.process and self.process.poll() is None:
            self.process.terminate()
            if self.log_viewer:
                self.log_viewer.add_line("Process terminated for restart", "system")

        # Small delay before restart
        import time

        time.sleep(0.5)
        self.start_process()

    def action_toggle_autoscroll(self) -> None:
        """Toggle auto-scroll functionality."""
        if self.log_viewer:
            self.log_viewer.auto_scroll = not self.log_viewer.auto_scroll
            status = "enabled" if self.log_viewer.auto_scroll else "disabled"
            self.log_viewer.add_line(f"Auto-scroll {status}", "system")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission."""
        if self.mode == Mode.INSERT:
            # Send to process stdin
            if (
                self.process
                and self.process.poll() is None
                and self.process.stdin
                and self.log_viewer
            ):
                try:
                    self.process.stdin.write(event.value + "\n")
                    self.process.stdin.flush()
                    self.log_viewer.add_line(f">>> {event.value}", "input")
                except Exception as e:
                    self.log_viewer.add_line(f"Error sending input: {e}", "stderr")

            if self.input_bar:
                self.input_bar.value = ""

        elif self.mode == Mode.SEARCH:
            # Perform search
            if self.log_viewer:
                self.log_viewer.set_search(event.value)
            self.action_normal_mode()

        elif self.mode == Mode.FILTER:
            # Apply filter
            if self.log_viewer:
                self.log_viewer.set_filter(event.value)
            self.action_normal_mode()

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle input changes for real-time search/filter."""
        if not self.log_viewer:
            return
        if self.mode == Mode.SEARCH:
            self.log_viewer.set_search(event.value)
        elif self.mode == Mode.FILTER:
            self.log_viewer.set_filter(event.value)

    def on_key(self, event: events.Key) -> None:
        """Handle key events."""
        if event.key == "escape":
            if self.mode != Mode.NORMAL:
                if self.mode in [Mode.SEARCH, Mode.FILTER] and self.log_viewer:
                    # Clear search/filter on escape
                    self.log_viewer.clear_search()
                    self.log_viewer.clear_filter()
                self.action_normal_mode()
        elif event.key == "ctrl+c":
            if self.mode == Mode.INSERT:
                self.action_normal_mode()
            else:
                self.exit()


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python log_viewer.py <command> [args...]")
        print("Example: python log_viewer.py tail -f /var/log/syslog")
        sys.exit(1)

    command_args = sys.argv[1:]
    app = LogViewerApp(command_args)
    app.run()


if __name__ == "__main__":
    main()
