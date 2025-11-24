import marimo

__generated_with = "0.17.8"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import plotly.graph_objects as go
    import math
    return go, math, mo


@app.cell
def _(mo):
    mo.md("""
    # Introduction to ROC Analysis

    Based on **"An Introduction to ROC Analysis"** by Tom Fawcett.

    This interactive notebook explores **Receiver Operating Characteristics (ROC)** graphs, a powerful tool for visualizing, organizing, and selecting classifiers based on their performance.
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## 1. The Confusion Matrix

    A classification model maps examples to classes. For a binary classification problem (Positive/Negative), there are four possible outcomes represented in a **Confusion Matrix**:

    *   **True Positive (TP)**: Correctly predicted positive.
    *   **False Negative (FN)**: Incorrectly predicted negative (Miss).
    *   **False Positive (FP)**: Incorrectly predicted positive (False Alarm).
    *   **True Negative (TN)**: Correctly predicted negative.
    """)
    return


@app.cell
def _(mo):
    # Interactive inputs for Confusion Matrix
    tp = mo.ui.number(value=50, label="TP (Hit)", step=1)
    fn = mo.ui.number(value=10, label="FN (Miss)", step=1)
    fp = mo.ui.number(value=10, label="FP (False Alarm)", step=1)
    tn = mo.ui.number(value=90, label="TN (Correct Rejection)", step=1)

    mo.md(
        f"""
        ### Interactive Confusion Matrix
        Adjust the values below to see how metrics change.

        {mo.hstack([tp, fn, fp, tn], justify="center")}
        """
    )
    return fn, fp, tn, tp


@app.cell
def _(fn, fp, mo, tn, tp):
    # Calculate totals and metrics
    P = tp.value + fn.value
    N = fp.value + tn.value

    tpr = tp.value / P if P > 0 else 0.0
    fpr = fp.value / N if N > 0 else 0.0

    accuracy = (tp.value + tn.value) / (P + N) if (P + N) > 0 else 0.0
    precision = (
        tp.value / (tp.value + fp.value) if (tp.value + fp.value) > 0 else 0.0
    )

    mo.md(
        f"""
        ### Calculated Metrics

        *   **Total Positives (P)**: {P}
        *   **Total Negatives (N)**: {N}

        #### Key Rates for ROC
        *   **True Positive Rate (Sensitivity, Recall)**:
            $$TPR = \\frac{{TP}}{{P}} = {tpr:.3f}$$
        *   **False Positive Rate (1 - Specificity)**:
            $$FPR = \\frac{{FP}}{{N}} = {fpr:.3f}$$

        #### Other Metrics
        *   **Accuracy**: {accuracy:.3f}
        *   **Precision**: {precision:.3f}
        """
    )
    return fpr, tpr


@app.cell
def _(fpr, go, mo, tpr):
    # ROC Space Plot
    fig = go.Figure()

    # The classifier point
    fig.add_trace(
        go.Scatter(
            x=[fpr],
            y=[tpr],
            mode="markers+text",
            text=["Classifier"],
            textposition="top center",
            marker=dict(size=15, color="red"),
            name="Current Classifier",
        )
    )

    # Random guess line
    fig.add_shape(
        type="line",
        x0=0,
        y0=0,
        x1=1,
        y1=1,
        line=dict(color="Gray", dash="dash"),
    )

    fig.update_layout(
        title="ROC Space",
        xaxis_title="False Positive Rate (FPR)",
        yaxis_title="True Positive Rate (TPR)",
        xaxis=dict(range=[-0.05, 1.05], constrain="domain"),
        yaxis=dict(range=[-0.05, 1.05], scaleanchor="x", scaleratio=1),
        width=500,
        height=500,
        template="plotly_white",
    )

    mo.vstack(
        [
            mo.md("## 2. ROC Space"),
            mo.md(
                "ROC graphs are two-dimensional graphs in which TP rate is plotted on the Y axis and FP rate is plotted on the X axis."
            ),
            mo.ui.plotly(fig),
        ]
    )
    return


