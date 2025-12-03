<template>
  <div id="app">
    <el-container style="height: 100vh;">
      <!-- 头部 -->
      <el-header style="background-color: #409EFF; color: white; display: flex; align-items: center; justify-content: space-between;">
        <h2 style="margin: 0;">{{ t('title') }}</h2>
        <el-select v-model="locale" style="width: 150px;" @change="changeLocale">
          <el-option label="中文" value="zh-CN"></el-option>
          <el-option label="English" value="en-US"></el-option>
        </el-select>
      </el-header>

      <!-- 主体内容 -->
      <el-main style="padding: 20px;">
        <el-row :gutter="20" style="height: 100%;">
          <!-- 左侧输入区 -->
          <el-col :span="12" style="height: 100%;">
            <el-card style="height: 100%; display: flex; flex-direction: column;">
              <template #header>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                  <span>{{ t('inputArea') }}</span>
                </div>
              </template>
              
              <div style="flex: 1; display: flex; flex-direction: column; gap: 15px;">
                <!-- 输入文本框 -->
                <el-input
                  v-model="inputText"
                  type="textarea"
                  :placeholder="t('inputPlaceholder')"
                  :rows="15"
                  style="flex: 1;"
                />

                <!-- Token 数量显示（折叠框） -->
                <el-collapse v-model="activeCollapse" style="margin-top: 10px;" v-if="tokenCount !== null">
                  <el-collapse-item name="token-details">
                    <template #title>
                      <!-- 折叠框标题：显示统计信息 -->
                      <div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">
                        <span>{{ t('tokenCount') }}: {{ tokenCount }}</span>
                        <el-tag v-if="tokenStatistics.words" size="small" type="info">
                          {{ tokenStatistics.words }} {{ t('words') }}
                        </el-tag>
                        <el-tag v-if="tokenStatistics.punctuation" size="small" type="success">
                          {{ tokenStatistics.punctuation }} {{ t('punctuation') }}
                        </el-tag>
                        <el-tag v-if="tokenStatistics.special_tokens" size="small" type="warning">
                          {{ tokenStatistics.special_tokens }} {{ t('specialTokens') }}
                        </el-tag>
                        <el-tag v-if="tokenStatistics.spaces" size="small" type="">
                          {{ tokenStatistics.spaces }} {{ t('spaces') }}
                        </el-tag>
                      </div>
                    </template>

                    <!-- 分词结果显示区域 -->
                    <div class="token-display-container">
                      <!-- 功能按钮 -->
                      <div class="token-actions">
                        <el-button size="small" @click="copyTokens" :icon="CopyDocument">
                          {{ t('copyTokens') }}
                        </el-button>
                        <el-button size="small" @click="exportTokens" :icon="Download">
                          {{ t('exportTokens') }}
                        </el-button>
                        <div style="flex: 1;"></div>
                        <span style="font-size: 12px; color: #909399;">
                          {{ t('totalTokens') }}: {{ tokenCount }}
                        </span>
                      </div>

                      <!-- 虚拟滚动容器 -->
                      <div class="virtual-scroll-container" ref="scrollContainer" @scroll="handleScroll">
                        <div class="virtual-scroll-content" :style="{ height: `${tokenDetails.length * virtualScrollOptions.itemSize}px` }">
                          <div
                            v-for="index in visibleTokenIndices"
                            :key="index"
                            class="token-item"
                            :class="tokenDetails[index].type"
                            :style="{ top: `${index * virtualScrollOptions.itemSize}px` }"
                          >
                            <span class="token-index">#{{ index + 1 }}</span>
                            <span class="token-string">{{ tokenDetails[index].string }}</span>
                            <span class="token-id">ID: {{ tokenDetails[index].id }}</span>
                          </div>
                        </div>
                      </div>

                      <!-- 加载更多提示（长文本时） -->
                      <div v-if="tokenDetails.length > virtualScrollOptions.visibleItems" class="load-more">
                        <span style="font-size: 12px; color: #909399;">
                          {{ t('showingTokens', { visible: Math.min(virtualScrollOptions.visibleItems, tokenDetails.length), total: tokenDetails.length }) }}
                        </span>
                      </div>
                    </div>
                  </el-collapse-item>
                </el-collapse>

                <!-- 输出速度设置 -->
                <div style="display: flex; align-items: center; gap: 10px;">
                  <span style="white-space: nowrap;">{{ t('tokensPerSecond') }}:</span>
                  <el-input-number
                    v-model="tokensPerSecond"
                    :min="1"
                    :max="1000"
                    :step="10"
                    style="flex: 1;"
                  />
                </div>

                <!-- 操作按钮 -->
                <div style="display: flex; gap: 10px;">
                  <el-button
                    type="primary"
                    @click="countTokens"
                    :loading="counting"
                    :disabled="!inputText || streaming || isRequestPending"
                    style="flex: 1;"
                  >
                    {{ t('countTokens') }}
                  </el-button>
                  <el-button
                    v-if="!streaming"
                    type="success"
                    @click="simulateOutput"
                    :disabled="!inputText || isRequestPending || streamingState === 'streaming'"
                    style="flex: 1;"
                  >
                    {{ t('simulateOutput') }}
                  </el-button>
                  <el-button
                    v-else
                    type="danger"
                    @click="stopOutput"
                    style="flex: 1;"
                  >
                    {{ t('stopOutput') }}
                  </el-button>
                </div>
              </div>
            </el-card>
          </el-col>

          <!-- 右侧输出区 -->
          <el-col :span="12" style="height: 100%;">
            <el-card style="height: 100%; display: flex; flex-direction: column;">
              <template #header>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                  <span>{{ t('outputArea') }}</span>
                  <div style="display: flex; gap: 8px; align-items: center;">
                    <!-- 状态标签 -->
                    <el-tag v-if="streamingState === 'starting'" type="warning" effect="dark">
                      {{ t('starting') || '准备中...' }}
                    </el-tag>
                    <el-tag v-else-if="streamingState === 'streaming'" type="success" effect="dark">
                      {{ t('streaming') }}
                    </el-tag>
                    <el-tag v-else-if="streamingState === 'stopping'" type="info" effect="dark">
                      {{ t('stopping') || '停止中...' }}
                    </el-tag>
                    <el-tag v-else-if="streamingState === 'error'" type="danger" effect="dark">
                      {{ t('error') }}
                    </el-tag>
                    <el-tag v-else-if="outputText && streamingState === 'idle'" type="info">
                      {{ t('completed') }}
                    </el-tag>

                    <!-- 请求锁状态提示 -->
                    <el-tag v-if="isRequestPending" type="warning" size="small">
                      {{ t('requestPending') || '请求中...' }}
                    </el-tag>
                  </div>
                </div>
              </template>

              <div style="flex: 1; display: flex; flex-direction: column; gap: 15px;">
                <!-- 输出文本框 -->
                <el-input
                  v-model="outputText"
                  type="textarea"
                  :placeholder="t('outputPlaceholder')"
                  :rows="15"
                  readonly
                  style="flex: 1;"
                />

                <!-- 进度信息 -->
                <div v-if="streaming || progress > 0" style="display: flex; flex-direction: column; gap: 10px;">
                  <el-progress
                    :percentage="Math.round(progress)"
                    :status="streaming ? 'success' : 'success'"
                  />
                  <div style="display: flex; justify-content: space-between; font-size: 14px; color: #606266;">
                    <span>{{ t('currentToken') }}: {{ currentToken }}</span>
                    <span>{{ t('totalTokens') }}: {{ totalTokens }}</span>
                    <span>{{ t('progress') }}: {{ Math.round(progress) }}%</span>
                  </div>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import { CopyDocument, Download } from '@element-plus/icons-vue'

