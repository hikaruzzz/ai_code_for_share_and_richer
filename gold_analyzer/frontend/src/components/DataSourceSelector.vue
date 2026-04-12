<template>
  <div class="data-source-selector">
    <el-select
      v-model="selectedSource"
      placeholder="选择数据源"
      @change="handleChange"
      :loading="loading"
    >
      <el-option
        v-for="source in sources"
        :key="source.name"
        :label="source.description"
        :value="source.name"
        :disabled="source.requires_api_key && !source.has_api_key"
      >
        <div class="source-option">
          <span>{{ source.description }}</span>
          <el-tag
            v-if="source.is_current"
            type="success"
            size="small"
            style="margin-left: 8px"
          >
            当前
          </el-tag>
          <el-tag
            v-if="source.requires_api_key && !source.has_api_key"
            type="warning"
            size="small"
            style="margin-left: 8px"
          >
            需要API Key
          </el-tag>
        </div>
      </el-option>
    </el-select>

    <!-- API Key输入框 -->
    <el-dialog
      v-model="showApiKeyDialog"
      title="设置API Key"
      width="400px"
    >
      <el-form>
        <el-form-item label="数据源">
          <span>{{ selectedSourceForApiKey?.description }}</span>
        </el-form-item>
        <el-form-item label="API Key">
          <el-input
            v-model="apiKeyInput"
            placeholder="请输入API Key"
            type="password"
            show-password
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showApiKeyDialog = false">取消</el-button>
        <el-button type="primary" @click="submitApiKey">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useGoldStore } from '@/stores/gold'
import { ElMessage } from 'element-plus'

const store = useGoldStore()

const selectedSource = ref('')
const loading = ref(false)
const showApiKeyDialog = ref(false)
const apiKeyInput = ref('')
const selectedSourceForApiKey = ref(null)

const sources = computed(() => store.sources)
const currentSource = computed(() => store.currentSource)

// 初始化选中数据源
onMounted(() => {
  selectedSource.value = currentSource.value
})

watch(currentSource, (newVal) => {
  selectedSource.value = newVal
})

// 处理数据源切换
async function handleChange(sourceName) {
  const source = sources.value.find(s => s.name === sourceName)

  if (source?.requires_api_key && !source.has_api_key) {
    // 需要API Key
    selectedSourceForApiKey.value = source
    showApiKeyDialog.value = true
    return
  }

  loading.value = true
  const success = await store.switchSource(sourceName)

  if (success) {
    ElMessage.success(`已切换到: ${source?.description}`)
  } else {
    ElMessage.error('切换数据源失败')
    selectedSource.value = currentSource.value
  }
  loading.value = false
}

// 提交API Key
async function submitApiKey() {
  if (!apiKeyInput.value) {
    ElMessage.warning('请输入API Key')
    return
  }

  const success = await store.setApiKey(
    selectedSourceForApiKey.value.name,
    apiKeyInput.value
  )

  if (success) {
    ElMessage.success('API Key设置成功')
    showApiKeyDialog.value = false
    apiKeyInput.value = ''

    // 尝试切换到该数据源
    await handleChange(selectedSourceForApiKey.value.name)
  } else {
    ElMessage.error('API Key设置失败')
  }
}
</script>

<style scoped>
.data-source-selector {
  display: inline-block;
}

.source-option {
  display: flex;
  align-items: center;
}
</style>