<script setup>
import * as Plot from "@observablehq/plot";
import { ref, computed, onMounted, useTemplateRef, watchEffect } from "vue";

const plotDiv = useTemplateRef('plotDiv');
const thresholdIndex = ref(0);

// Data: 20 emails with scores
const data = [
  { id: 1, score: 0.99, isSpam: true },
  { id: 2, score: 0.95, isSpam: true },
  { id: 3, score: 0.93, isSpam: true },
  { id: 4, score: 0.90, isSpam: false }, // FP
  { id: 5, score: 0.85, isSpam: true },
  { id: 6, score: 0.80, isSpam: true },
  { id: 7, score: 0.75, isSpam: false }, // FP
  { id: 8, score: 0.70, isSpam: true },
  { id: 9, score: 0.65, isSpam: true },
  { id: 10, score: 0.60, isSpam: false }, // FP
  { id: 11, score: 0.55, isSpam: true },
  { id: 12, score: 0.50, isSpam: false },
  { id: 13, score: 0.45, isSpam: false },
  { id: 14, score: 0.40, isSpam: true }, // FN (if threshold > 0.4)
  { id: 15, score: 0.35, isSpam: false },
  { id: 16, score: 0.30, isSpam: false },
  { id: 17, score: 0.25, isSpam: false },
  { id: 18, score: 0.20, isSpam: false },
  { id: 19, score: 0.15, isSpam: false },
  { id: 20, score: 0.10, isSpam: false },
];

const totalPos = data.filter(d => d.isSpam).length;
const totalNeg = data.filter(d => !d.isSpam).length;

// Calculate ROC points
const rocPoints = computed(() => {
  let tp = 0;
  let fp = 0;
  // Start at 0,0
  const points = [{ fpr: 0, tpr: 0, score: 1.0, index: 0 }];

  data.forEach((d, i) => {
    if (d.isSpam) tp++;
    else fp++;

    points.push({
      fpr: fp / totalNeg,
      tpr: tp / totalPos,
      score: d.score,
      index: i + 1
    });
  });
  return points;
});

const currentPoint = computed(() => rocPoints.value[thresholdIndex.value]);

const currentMetrics = computed(() => {
  const idx = thresholdIndex.value;
  let tp = 0;
  let fp = 0;
  let fn = 0;
  let tn = 0;

  data.forEach((d, i) => {
    const predictedSpam = i < idx;
    if (predictedSpam && d.isSpam) tp++;
    else if (predictedSpam && !d.isSpam) fp++;
    else if (!predictedSpam && d.isSpam) fn++;
    else if (!predictedSpam && !d.isSpam) tn++;
  });

  const accuracy = (tp + tn) / data.length;
  const precision = (tp + fp) === 0 ? 0 : tp / (tp + fp);
  const recall = (tp + fn) === 0 ? 0 : tp / (tp + fn);
  const f1 = (precision + recall) === 0 ? 0 : 2 * (precision * recall) / (precision + recall);

  return { accuracy, precision, recall, f1 };
});

const formatPercent = (val) => (val * 100).toFixed(1) + '%';

onMounted(() => {
  watchEffect(() => {
    if (!plotDiv.value) return;
    plotDiv.value.innerHTML = '';

    const plot = Plot.plot({
      width: 400,
      height: 300,
      grid: true,
      x: { domain: [0, 1], label: "False Positive Rate (FPR)" },
      y: { domain: [0, 1], label: "True Positive Rate (TPR)" },
      marks: [
        Plot.line(rocPoints.value, { x: "fpr", y: "tpr", strokeWidth: 2 }),
        Plot.dot(rocPoints.value, { x: "fpr", y: "tpr", fill: "black", r: 2 }),
        Plot.dot([currentPoint.value], { x: "fpr", y: "tpr", fill: "red", r: 6 }),
        Plot.ruleX([currentPoint.value.fpr], { stroke: "red", strokeOpacity: 0.3 }),
        Plot.ruleY([currentPoint.value.tpr], { stroke: "red", strokeOpacity: 0.3 }),
        Plot.text([currentPoint.value], { x: "fpr", y: "tpr", text: d => `Threshold ≥ ${d.score.toFixed(2)}`, dy: -10, fill: "red", textAnchor: "start", fontWeight: "bold" }),
        Plot.line([{x:0, y:0}, {x:1, y:1}], {x: "x", y: "y", stroke: "gray", strokeDasharray: "4,4"})
      ]
    });

    plotDiv.value.append(plot);
  });
});
</script>