const { t, locale } = useI18n()

// 数据
const inputText = ref('')
const outputText = ref('')
const tokenCount = ref(null)
const tokensPerSecond = ref(50)
const counting = ref(false)
const streaming = ref(false)
const progress = ref(0)
const currentToken = ref(0)
const totalTokens = ref(0)

// 新增：分词详情相关数据
const tokenDetails = ref([])  // 存储分词详情
const tokenStatistics = ref({})  // 存储统计信息
const activeCollapse = ref([])  // 控制折叠框状态
const virtualScrollOptions = ref({
  itemSize: 40,  // 每个token项的高度(px)
  visibleItems: 20,  // 可见区域显示的数量
})
const scrollTop = ref(0)
const scrollContainer = ref(null)

let eventSource = null

// 防重复点击相关状态
const streamingController = ref(null) // AbortController实例
const isRequestPending = ref(false)   // 请求锁，防止重复点击
const streamingState = ref('idle')    // 状态机：'idle' | 'starting' | 'streaming' | 'stopping' | 'error'

// 计算可见的token索引（虚拟滚动）
const visibleTokenIndices = computed(() => {
  if (!tokenDetails.value.length) return []

  const startIndex = Math.floor(scrollTop.value / virtualScrollOptions.value.itemSize)
  const endIndex = Math.min(
    startIndex + virtualScrollOptions.value.visibleItems,
    tokenDetails.value.length
  )

  return Array.from({ length: endIndex - startIndex }, (_, i) => startIndex + i)
})

