<script setup>
import * as Plot from "@observablehq/plot";
import { onMounted, useTemplateRef } from "vue";

const plotDiv = useTemplateRef('plotDiv');

onMounted(() => {
  const plot = Plot.plot({
    width: 350,
    height: 350,
    grid: true,
    x: { domain: [0, 1], label: "False Positive Rate (FPR)" },
    y: { domain: [0, 1], label: "True Positive Rate (TPR)" },
    marks: [
      // Diagonal line
      Plot.line([{x:0, y:0}, {x:1, y:1}], {x: "x", y: "y", stroke: "gray", strokeDasharray: "4,4"}),
      // Random label
      Plot.text([{x: 0.5, y: 0.5}], {x: "x", y: "y", text: () => "Random Guessing", rotate: -45, dy: -10, fill: "gray"}),
      // Perfect point
      Plot.dot([{x: 0, y: 1}], {x: "x", y: "y", fill: "green", r: 6}),
      Plot.text([{x: 0, y: 1}], {x: "x", y: "y", text: () => "Perfect (0,1)", dy: 15, dx: 5, fill: "green", textAnchor: "start", fontWeight: "bold"}),
      // Worst point
      Plot.dot([{x: 1, y: 0}], {x: "x", y: "y", fill: "red", r: 6}),
      Plot.text([{x: 1, y: 0}], {x: "x", y: "y", text: () => "Worst (1,0)", dy: -15, dx: -5, fill: "red", textAnchor: "end", fontWeight: "bold"}),
    ]
  });
  plotDiv.value.append(plot);
});
</script>

<template>
  <div ref="plotDiv" class="bg-white rounded p-4 shadow-lg flex justify-center"></div>
</template>