<template>
  <div class="flex gap-4 items-start">
    <!-- Left Column: List of Emails + Slider -->
    <div class="w-1/2 flex flex-col gap-2">
      <div class="bg-white p-2 rounded shadow overflow-y-auto h-[250px] text-xs">
        <table class="w-full text-left border-collapse">
          <thead class="sticky top-0 bg-white shadow-sm">
            <tr class="border-b">
              <th class="p-1">ID</th>
              <th class="p-1">Score</th>
              <th class="p-1">Actual</th>
              <th class="p-1">Pred</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, idx) in data" :key="item.id"
                :class="{'bg-blue-100': idx < thresholdIndex, 'border-b-2 border-red-500': idx === thresholdIndex - 1}">
              <td class="p-1">#{{ item.id }}</td>
              <td class="p-1 font-mono">{{ item.score.toFixed(2) }}</td>
              <td class="p-1">
                <span :class="item.isSpam ? 'text-red-600 font-bold' : 'text-green-600'">
                  {{ item.isSpam ? 'Spam' : 'Ham' }}
                </span>
              </td>
              <td class="p-1">
                 <span v-if="idx < thresholdIndex" class="text-red-600 font-bold">Spam</span>
                 <span v-else class="text-green-600">Ham</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="w-full px-4 bg-slate-100 p-4 rounded">
        <label class="block text-sm font-bold mb-2 text-slate-700">Threshold Slider</label>
        <input type="range" min="0" :max="data.length" v-model.number="thresholdIndex" class="w-full accent-blue-600" />
        <div class="text-center text-sm mt-2 text-slate-600">
          Classifying top <strong>{{ thresholdIndex }}</strong> emails as Spam
        </div>
        <div class="flex justify-between text-xs mt-2 text-slate-500">
            <span>Conservative (High Threshold)</span>
            <span>Liberal (Low Threshold)</span>
        </div>
      </div>
    </div>

    <!-- Right Column: Plot and Metrics -->
    <div class="w-1/2 flex flex-col items-center">
      <div ref="plotDiv" class="bg-white p-2 rounded shadow"></div>

      <div class="w-full grid grid-cols-2 gap-2 mt-2 mb-2 text-xs">
          <div class="bg-slate-50 p-2 rounded border border-slate-200 flex justify-between">
              <span class="font-bold text-slate-600">Accuracy</span>
              <span class="font-mono">{{ formatPercent(currentMetrics.accuracy) }}</span>
          </div>
          <div class="bg-slate-50 p-2 rounded border border-slate-200 flex justify-between">
              <span class="font-bold text-purple-600">Precision</span>
              <span class="font-mono">{{ formatPercent(currentMetrics.precision) }}</span>
          </div>
          <div class="bg-slate-50 p-2 rounded border border-slate-200 flex justify-between">
              <span class="font-bold text-blue-600">Recall</span>
              <span class="font-mono">{{ formatPercent(currentMetrics.recall) }}</span>
          </div>
          <div class="bg-slate-50 p-2 rounded border border-slate-200 flex justify-between">
              <span class="font-bold text-teal-600">F1 Score</span>
              <span class="font-mono">{{ formatPercent(currentMetrics.f1) }}</span>
          </div>
      </div>
    </div>
  </div>
</template>
