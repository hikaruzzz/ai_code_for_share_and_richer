<template>
  <div class="price-chart">
    <div ref="chartRef" class="chart-container"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, onUnmounted } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  title: {
    type: String,
    default: '价格走势'
  },
  data: {
    type: Array,
    default: () => []
  },
  symbol: {
    type: String,
    default: 'GC=F'
  },
  height: {
    type: String,
    default: '400px'
  }
})

const chartRef = ref(null)
let chart = null

const initChart = () => {
  if (!chartRef.value) return

  chart = echarts.init(chartRef.value)

  const option = {
    title: {
      text: props.title,
      left: 'center',
      textStyle: {
        fontSize: 16,
        fontWeight: 'normal'
      }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      },
      formatter: (params) => {
        const data = params[0]
        return `
          <div style="padding: 8px;">
            <div><strong>${data.axisValue}</strong></div>
            <div>收盘价: $${data.value?.toFixed(2) || '-'}</div>
          </div>
        `
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: [],
      axisLabel: {
        rotate: 45
      }
    },
    yAxis: {
      type: 'value',
      scale: true,
      splitLine: {
        lineStyle: {
          type: 'dashed'
        }
      }
    },
    dataZoom: [
      {
        type: 'inside',
        start: 80,
        end: 100
      },
      {
        start: 80,
        end: 100
      }
    ],
    series: [
      {
        name: '收盘价',
        type: 'line',
        smooth: true,
        symbol: 'none',
        lineStyle: {
          width: 2
        },
        areaStyle: {
          opacity: 0.1
        },
        data: []
      }
    ]
  }

  chart.setOption(option)
}

const updateChart = () => {
  if (!chart || !props.data.length) return

  const dates = props.data.map(item => {
    const d = new Date(item.timestamp || item.Date)
    return d.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' })
  })
  const values = props.data.map(item => item.close || item.Close)

  chart.setOption({
    xAxis: {
      data: dates
    },
    series: [{
      data: values
    }]
  })
}

const resizeChart = () => {
  chart?.resize()
}

onMounted(() => {
  initChart()
  updateChart()
  window.addEventListener('resize', resizeChart)
})

onUnmounted(() => {
  window.removeEventListener('resize', resizeChart)
  chart?.dispose()
})

watch(() => props.data, updateChart, { deep: true })
</script>

<style scoped>
.price-chart {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  padding: 16px;
}

.chart-container {
  height: v-bind(height);
  min-height: 300px;
}
</style>