<script setup>
import * as Plot from "@observablehq/plot";
import { ref, computed, onMounted, useTemplateRef, watchEffect } from "vue";

const plotDiv = useTemplateRef('plotDiv');

// Fixed Ground Truth
const totalPositives = 100;
const totalNegatives = 100;

// Sliders control these (Current Operating Point)
const tp = ref(70);
const fp = ref(30);

// Derived values
const fn = computed(() => totalPositives - tp.value);
const tn = computed(() => totalNegatives - fp.value);

const tpr = computed(() => tp.value / totalPositives);
const fpr = computed(() => fp.value / totalNegatives);

// Generate a hypothetical ROC curve that passes through the current point (FPR, TPR)
// We'll use a simple power law curve y = x^a to approximate a ROC curve
// TPR = FPR^a  => a = log(TPR) / log(FPR)
// This ensures the curve goes through (0,0), (1,1) and our point.
// Note: This is a simplification for visualization purposes.
const rocCurveData = computed(() => {
    const currentFpr = fpr.value;
    const currentTpr = tpr.value;

    // Avoid division by zero or log(0) issues
    if (currentFpr <= 0.01 || currentTpr <= 0.01 || currentFpr >= 0.99 || currentTpr >= 0.99) {
        // Fallback to straight lines if point is extreme
        return [
            { fpr: 0, tpr: 0 },
            { fpr: currentFpr, tpr: currentTpr },
            { fpr: 1, tpr: 1 }
        ];
    }

    // Calculate exponent 'a' for y = x^a (or x = y^(1/a) depending on shape)
    // Actually, a better simple model for ROC is often based on Gaussian distributions,
    // but a power law y = x^k is easiest to force through a point.
    // Let's try to fit a curve: TPR = FPR^k
    // k = log(TPR) / log(FPR)

    let k = Math.log(currentTpr) / Math.log(currentFpr);

    // If the point is below diagonal (TPR < FPR), k will be > 1.
    // If above diagonal, k < 1.

    const points = [];
    for (let x = 0; x <= 1.01; x += 0.02) {
        // Ensure x is within [0,1]
        const valX = Math.min(x, 1);
        const valY = Math.pow(valX, k);
        points.push({ fpr: valX, tpr: valY });
    }
    return points;
});

// Calculate AUC for y = x^k
// Integral of x^k dx from 0 to 1 is [x^(k+1)/(k+1)] from 0 to 1 = 1/(k+1)
const auc = computed(() => {
    const currentFpr = fpr.value;
    const currentTpr = tpr.value;

    if (currentFpr <= 0.001 || currentTpr <= 0.001) return 0.5; // Fallback
    if (currentFpr >= 0.999 || currentTpr >= 0.999) return 0.5;

    const k = Math.log(currentTpr) / Math.log(currentFpr);
    return 1 / (k + 1);
});


onMounted(() => {
  watchEffect(() => {
    if (!plotDiv.value) return;
    plotDiv.value.innerHTML = '';

    const plot = Plot.plot({
      width: 350,
      height: 350,
      grid: true,
      x: { domain: [0, 1], label: "False Positive Rate (FPR)" },
      y: { domain: [0, 1], label: "True Positive Rate (TPR)" },
      marks: [
        // The Curve
        Plot.line(rocCurveData.value, { x: "fpr", y: "tpr", strokeWidth: 2, stroke: "steelblue" }),
        Plot.areaY(rocCurveData.value, { x: "fpr", y: "tpr", fill: "steelblue", fillOpacity: 0.1 }),

        // The Current Point
        Plot.dot([{fpr: fpr.value, tpr: tpr.value}], { x: "fpr", y: "tpr", fill: "red", r: 6 }),
        Plot.text([{fpr: fpr.value, tpr: tpr.value}], { x: "fpr", y: "tpr", text: d => `(${d.fpr.toFixed(2)}, ${d.tpr.toFixed(2)})`, dy: -10, fill: "red", fontWeight: "bold" }),

        // AUC Legend
        Plot.text([{x: 0.7, y: 0.1}], { x: "x", y: "y", text: d => `AUC: ${auc.value.toFixed(3)}`, fill: "blue", fontWeight: "bold", fontSize: 16 }),

        // Crosshairs
        Plot.ruleX([fpr.value], { stroke: "red", strokeOpacity: 0.3 }),
        Plot.ruleY([tpr.value], { stroke: "red", strokeOpacity: 0.3 }),

        // Diagonal
        Plot.line([{x:0, y:0}, {x:1, y:1}], {x: "x", y: "y", stroke: "gray", strokeDasharray: "4,4"})
      ]
    });

    plotDiv.value.append(plot);
  });
});

const formatPercent = (val) => (val * 100).toFixed(1) + '%';
</script>

<template>
  <div class="flex gap-8 items-start bg-white p-4 rounded shadow-lg">
    <!-- Controls -->
    <div class="w-1/2 flex flex-col gap-6">
        <div>
            <h3 class="font-bold text-lg mb-2">Confusion Matrix Sliders</h3>
            <p class="text-xs text-slate-500 mb-4">Adjust TP and FP to move the point in ROC space.</p>

            <!-- TP Slider -->
            <div class="bg-green-50 p-4 rounded border border-green-200 mb-4">
                <div class="flex justify-between mb-2">
                    <label class="font-bold text-green-800 text-sm">True Positives (TP)</label>
                    <span class="font-mono font-bold text-green-800">{{ tp }} / {{ totalPositives }}</span>
                </div>
                <input type="range" v-model.number="tp" min="1" :max="totalPositives - 1" class="w-full accent-green-600" />
                <div class="text-xs text-green-600 mt-1 text-right">TPR = {{ tpr.toFixed(2) }}</div>
            </div>

            <!-- FP Slider -->
            <div class="bg-red-50 p-4 rounded border border-red-200">
                <div class="flex justify-between mb-2">
                    <label class="font-bold text-red-800 text-sm">False Positives (FP)</label>
                    <span class="font-mono font-bold text-red-800">{{ fp }} / {{ totalNegatives }}</span>
                </div>
                <input type="range" v-model.number="fp" min="1" :max="totalNegatives - 1" class="w-full accent-red-600" />
                <div class="text-xs text-red-600 mt-1 text-right">FPR = {{ fpr.toFixed(2) }}</div>
            </div>
        </div>
    </div>

    <!-- Plot -->
    <div class="w-1/2 flex justify-center">
        <div ref="plotDiv"></div>
    </div>
  </div>
</template>
