---
theme: seriph
background: https://cover.sli.dev
title: An Introduction to ROC Analysis
info: |
  ## An Introduction to ROC Analysis
  Based on the paper by Tom Fawcett (2006).
drawings:
  persist: false
transition: slide-left
mdc: true
layout: intro
---

# An Introduction to ROC Analysis

> From the paper by Tom Fawcett

Vauwez Sam El Fareez

20249258020@cumhuriyet.edu.tr

<div class="abs-br m-6 flex gap-2">
  <a href="https://github.com/zeerafle/roc-analysis" target="_blank" alt="GitHub"
    class="text-xl slidev-icon-btn opacity-50 !border-none !hover:text-white">
    <carbon-logo-github />
  </a>
</div>

---

# Introduction

**Receiver Operating Characteristics (ROC)** graphs are useful for organizing classifiers and visualizing their performance.

-   **Origin**: Signal detection theory (WWII radar analysis).
-   **Adoption**: Adopted by medical decision making, and later by the machine learning community.
-   **Why?**: Accuracy is often not enough!
    -   Class distributions can be skewed (e.g., 99% negative, 1% positive).
    -   Error costs can be unequal (False Positive vs False Negative).

ROC analysis helps us understand the trade-offs.

---

# The Confusion Matrix

For a binary classification problem (Positive vs Negative), there are four possible outcomes:

| | Predicted Positive | Predicted Negative |
|---|---|---|
| **Actual Positive** | **True Positive (TP)** <br> (Hit) | **False Negative (FN)** <br> (Miss) |
| **Actual Negative** | **False Positive (FP)** <br> (False Alarm) | **True Negative (TN)** <br> (Correct Rejection) |

From these, we derive key metrics:

-   **True Positive Rate (TPR)** (Recall, Sensitivity): $TPR = \frac{TP}{TP + FN}$
    -   *How many positives did we catch?*
-   **False Positive Rate (FPR)** (1 - Specificity): $FPR = \frac{FP}{FP + TN}$
    -   *How many negatives did we falsely call positive?*

---

# Interactive Confusion Matrix

<InteractiveConfusionMatrix />

---
layout: two-cols
---

# ROC Space

We plot **FPR** on the X-axis and **TPR** on the Y-axis.

-   **Top-Left (0, 1)**: Perfect Classification.
    -   0% False Positives, 100% True Positives.
-   **Diagonal Line (y = x)**: Random Guessing.
    -   A classifier that guesses randomly will fall on this line.
-   **Bottom-Right (1, 0)**: Worst possible.
    -   Always wrong.
-   **Below Diagonal**: Worse than random (invert the predictions to make it better!).

::right::

<div class="flex justify-center items-center h-full">
  <RocSpace />
</div>

---

# The ROC Curve

Most classifiers (like Neural Networks or Naive Bayes) output a **score** or **probability**, not just a class label.

-   We need to choose a **threshold** to convert the score into a label (Positive/Negative).
-   **High Threshold**: Conservative. Few False Positives, but low True Positive Rate. (Bottom-left)
-   **Low Threshold**: Liberal. High True Positive Rate, but many False Positives. (Top-right)

By varying the threshold from $-\infty$ to $+\infty$, we trace out the **ROC Curve**.

---
layout: center
---

# Interactive ROC Visualization

Adjust the **Separation** (how easy the problem is) and the **Threshold**.

<InteractiveROC />

---
layout: center
---

# Empirical ROC Curve (Spam Example)

Real-world ROC curves are often "jagged" (step functions) because they are built from a finite set of test examples.

<SpamRoc />

<!-- Explain how to draw the roc curve -->

---

# Area Under the Curve (AUC)

The **AUC** (Area Under the ROC Curve) reduces the curve to a single number.

-   **Range**: 0.5 (Random) to 1.0 (Perfect).
-   **Interpretation**: The probability that the classifier will rank a randomly chosen positive instance higher than a randomly chosen negative instance.
-   **Wilcoxon Statistic**: AUC is equivalent to the Wilcoxon-Mann-Whitney statistic.

$$ AUC = P(Score(x^+) > Score(x^-)) $$

It is a measure of **ranking quality**, independent of the threshold.

---

