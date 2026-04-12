<template>
  <div class="dashboard">
    <!-- 顶部工具栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <span class="label">数据源：</span>
        <DataSourceSelector />
        <el-tag
          v-if="currentSourceInfo"
          size="small"
          type="info"
          style="margin-left: 8px"
        >
          {{ currentSourceInfo.description }}
        </el-tag>
      </div>
      <div class="toolbar-right">
        <el-button
          type="primary"
          :loading="loading"
          @click="refreshData"
        >
          <el-icon><Refresh /></el-icon>
          刷新数据
        </el-button>
      </div>
    </div>

    <!-- 价格卡片区域 -->
    <div class="price-cards">
      <PriceCard
        symbol="GC=F"
        name="黄金期货"
        :price="goldPrice"
      />
      <PriceCard
        symbol="DX-Y.NYB"
        name="美元指数"
        :price="dxyPrice"
      />
    </div>

    <!-- 相关性分析 -->
    <el-card class="correlation-card" v-if="correlation">
      <template #header>
        <div class="card-header">
          <span>黄金与美元相关性</span>
        </div>
      </template>
      <div class="correlation-content">
        <div class="correlation-value">
          <span class="value">{{ correlation?.correlation?.toFixed(3) || '-' }}</span>
          <el-tag :type="getCorrelationType">
            {{ correlation?.interpretation || '-' }}
          </el-tag>
        </div>
        <div class="correlation-desc">
          黄金与美元指数通常呈负相关关系（美元强则黄金弱）
        </div>
      </div>
    </el-card>

    <!-- 图表区域 -->
    <div class="charts-container">
      <div class="chart-row">
        <KlineChart
          title="黄金K线图 (GC=F)"
          :data="goldHistory"
          height="450px"
        />
      </div>
      <div class="chart-row">
        <PriceChart
          title="美元指数走势 (DX-Y.NYB)"
          :data="dxyHistory"
          symbol="DX-Y.NYB"
          height="350px"
        />
      </div>
    </div>

    <!-- 加载状态 -->
    <el-overlay v-if="loading">
      <div class="loading-content">
        <el-icon class="is-loading"><Loading /></el-icon>
        <span>加载中...</span>
      </div>
    </el-overlay>
  </div>
</template>

<script setup>
import { onMounted, computed } from 'vue'
import { Loading, Refresh } from '@element-plus/icons-vue'
import { useGoldStore } from '@/stores/gold'
import PriceCard from '@/components/PriceCard.vue'
import KlineChart from '@/components/KlineChart.vue'
import PriceChart from '@/components/PriceChart.vue'
import DataSourceSelector from '@/components/DataSourceSelector.vue'

const store = useGoldStore()

// 从store获取数据
const goldPrice = computed(() => store.goldPrice)
const dxyPrice = computed(() => store.dxyPrice)
const goldHistory = computed(() => store.goldHistory)
const dxyHistory = computed(() => store.dxyHistory)
const correlation = computed(() => store.correlation)
const loading = computed(() => store.loading)
const currentSourceInfo = computed(() => store.currentSourceInfo)

// 相关性标签类型
const getCorrelationType = computed(() => {
  const corr = correlation.value?.correlation
  if (!corr) return 'info'
  if (corr < -0.3) return 'success'  // 负相关（符合预期）
  if (corr > 0.3) return 'warning'   // 正相关（不符合预期）
  return 'info'
})

// 刷新数据
async function refreshData() {
  await store.initialize()
}

onMounted(() => {
  store.initialize()
})
</script>

<style scoped>
.dashboard {
  padding: 0;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 12px 16px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.toolbar-left {
  display: flex;
  align-items: center;
}

.toolbar-left .label {
  font-weight: 500;
  margin-right: 8px;
  color: #606266;
}

.price-cards {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.correlation-card {
  margin-bottom: 20px;
}

.card-header {
  font-weight: 600;
}

.correlation-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.correlation-value {
  display: flex;
  align-items: center;
  gap: 12px;
}

.correlation-value .value {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.correlation-desc {
  color: #909399;
  font-size: 14px;
}

.charts-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.chart-row {
  flex: 1;
}

.loading-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: #409eff;
}
</style>