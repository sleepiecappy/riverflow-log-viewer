# Riverflow

> **Interactive Terminal UI for Command Output Monitoring**

Riverflow is a powerful, Textual-based terminal user interface that provides real-time monitoring and interaction with command output. Think of it as a supercharged `tail -f` with vim-like navigation, search capabilities, and interactive features.

## Features

- **Real-time Command Monitoring**: Execute and monitor any command with live output streaming
- **Vi-like Interface**: Familiar modal editing with Normal, Insert, Search, and Filter modes
- **Interactive Search & Filter**: Highlight search terms and filter output in real-time
- **Dual Stream Support**: Separate handling of stdout and stderr with visual distinction
- **Process Control**: Start, stop, restart, and interact with running processes
- **Auto-scroll Management**: Toggle automatic scrolling to follow new output
- **Cross-platform**: Works on Windows, macOS, and Linux
- **Modern UI**: Beautiful terminal interface with syntax highlighting and intuitive navigation

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/sleepiecappy/riverflow-log-viewer.git
cd riverflow

# Install dependencies (using uv - recommended)
uv sync

# Or using pip
pip install -r requirements.txt
```

### Basic Usage

```bash
# Monitor a long-running command
python log_viewer_ui.py python dummy_program.py

# Monitor system logs (Unix/Linux)
python log_viewer_ui.py tail -f /var/log/system.log

# Watch a build process
python log_viewer_ui.py npm run build

# Monitor a development server
python log_viewer_ui.py python manage.py runserver
```

## Controls & Navigation

### Modes

| Mode | Description | Activation |
|------|-------------|------------|
| **Normal** | Default navigation mode | `Esc` |
| **Insert** | Send input to the running process | `i` |
| **Search** | Highlight text in output | `/` |
| **Filter** | Show only matching lines | `f` |

### Key Bindings

| Key | Action | Description |
|-----|---------|-------------|
| `i` | Insert Mode | Send commands to the running process |
| `/` | Search Mode | Search and highlight text in output |
| `f` | Filter Mode | Filter output to show only matching lines |
| `Esc` | Normal Mode | Return to navigation mode |
| `Ctrl+C` | Quit | Exit the application |
| `Ctrl+L` | Clear Log | Clear the current output |
| `Ctrl+K` | Kill Process | Terminate the running process |
| `Ctrl+R` | Restart | Restart the monitored command |
| `Ctrl+S` | Toggle Auto-scroll | Enable/disable automatic scrolling |

## Usage Examples

### Development Server Monitoring

```bash
# Monitor a Django development server
python log_viewer_ui.py python manage.py runserver

# Monitor a Node.js application
python log_viewer_ui.py npm start

# Monitor a Flask app with debug output
python log_viewer_ui.py flask run --debug
```

### System Administration

```bash
# Monitor system logs
python log_viewer_ui.py journalctl -f

# Watch file changes
python log_viewer_ui.py inotifywait -m /path/to/directory

# Monitor network connections
python log_viewer_ui.py netstat -c
```

### Build & CI Monitoring

```bash
# Watch a build process
python log_viewer_ui.py make build

# Monitor test execution
python log_viewer_ui.py pytest -v

# Watch Docker build
python log_viewer_ui.py docker build -t myapp .
```

## Demo

Try the included demo to see Riverflow in action:

```bash
# Run the enhanced demo
python log_viewer_ui.py python demo_enhanced_ui.py

# Or the basic dummy program
python log_viewer_ui.py python dummy_program.py
```

The demo will generate sample log output with different types of messages, including normal output, warnings, and errors, demonstrating the color-coded display and filtering capabilities.

## Technical Details

### Built With

- **[Textual](https://textual.textualize.io/)** 
- **Python 3.12+**
- **asyncio**
- **Cross-platform** 

### Development Setup

```bash
# Clone the repository
git clone https://github.com/sleepiecappy/riverflow-log-viewer.git
cd riverflow

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv sync


# Run the demo
python log_viewer_ui.py python demo_enhanced_ui.py
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

##  Acknowledgments

- [Textual](https://textual.textualize.io/) for the amazing TUI framework
- Vi/Vim for inspiration on modal editing interfaces
- The Python community for excellent tooling and libraries

---