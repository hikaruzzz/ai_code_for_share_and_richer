<template>
  <div class="review-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>历史复盘</span>
          <el-button type="primary" size="small">导出数据</el-button>
        </div>
      </template>

      <el-empty description="复盘功能开发中..." />
    </el-card>
  </div>
</template>

<script setup>
</script>

<style scoped>
.review-page {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>