@app.cell
def _(mo):
    mo.md("""
    ## 3. Scoring Classifiers & Thresholds

    Many classifiers (e.g., Naive Bayes, Neural Networks) output a **score** or **probability** rather than a discrete class label.
    A **threshold** is applied to this score to decide the class.

    *   Score $\gt$ Threshold $\rightarrow$ Positive
    *   Score $\le$ Threshold $\rightarrow$ Negative

    Changing the threshold changes the TP and FP rates, creating a curve in ROC space.
    """)
    return


@app.cell
def _(mo):
    # Threshold Slider
    threshold_slider = mo.ui.slider(
        start=0, stop=100, step=1, value=50, label="Threshold"
    )

    # Distribution parameters
    mu_neg = mo.ui.slider(
        start=20, stop=45, value=30, label="Mean (Negative Class)"
    )
    mu_pos = mo.ui.slider(
        start=55, stop=80, value=60, label="Mean (Positive Class)"
    )
    sigma = mo.ui.slider(start=5, stop=20, value=10, label="Std Dev (Both)"
    )

    mo.md(
        f"""
        ### Interactive Distributions
        Adjust the class distributions and the decision threshold to see how the ROC curve forms.

        {mo.vstack([threshold_slider, mu_neg, mu_pos, sigma])}
        """
    )
    return mu_neg, mu_pos, sigma, threshold_slider


