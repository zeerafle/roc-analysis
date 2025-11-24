import marimo

__generated_with = "0.17.8"
app = marimo.App(width="medium", layout_file="layouts/roc.slides.json")


@app.cell
def _():
    import marimo as mo
    import plotly.graph_objects as go
    import math
    import datetime
    return datetime, go, math, mo


@app.cell
def _(datetime, mo):
    mo.md(f"""
    # Introduction to ROC Analysis

    > Vauwez Sam El Fareez | 20249258020@cumhuriyet.edu.tr


    ---

    {datetime.datetime.now().strftime("%d.%m.%Y")}
    """)
    return


@app.cell
def _(fig_empirical_roc, mo):
    mo.vstack(
        [
            mo.md("# Receiver Operating Characteristics (ROC)"),
            mo.hstack(
                [
                    mo.md("""
    * **Visualization and Organization:** ROC graphs are a powerful **two-dimensional graphical technique** used for **visualizing, organizing, and selecting classifiers** based on their performance, especially in domains like medical decision making and machine learning.
    * **Trade-off Representation:** The graphs depict the **relative trade-off** between the **benefits** of a classifier—measured by the **True Positive Rate (tp rate)** on the Y-axis—and its **costs**—measured by the **False Positive Rate (fp rate)** on the X-axis. 
    * **Historical Context and Utility:** Originating in **signal detection theory**, ROC analysis has gained traction in machine learning because it offers a more robust performance metric than simple classification accuracy, particularly for problems involving **skewed class distributions** and **unequal classification error costs**.
                    """),
                    mo.ui.plotly(fig_empirical_roc),
                ]
            ),
        ],
        gap=3,
    )
    return


@app.cell
def _(mo):
    mo.md(f"""
    ## 1. Simulating a Classifier

    - Let's start with a concrete example: a classifier that produces scores for 20 examples.
    - The **true labels** (1=Positive, 0=Negative) are known, and the classifier assigns a **confidence score** to each.
    - Adjust the **decision threshold** to see how it affects classification performance.
    """)
    return


@app.cell
def _(mo):
    # Threshold Slider with on_change callback
    decision_threshold = mo.ui.slider(
        start=0.0,
        stop=1.0,
        step=0.05,
        label="Decision Threshold",
    )

    mo.md(f"""

    ### Decision Threshold

    - Scores ≥ threshold → Predicted **Positive**
    - Scores < threshold → Predicted **Negative**

    {decision_threshold}
    """)
    return (decision_threshold,)


@app.cell
def _(decision_threshold, go):
    # Discrete Dataset Simulation
    # 1 = Positive, 0 = Negative
    true_labels = [1, 1, 0, 1, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0]
    # Classifier scores (confidence)
    classifier_scores = [
        0.95,
        0.91,
        0.85,
        0.81,
        0.78,
        0.75,
        0.72,
        0.68,
        0.65,
        0.61,
        0.58,
        0.55,
        0.52,
        0.49,
        0.45,
        0.42,
        0.38,
        0.35,
        0.31,
        0.10,
    ]

    # Use the state value
    threshold_val = decision_threshold.value
    predictions = [
        1 if score >= threshold_val else 0 for score in classifier_scores
    ]

    # Calculate confusion matrix from predictions
    tp_sim = sum(
        1
        for i in range(len(true_labels))
        if true_labels[i] == 1 and predictions[i] == 1
    )
    fn_sim = sum(
        1
        for i in range(len(true_labels))
        if true_labels[i] == 1 and predictions[i] == 0
    )
    fp_sim = sum(
        1
        for i in range(len(true_labels))
        if true_labels[i] == 0 and predictions[i] == 1
    )
    tn_sim = sum(
        1
        for i in range(len(true_labels))
        if true_labels[i] == 0 and predictions[i] == 0
    )

    # Create visualization of the data
    colors = [
        "green" if t == p else "red" for t, p in zip(true_labels, predictions)
    ]
    symbols = ["circle" if t == 1 else "square" for t in true_labels]

    fig_data = go.Figure()
    fig_data.add_trace(
        go.Scatter(
            x=list(range(len(classifier_scores))),
            y=classifier_scores,
            mode="markers+text",
            marker=dict(
                size=12,
                color=colors,
                symbol=symbols,
                line=dict(width=2, color="black"),
            ),
            text=[f"{'P' if t == 1 else 'N'}" for t in true_labels],
            textposition="top center",
            hovertemplate="Example %{x}<br>Score: %{y:.2f}<br>True: %{text}<br>Pred: %{marker.color}<extra></extra>",
            showlegend=False,
        )
    )

    # Add threshold line
    fig_data.add_hline(
        y=threshold_val,
        line_dash="dash",
        line_color="blue",
        annotation_text=f"Threshold = {threshold_val:.2f}",
        annotation_position="right",
    )

    fig_data.update_layout(
        title="Classifier Scores & True Labels",
        xaxis_title="Example Index",
        yaxis_title="Classifier Score",
        height=350,
        template="plotly_white",
        annotations=[
            dict(
                x=0.02,
                y=0.98,
                xref="paper",
                yref="paper",
                text="🟢 = Correct | 🔴 = Wrong",
                showarrow=False,
                xanchor="left",
            ),
            dict(
                x=0.02,
                y=0.92,
                xref="paper",
                yref="paper",
                text="● = Positive | ■ = Negative",
                showarrow=False,
                xanchor="left",
            ),
        ],
    )
    print("plot")
    return (
        classifier_scores,
        fig_data,
        fn_sim,
        fp_sim,
        tn_sim,
        tp_sim,
        true_labels,
    )


