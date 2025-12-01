<script setup>
import { ref, computed, onMounted, watchEffect } from 'vue'
import * as Plot from '@observablehq/plot'
import * as d3 from 'd3'

const container = ref(null)
const hoveredCurve = ref(null)

// Generate synthetic data
const generateCurve = (id, fn, color, label) => {
  const points = []
  for (let i = 0; i <= 50; i++) {
    const x = i / 50
    points.push({ fpr: x, tpr: fn(x), id, label, color })
  }
  return { id, points, color, label }
}

// Curve A: Good early performance (e.g., x^0.15)
const fnA = x => Math.pow(x, 0.3)
const curveA = generateCurve('A', fnA, '#ef4444', 'Classifier A')

// Curve C: Good late performance (S-shaped)
const fnC = x => {
  const k = 10, x0 = 0.23
  const sigmoid = t => 1 / (1 + Math.exp(-k * (t - x0)))
  const min = sigmoid(0), max = sigmoid(1)
  return (sigmoid(x) - min) / (max - min)
}
const curveC = generateCurve('C', fnC, '#3b82f6', 'Classifier C')

// Curve B: Suboptimal (e.g., x^0.6)
const curveB = generateCurve('B', x => Math.pow(x, 0.6), '#10b981', 'Classifier B')

// Curve D: Poor (e.g., x^0.9)
const curveD = generateCurve('D', x => Math.pow(x, 0.9), '#f59e0b', 'Classifier D')

const allCurves = [curveA, curveB, curveC, curveD]
const flatData = allCurves.flatMap(c => c.points)

// Compute Convex Hull
const hullData = computed(() => {
  const points = flatData.map(p => [p.fpr, p.tpr])
  // Add (0,0) and (1,1) explicitly to ensure they are in the set,
  // though they should be covered by the curves.
  points.push([0, 0], [1, 1])

  const hull = d3.polygonHull(points)
  if (!hull) return []

  // The hull of a set of ROC curves (which are monotonic and start at 0,0 end at 1,1)
  // consists of the "upper frontier" and the diagonal (if we consider the area).
  // The vertices returned by polygonHull will be the points on the upper frontier
  // plus (0,0) and (1,1).
  // If we sort them by FPR, we get the upper frontier curve.

  return hull.map(p => ({ fpr: p[0], tpr: p[1] }))
             .sort((a, b) => a.fpr - b.fpr)
})

onMounted(() => {
  watchEffect(() => {
    if (!container.value) return

    // Calculate Iso-Performance Lines
    // Line Alpha: Tangent to A (Red) at low FPR
    const xa = 0.02
    const ya = fnA(xa)
    const ma = (fnA(xa + 0.0001) - fnA(xa)) / 0.0001 // Numerical derivative
    const alphaPoints = [
        { x: 0, y: ya - ma * xa },
        { x: 0.5, y: ma * (0.5 - xa) + ya } // Extend enough to cross view
    ]

    // Line Beta: Tangent to C (Blue) at high FPR
    const xb = 0.7
    const yb = fnC(xb)
    const mb = (fnC(xb + 0.0001) - fnC(xb)) / 0.0001
    const betaPoints = [
        { x: 0, y: yb - mb * xb },
        { x: 1, y: mb * (1 - xb) + yb }
    ]

    const plot = Plot.plot({
      width: 370,
      height: 370,
      grid: true,
      x: { label: "False Positive Rate", domain: [0, 1] },
      y: { label: "True Positive Rate", domain: [0, 1] },
      color: { legend: true, domain: allCurves.map(c => c.label), range: allCurves.map(c => c.color) },
      marks: [
        Plot.ruleY([0, 1]),
        Plot.ruleX([0, 1]),
        Plot.line([[0,0], [1,1]], { stroke: "#ddd", strokeDasharray: "4,4" }),

        // Convex Hull Area - Fill down to 0 to make it more visible
        Plot.areaY(hullData.value, {
            x: "fpr", y: "tpr", y2: 0,
            fill: "#71717a", fillOpacity: 0.15
        }),
        // Convex Hull Line
        Plot.line(hullData.value, {
            x: "fpr", y: "tpr",
            stroke: "#18181b", strokeWidth: 4, strokeDasharray: "6,4",
            title: "Convex Hull"
        }),

        // Iso-Performance Lines
        Plot.line(alphaPoints, { x: "x", y: "y", stroke: "#333", strokeDasharray: "3,3", strokeWidth: 1.5 }),
        Plot.text([{x: 0.06, y: 0.95, label: "α"}], { x: "x", y: "y", text: "label", fill: "#333", fontWeight: "bold", fontSize: 14 }),

        Plot.line(betaPoints, { x: "x", y: "y", stroke: "#333", strokeDasharray: "3,3", strokeWidth: 1.5 }),
        Plot.text([{x: 0.5, y: 0.95, label: "β"}], { x: "x", y: "y", text: "label", fill: "#333", fontWeight: "bold", fontSize: 14 }),

        // Curves
        Plot.line(flatData, {
          x: "fpr", y: "tpr", z: "id",
          stroke: "label",
          strokeWidth: (d) => (hoveredCurve.value && hoveredCurve.value !== d.id) ? 1 : 3,
          strokeOpacity: (d) => (hoveredCurve.value && hoveredCurve.value !== d.id) ? 0.3 : 1,
          title: d => d.label
        }),

        // Invisible interaction layer
        Plot.line(flatData, {
          x: "fpr", y: "tpr", z: "id",
          strokeWidth: 20,
          strokeOpacity: 0,
          title: d => d.label
        }),

        Plot.text([{x: 0.2, y: 0.9, label: "ROCCH"}], {
            x: "x", y: "y", text: "label", fill: "#18181b", fontWeight: "bold", fontSize: 16
        })
      ]
    })

    container.value.innerHTML = ''
    container.value.appendChild(plot)

    // Add event listeners manually to the invisible interaction paths
    d3.select(container.value).selectAll("path").each(function() {
      const path = d3.select(this)
      const titleNode = path.select("title")
      if (!titleNode.empty()) {
        const title = titleNode.text()
        const curve = allCurves.find(c => c.label === title)

        // Check for the invisible interaction layer
        // Plot sets stroke-width as an attribute usually, but let's check style too
        const strokeWidthAttr = path.attr("stroke-width")
        const strokeOpacityAttr = path.attr("stroke-opacity")

        // We identify the interaction layer by its opacity being 0
        if (curve && (strokeOpacityAttr === "0" || path.style("stroke-opacity") === "0")) {
          path.on("mouseenter", () => hoveredCurve.value = curve.id)
          path.on("mouseleave", () => hoveredCurve.value = null)
          path.style("cursor", "pointer")
        }
      }
    })
  })
})
</script>

<template>
  <div class="flex flex-col items-center">
    <div ref="container"></div>
    <div class="mt-4 text-sm text-gray-500">
      Hover over curves to highlight. The dashed line is the <b>Convex Hull</b>.
      <br>
      <span v-if="hoveredCurve" :style="{ color: allCurves.find(c => c.id === hoveredCurve).color, fontWeight: 'bold' }">
        {{ allCurves.find(c => c.id === hoveredCurve).label }}
        {{ ['B', 'D'].includes(hoveredCurve) ? '(Suboptimal)' : '(Optimal on Hull)' }}
      </span>
      <span v-else>&nbsp;</span>
    </div>
  </div>
</template>
