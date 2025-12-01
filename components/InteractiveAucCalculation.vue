<script setup>
import { ref, computed, onMounted, watchEffect } from 'vue'
import * as Plot from '@observablehq/plot'

// Data with a tie to demonstrate trapezoid method
const rawData = [
  { id: 1, class: 'P', score: 0.95 },
  { id: 2, class: 'P', score: 0.85 },
  { id: 3, class: 'N', score: 0.70 },
  { id: 4, class: 'P', score: 0.60 },
  { id: 5, class: 'N', score: 0.50 }, // Tie
  { id: 6, class: 'P', score: 0.50 }, // Tie
  { id: 7, class: 'N', score: 0.40 },
  { id: 8, class: 'P', score: 0.30 },
  { id: 9, class: 'N', score: 0.20 },
  { id: 10, class: 'N', score: 0.10 },
]

const sortedData = computed(() => [...rawData].sort((a, b) => b.score - a.score))

const totalP = rawData.filter(d => d.class === 'P').length
const totalN = rawData.filter(d => d.class === 'N').length

// Simulation State
const currentStep = ref(0)
const steps = computed(() => {
  const history = []
  let FP = 0, TP = 0, FPprev = 0, TPprev = 0, Area = 0
  let prevScore = Infinity

  // Initial state
  history.push({
    idx: -1, FP, TP, FPprev, TPprev, Area,
    action: 'Start',
    trapezoid: null
  })

  for (let i = 0; i < sortedData.value.length; i++) {
    const item = sortedData.value[i]

    // Check for score change (or end of list logic handled naturally by next iteration)
    if (item.score !== prevScore) {
      // Calculate Trapezoid
      const width = FP - FPprev
      const avgHeight = (TP + TPprev) / 2
      const trapArea = width * avgHeight

      if (width > 0 || (TP - TPprev) > 0) {
          // Only record a step if we actually moved
          // But for the algorithm visualization, we want to show the "check"
      }

      if (i > 0) { // Don't add area on first item (prev was start)
          Area += trapArea
          history.push({
            idx: i, FP, TP, FPprev, TPprev, Area,
            action: 'Add Trapezoid',
            trapezoid: { x1: FPprev, x2: FP, y1: TPprev, y2: TP }
          })
      }

      FPprev = FP
      TPprev = TP
      prevScore = item.score
    }

    // Update Counts
    if (item.class === 'P') TP++
    else FP++

    history.push({
      idx: i, FP, TP, FPprev, TPprev, Area,
      action: `Process ${item.class} (Score ${item.score})`,
      trapezoid: null
    })
  }

  // Final Trapezoid
  const width = FP - FPprev
  const avgHeight = (TP + TPprev) / 2
  Area += width * avgHeight

  history.push({
    idx: sortedData.value.length, FP, TP, FPprev, TPprev, Area,
    action: 'Finalize Area',
    trapezoid: { x1: FPprev, x2: FP, y1: TPprev, y2: TP }
  })

  // Scale
  history.push({
    idx: sortedData.value.length, FP, TP, FPprev, TPprev, Area,
    action: 'Scale Result',
    finalAuc: Area / (totalP * totalN),
    trapezoid: null
  })

  return history
})

const currentState = computed(() => steps.value[currentStep.value])

const next = () => {
  if (currentStep.value < steps.value.length - 1) currentStep.value++
}

const prev = () => {
  if (currentStep.value > 0) currentStep.value--
}

const reset = () => {
  currentStep.value = 0
}

// Plotting
const plotContainer = ref(null)

