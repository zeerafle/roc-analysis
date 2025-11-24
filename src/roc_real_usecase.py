import marimo

__generated_with = "0.17.8"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import plotly.graph_objects as go
    import math
    import random
    import statistics
    return go, mo, random


@app.cell
def _(mo):
    mo.md("""
    # 🩺 ROC Analysis in the Real World: Medical Diagnosis

    **Receiver Operating Characteristics (ROC)** graphs are not just abstract lines; they are critical tools in fields like medicine, machine learning, and signal detection.

    ### The Scenario
    Imagine we are developing a test for a rare disease.
    - **Healthy Patients** (Negative Class): Typically have lower levels of a certain blood marker.
    - **Sick Patients** (Positive Class): Typically have higher levels of that marker.

    However, biology is messy. There is **overlap**. Some healthy people have high levels, and some sick people have low levels.

    **Your Goal**: Choose the "Cut-off" (Threshold) that balances catching the disease (Sensitivity) vs. not scaring healthy people (Specificity).
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## 1. Simulate the Population
    Adjust the parameters to see how the "separability" of the classes affects the ROC curve.
    """)
    return


@app.cell
def _(mo):
    # Controls for the simulation
    separation = mo.ui.slider(0.0, 5.0, step=0.1, value=2.0, label="Disease Signal Strength (Separation)")
    noise = mo.ui.slider(0.5, 2.0, step=0.1, value=1.0, label="Population Variance (Noise)")

    # The decision threshold
    threshold_slider = mo.ui.slider(
        start=-5.0, stop=10.0, step=0.1, value=1.0, label="Diagnostic Cut-off (Threshold)"
    )

    mo.vstack([
        mo.md("### ⚙️ Simulation Parameters"),
        separation,
        noise,
        mo.md("### ✂️ Decision Rule"),
        threshold_slider
    ])
    return noise, separation, threshold_slider


@app.cell
def _(noise, random, separation, threshold_slider):
    # Generate Synthetic Data
    # Healthy (Negative): Mean = 0
    # Disease (Positive): Mean = separation

    random.seed(42) # Reproducibility
    n_samples = 500

    # Generate scores
    healthy_scores = [random.gauss(0, noise.value) for _ in range(n_samples)]
    disease_scores = [random.gauss(separation.value, noise.value) for _ in range(n_samples)]

    all_scores = healthy_scores + disease_scores
    true_labels = [0] * n_samples + [1] * n_samples

    # Calculate Metrics based on Threshold
    t_val = threshold_slider.value

    # Confusion Matrix Counts
    # TP: Disease people correctly identified (score >= threshold)
    tp = sum(1 for s in disease_scores if s >= t_val)
    # FN: Disease people missed (score < threshold)
    fn = sum(1 for s in disease_scores if s < t_val)
    # FP: Healthy people incorrectly identified as sick (score >= threshold)
    fp = sum(1 for s in healthy_scores if s >= t_val)
    # TN: Healthy people correctly identified as healthy (score < threshold)
    tn = sum(1 for s in healthy_scores if s < t_val)

    # Rates
    tpr = tp / (tp + fn) if (tp + fn) > 0 else 0 # Sensitivity
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0 # 1 - Specificity

    # Generate ROC Curve Data (for the line)
    # We sweep thresholds from min to max score
    roc_x = []
    roc_y = []
    sorted_scores = sorted(all_scores)
    # Optimization: just take 100 points to smooth it out
    min_s, max_s = min(all_scores), max(all_scores)
    step = (max_s - min_s) / 100

    for thr in [min_s + i * step for i in range(101)]:
        # Calculate TPR/FPR for this specific threshold 'thr'
        # Note: This is a bit slow for large N, but fine for 1000 points
        curr_tp = sum(1 for s in disease_scores if s >= thr)
        curr_fp = sum(1 for s in healthy_scores if s >= thr)
        curr_tpr = curr_tp / n_samples
        curr_fpr = curr_fp / n_samples
        roc_x.append(curr_fpr)
        roc_y.append(curr_tpr)
    return (
        disease_scores,
        fn,
        fp,
        fpr,
        healthy_scores,
        roc_x,
        roc_y,
        t_val,
        tn,
        tp,
        tpr,
    )


@app.cell
def _(disease_scores, fpr, go, healthy_scores, mo, roc_x, roc_y, t_val, tpr):
    # --- Plot 1: Distributions ---
    fig_dist = go.Figure()

    # Healthy Distribution
    fig_dist.add_trace(go.Histogram(
        x=healthy_scores,
        name='Healthy (Neg)',
        marker_color='blue',
        opacity=0.6,
        nbinsx=50,
        histnorm='probability density'
    ))

    # Disease Distribution
    fig_dist.add_trace(go.Histogram(
        x=disease_scores,
        name='Disease (Pos)',
        marker_color='red',
        opacity=0.6,
        nbinsx=50,
        histnorm='probability density'
    ))

    # Threshold Line
    fig_dist.add_vline(
        x=t_val,
        line_width=3,
        line_dash="dash",
        line_color="black",
        annotation_text="Threshold",
        annotation_position="top right"
    )

    fig_dist.update_layout(
        title="<b>1. Population Distributions</b><br>Where do we draw the line?",
        xaxis_title="Diagnostic Score",
        yaxis_title="Density",
        barmode='overlay',
        legend=dict(x=0.01, y=0.99),
        margin=dict(l=40, r=40, t=60, b=40),
        height=400
    )

    # --- Plot 2: ROC Curve ---
    fig_roc = go.Figure()

    # The Curve
    fig_roc.add_trace(go.Scatter(
        x=roc_x,
        y=roc_y,
        mode='lines',
        name='ROC Curve',
        line=dict(color='purple', width=3)
    ))

    # The Current Point
    fig_roc.add_trace(go.Scatter(
        x=[fpr],
        y=[tpr],
        mode='markers',
        name='Current Threshold',
        marker=dict(size=15, color='black', symbol='x')
    ))

    # Random Guess Line
    fig_roc.add_trace(go.Scatter(
        x=[0, 1],
        y=[0, 1],
        mode='lines',
        name='Random Guess',
        line=dict(dash='dash', color='gray')
    ))

    fig_roc.update_layout(
        title=f"<b>2. ROC Curve</b><br>TPR vs FPR trade-off",
        xaxis_title="False Positive Rate (1 - Specificity)",
        yaxis_title="True Positive Rate (Sensitivity)",
        xaxis=dict(range=[0, 1]),
        yaxis=dict(range=[0, 1]),
        width=500,
        height=500,
        margin=dict(l=40, r=40, t=60, b=40)
    )

    # Display side by side
    mo.hstack([mo.ui.plotly(fig_dist), mo.ui.plotly(fig_roc)], justify="center")
    return


