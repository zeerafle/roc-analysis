# ROC Analysis Project Instructions

This project is a reactive Python notebook application built with **Marimo**.


## Project Structure
- **Framework**: [Marimo](https://marimo.io/) (Reactive Python Notebooks).
- **Entry Point**: `src/roc.py`.
- **Dependencies**: Managed in `pyproject.toml` (includes `marimo`, `plotly`, `polars`, `openai`).

## Marimo Development Conventions

### Cell Structure
- Define code blocks as functions decorated with `@app.cell`.
- Use `_` as the function name for cells.
- **Inputs**: Function arguments represent variables returned by other cells (dependency injection).
- **Outputs**: Return a tuple of variables defined in the cell to make them available to other cells.
- **Display**: The last expression in the cell function is automatically displayed in the notebook output.

### Imports
- `import marimo` is at the module level.
- `import marimo as mo` is typically done in a dedicated setup cell.
- Library imports (e.g., `import plotly.graph_objects as go`) should be placed inside the cells where they are first used or in a dedicated imports cell.

### Reactivity & UI
- Use `mo.ui` (e.g., `mo.ui.number`, `mo.ui.slider`) for interactive inputs.
- Reference UI values using `.value` (e.g., `tp_input.value`).
- Data flow is reactive: changing a UI element automatically re-runs dependent cells.

### Visualization
- Use **Plotly** (`plotly.graph_objects` or `plotly.express`) for charts.
- Return the figure object at the end of the cell to render it.

## Example Pattern
```python
@app.cell
def _(mo):
    # UI Component definition
    slider = mo.ui.slider(0, 100, label="Threshold")
    return slider,

@app.cell
def _(slider):
    # Dependent cell using the slider value
    result = slider.value * 2
    result # Displayed output
    return result,
```

---

Always use context7 when I need code generation, setup or configuration steps, or
library/API documentation. This means you should automatically use the Context7 MCP
tools to resolve library id and get library docs without me having to explicitly ask.