// 切换语言
const changeLocale = (value) => {
  locale.value = value
}

// 计算 Token 数量
const countTokens = async () => {
  if (!inputText.value) {
    ElMessage.warning(t('inputRequired'))
    return
  }

  counting.value = true
  try {
    const response = await axios.post('/api/count_tokens', {
      text: inputText.value
    })
    tokenCount.value = response.data.token_count
    tokenDetails.value = response.data.token_details || []
    tokenStatistics.value = response.data.statistics || {}

    // 默认展开折叠框
    if (tokenDetails.value.length > 0) {
      activeCollapse.value = ['token-details']
    }

    ElMessage.success(`${t('tokenCount')}: ${tokenCount.value}`)
  } catch (error) {
    ElMessage.error(`${t('error')}: ${error.message}`)
  } finally {
    counting.value = false
  }
}

// JSON字符串清理方法
const cleanJsonString = (str) => {
  // 移除控制字符
  let cleaned = str.replace(/[\u0000-\u001F\u007F-\u009F]/g, '')

  // 修复常见的JSON格式问题
  // 1. 修复未转义的双引号
  cleaned = cleaned.replace(/([^\\])"/g, '$1\\"')

  // 2. 修复未转义的反斜杠
  cleaned = cleaned.replace(/\\([^"\\/bfnrtu])/g, '\\\\$1')

  // 3. 修复未闭合的字符串
  // 如果字符串以未转义的双引号开始但没有结束，添加结束引号
  if ((cleaned.match(/"/g) || []).length % 2 === 1) {
    cleaned += '"'
  }

  return cleaned
}

// 模拟输出（防重复点击版本）
const simulateOutput = async () => {
  // 1. 防重复检查：检查请求锁和当前状态
  if (isRequestPending.value || streamingState.value === 'streaming') {
    ElMessage.warning(t('requestInProgress') || '请求正在进行中，请稍候')
    return
  }

  // 2. 验证输入
  if (!inputText.value) {
    ElMessage.warning(t('inputRequired'))
    return
  }

  if (tokensPerSecond.value <= 0) {
    ElMessage.warning(t('speedRequired'))
    return
  }

  // 3. 设置状态锁和状态机
  isRequestPending.value = true
  streamingState.value = 'starting'
  streaming.value = true

  // 4. 重置输出状态
  outputText.value = ''
  progress.value = 0
  currentToken.value = 0
  totalTokens.value = 0

  // 5. 创建 AbortController 用于取消请求
  const controller = new AbortController()
  streamingController.value = controller

  // 6. 设置请求超时（30秒）
  let timeoutId = null
  if (typeof setTimeout !== 'undefined') {
    timeoutId = setTimeout(() => {
      if (controller && !controller.signal.aborted) {
        controller.abort()
        ElMessage.warning(t('requestTimeout') || '请求超时，请重试')
      }
    }, 30000) // 30秒超时
  }

  try {
    // 7. 发起请求（传递 signal 以支持取消）
    const response = await fetch('/api/stream_text', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        text: inputText.value,
        tokens_per_second: tokensPerSecond.value
      }),
      signal: controller.signal
    })

    // 8. 检查响应状态
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    // 9. 更新状态：请求已发出，开始流式处理
    isRequestPending.value = false
    streamingState.value = 'streaming'

    // 10. 处理流数据
    const reader = response.body.getReader()
    const decoder = new TextDecoder()

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      const chunk = decoder.decode(value)
      const lines = chunk.split('\n')

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const jsonStr = line.slice(6)

          // 调试：记录JSON字符串信息
          console.debug('原始JSON字符串:', jsonStr)
          console.debug('JSON字符串长度:', jsonStr.length)

          try {
            const data = JSON.parse(jsonStr)

            if (data.error) {
              ElMessage.error(`${t('error')}: ${data.error}`)
              streamingState.value = 'error'
              streaming.value = false
              break
            }

            if (data.done) {
              streamingState.value = 'idle'
              streaming.value = false
              ElMessage.success(t('completed'))
              break
            }

            outputText.value = data.text
            currentToken.value = data.current_token
            totalTokens.value = data.total_tokens
            progress.value = data.progress
          } catch (error) {
            console.error('JSON解析错误:', error.message)
            console.error('错误详情:', error)
            console.error('有问题的JSON字符串:', JSON.stringify(jsonStr))

            // 显示第529个字符附近的上下文
            const start = Math.max(0, 528 - 20)
            const end = Math.min(jsonStr.length, 528 + 20)
            console.error('错误位置上下文:', jsonStr.substring(start, end))
            console.error('第529个字符:', jsonStr.charAt(528))

            // 尝试清理JSON字符串
            const cleanedJson = cleanJsonString(jsonStr)
            console.debug('清理后的JSON:', cleanedJson)

            try {
              const data = JSON.parse(cleanedJson)

              if (data.error) {
                ElMessage.error(`${t('error')}: ${data.error}`)
                streamingState.value = 'error'
                streaming.value = false
                break
              }

              if (data.done) {
                streamingState.value = 'idle'
                streaming.value = false
                ElMessage.success(t('completed'))
                break
              }

              outputText.value = data.text
              currentToken.value = data.current_token
              totalTokens.value = data.total_tokens
              progress.value = data.progress
            } catch (e) {
              console.error('清理后仍然解析失败:', e)
              // 跳过这条数据，继续处理其他SSE事件
              // 不中断整个流程，只记录错误
            }
          }
        }
      }
    }
  } catch (error) {
    // 11. 错误处理
    if (error.name === 'AbortError') {
      // 请求被取消（用户点击停止或超时）
      ElMessage.info(t('requestCancelled') || '请求已取消')
      streamingState.value = 'stopping'
    } else {
      // 其他错误
      ElMessage.error(`${t('error')}: ${error.message}`)
      streamingState.value = 'error'
    }
    streaming.value = false
  } finally {
    // 12. 清理资源
    if (timeoutId) {
      clearTimeout(timeoutId)
    }
    isRequestPending.value = false

    // 如果当前不是流式状态，则重置为idle
    if (streamingState.value !== 'streaming') {
      streamingState.value = 'idle'
    }

    streamingController.value = null
  }
}