@app.cell
def _(mo):
    mo.md("""
    ## 2. The Confusion Matrix

    A classification model maps examples to classes. For a binary classification problem (Positive/Negative), there are four possible outcomes represented in a **Confusion Matrix**:

    *   **True Positive (TP)**: Correctly predicted positive.
    *   **False Negative (FN)**: Incorrectly predicted negative (Miss).
    *   **False Positive (FP)**: Incorrectly predicted positive (False Alarm).
    *   **True Negative (TN)**: Correctly predicted negative.
    """)
    return


@app.cell
def _(fn_sim, fp_sim, go, tn_sim, tp_sim):
    # Use values from simulation
    tp = tp_sim
    fn = fn_sim
    fp = fp_sim
    tn = tn_sim

    # Visualize confusion matrix as heatmap
    conf_matrix = [
        [tn, fp],  # Actual Negative
        [fn, tp],  # Actual Positive
    ]

    fig_conf = go.Figure(
        data=go.Heatmap(
            z=conf_matrix,
            x=["Predicted Negative", "Predicted Positive"],
            y=["Actual Negative", "Actual Positive"],
            text=conf_matrix,
            texttemplate="%{text}",
            textfont={"size": 20},
            colorscale="Blues",
            showscale=False,
        )
    )

    fig_conf.update_layout(
        title="Confusion Matrix", height=400, width=500, template="plotly_white"
    )

    print("confusion matrix")
    return fig_conf, fn, fp, tn, tp


@app.cell
def _(fn, fp, tn, tp):
    # Calculate totals and metrics
    P = tp + fn
    N = fp + tn

    tpr = tp / P if P > 0 else 0.0
    fpr = fp / N if N > 0 else 0.0

    accuracy = (tp + tn) / (P + N) if (P + N) > 0 else 0.0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fp) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall)

    return N, P, accuracy, f1, fpr, precision, recall, tpr


@app.cell
def _(
    N,
    P,
    accuracy,
    f1,
    fig_conf,
    fig_data,
    fn,
    fp,
    fpr,
    mo,
    precision,
    recall,
    tn,
    tp,
    tpr,
):
    mo.vstack(
        [
            mo.hstack(
                [
                    mo.vstack(
                        [
                            mo.md(f"""
                            ### Confusion Matrix from Classifier
                        
                            The confusion matrix shows the four possible outcomes:
                            - **TP = {tp}** (True Positives)
                            - **FN = {fn}** (False Negatives / Misses)
                            - **FP = {fp}** (False Positives / False Alarms)
                            - **TN = {tn}** (True Negatives)
                            """),
                            mo.ui.plotly(fig_conf),
                        ],
                        gap=0,
                    ),
                    mo.vstack(
                        [
                            mo.md(f"""
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
                            *   **Recall**: {recall:.3f}
                            *   **F1**: {f1:.3f}
                            """),
                        ],
                        gap=0,
                    ),
                ]
            ),
            fig_data,
        ]
    )
    return


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
            mo.md("## 3. ROC Space"),
            mo.md(
                "ROC graphs are two-dimensional graphs in which TP rate is plotted on the Y axis and FP rate is plotted on the X axis. The red point shows our current classifier's performance."
            ),
            mo.ui.plotly(fig),
        ]
    )
    return