# AUC Calculation: The Trapezoid Method

We calculate AUC by summing the area of trapezoids formed as we walk down the ranked list of predictions.

<InteractiveAucCalculation />

---

# Interactive AUC Visualization

Move the sliders to change the classifier's operating point (TP and FP).
See how the **ROC Curve** bends and the **AUC** changes.

<InteractiveAuc />

---
layout: two-cols
gap: 8
---

# Convex Hull & Iso-Performance

- __ROC Convex Hull (ROCCH)__
  - The "best" system is the convex hull of all classifiers.
  - Classifiers **A** and **C** form the hull.
  - Classifiers **B** and **D** are suboptimal (below the hull).

- __Iso-Performance Lines__
  - Lines of equal **Expected Cost**.
  - Slope $m = \frac{P(N) \cdot C(FP)}{P(P) \cdot C(FN)}$.
  - Optimal point is tangent to the line with slope $m$.

::right::

<div class="flex justify-center items-center h-full">
  <InteractiveConvexHull />
</div>

---

# Precision-Recall vs ROC

**Rule of Thumb**: Use ROC when you want a stable metric across different class balances. Use PR when you care deeply about the "needle in the haystack" (rare positive class) and false positives are very expensive.

<InteractivePrVsRoc />

<!-- Sometimes people use **Precision-Recall (PR)** curves instead.

-   **Precision**: $\frac{TP}{TP + FP}$ (How many predicted positives are actually positive?)
-   **Recall**: Same as TPR.

**Difference**:
-   **ROC** is insensitive to class skew. If negatives increase by 10x, FPR stays the same (TN increases proportionally).
-   **PR** is sensitive to class skew. If negatives increase, False Positives might increase, lowering Precision. -->
---

# Multi-Class ROC: One-vs-All

To handle $N > 2$ classes, we use the **One-vs-All** approach.
We create $N$ separate ROC graphs. For each class $C_i$:

<InteractiveMultiClass />

<!--
-   **Positive**: Class $C_i$
-   **Negative**: All other classes ($\neg C_i$)
-->

---

# Multi-Class AUC

## The Weighted Average Method

This method calculates the total AUC by looking at the "One-vs-All" graphs described before.

$$AUC_{total} = \sum_{c_i \in C} AUC(c_i) \cdot p(c_i)$$

Calculation: Calculate the AUC for each of the separate class graphs (Cat vs. All, Dog vs. All, etc.). Then, you calculate a weighted average of these scores based on how common each class is (its "prevalence") in the data.

$$AUC_{total} = (AUC_{Cat} \times p_{Cat}) + (AUC_{Dog} \times p_{Dog}) + (AUC_{Bird} \times p_{Bird})$$

<hr></hr>

**$p_{Cat}$**: The **prevalence** (probability) of Cats in your dataset. This is calculated as:

$$p_{Cat} = \frac{\text{Total Number of Cats}}{\text{Total Number of Instances in Dataset}}$$

*(Repeat this logic for Dog and Bird).*

<!-- By multiplying by $p$, classes that appear more often in your data contribute more to the final score[cite: 842]. If 90% of your data are Dogs, the model's ability to recognize Dogs effectively becomes 90% of the final grade. -->

---

# Multi-Class AUC

## The Pairwise Method

This method tries to measure how distinct the classes are from each other, ignoring how many items are in each class.

Calculation: Instead of grouping classes together, this method looks at every possible pair of classes (e.g., Cat vs. Dog, Cat vs. Bird, Dog vs. Bird).

- It calculates the AUC for every pair.
- It averages these pairwise AUCs to get a final score (called M).

Pros/Cons: This measure is excellent if you want a score that does not change just because the number of items in a class changes (insensitive to class distribution). However, it is purely mathematical and difficult to visualize as a single graph surface.

---

# Conclusion

-   **ROC Analysis** provides a robust way to evaluate classifier performance, especially with imbalanced data or unequal costs.
-   **ROC Space** separates classifier performance (curve) from operating conditions (threshold).
-   **AUC** gives a single-number summary of ranking ability.
-   **Convex Hull** helps select the best set of classifiers.

**Takeaway**: Don't just look at accuracy! Look at the curve.


---
layout: end
---

# Thank You!
