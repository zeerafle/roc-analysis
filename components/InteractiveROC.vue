<script setup>
import * as Plot from "@observablehq/plot";
import * as d3 from "d3";
import { ref, computed, onMounted, watch, useTemplateRef } from "vue";

const separation = ref(2);
const threshold = ref(0);
const plotDiv = useTemplateRef('plotDiv');

// Generate data for distributions
const xDomain = [-5, 10];
const x = d3.range(xDomain[0], xDomain[1], 0.1);

// Error function approximation
const erf = (x) => {
  var sign = (x >= 0) ? 1 : -1;
  x = Math.abs(x);
  var a1 =  0.254829592;
  var a2 = -0.284496736;
  var a3 =  1.421413741;
  var a4 = -1.453152027;
  var a5 =  1.061405429;
  var p  =  0.3275911;
  var t = 1.0/(1.0 + p*x);
  var y = 1.0 - (((((a5*t + a4)*t) + a3)*t + a2)*t + a1)*t*Math.exp(-x*x);
  return sign*y;
}

const cdf = (x, mean, sigma) => {
    return 0.5 * (1 + erf((x - mean) / (sigma * Math.sqrt(2))));
};

const distributions = computed(() => {
  const noiseMean = 0;
  const signalMean = separation.value;
  const stdDev = 1;

  const noise = x.map(v => ({ x: v, y: (1 / (stdDev * Math.sqrt(2 * Math.PI))) * Math.exp(-0.5 * Math.pow((v - noiseMean) / stdDev, 2)), type: 'Noise' }));
  const signal = x.map(v => ({ x: v, y: (1 / (stdDev * Math.sqrt(2 * Math.PI))) * Math.exp(-0.5 * Math.pow((v - signalMean) / stdDev, 2)), type: 'Signal' }));

  return [...noise, ...signal];
});

// Calculate ROC curve
const rocData = computed(() => {
  const noiseMean = 0;
  const signalMean = separation.value;
  const stdDev = 1;

  const points = [];
  // Sweep threshold from high to low
  for (let t = xDomain[1]; t >= xDomain[0]; t -= 0.1) {
    const tpr = 1 - cdf(t, signalMean, stdDev);
    const fpr = 1 - cdf(t, noiseMean, stdDev);
    points.push({ fpr, tpr, threshold: t });
  }
  return points;
});

const currentPoint = computed(() => {
    const noiseMean = 0;
    const signalMean = separation.value;
    const stdDev = 1;

    const tpr = 1 - cdf(threshold.value, signalMean, stdDev);
    const fpr = 1 - cdf(threshold.value, noiseMean, stdDev);
    return { fpr, tpr, threshold: threshold.value };
});

watch([separation, threshold], () => {
  renderPlot();
});

onMounted(() => {
  renderPlot();
});

function renderPlot() {
  if (!plotDiv.value) return;

  plotDiv.value.innerHTML = '';

  const distPlot = Plot.plot({
    width: 400,
    height: 300,
    x: { domain: xDomain, label: "Score" },
    y: { label: "Density" },
    color: { legend: true, domain: ["Noise", "Signal"], range: ["steelblue", "orange"] },
    marks: [
      Plot.lineY(distributions.value, { x: "x", y: "y", stroke: "type", strokeWidth: 2 }),
      Plot.areaY(distributions.value, { x: "x", y: "y", fill: "type", fillOpacity: 0.1 }),
      Plot.ruleX([threshold.value], { stroke: "red", strokeWidth: 2, strokeDasharray: "4,4" }),
      Plot.text([threshold.value], { x: threshold.value, y: 0.4, text: d => `Threshold: ${d.toFixed(1)}`, dy: -10, fill: "red" })
    ]
  });

  const rocPlot = Plot.plot({
    width: 400,
    height: 400,
    x: { domain: [0, 1], label: "False Positive Rate (FPR)" },
    y: { domain: [0, 1], label: "True Positive Rate (TPR)" },
    grid: true,
    marks: [
      Plot.line(rocData.value, { x: "fpr", y: "tpr", strokeWidth: 2 }),
      Plot.dot([currentPoint.value], { x: "fpr", y: "tpr", fill: "red", r: 5 }),
      Plot.ruleY([currentPoint.value.tpr], { stroke: "red", strokeOpacity: 0.5 }),
      Plot.ruleX([currentPoint.value.fpr], { stroke: "red", strokeOpacity: 0.5 }),
      Plot.text([currentPoint.value], { x: "fpr", y: "tpr", text: d => `(${d.fpr.toFixed(2)}, ${d.tpr.toFixed(2)})`, dy: -10, fill: "red" }),
      Plot.line([{x:0, y:0}, {x:1, y:1}], {x:"x", y:"y", stroke: "gray", strokeDasharray: "4,4"}) // Random guess line
    ]
  });

  const container = document.createElement("div");
  container.style.display = "flex";
  container.style.gap = "20px";
  container.style.flexWrap = "wrap";
  container.appendChild(distPlot);
  container.appendChild(rocPlot);

  plotDiv.value.appendChild(container);
}

</script>

<template>
  <div class="interactive-roc p-4 bg-white rounded shadow text-black">
    <div class="controls mb-4 flex gap-4 flex-wrap">
      <label class="flex flex-col">
        <span class="font-bold">Separation (d'): {{ separation }}</span>
        <input type="range" min="0" max="5" step="0.1" v-model.number="separation" />
      </label>
      <label class="flex flex-col">
        <span class="font-bold">Threshold: {{ threshold }}</span>
        <input type="range" :min="xDomain[0]" :max="xDomain[1]" step="0.1" v-model.number="threshold" />
      </label>
    </div>
    <div ref="plotDiv"></div>
  </div>
</template>

<style scoped>
.interactive-roc {
    color: #333;
}
</style>
