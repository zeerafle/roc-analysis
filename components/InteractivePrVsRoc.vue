<script setup>
import { ref, computed, onMounted, watchEffect } from 'vue'
import * as Plot from '@observablehq/plot'
import * as d3 from 'd3'

const numPos = ref(100)
const numNeg = ref(100)
const separation = ref(1.5)

const data = computed(() => {
  // Seeded random for stability would be nice, but standard random is fine for demo
  const rngPos = d3.randomNormal(separation.value, 1)
  const rngNeg = d3.randomNormal(0, 1)
  
  const pos = Array.from({length: Number(numPos.value)}, () => ({ label: 1, score: rngPos() }))
  const neg = Array.from({length: Number(numNeg.value)}, () => ({ label: 0, score: rngNeg() }))
  
  const all = [...pos, ...neg].sort((a, b) => b.score - a.score)
  
  const rocPoints = [{fpr: 0, tpr: 0}]
  const prPoints = [{recall: 0, precision: 1}]
  
  let TP = 0
  let FP = 0
  const P = Number(numPos.value)
  const N = Number(numNeg.value)
  
  all.forEach(d => {
    if (d.label === 1) TP++
    else FP++
    
    const tpr = TP / P
    const fpr = FP / N
    const precision = TP / (TP + FP)
    
    rocPoints.push({fpr, tpr})
    prPoints.push({recall: tpr, precision})
  })
  
  return { rocPoints, prPoints, ratio: N/P }
})

const rocDiv = ref(null)
const prDiv = ref(null)

onMounted(() => {
  watchEffect(() => {
    if (!rocDiv.value || !prDiv.value) return
    
    const { rocPoints, prPoints } = data.value
    
    // ROC Plot
    const rocPlot = Plot.plot({
      width: 350,
      height: 300,
      grid: true,
      x: { label: "False Positive Rate", domain: [0, 1] },
      y: { label: "True Positive Rate", domain: [0, 1] },
      marks: [
        Plot.ruleY([0, 1]),
        Plot.ruleX([0, 1]),
        Plot.line(rocPoints, {x: "fpr", y: "tpr", stroke: "#3b82f6", strokeWidth: 2}),
        Plot.line([[0,0], [1,1]], {stroke: "#ddd", strokeDasharray: "4,4"}),
        Plot.text([{x: 0.5, y: 0.1, label: "Insensitive to Skew"}], {x: "x", y: "y", text: "label", fill: "#666"})
      ]
    })
    
    rocDiv.value.innerHTML = ''
    rocDiv.value.appendChild(rocPlot)
    
    // PR Plot
    const prPlot = Plot.plot({
      width: 350,
      height: 300,
      grid: true,
      x: { label: "Recall (TPR)", domain: [0, 1] },
      y: { label: "Precision", domain: [0, 1] },
      marks: [
        Plot.ruleY([0, 1]),
        Plot.ruleX([0, 1]),
        Plot.line(prPoints, {x: "recall", y: "precision", stroke: "#ef4444", strokeWidth: 2}),
        Plot.text([{x: 0.5, y: 0.1, label: "Sensitive to Skew"}], {x: "x", y: "y", text: "label", fill: "#666"}),
        // Baseline for PR changes with skew: P / (P + N)
        Plot.ruleY([numPos.value / (Number(numPos.value) + Number(numNeg.value))], {stroke: "#ddd", strokeDasharray: "4,4"})
      ]
    })
    
    prDiv.value.innerHTML = ''
    prDiv.value.appendChild(prPlot)
  })
})
</script>

<template>
  <div class="flex flex-col items-center gap-4">
    <div class="flex gap-8 bg-gray-50 p-4 rounded border">
      <div class="flex flex-col gap-1">
        <label class="text-xs font-bold">Positives (P)</label>
        <input type="range" v-model="numPos" min="50" max="500" step="50" />
        <span class="text-xs text-center">{{ numPos }}</span>
      </div>
      <div class="flex flex-col gap-1">
        <label class="text-xs font-bold">Negatives (N)</label>
        <input type="range" v-model="numNeg" min="100" max="5000" step="100" />
        <span class="text-xs text-center">{{ numNeg }}</span>
      </div>
      <div class="flex flex-col gap-1">
        <label class="text-xs font-bold">Separation (d')</label>
        <input type="range" v-model="separation" min="0.5" max="3" step="0.1" />
        <span class="text-xs text-center">{{ separation }}</span>
      </div>
      <div class="flex flex-col justify-center">
        <div class="text-sm font-bold">Skew Ratio (N:P)</div>
        <div class="text-xl text-center text-purple-600">1 : {{ (numNeg/numPos).toFixed(1) }}</div>
      </div>
    </div>
    
    <div class="flex gap-4">
      <div class="flex flex-col items-center">
        <h3 class="font-bold text-blue-600">ROC Curve</h3>
        <div ref="rocDiv" class="bg-white p-2 rounded shadow-sm border"></div>
      </div>
      <div class="flex flex-col items-center">
        <h3 class="font-bold text-red-600">Precision-Recall Curve</h3>
        <div ref="prDiv" class="bg-white p-2 rounded shadow-sm border"></div>
      </div>
    </div>
  </div>
</template>
