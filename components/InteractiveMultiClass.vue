<script setup>
import { ref, computed, onMounted, watchEffect } from 'vue'
import * as Plot from '@observablehq/plot'

const classes = ['Cat', 'Dog', 'Bird']
const selectedClass = ref('Cat')

// Synthetic Confusion Matrix Data (Rows: Actual, Cols: Predicted)
// [ [Pred Cat, Pred Dog, Pred Bird], ... ]
const matrix = ref([
  [50, 10, 5],  // Actual Cat
  [5, 45, 10],  // Actual Dog
  [2, 8, 60]    // Actual Bird
])

const cellType = (actual, predicted) => {
  const target = selectedClass.value

  if (actual === target && predicted === target) return 'TP'
  if (actual === target && predicted !== target) return 'FN'
  if (actual !== target && predicted === target) return 'FP'
  if (actual !== target && predicted !== target) return 'TN'
  return ''
}

const cellColor = (type) => {
  switch (type) {
    case 'TP': return 'bg-green-100 border-green-500 text-green-700'
    case 'FN': return 'bg-red-100 border-red-500 text-red-700'
    case 'FP': return 'bg-yellow-100 border-yellow-500 text-yellow-700'
    case 'TN': return 'bg-gray-100 border-gray-400 text-gray-600'
    default: return 'bg-white'
  }
}

const stats = computed(() => {
  const target = selectedClass.value
  const targetIdx = classes.indexOf(target)

  let TP = 0, FN = 0, FP = 0, TN = 0

  matrix.value.forEach((row, rIdx) => {
    row.forEach((val, cIdx) => {
      const actual = classes[rIdx]
      const predicted = classes[cIdx]
      const type = cellType(actual, predicted)

      if (type === 'TP') TP += val
      if (type === 'FN') FN += val
      if (type === 'FP') FP += val
      if (type === 'TN') TN += val
    })
  })

  const TPR = TP / (TP + FN)
  const FPR = FP / (FP + TN)

  return { TP, FN, FP, TN, TPR, FPR }
})

const plotContainer = ref(null)

// Generate a synthetic curve that passes near the point
const generateCurve = (fpr, tpr) => {
    // Simple power law y = x^k passing through (fpr, tpr)
    // tpr = fpr^k => log(tpr) = k * log(fpr) => k = log(tpr) / log(fpr)
    // Clamp k to avoid weird shapes
    let k = Math.log(tpr) / Math.log(fpr)
    if (!isFinite(k) || k <= 0) k = 0.5 // Fallback

    const points = []
    for(let i=0; i<=50; i++) {
        const x = i/50
        points.push({x, y: Math.pow(x, k)})
    }
    return points
}

onMounted(() => {
  watchEffect(() => {
    if (!plotContainer.value) return

    const { TPR, FPR } = stats.value
    const curveData = generateCurve(FPR, TPR)

    const plot = Plot.plot({
      width: 300,
      height: 300,
      grid: true,
      x: { label: "FPR", domain: [0, 1] },
      y: { label: "TPR", domain: [0, 1] },
      marks: [
        Plot.ruleY([0, 1]),
        Plot.ruleX([0, 1]),
        Plot.line([[0,0], [1,1]], { stroke: "#ddd", strokeDasharray: "4,4" }),
        Plot.line(curveData, { x: "x", y: "y", stroke: "#3b82f6", strokeWidth: 3 }),
        Plot.dot([{x: FPR, y: TPR}], { x: "x", y: "y", fill: "red", r: 6 }),
        Plot.text([{x: FPR, y: TPR, label: selectedClass.value}], { x: "x", y: "y", text: "label", dy: -10, fontWeight: "bold" })
      ]
    })

    plotContainer.value.innerHTML = ''
    plotContainer.value.appendChild(plot)
  })
})

</script>

<template>
  <div class="flex gap-8 items-start justify-center">

    <!-- Matrix Side -->
    <div class="flex flex-col gap-4">
      <h3 class="text-center font-bold">Select Positive Class</h3>
      <div class="flex justify-center gap-2 mb-2">
        <button
          v-for="cls in classes"
          :key="cls"
          @click="selectedClass = cls"
          class="px-3 py-1 rounded border"
          :class="selectedClass === cls ? 'bg-blue-500 text-white' : 'bg-gray-100 hover:bg-gray-200'"
        >
          {{ cls }}
        </button>
      </div>

      <div class="grid grid-cols-4 gap-1 text-sm">
        <!-- Header Row -->
        <div class="font-bold text-center self-end">Actual \ Pred</div>
        <div v-for="cls in classes" :key="'h-'+cls" class="font-bold text-center p-2 bg-gray-50 rounded">
          {{ cls }}
        </div>

        <!-- Data Rows -->
        <template v-for="(row, rIdx) in matrix" :key="'row-'+rIdx">
          <div class="font-bold flex items-center justify-end pr-2 bg-gray-50 rounded">
            {{ classes[rIdx] }}
          </div>
          <div
            v-for="(val, cIdx) in row"
            :key="'cell-'+rIdx+'-'+cIdx"
            class="border-2 rounded p-3 flex flex-col items-center justify-center transition-colors duration-300"
            :class="cellColor(cellType(classes[rIdx], classes[cIdx]))"
          >
            <span class="text-lg font-bold">{{ val }}</span>
            <span class="text-xs font-mono uppercase">{{ cellType(classes[rIdx], classes[cIdx]) }}</span>
          </div>
        </template>
      </div>

      <div class="grid grid-cols-2 gap-2 text-xs mt-2">
        <div class="flex items-center gap-2"><div class="w-4 h-4 bg-green-100 border border-green-500"></div> TP: True Positive</div>
        <div class="flex items-center gap-2"><div class="w-4 h-4 bg-red-100 border border-red-500"></div> FN: False Negative</div>
        <div class="flex items-center gap-2"><div class="w-4 h-4 bg-yellow-100 border border-yellow-500"></div> FP: False Positive</div>
        <div class="flex items-center gap-2"><div class="w-4 h-4 bg-gray-100 border border-gray-400"></div> TN: True Negative</div>
      </div>
    </div>

    <!-- Graph Side -->
    <div class="flex flex-col items-center">
      <h3 class="font-bold mb-2">ROC for {{ selectedClass }}</h3>
      <div ref="plotContainer" class="bg-white p-2 rounded shadow-sm border"></div>
      <div class="mt-4 text-sm grid grid-cols-2 gap-x-8 gap-y-1">
        <div>TPR: <b>{{ stats.TPR.toFixed(2) }}</b></div>
        <div>FPR: <b>{{ stats.FPR.toFixed(2) }}</b></div>
        <div>TP: {{ stats.TP }}</div>
        <div>FP: {{ stats.FP }}</div>
        <div>TN: {{ stats.TN }}</div>
        <div>FN: {{ stats.FN }}</div>
      </div>
    </div>

  </div>
</template>