@app.cell
def _(mo):
    mo.md("""
    ## 4. Empirical ROC Curve

    Now let's generate the **complete ROC curve** by sweeping the threshold across all possible values.
    Each point on the curve represents a different threshold applied to our classifier scores.
    """)
    return


@app.cell
def _(classifier_scores, go, mo, true_labels):
    # Generate ROC curve by varying threshold
    # Sort by score descending
    data_sorted = sorted(
        zip(classifier_scores, true_labels), key=lambda x: x[0], reverse=True
    )
    sorted_scores_roc = [x[0] for x in data_sorted]
    sorted_labels_roc = [x[1] for x in data_sorted]

    # Calculate ROC points
    P_total_roc = sum(sorted_labels_roc)
    N_total_roc = len(sorted_labels_roc) - P_total_roc

    tp_count_roc = 0
    fp_count_roc = 0

    discrete_fpr = [0.0]
    discrete_tpr = [0.0]
    threshold_points = [1.0]  # Start with threshold above all scores

    for i, label in enumerate(sorted_labels_roc):
        if label == 1:
            tp_count_roc += 1
        else:
            fp_count_roc += 1

        discrete_fpr.append(fp_count_roc / N_total_roc)
        discrete_tpr.append(tp_count_roc / P_total_roc)
        threshold_points.append(sorted_scores_roc[i])

    # Plot empirical ROC
    fig_empirical_roc = go.Figure()
    fig_empirical_roc.add_trace(
        go.Scatter(
            x=discrete_fpr,
            y=discrete_tpr,
            mode="lines+markers",
            name="Empirical ROC",
            line_shape="hv",  # Step plot for discrete data
            marker=dict(size=6),
            hovertemplate="FPR: %{x:.2f}<br>TPR: %{y:.2f}<extra></extra>",
        )
    )

    fig_empirical_roc.add_shape(
        type="line",
        x0=0,
        y0=0,
        x1=1,
        y1=1,
        line=dict(color="Gray", dash="dash"),
    )

    fig_empirical_roc.update_layout(
        title="ROC Curve",
        xaxis_title="False Positive Rate (FPR)",
        yaxis_title="True Positive Rate (TPR)",
        xaxis=dict(range=[-0.05, 1.05]),
        yaxis=dict(range=[-0.05, 1.05]),
        width=600,
        height=500,
        template="plotly_white",
    )

    mo.vstack(
        [
            mo.md("""
        ### The 'Jagged' Curve

        This is what **real ROC curves** look like! The step-like pattern occurs because:
        - Each step **up** = correctly classifying a Positive example (TP increases)
        - Each step **right** = incorrectly classifying a Negative example (FP increases)

        Change the decision threshold above to see where your current operating point falls on this curve.
        """),
            mo.ui.plotly(fig_empirical_roc),
        ]
    )
    return (fig_empirical_roc,)


@app.cell
def _(mo):
    mo.md("""
    ## 5. Theoretical ROC: Continuous Distributions

    The jagged curve above comes from discrete data. In contrast, when we model classifiers using **continuous probability distributions**, we get smooth ROC curves.

    This is useful for theoretical analysis and understanding the relationship between class distributions and ROC curves.
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
    sigma = mo.ui.slider(start=5, stop=20, value=10, label="Std Dev (Both)")

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
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
        ),
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
    fig_roc.add_trace(go.Scatter(x=roc_x, y=roc_y, mode="lines", name="ROC Curve"))

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
    ## 6. Area Under the Curve (AUC)

    The **AUC** (Area Under the ROC Curve) reduces the ROC performance to a single scalar value representing expected performance.

    *   **AUC = 1.0**: Perfect classifier.
    *   **AUC = 0.5**: Random guessing (diagonal line).

    The AUC is equivalent to the probability that the classifier will rank a randomly chosen positive instance higher than a randomly chosen negative instance.
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## 7. Advanced Concepts: Convex Hull & Costs

    *   **Convex Hull**: The ROC Convex Hull (ROCCH) represents the potentially optimal classifiers. Classifiers below the convex hull are always sub-optimal.
    *   **Costs & Class Skew**: Different operating points on the ROC curve are optimal for different class distributions (ratio of Pos/Neg) and misclassification costs.

    Iso-performance lines can be drawn tangent to the ROC curve to find the optimal threshold for specific cost/skew conditions.
    """)
    return


if __name__ == "__main__":
    app.run()
