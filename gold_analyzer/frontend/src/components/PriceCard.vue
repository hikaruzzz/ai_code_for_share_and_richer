<template>
  <el-card class="price-card" :body-style="{ padding: '20px' }">
    <div class="price-header">
      <span class="symbol-name">{{ name }}</span>
      <el-tag :type="priceType" size="small">{{ symbol }}</el-tag>
    </div>
    <div class="price-main">
      <span class="price-value">${{ formatPrice(price?.price) }}</span>
      <span class="price-change" :class="changeClass">
        {{ changeText }}
      </span>
    </div>
    <div class="price-details">
      <div class="detail-item">
        <span class="label">开盘</span>
        <span class="value">${{ formatPrice(price?.open) }}</span>
      </div>
      <div class="detail-item">
        <span class="label">最高</span>
        <span class="value">${{ formatPrice(price?.high) }}</span>
      </div>
      <div class="detail-item">
        <span class="label">最低</span>
        <span class="value">${{ formatPrice(price?.low) }}</span>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  symbol: {
    type: String,
    default: 'GC=F'
  },
  name: {
    type: String,
    default: '黄金期货'
  },
  price: {
    type: Object,
    default: () => ({})
  }
})

const priceType = computed(() => {
  if (!props.price?.change_percent) return 'info'
  return props.price.change_percent > 0 ? 'danger' : 'success'
})

const changeClass = computed(() => {
  if (!props.price?.change_percent) return ''
  return props.price.change_percent > 0 ? 'up' : 'down'
})

const changeText = computed(() => {
  if (!props.price) return '-'
  const change = props.price.change || 0
  const percent = props.price.change_percent || 0
  const sign = percent >= 0 ? '+' : ''
  return `${sign}${change.toFixed(2)} (${sign}${percent.toFixed(2)}%)`
})

const formatPrice = (value) => {
  if (!value) return '-'
  return value.toFixed(2)
}
</script>

<style scoped>
.price-card {
  min-width: 200px;
}

.price-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.symbol-name {
  font-size: 14px;
  color: #606266;
}

.price-main {
  display: flex;
  align-items: baseline;
  gap: 12px;
  margin-bottom: 16px;
}

.price-value {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
}

.price-change {
  font-size: 14px;
  font-weight: 500;
}

.price-change.up {
  color: #f56c6c;
}

.price-change.down {
  color: #67c23a;
}

.price-details {
  display: flex;
  gap: 20px;
}

.detail-item {
  display: flex;
  flex-direction: column;
}

.detail-item .label {
  font-size: 12px;
  color: #909399;
}

.detail-item .value {
  font-size: 14px;
  color: #303133;
  font-weight: 500;
}
</style>