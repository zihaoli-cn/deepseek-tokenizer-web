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

                <!-- Token 数量显示 -->
                <el-alert
                  v-if="tokenCount !== null"
                  :title="`${t('tokenCount')}: ${tokenCount}`"
                  type="info"
                  :closable="false"
                />

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
                    :disabled="!inputText || streaming"
                    style="flex: 1;"
                  >
                    {{ t('countTokens') }}
                  </el-button>
                  <el-button
                    v-if="!streaming"
                    type="success"
                    @click="simulateOutput"
                    :disabled="!inputText"
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
                  <el-tag v-if="streaming" type="success" effect="dark">
                    {{ t('streaming') }}
                  </el-tag>
                  <el-tag v-else-if="outputText" type="info">
                    {{ t('completed') }}
                  </el-tag>
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
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import axios from 'axios'

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

let eventSource = null

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
    ElMessage.success(`${t('tokenCount')}: ${tokenCount.value}`)
  } catch (error) {
    ElMessage.error(`${t('error')}: ${error.message}`)
  } finally {
    counting.value = false
  }
}

// 模拟输出
const simulateOutput = async () => {
  if (!inputText.value) {
    ElMessage.warning(t('inputRequired'))
    return
  }

  if (tokensPerSecond.value <= 0) {
    ElMessage.warning(t('speedRequired'))
    return
  }

  streaming.value = true
  outputText.value = ''
  progress.value = 0
  currentToken.value = 0
  totalTokens.value = 0

  try {
    const response = await fetch('/api/stream_text', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        text: inputText.value,
        tokens_per_second: tokensPerSecond.value
      })
    })

    const reader = response.body.getReader()
    const decoder = new TextDecoder()

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      const chunk = decoder.decode(value)
      const lines = chunk.split('\n')

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = JSON.parse(line.slice(6))
          
          if (data.error) {
            ElMessage.error(`${t('error')}: ${data.error}`)
            streaming.value = false
            break
          }

          if (data.done) {
            streaming.value = false
            ElMessage.success(t('completed'))
            break
          }

          outputText.value = data.text
          currentToken.value = data.current_token
          totalTokens.value = data.total_tokens
          progress.value = data.progress
        }
      }
    }
  } catch (error) {
    ElMessage.error(`${t('error')}: ${error.message}`)
    streaming.value = false
  }
}

// 停止输出
const stopOutput = () => {
  if (eventSource) {
    eventSource.close()
    eventSource = null
  }
  streaming.value = false
  ElMessage.info(t('stopOutput'))
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
</style>