onMounted(() => {
  watchEffect(() => {
    if (!plotContainer.value) return

    const state = currentState.value

    // Collect path points up to current state
    // We need to reconstruct the path from the history up to this point
    // The path consists of (FPprev, TPprev) points committed
    const path = []
    // Always start at 0,0
    path.push({x: 0, y: 0})

    // Add points from history where we updated FPprev/TPprev (Trapezoid steps)
    // Or just use the current FP/TP as the "head"

    // Let's build the full path of "committed" points plus current head
    // Actually, simpler: The path is the sequence of (FP, TP) at each 'Process' step?
    // No, the ROC curve connects the points (FP, TP) where the score changes.
    // So we should plot the points where action == 'Add Trapezoid' or 'Finalize Area'

    const curvePoints = [{x:0, y:0}]
    const areas = []

    for (let i = 0; i <= currentStep.value; i++) {
        const s = steps.value[i]
        if (s.trapezoid) {
            curvePoints.push({x: s.trapezoid.x2, y: s.trapezoid.y2})
            areas.push(s.trapezoid)
        }
    }

    // Current head position (ghost dot)
    const head = { x: state.FP, y: state.TP }

    const plot = Plot.plot({
      width: 350,
      height: 250,
      grid: true,
      x: { label: "False Positives (FP)", domain: [0, totalN] },
      y: { label: "True Positives (TP)", domain: [0, totalP] },
      marks: [
        Plot.ruleY([0]),
        Plot.ruleX([0]),

        // Completed Area
        ...areas.map(t => Plot.areaY([
            {x: t.x1, y: t.y1},
            {x: t.x2, y: t.y2}
        ], {x: "x", y: "y", fill: "#3b82f6", fillOpacity: 0.2})),

        // Current Trapezoid Highlight
        state.trapezoid ? Plot.areaY([
            {x: state.trapezoid.x1, y: state.trapezoid.y1},
            {x: state.trapezoid.x2, y: state.trapezoid.y2}
        ], {x: "x", y: "y", fill: "#f59e0b", fillOpacity: 0.5}) : null,

        // The Curve
        Plot.line(curvePoints, {x: "x", y: "y", stroke: "#3b82f6", strokeWidth: 2}),

        // Current Position Head
        Plot.dot([head], {x: "x", y: "y", fill: "red", r: 5}),
        Plot.text([head], {x: "x", y: "y", text: d => `(${d.x}, ${d.y})`, dy: -10, fontWeight: "bold"}),

        // Diagonal (Random)
        Plot.line([{x:0, y:0}, {x: totalN, y: totalP}], {x: "x", y: "y", stroke: "#ddd", strokeDasharray: "4,4"})
      ]
    })

    plotContainer.value.innerHTML = ''
    plotContainer.value.appendChild(plot)
  })
})
</script>

<template>
  <div class="flex gap-4">
    <!-- Left: Data Table -->
    <div class="w-1/3 text-xs">
      <div class="flex justify-between items-center mb-2">
        <h3 class="font-bold">Sorted Test Data</h3>
        <div class="text-gray-500">Total P: {{totalP}}, Total N: {{totalN}}</div>
      </div>
      <div class="border rounded overflow-y-auto max-h-[200px]">
        <table class="w-full text-center">
          <thead class="bg-gray-100 border-b">
            <tr>
              <th class="p-1">#</th>
              <th class="p-1">Class</th>
              <th class="p-1">Score</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(row, idx) in sortedData"
              :key="row.id"
              :class="{
                'bg-blue-100 font-bold': currentState.idx === idx,
                'bg-gray-50': idx % 2 === 0 && currentState.idx !== idx
              }"
            >
              <td class="p-1">{{ idx + 1 }}</td>
              <td class="p-1" :class="row.class === 'P' ? 'text-green-600' : 'text-red-600'">{{ row.class }}</td>
              <td class="p-1">{{ row.score.toFixed(2) }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Controls -->
      <div class="mt-4 flex gap-2 justify-center">
        <button @click="prev" :disabled="currentStep === 0" class="px-3 py-1 bg-gray-200 rounded hover:bg-gray-300 disabled:opacity-50">Prev</button>
        <button @click="next" :disabled="currentStep === steps.length - 1" class="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50">Next</button>
        <button @click="reset" class="px-3 py-1 bg-gray-200 rounded hover:bg-gray-300">Reset</button>
      </div>
    </div>

    <!-- Right: Visualization -->
    <div class="w-2/3 flex flex-col items-center">
      <div ref="plotContainer" class="bg-white p-2 rounded shadow-sm border mb-2"></div>

      <!-- Status Box -->
      <div class="w-full bg-gray-50 p-2 rounded border text-xs">
        <div class="font-bold mb-1 border-b pb-1">Step {{ currentStep + 1 }}: {{ currentState.action }}</div>
        <div class="grid grid-cols-2 gap-x-2 gap-y-1">
          <div>Current Pos: <b>({{ currentState.FP }}, {{ currentState.TP }})</b></div>
          <div>Previous Pos: <b>({{ currentState.FPprev }}, {{ currentState.TPprev }})</b></div>
          <div>Accumulated Area: <b>{{ currentState.Area.toFixed(2) }}</b></div>
          <div v-if="currentState.finalAuc" class="col-span-2 text-blue-600 font-bold mt-1 border-t pt-1">
            Final AUC = {{ currentState.Area.toFixed(2) }} / ({{totalP}} × {{totalN}}) = {{ currentState.finalAuc.toFixed(3) }}
          </div>
        </div>
        <div v-if="currentState.trapezoid" class="mt-1 text-xs text-orange-600 bg-orange-50 p-1 rounded">
          Adding Trapezoid: Width {{ (currentState.trapezoid.x2 - currentState.trapezoid.x1).toFixed(1) }} ×
          Avg Height {{ ((currentState.trapezoid.y1 + currentState.trapezoid.y2)/2).toFixed(1) }}
          = {{ ((currentState.trapezoid.x2 - currentState.trapezoid.x1) * (currentState.trapezoid.y1 + currentState.trapezoid.y2)/2).toFixed(2) }}
        </div>
      </div>
    </div>
  </div>
</template>