// 停止输出（使用AbortController取消请求）
const stopOutput = () => {
  // 1. 使用AbortController取消正在进行的请求
  if (streamingController.value) {
    streamingState.value = 'stopping'
    streamingController.value.abort()
    streamingController.value = null
  }

  // 2. 清理旧的eventSource（兼容旧代码）
  if (eventSource) {
    eventSource.close()
    eventSource = null
  }

  // 3. 更新状态
  streaming.value = false
  streamingState.value = 'idle'
  isRequestPending.value = false

  // 4. 显示提示
  ElMessage.info(t('stopOutput'))
}

// 处理滚动事件（虚拟滚动）
const handleScroll = () => {
  if (scrollContainer.value) {
    scrollTop.value = scrollContainer.value.scrollTop
  }
}

// 复制分词结果
const copyTokens = async () => {
  try {
    // 复制所有token字符串（用空格连接）
    const tokenStrings = tokenDetails.value.map(t => t.string).join(' ')
    await navigator.clipboard.writeText(tokenStrings)
    ElMessage.success(t('copySuccess'))
  } catch (error) {
    console.error('复制失败:', error)
    ElMessage.error(t('copyError'))
  }
}

// 导出分词结果
const exportTokens = () => {
  try {
    const exportData = {
      text: inputText.value,
      timestamp: new Date().toISOString(),
      token_count: tokenCount.value,
      statistics: tokenStatistics.value,
      tokens: tokenDetails.value
    }

    const jsonStr = JSON.stringify(exportData, null, 2)
    const blob = new Blob([jsonStr], { type: 'application/json' })
    const url = URL.createObjectURL(blob)

    const a = document.createElement('a')
    a.href = url
    a.download = `tokenizer_analysis_${Date.now()}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)

    ElMessage.success(t('exportSuccess'))
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error(t('exportError'))
  }
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

#app {
  width: 100%;
  height: 100vh;
}

.el-textarea__inner {
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.6;
}

/* 分词详情显示样式 */
.token-display-container {
  padding: 16px;
  background: #f9f9f9;
  border-radius: 8px;
}

.token-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid #ebeef5;
}

/* 虚拟滚动容器 */
.virtual-scroll-container {
  height: 400px; /* 固定高度 */
  overflow-y: auto;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  background: white;
  position: relative;
}

.virtual-scroll-content {
  position: relative;
}

/* Token项样式 */
.token-item {
  position: absolute;
  left: 0;
  right: 0;
  height: 36px;
  display: flex;
  align-items: center;
  padding: 0 12px;
  border-bottom: 1px solid #f0f0f0;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 13px;
  transition: background-color 0.2s;
}

.token-item:hover {
  background-color: #f5f7fa !important;
}

.token-index {
  min-width: 40px;
  color: #909399;
  font-size: 11px;
  font-weight: 600;
}

.token-string {
  flex: 1;
  margin: 0 12px;
  padding: 2px 6px;
  border-radius: 3px;
  background: rgba(64, 158, 255, 0.1);
  border: 1px solid rgba(64, 158, 255, 0.2);
}

.token-id {
  min-width: 60px;
  color: #67c23a;
  font-size: 11px;
  text-align: right;
}

/* Token类型样式 */
.token-item.word .token-string {
  background: rgba(64, 158, 255, 0.1);
  border-color: rgba(64, 158, 255, 0.2);
  color: #409eff;
}

.token-item.punctuation .token-string {
  background: rgba(103, 194, 58, 0.1);
  border-color: rgba(103, 194, 58, 0.2);
  color: #67c23a;
}

.token-item.special .token-string {
  background: rgba(230, 162, 60, 0.1);
  border-color: rgba(230, 162, 60, 0.2);
  color: #e6a23c;
}

.token-item.space .token-string {
  background: rgba(144, 147, 153, 0.1);
  border-color: rgba(144, 147, 153, 0.2);
  color: #909399;
}

.load-more {
  text-align: center;
  padding: 8px;
  margin-top: 8px;
  font-size: 12px;
  color: #909399;
  border-top: 1px solid #ebeef5;
}
</style>
