import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { priceApi, dataSourceApi } from '@/api'
import { ElMessage } from 'element-plus'

export const useGoldStore = defineStore('gold', () => {
  // 数据源状态
  const currentSource = ref('yahoo_finance')
  const sources = ref([])
  const sourceAvailability = ref({})

  // 价格状态
  const goldPrice = ref(null)
  const dxyPrice = ref(null)
  const goldHistory = ref([])
  const dxyHistory = ref([])
  const correlation = ref(null)
  const loading = ref(false)
  const error = ref(null)

  // 计算属性
  const goldChangePercent = computed(() => {
    if (!goldPrice.value?.change_percent) return 0
    return goldPrice.value.change_percent
  })

  const isGoldUp = computed(() => goldChangePercent.value > 0)

  const currentSourceInfo = computed(() => {
    return sources.value.find(s => s.name === currentSource.value) || null
  })

  // 获取数据源列表
  async function fetchSources() {
    try {
      const res = await dataSourceApi.getSources()
      sources.value = res.data?.sources || []
      currentSource.value = res.data?.current_source || 'yahoo_finance'
    } catch (e) {
      console.error('获取数据源列表失败:', e)
    }
  }

  // 切换数据源
  async function switchSource(sourceName) {
    try {
      const res = await dataSourceApi.switchSource(sourceName)
      if (res.data?.success) {
        currentSource.value = sourceName
        // 重新获取数据
        await initialize()
        return true
      } else {
        ElMessage.error(res.data?.error || '切换数据源失败')
        return false
      }
    } catch (e) {
      console.error('切换数据源失败:', e)
      ElMessage.error('切换数据源失败')
      return false
    }
  }

  // 设置API Key
  async function setApiKey(sourceName, apiKey) {
    try {
      const res = await dataSourceApi.setApiKey(sourceName, apiKey)
      if (res.data?.success) {
        return true
      } else {
        ElMessage.error(res.data?.error || '设置API Key失败')
        return false
      }
    } catch (e) {
      console.error('设置API Key失败:', e)
      ElMessage.error('设置API Key失败')
      return false
    }
  }

  // 检查数据源可用性
  async function checkAvailability() {
    try {
      const res = await dataSourceApi.checkAvailability()
      sourceAvailability.value = res.data?.availability || {}
      return sourceAvailability.value
    } catch (e) {
      console.error('检查数据源可用性失败:', e)
      return {}
    }
  }

  // 获取实时价格
  async function fetchRealtimePrices() {
    loading.value = true
    error.value = null

    try {
      const [goldRes, dxyRes] = await Promise.all([
        priceApi.getRealtime('GC=F', currentSource.value),
        priceApi.getRealtime('DX-Y.NYB', currentSource.value)
      ])

      // 处理黄金价格
      if (goldRes.data?.error) {
        ElMessage.warning(`黄金价格: ${goldRes.data.error}`)
        goldPrice.value = null
      } else {
        goldPrice.value = goldRes.data
      }

      // 处理美元指数
      if (dxyRes.data?.error) {
        ElMessage.warning(`美元指数: ${dxyRes.data.error}`)
        dxyPrice.value = null
      } else {
        dxyPrice.value = dxyRes.data
      }

    } catch (e) {
      error.value = e.message
      ElMessage.error('获取价格失败: ' + e.message)
    } finally {
      loading.value = false
    }
  }

  // 获取历史数据
  async function fetchHistoryData(period = '1y') {
    loading.value = true
    error.value = null

    try {
      const [goldRes, dxyRes] = await Promise.all([
        priceApi.getHistory('GC=F', period, '1d', currentSource.value),
        priceApi.getHistory('DX-Y.NYB', period, '1d', currentSource.value)
      ])

      // 处理黄金历史数据
      if (goldRes.data?.error) {
        ElMessage.warning(`黄金历史数据: ${goldRes.data.error}`)
        goldHistory.value = []
      } else {
        goldHistory.value = goldRes.data?.data || []
      }

      // 处理美元指数历史数据
      if (dxyRes.data?.error) {
        ElMessage.warning(`美元指数历史数据: ${dxyRes.data.error}`)
        dxyHistory.value = []
      } else {
        dxyHistory.value = dxyRes.data?.data || []
      }

    } catch (e) {
      error.value = e.message
      ElMessage.error('获取历史数据失败: ' + e.message)
    } finally {
      loading.value = false
    }
  }

  // 获取相关性
  async function fetchCorrelation() {
    try {
      const res = await priceApi.getCorrelation('GC=F', 'DX-Y.NYB', '1y', currentSource.value)
      if (res.data?.error) {
        correlation.value = null
      } else {
        correlation.value = res.data
      }
    } catch (e) {
      console.error('获取相关性失败:', e)
      correlation.value = null
    }
  }

  // 初始化数据
  async function initialize() {
    await fetchSources()
    await Promise.all([
      fetchRealtimePrices(),
      fetchHistoryData(),
      fetchCorrelation()
    ])
  }

  // 刷新数据
  async function refreshData() {
    await Promise.all([
      fetchRealtimePrices(),
      fetchHistoryData(),
      fetchCorrelation()
    ])
  }

  return {
    // 数据源状态
    currentSource,
    sources,
    sourceAvailability,
    currentSourceInfo,
    // 价格状态
    goldPrice,
    dxyPrice,
    goldHistory,
    dxyHistory,
    correlation,
    loading,
    error,
    // 计算属性
    goldChangePercent,
    isGoldUp,
    // 数据源方法
    fetchSources,
    switchSource,
    setApiKey,
    checkAvailability,
    // 价格方法
    fetchRealtimePrices,
    fetchHistoryData,
    fetchCorrelation,
    initialize,
    refreshData
  }
})