@app.cell
def _(go, math, mo, mu_neg, mu_pos, sigma, threshold_slider):
    # Generate distributions
    x_vals = list(range(0, 101))

    def get_pdf(x, mu, s):
        return (1.0 / (s * math.sqrt(2 * math.pi))) * math.exp(
            -0.5 * ((x - mu) / s) ** 2
        )

    y_neg = [get_pdf(x, mu_neg.value, sigma.value) for x in x_vals]
    y_pos = [get_pdf(x, mu_pos.value, sigma.value) for x in x_vals]

    # Calculate areas (TPR and FPR) based on threshold
    t_val = threshold_slider.value

    # Normalize to sum to 1 for correct probability interpretation
    sum_neg = sum(y_neg)
    sum_pos = sum(y_pos)

    fpr_curve = sum(y_neg[t_val:]) / sum_neg if sum_neg > 0 else 0
    tpr_curve = sum(y_pos[t_val:]) / sum_pos if sum_pos > 0 else 0

    # Plot Distributions
    fig_dist = go.Figure()
    fig_dist.add_trace(
        go.Scatter(
            x=x_vals,
            y=y_neg,
            fill="tozeroy",
            name="Negative Class",
            line_color="blue",
        )
    )
    fig_dist.add_trace(
        go.Scatter(
            x=x_vals,
            y=y_pos,
            fill="tozeroy",
            name="Positive Class",
            line_color="red",
        )
    )

    # Threshold line
    fig_dist.add_vline(
        x=t_val,
        line_width=3,
        line_dash="dash",
        line_color="green",
        annotation_text="Threshold",
    )

    fig_dist.update_layout(
        title="Class Distributions & Threshold",
        xaxis_title="Score",
        yaxis_title="Probability Density",
        height=400,
        margin=dict(l=20, r=20, t=40, b=20),
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    # Plot ROC Curve (dynamically generated from these distributions)
    roc_x = []
    roc_y = []

    # Calculate full curve
    for t in range(0, 101):
        f = sum(y_neg[t:]) / sum_neg if sum_neg > 0 else 0
        t_rate = sum(y_pos[t:]) / sum_pos if sum_pos > 0 else 0
        roc_x.append(f)
        roc_y.append(t_rate)

    fig_roc = go.Figure()
    fig_roc.add_trace(
        go.Scatter(x=roc_x, y=roc_y, mode="lines", name="ROC Curve")
    )

    # Current point
    fig_roc.add_trace(
        go.Scatter(
            x=[fpr_curve],
            y=[tpr_curve],
            mode="markers",
            marker=dict(size=12, color="green"),
            name="Current Threshold",
        )
    )

    fig_roc.add_shape(
        type="line",
        x0=0,
        y0=0,
        x1=1,
        y1=1,
        line=dict(color="Gray", dash="dash"),
    )
    fig_roc.update_layout(
        title="Resulting ROC Curve",
        xaxis_title="FPR",
        yaxis_title="TPR",
        xaxis=dict(range=[0, 1]),
        yaxis=dict(range=[0, 1]),
        height=400,
        margin=dict(l=20, r=20, t=40, b=20),
        template="plotly_white",
    )

    mo.vstack(
        [
            mo.hstack([mo.ui.plotly(fig_dist), mo.ui.plotly(fig_roc)]),
            mo.md(
                f"**Current State**: Threshold = {t_val}, FPR = {fpr_curve:.2f}, TPR = {tpr_curve:.2f}"
            ),
        ]
    )
    return


@app.cell
def _(mo):
    mo.md("""
    ## 4. Empirical ROC Curves (Discrete Data)

    The smooth curve above represents theoretical distributions. In practice, we work with finite datasets, which produce **jagged, step-like** ROC curves.

    *   **Step Up**: When we correctly classify a Positive instance (TP increases).
    *   **Step Right**: When we incorrectly classify a Negative instance (FP increases).

    Below is a simulation of a discrete dataset with 20 examples.
    """)
    return


@app.cell
def _(go, mo):
    # Discrete Dataset Simulation
    # 1 = Positive, 0 = Negative
    true_labels = [1, 1, 0, 1, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0]
    # Random-ish scores sorted roughly by label to make a decent curve
    scores = [
        0.95, 0.91, 0.85, 0.81, 0.78, 0.75, 0.72, 0.68, 0.65, 0.61,
        0.58, 0.55, 0.52, 0.49, 0.45, 0.42, 0.38, 0.35, 0.31, 0.10
    ]

    # Sort by score descending
    data = sorted(zip(scores, true_labels), key=lambda x: x[0], reverse=True)
    sorted_scores = [x[0] for x in data]
    sorted_labels = [x[1] for x in data]

    # Calculate ROC points
    P_total = sum(sorted_labels)
    N_total = len(sorted_labels) - P_total

    tp_count = 0
    fp_count = 0

    discrete_fpr = [0.0]
    discrete_tpr = [0.0]
    text_labels = ["Start"]

    for i, label in enumerate(sorted_labels):
        if label == 1:
            tp_count += 1
        else:
            fp_count += 1

        discrete_fpr.append(fp_count / N_total)
        discrete_tpr.append(tp_count / P_total)
        text_labels.append(f"Score: {sorted_scores[i]}")

    # Plot
    fig_empirical = go.Figure()
    fig_empirical.add_trace(
        go.Scatter(
            x=discrete_fpr,
            y=discrete_tpr,
            mode="lines+markers",
            name="Empirical ROC",
            line_shape="hv", # Step plot
            text=text_labels,
            hovertemplate="FPR: %{x:.2f}<br>TPR: %{y:.2f}<br>%{text}<extra></extra>"
        )
    )

    fig_empirical.add_shape(
        type="line", x0=0, y0=0, x1=1, y1=1,
        line=dict(color="Gray", dash="dash"),
    )

    fig_empirical.update_layout(
        title="Empirical ROC (Discrete Dataset)",
        xaxis_title="False Positive Rate",
        yaxis_title="True Positive Rate",
        xaxis=dict(range=[-0.05, 1.05]),
        yaxis=dict(range=[-0.05, 1.05]),
        width=600,
        height=500,
        template="plotly_white"
    )

    mo.vstack([
        mo.md("### The 'Jagged' Curve"),
        mo.ui.plotly(fig_empirical)
    ])
    return


@app.cell
def _(mo):
    mo.md("""
    ## 5. Area Under the Curve (AUC)

    The **AUC** (Area Under the ROC Curve) reduces the ROC performance to a single scalar value representing expected performance.

    *   **AUC = 1.0**: Perfect classifier.
    *   **AUC = 0.5**: Random guessing (diagonal line).

    The AUC is equivalent to the probability that the classifier will rank a randomly chosen positive instance higher than a randomly chosen negative instance.
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## 6. Advanced Concepts: Convex Hull & Costs

    *   **Convex Hull**: The ROC Convex Hull (ROCCH) represents the potentially optimal classifiers. Classifiers below the convex hull are always sub-optimal.
    *   **Costs & Class Skew**: Different operating points on the ROC curve are optimal for different class distributions (ratio of Pos/Neg) and misclassification costs.

    Iso-performance lines can be drawn tangent to the ROC curve to find the optimal threshold for specific cost/skew conditions.
    """)
    return


if __name__ == "__main__":
    app.run()
