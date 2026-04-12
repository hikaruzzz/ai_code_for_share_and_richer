<template>
  <div class="kline-chart">
    <div ref="chartRef" class="chart-container"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, onUnmounted } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  title: {
    type: String,
    default: 'K线图'
  },
  data: {
    type: Array,
    default: () => []
  },
  height: {
    type: String,
    default: '500px'
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
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      },
      formatter: function(params) {
        const kline = params[0]
        if (!kline.data) return ''
        const [open, close, low, high] = kline.data
        return `
          <div style="padding: 8px;">
            <div><strong>${kline.axisValue}</strong></div>
            <div>开盘: ${open?.toFixed(2)}</div>
            <div>收盘: ${close?.toFixed(2)}</div>
            <div>最低: ${low?.toFixed(2)}</div>
            <div>最高: ${high?.toFixed(2)}</div>
          </div>
        `
      }
    },
    legend: {
      data: ['K线', 'MA5', 'MA10', 'MA20'],
      top: 30
    },
    grid: {
      left: '3%',
      right: '3%',
      bottom: '15%',
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
        type: 'slider',
        start: 80,
        end: 100
      }
    ],
    series: [
      {
        name: 'K线',
        type: 'candlestick',
        data: [],
        itemStyle: {
          color: '#ef5350',
          color0: '#26a69a',
          borderColor: '#ef5350',
          borderColor0: '#26a69a'
        }
      },
      {
        name: 'MA5',
        type: 'line',
        smooth: true,
        symbol: 'none',
        lineStyle: { width: 1 },
        data: []
      },
      {
        name: 'MA10',
        type: 'line',
        smooth: true,
        symbol: 'none',
        lineStyle: { width: 1 },
        data: []
      },
      {
        name: 'MA20',
        type: 'line',
        smooth: true,
        symbol: 'none',
        lineStyle: { width: 1 },
        data: []
      }
    ]
  }

  chart.setOption(option)
}

// 计算移动平均线
const calculateMA = (data, period) => {
  const result = []
  for (let i = 0; i < data.length; i++) {
    if (i < period - 1) {
      result.push('-')
    } else {
      let sum = 0
      for (let j = 0; j < period; j++) {
        sum += data[i - j]?.close || data[i - j]?.Close || 0
      }
      result.push((sum / period).toFixed(2))
    }
  }
  return result
}

const updateChart = () => {
  if (!chart || !props.data.length) return

  const dates = props.data.map(item => {
    const d = new Date(item.timestamp || item.Date)
    return d.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' })
  })

  // K线数据: [open, close, low, high]
  const klineData = props.data.map(item => [
    item.open || item.Open,
    item.close || item.Close,
    item.low || item.Low,
    item.high || item.High
  ])

  // 计算均线
  const ma5 = calculateMA(props.data, 5)
  const ma10 = calculateMA(props.data, 10)
  const ma20 = calculateMA(props.data, 20)

  chart.setOption({
    xAxis: {
      data: dates
    },
    series: [
      { data: klineData },
      { data: ma5 },
      { data: ma10 },
      { data: ma20 }
    ]
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
.kline-chart {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  padding: 16px;
}

.chart-container {
  height: v-bind(height);
  min-height: 400px;
}
</style>