@app.cell
def _(fn, fp, mo, tn, tp):
    # Calculate Metrics
    total_pos = tp + fn
    total_neg = tn + fp

    sensitivity = tp / total_pos if total_pos > 0 else 0
    specificity = tn / total_neg if total_neg > 0 else 0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    accuracy = (tp + tn) / (total_pos + total_neg) if (total_pos + total_neg) > 0 else 0

    mo.md(
        f"""
        ### 📊 Performance Metrics

        | Metric | Value | Formula | Meaning |
        | :--- | :--- | :--- | :--- |
        | **Sensitivity** (TPR) | **{sensitivity:.2f}** | $TP / (TP + FN)$ | How many sick people did we find? |
        | **Specificity** (TNR) | **{specificity:.2f}** | $TN / (TN + FP)$ | How many healthy people did we correctly clear? |
        | **Precision** | **{precision:.2f}** | $TP / (TP + FP)$ | If we say they are sick, how likely is it true? |
        | **Accuracy** | **{accuracy:.2f}** | $(TP + TN) / Total$ | Overall correctness (can be misleading!) |

        ---

        ### 🧮 Confusion Matrix

        | | Predicted Healthy (Neg) | Predicted Sick (Pos) |
        | :--- | :---: | :---: |
        | **Actual Healthy** | **TN = {tn}** (Correct) | **FP = {fp}** (False Alarm) |
        | **Actual Sick** | **FN = {fn}** (Missed) | **TP = {tp}** (Correct) |
        """
    )
    return


@app.cell
def _(mo):
    mo.md("""
    ## 3. Area Under the Curve (AUC)

    The **AUC** (Area Under the ROC Curve) is a single number that summarizes the classifier's ability to distinguish between classes.

    *   **AUC = 0.5**: Random guessing (the diagonal line).
    *   **AUC = 1.0**: Perfect classification.
    *   **AUC = 0.8**: Good classification.

    **Interpretation**: The AUC is the probability that the classifier will rank a randomly chosen positive instance higher than a randomly chosen negative instance.
    """)
    return


@app.cell
def _(mo, roc_x, roc_y):
    # Calculate AUC using Trapezoidal Rule
    auc = 0.0
    # We need to sort by FPR (x-axis) to integrate correctly
    # My roc_x is sorted descending (from 1 to 0) because I swept threshold min->max
    # Let's reverse them to integrate 0->1

    # Zip and sort by FPR
    points = sorted(zip(roc_x, roc_y), key=lambda p: p[0])
    sorted_x = [p[0] for p in points]
    sorted_y = [p[1] for p in points]

    for i in range(1, len(sorted_x)):
        # Trapezoid area: (x_i - x_{i-1}) * (y_i + y_{i-1}) / 2
        dx = sorted_x[i] - sorted_x[i-1]
        avg_y = (sorted_y[i] + sorted_y[i-1]) / 2
        auc += dx * avg_y

    mo.md(
        f"""
        ### 🏆 Current AUC: **{auc:.3f}**

        Try changing the **Separation** slider at the top.
        - Increase separation -> AUC approaches 1.0
        - Decrease separation -> AUC approaches 0.5
        """
    )
    return


@app.cell
def _(mo):
    mo.md("""
    ## 4. Deep Dive: Key Concepts from "An Introduction to ROC Analysis"

    ### 1. The Trade-off
    ROC analysis is fundamentally about the trade-off between **Sensitivity** (catching the disease) and **Specificity** (avoiding false alarms). You cannot maximize both simultaneously unless the distributions are perfectly separated.

    ### 2. Class Skew Independence
    One of the biggest advantages of ROC curves is that they are **insensitive to changes in class distribution**.
    - If the proportion of positive to negative instances changes (e.g., the disease becomes more common), the ROC curve **does not change**.
    - This is unlike **Precision-Recall (PR)** curves, which *do* change with class skew.

    ### 3. The Convex Hull
    The **ROC Convex Hull (ROCCH)** is the "upper boundary" of all available classifiers.
    - Any classifier **on** the hull is potentially optimal.
    - Any classifier **below** the hull is sub-optimal (you can do better by combining other classifiers).

    ### 4. Choosing the Optimal Point
    Where should you be on the curve? It depends on **Costs**:
    - If missing a disease is fatal (High Cost of FN), you pick a point high up on the Y-axis (High Sensitivity), accepting more False Positives.
    - If the treatment is dangerous or expensive (High Cost of FP), you pick a point further left (High Specificity).
    """)
    return


if __name__ == "__main__":
    app.run()
