<script setup>
import { ref, computed } from 'vue'

// Fixed Ground Truth
const totalPositives = 100 // Actual Spam
const totalNegatives = 900 // Actual Ham

// Sliders control these
const tp = ref(90)
const fp = ref(30)

// Derived values
const fn = computed(() => totalPositives - tp.value)
const tn = computed(() => totalNegatives - fp.value)

const total = computed(() => totalPositives + totalNegatives)
const actualPositive = computed(() => totalPositives)
const actualNegative = computed(() => totalNegatives)
const predictedPositive = computed(() => tp.value + fp.value)
const predictedNegative = computed(() => fn.value + tn.value)

// Metrics
const accuracy = computed(() => (tp.value + tn.value) / total.value)
const tpr = computed(() => tp.value / actualPositive.value || 0) // Recall / Sensitivity
const fpr = computed(() => fp.value / actualNegative.value || 0)
const precision = computed(() => tp.value / predictedPositive.value || 0)
const f1 = computed(() => {
  const p = precision.value
  const r = tpr.value
  return (p + r) === 0 ? 0 : 2 * (p * r) / (p + r)
})

const formatPercent = (val) => (val * 100).toFixed(1) + '%'
</script>

<template>
  <div class="bg-white p-6 rounded-lg shadow-xl text-slate-800 text-sm max-w-4xl mx-auto">
    <div class="flex justify-between items-center mb-6">
      <div>
        <p class="text-slate-500">Scenario: Spam Filter (Positive = Spam, Negative = Ham)</p>
      </div>
      <div class="text-right">
        <div class="text-xs text-slate-400 uppercase tracking-wider">Total Samples</div>
        <div class="text-2xl font-mono font-bold">{{ total }}</div>
      </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
      <!-- Matrix Inputs -->
      <div class="relative">
        <!-- Labels -->
        <div class="absolute -top-6 left-1/2 -translate-x-1/2 font-bold text-slate-600">Actual Class</div>
        <div class="absolute top-1/2 -left-8 -translate-y-1/2 -rotate-90 font-bold text-slate-600 whitespace-nowrap">Predicted Class</div>

        <div class="grid grid-cols-[auto_1fr_1fr] gap-2">
          <!-- Header Row -->
          <div></div>
          <div class="text-center font-semibold text-slate-600 pb-1">Positive (Spam)</div>
          <div class="text-center font-semibold text-slate-600 pb-1">Negative (Ham)</div>

          <!-- Row 1: Predicted Positive -->
          <div class="flex items-center justify-end font-semibold text-slate-600 pr-2">Positive</div>
          <div class="bg-green-50 p-3 rounded border-2 border-green-200 hover:border-green-400 transition-colors flex flex-col justify-between">
            <label class="block text-xs text-green-700 font-bold uppercase mb-1">True Positive (TP)</label>
            <div class="text-2xl font-mono font-bold text-center text-green-800">{{ tp }}</div>
            <input type="range" v-model.number="tp" min="0" :max="totalPositives" class="w-full accent-green-600 mt-2" />
            <div class="text-[10px] text-green-600 text-center mt-1">Slider: Caught Spam</div>
          </div>
          <div class="bg-red-50 p-3 rounded border-2 border-red-200 hover:border-red-400 transition-colors flex flex-col justify-between">
            <label class="block text-xs text-red-700 font-bold uppercase mb-1">False Positive (FP)</label>
            <div class="text-2xl font-mono font-bold text-center text-red-800">{{ fp }}</div>
            <input type="range" v-model.number="fp" min="0" :max="totalNegatives" class="w-full accent-red-600 mt-2" />
            <div class="text-[10px] text-red-500 text-center mt-1">Slider: False Alarms</div>
          </div>

          <!-- Row 2: Predicted Negative -->
          <div class="flex items-center justify-end font-semibold text-slate-600 pr-2">Negative</div>
          <div class="bg-red-50 p-3 rounded border-2 border-red-200 hover:border-red-400 transition-colors flex flex-col justify-between">
            <label class="block text-xs text-red-700 font-bold uppercase mb-1">False Negative (FN)</label>
            <div class="text-2xl font-mono font-bold text-center text-red-800 py-2">{{ fn }}</div>
            <div class="text-[10px] text-red-500 text-center mt-1">Missed Spam</div>
          </div>
          <div class="bg-green-50 p-3 rounded border-2 border-green-200 hover:border-green-400 transition-colors flex flex-col justify-between">
            <label class="block text-xs text-green-700 font-bold uppercase mb-1">True Negative (TN)</label>
            <div class="text-2xl font-mono font-bold text-center text-green-800 py-2">{{ tn }}</div>
            <div class="text-[10px] text-green-600 text-center mt-1">Correctly Ignored</div>
          </div>
        </div>
      </div>

      <!-- Metrics Display -->
      <div class="flex flex-col justify-center space-y-3 bg-slate-50 p-4 rounded-lg border border-slate-200">
        <div class="metric-row">
            <div class="flex flex-col">
                <span class="font-bold text-slate-700">Accuracy</span>
                <span class="text-xs text-slate-400">(TP+TN)/Total</span>
            </div>
            <span class="font-mono text-xl font-bold text-slate-800">{{ formatPercent(accuracy) }}</span>
        </div>
        <div class="h-px bg-slate-200 my-1"></div>
        <div class="metric-row">
            <div class="flex flex-col">
                <span class="font-bold text-blue-600">TPR (Recall)</span>
                <span class="text-xs text-slate-400">TP / (TP+FN)</span>
            </div>
            <span class="font-mono text-xl font-bold text-blue-600">{{ formatPercent(tpr) }}</span>
        </div>
        <div class="metric-row">
            <div class="flex flex-col">
                <span class="font-bold text-red-600">FPR</span>
                <span class="text-xs text-slate-400">FP / (FP+TN)</span>
            </div>
            <span class="font-mono text-xl font-bold text-red-600">{{ formatPercent(fpr) }}</span>
        </div>
        <div class="h-px bg-slate-200 my-1"></div>
        <div class="metric-row">
            <div class="flex flex-col">
                <span class="font-bold text-purple-600">Precision</span>
                <span class="text-xs text-slate-400">TP / (TP+FP)</span>
            </div>
            <span class="font-mono text-xl font-bold text-purple-600">{{ formatPercent(precision) }}</span>
        </div>
        <div class="metric-row">
            <div class="flex flex-col">
                <span class="font-bold text-teal-600">F1 Score</span>
                <span class="text-xs text-slate-400">Harmonic Mean</span>
            </div>
            <span class="font-mono text-xl font-bold text-teal-600">{{ formatPercent(f1) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.metric-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
}
</style>
