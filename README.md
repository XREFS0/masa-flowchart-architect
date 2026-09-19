# MASA FlowChart Architect

Visual node-based diagramming tool for designing process workflows and system architectures

## Technical Architecture

The application is architected with modular separation of concerns adhering to modern clean code standards:

- **Component Layering**: Isolated view layouts, state managers, and service controllers.
- **Defensive Engineering**: Robust input sanitization and exception management.
- **Modern Design Standards**: High-contrast dark-mode interface styled for optimal usability and visual polish.

## Preview

![Application Interface](screenshots/app_interface.png)

## Features

- Interactive canvas supporting Decision, Process, Input/Output, and Start/End nodes.
- Dynamic bezier and orthogonal connector routing with arrowheads.
- Node properties inspector (text, color palettes, border radius).
- Vector SVG and raster PNG diagram export engine.

## Prerequisites

- Python 3.10 or higher
- Required packages:

```bash
pip install customtkinter pillow requests
```

## Execution

Launch the application via Python:

```bash
python "Flow Chart Generator App Using Tkinter in Python/main.py"
```

## Project Structure

```
.
├── Flow Chart Generator App Using Tkinter in Python
├── screenshots/
│   └── app_interface.png
├── .gitignore
├── LICENSE             # MIT License
└── README.md           # Developer documentation
```

## License

This project is licensed under the terms of the MIT License. Refer to the `LICENSE` file for details.
