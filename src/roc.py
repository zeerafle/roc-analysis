import marimo

__generated_with = "0.17.8"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _(mo):
    import plotly.graph_objects as go  # only import once

    tp_input = mo.ui.number(value=50, label="TP", step=1)
    tn_input = mo.ui.number(value=40, label="TN", step=1)
    fp_input = mo.ui.number(value=5,  label="FP", step=1)
    fn_input = mo.ui.number(value=8,  label="FN", step=1)

    mo.hstack([tp_input, tn_input, fp_input, fn_input])
    return fn_input, fp_input, go, tn_input, tp_input


@app.cell
def _(fn_input, fp_input, go, tn_input, tp_input):
    z = [
        [tn_input.value, fp_input.value],  # Actual Negative (row 0)
        [fn_input.value, tp_input.value],  # Actual Positive (row 1)
    ]

    x_labels = ["Predicted Negative", "Predicted Positive"]
    y_labels = ["Actual Negative", "Actual Positive"]

    fig = go.Figure(
        data=go.Heatmap(
            z=z,
            x=x_labels,
            y=y_labels,
            colorscale="Blues",
            text=z,                 # show counts
            texttemplate="%{text}",
            textfont=dict(size=18),
            hovertemplate=(
                "Actual: %{y}<br>"
                "Predicted: %{x}<br>"
                "Count: %{z}<extra></extra>"
            ),
            reversescale=False,
        )
    )

    fig.update_layout(
        title="Interactive Confusion Matrix",
        xaxis_title="Predicted label",
        yaxis_title="Actual label",
        font=dict(size=16),
    )

    fig


    fig  # last expression: displayed as an interactive Plotly chart
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
