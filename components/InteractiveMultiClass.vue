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

onMounted(() => {
  watchEffect(() => {
    if (!plotContainer.value) return

    const { TPR, FPR } = stats.value

    // In One-vs-All, we only have ONE point (TPR, FPR) for the selected class
    // because we have a fixed confusion matrix (fixed threshold).
    // We don't have a full curve. We just connect (0,0) -> Point -> (1,1)
    // to show the "convex hull" of this single classifier.
    const curveData = [
        {x: 0, y: 0},
        {x: FPR, y: TPR},
        {x: 1, y: 1}
    ]

    const plot = Plot.plot({
      width: 300,
      height: 250,
      grid: true,
      x: { label: "FPR", domain: [0, 1] },
      y: { label: "TPR", domain: [0, 1] },
      marks: [
        Plot.ruleY([0, 1]),
        Plot.ruleX([0, 1]),
        Plot.line([[0,0], [1,1]], { stroke: "#ddd", strokeDasharray: "4,4" }),
        Plot.line(curveData, { x: "x", y: "y", stroke: "#3b82f6", strokeWidth: 2 }),
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
    <div class="flex gap-4 items-start">
      <div class="flex flex-col items-center">
        <h3 class="font-bold mb-2">ROC for {{ selectedClass }}</h3>
        <div ref="plotContainer" class="bg-white p-2 rounded shadow-sm border"></div>
      </div>

      <div class="mt-8 text-xs grid grid-cols-1 gap-y-2 bg-gray-50 p-3 rounded border">
        <div class="font-bold border-b pb-1 mb-1">Metrics</div>
        <div class="flex justify-between gap-4"><span>TPR:</span> <b>{{ stats.TPR.toFixed(2) }}</b></div>
        <div class="flex justify-between gap-4"><span>FPR:</span> <b>{{ stats.FPR.toFixed(2) }}</b></div>
        <div class="flex justify-between gap-4"><span>TP:</span> <span>{{ stats.TP }}</span></div>
        <div class="flex justify-between gap-4"><span>FP:</span> <span>{{ stats.FP }}</span></div>
        <div class="flex justify-between gap-4"><span>TN:</span> <span>{{ stats.TN }}</span></div>
        <div class="flex justify-between gap-4"><span>FN:</span> <span>{{ stats.FN }}</span></div>
      </div>
    </div>

  </div>
</template>
