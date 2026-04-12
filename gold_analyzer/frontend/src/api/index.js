import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000
})

// 价格相关API
export const priceApi = {
  // 获取实时价格
  getRealtime(symbol = 'GC=F', source = null) {
    let url = `/price/realtime?symbol=${symbol}`
    if (source) url += `&source=${source}`
    return api.get(url)
  },

  // 获取历史价格
  getHistory(symbol, period = '1y', interval = '1d', source = null) {
    let url = `/price/history?symbol=${symbol}&period=${period}&interval=${interval}`
    if (source) url += `&source=${source}`
    return api.get(url)
  },

  // 获取K线数据
  getKline(symbol, startDate, endDate, interval = '1d', source = null) {
    let url = `/price/kline?symbol=${symbol}&interval=${interval}`
    if (startDate) url += `&start_date=${startDate}`
    if (endDate) url += `&end_date=${endDate}`
    if (source) url += `&source=${source}`
    return api.get(url)
  },

  // 获取相关性分析
  getCorrelation(symbol1 = 'GC=F', symbol2 = 'DX-Y.NYB', period = '1y', source = null) {
    let url = `/price/correlation?symbol1=${symbol1}&symbol2=${symbol2}&period=${period}`
    if (source) url += `&source=${source}`
    return api.get(url)
  },

  // 同步价格数据
  syncData(symbol, period = '1mo', source = null) {
    let url = `/price/sync?symbol=${symbol}&period=${period}`
    if (source) url += `&source=${source}`
    return api.post(url)
  }
}

// 数据源管理API
export const dataSourceApi = {
  // 获取所有数据源
  getSources() {
    return api.get('/price/sources')
  },

  // 切换数据源
  switchSource(source) {
    return api.post(`/price/sources/switch?source=${source}`)
  },

  // 设置API Key
  setApiKey(source, apiKey) {
    return api.post(`/price/sources/api-key?source=${source}&api_key=${apiKey}`)
  },

  // 检查数据源可用性
  checkAvailability() {
    return api.get('/price/sources/check')
  }
}

// 新闻相关API
export const newsApi = {
  getList(limit = 20) {
    return api.get(`/news?limit=${limit}`)
  },

  getSentiment() {
    return api.get('/news/sentiment')
  }
}

// 分析相关API
export const analysisApi = {
  getIndicators(symbol = 'GC=F') {
    return api.get(`/indicators?symbol=${symbol}`)
  },

  getCurrentSignal(symbol = 'GC=F') {
    return api.get(`/signals/current?symbol=${symbol}`)
  },

  getReport(symbol = 'GC=F') {
    return api.get(`/analysis/report?symbol=${symbol}`)
  }
}

// 复盘相关API
export const reviewApi = {
  getList(limit = 100) {
    return api.get(`/reviews?limit=${limit}`)
  },

  create(data) {
    return api.post('/reviews', data)
  },

  getStats() {
    return api.get('/reviews/stats')
  }
}

export default api
