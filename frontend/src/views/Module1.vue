<template>
  <div class="module">
    <h1>日志分析系统</h1>
    
    <!-- 功能选项卡 -->
    <div class="tabs">
      <button 
        v-for="tab in tabs" 
        :key="tab.key"
        :class="['tab-button', { active: activeTab === tab.key }]"
        @click="activeTab = tab.key"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- 信令流程分析 -->
    <div v-if="activeTab === 'protocol'" class="content">
      <h2>信令流程分析</h2>
      <div class="upload-section">
        <input type="file" @change="handleFileUpload" accept=".txt" ref="fileInput" />
        <button @click="analyzeProtocol" :disabled="!selectedFile || loading">分析日志</button>
      </div>

      <div v-if="loading" class="loading">
        分析中...
      </div>

      <div v-if="error" class="error">
        {{ error }}
      </div>

      <div v-if="analysisResult" class="analysis-result">
        <!-- ...existing analysis result code... -->
        <h3>分析结果</h3>
        
        <!-- 摘要信息 -->
        <div class="summary-section">
          <h4>摘要</h4>
          <div class="summary-grid">
            <div class="summary-item">
              <span class="label">总流程数:</span>
              <span class="value">{{ analysisResult.report.summary.total_flows }}</span>
            </div>
            <div class="summary-item">
              <span class="label">已完成:</span>
              <span class="value">{{ analysisResult.report.summary.completed }}</span>
            </div>
            <div class="summary-item">
              <span class="label">进行中:</span>
              <span class="value">{{ analysisResult.report.summary.in_progress }}</span>
            </div>
            <div class="summary-item">
              <span class="label">未开始:</span>
              <span class="value">{{ analysisResult.report.summary.not_started }}</span>
            </div>
          </div>
        </div>

        <!-- 第一个错误信息 -->
        <div class="error-section" v-if="analysisResult.first_error.status !== 'all_flows_completed'">
          <h4>第一个错误</h4>
          <div class="error-details">
            <p><strong>阻塞流程:</strong> {{ analysisResult.first_error.blocking_flow }}</p>
            <p><strong>状态:</strong> {{ analysisResult.first_error.status }}</p>
            <div v-if="analysisResult.first_error.status_details">
              <p v-for="(value, key) in analysisResult.first_error.status_details" :key="key">
                <strong>{{ formatKey(key) }}:</strong> {{ formatValue(value) }}
              </p>
            </div>
          </div>
        </div>

        <!-- 进行中的流程 -->
        <div class="in-progress-section" v-if="analysisResult.report.in_progress_flows.length > 0">
          <h4>进行中的流程</h4>
          <div v-for="flow in analysisResult.report.in_progress_flows" :key="flow.flow_name" class="flow-item">
            <h5>{{ flow.flow_name }}</h5>
            <p>进度: {{ flow.completed_steps }}/{{ flow.total_steps }}</p>
            <div v-if="flow.missing_steps.length > 0">
              <p>缺失步骤:</p>
              <ul>
                <li v-for="(step, index) in flow.missing_steps" :key="index">
                  {{ step.msg }} ({{ step.protocol }}, {{ step.dir }})
                </li>
              </ul>
            </div>
          </div>
        </div>

        <!-- 问题流程 -->
        <div class="problematic-section" v-if="analysisResult.report.problematic_flows.length > 0">
          <h4>问题流程</h4>
          <div v-for="flow in analysisResult.report.problematic_flows" :key="flow.flow_name" class="flow-item">
            <h5>{{ flow.flow_name }}</h5>
            <p>问题: {{ flow.issue }}</p>
            <p>预期第一步: {{ flow.missing_initial_step.msg }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 异常检测 -->
    <div v-if="activeTab === 'anomaly'" class="content">
      <h2>异常检测</h2>
      <div class="anomaly-detection">
        <div class="detection-type">
          <label>检测类型:</label>
          <select v-model="detectionType">
            <option value="comparison">与正常日志对比</option>
            <option value="fault_identify">故障类型识别</option>
          </select>
        </div>

        <!-- 对比检测 -->
        <div v-if="detectionType === 'comparison'" class="comparison-detection">
          <div class="file-upload-group">
            <div class="upload-item">
              <label>正常日志文件:</label>
              <input type="file" @change="handleNormalFileUpload" accept=".txt" />
              <span v-if="normalFile" class="file-name">{{ normalFile.name }}</span>
            </div>
            <div class="upload-item">
              <label>待检测日志文件:</label>
              <input type="file" @change="handleTestFileUpload" accept=".txt" />
              <span v-if="testFile" class="file-name">{{ testFile.name }}</span>
            </div>
          </div>
          <button @click="detectAnomaly" :disabled="!normalFile || !testFile || loading" class="btn btn-primary">
            开始异常检测
          </button>
        </div>

        <!-- 故障识别 -->
        <div v-if="detectionType === 'fault_identify'" class="fault-identification">
          <div class="upload-item">
            <label>待检测日志文件:</label>
            <input type="file" @change="handleTestFileUpload" accept=".txt" />
            <span v-if="testFile" class="file-name">{{ testFile.name }}</span>
          </div>
          <button @click="identifyFault" :disabled="!testFile || loading" class="btn btn-primary">
            识别故障类型
          </button>
        </div>

        <!-- 检测结果 -->
        <div v-if="detectionResult" class="detection-result">
          <h3>检测结果</h3>
          <div v-if="detectionResult.type === 'anomaly'" class="anomaly-result">
            <div class="result-item">
              <span class="label">相似度:</span>
              <span class="value">{{ detectionResult.similarity.toFixed(4) }}</span>
            </div>
            <div class="result-item">
              <span class="label">阈值:</span>
              <span class="value">{{ detectionResult.threshold }}</span>
            </div>
            <div class="result-status" :class="detectionResult.is_anomaly ? 'anomaly' : 'normal'">
              {{ detectionResult.is_anomaly ? '🚨 检测到异常' : '✅ 日志正常' }}
            </div>
            <p class="result-description">{{ detectionResult.description }}</p>
          </div>

          <div v-if="detectionResult.type === 'fault'" class="fault-result">
            <div class="result-item">
              <span class="label">预测故障类型:</span>
              <span class="value fault-type">{{ detectionResult.predicted_fault }}</span>
            </div>
            <div class="result-item">
              <span class="label">置信度:</span>
              <span class="value">{{ detectionResult.confidence.toFixed(4) }}</span>
            </div>
            <div v-if="detectionResult.top_matches" class="top-matches">
              <h4>相似度排名:</h4>
              <div v-for="(match, index) in detectionResult.top_matches" :key="index" class="match-item">
                <span class="rank">{{ index + 1 }}.</span>
                <span class="fault-name">{{ match.fault_type }}</span>
                <span class="similarity">({{ match.similarity.toFixed(4) }})</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 故障库管理 -->
    <div v-if="activeTab === 'faultdb'" class="content">
      <h2>故障库管理</h2>
      <div class="fault-database">
        <!-- 添加故障记录 -->
        <div class="add-fault-section">
          <h3>添加故障记录</h3>
          <div class="upload-item">
            <label>故障日志文件:</label>
            <input type="file" @change="handleFaultFileUpload" accept=".txt" />
            <span v-if="faultFile" class="file-name">{{ faultFile.name }}</span>
          </div>
          <div class="form-group">
            <label>故障类型:</label>
            <input v-model="faultType" placeholder="例如: 连接超时, 内存溢出, 配置错误" />
          </div>
          <button @click="addFaultRecord" :disabled="!faultFile || !faultType || loading" class="btn btn-success">
            添加到故障库
          </button>
        </div>

        <!-- 故障库信息 -->
        <div class="fault-info-section">
          <h3>故障库信息</h3>
          <div class="info-grid">
            <div class="info-item">
              <span class="label">记录总数:</span>
              <span class="value">{{ faultDbInfo.total_records }}</span>
            </div>
            <div class="info-item">
              <span class="label">故障类型数:</span>
              <span class="value">{{ faultDbInfo.fault_types.length }}</span>
            </div>
          </div>
          <button @click="loadFaultDbInfo" class="btn btn-secondary">刷新信息</button>
        </div>

        <!-- 故障类型列表 -->
        <div v-if="faultDbInfo.fault_types.length > 0" class="fault-types-section">
          <h3>故障类型列表</h3>
          <div class="fault-types-list">
            <div v-for="(type, index) in faultDbInfo.fault_types" :key="index" class="fault-type-item">
              <span class="type-name">{{ type.name }}</span>
              <span class="type-count">{{ type.count }} 条记录</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-spinner">
        <div class="spinner"></div>
        <p>{{ loadingMessage }}</p>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'ModuleOneView',
  data() {
    return {
      // 选项卡管理
      activeTab: 'protocol',
      tabs: [
        { key: 'protocol', label: '信令流程分析' },
        { key: 'anomaly', label: '异常检测' },
        { key: 'faultdb', label: '故障库管理' }
      ],
      
      // 原有的数据
      selectedFile: null,
      loading: false,
      error: null,
      analysisResult: null,
      loadingMessage: '处理中...',
      
      // 异常检测相关
      detectionType: 'comparison',
      normalFile: null,
      testFile: null,
      detectionResult: null,
      
      // 故障库管理相关
      faultFile: null,
      faultType: '',
      faultDbInfo: {
        total_records: 0,
        fault_types: []
      }
    }
  },
  
  mounted() {
    this.loadFaultDbInfo()
  },
  
  methods: {
    // 原有方法
    handleFileUpload(event) {
      this.selectedFile = event.target.files[0]
      this.error = null
      this.analysisResult = null
    },
    
    async analyzeProtocol() {
      if (!this.selectedFile) {
        this.error = '请先选择文件'
        return
      }

      this.loading = true
      this.error = null
      this.analysisResult = null
      this.loadingMessage = '分析信令流程中...'

      try {
        const fileContent = await this.readFile(this.selectedFile)
        const response = await axios.post('http://localhost:8000/api/analyze-protocol/', {
          log_content: fileContent
        })
        this.analysisResult = response.data
      } catch (error) {
        console.error('Error:', error)
        this.error = error.response?.data?.error || '分析失败'
      } finally {
        this.loading = false
      }
    },
    
    // 文件处理方法
    handleNormalFileUpload(event) {
      this.normalFile = event.target.files[0]
      this.error = null
      this.detectionResult = null
    },
    
    handleTestFileUpload(event) {
      this.testFile = event.target.files[0]
      this.error = null
      this.detectionResult = null
    },
    
    handleFaultFileUpload(event) {
      this.faultFile = event.target.files[0]
      this.error = null
    },
    
    // 异常检测方法
    async detectAnomaly() {
      if (!this.normalFile || !this.testFile) {
        this.error = '请先选择正常日志和待检测日志文件'
        return
      }

      this.loading = true
      this.error = null
      this.detectionResult = null
      this.loadingMessage = '进行异常检测...'

      try {
        const normalContent = await this.readFile(this.normalFile)
        const testContent = await this.readFile(this.testFile)
        
        const response = await axios.post('http://localhost:8000/api/anomaly-detection/', {
          normal_log: normalContent,
          test_log: testContent
        })
        
        this.detectionResult = {
          type: 'anomaly',
          ...response.data
        }
      } catch (error) {
        console.error('Error:', error)
        this.error = error.response?.data?.error || '异常检测失败'
      } finally {
        this.loading = false
      }
    },
    
    // 故障类型识别
    async identifyFault() {
      if (!this.testFile) {
        this.error = '请先选择待检测日志文件'
        return
      }

      this.loading = true
      this.error = null
      this.detectionResult = null
      this.loadingMessage = '识别故障类型...'

      try {
        const testContent = await this.readFile(this.testFile)
        
        const response = await axios.post('http://localhost:8000/api/fault-identification/', {
          log_content: testContent
        })
        
        this.detectionResult = {
          type: 'fault',
          ...response.data
        }
      } catch (error) {
        console.error('Error:', error)
        this.error = error.response?.data?.error || '故障识别失败'
      } finally {
        this.loading = false
      }
    },
    
    // 添加故障记录
    async addFaultRecord() {
      if (!this.faultFile || !this.faultType.trim()) {
        this.error = '请选择故障日志文件并输入故障类型'
        return
      }

      this.loading = true
      this.error = null
      this.loadingMessage = '添加故障记录...'

      try {
        const faultContent = await this.readFile(this.faultFile)
        
        const response = await axios.post('http://localhost:8000/api/add-fault-record/', {
          log_content: faultContent,
          fault_type: this.faultType.trim()
        })
        
        if (response.data.success) {
          this.showSuccess('故障记录添加成功')
          this.faultFile = null
          this.faultType = ''
          this.loadFaultDbInfo() // 刷新故障库信息
        } else {
          this.error = response.data.error || '添加失败'
        }
      } catch (error) {
        console.error('Error:', error)
        this.error = error.response?.data?.error || '添加故障记录失败'
      } finally {
        this.loading = false
      }
    },
    
    // 加载故障库信息
    async loadFaultDbInfo() {
      try {
        const response = await axios.get('http://localhost:8000/api/fault-database-info/')
        this.faultDbInfo = response.data
      } catch (error) {
        console.error('加载故障库信息失败:', error)
        // 不显示错误，因为这是后台操作
      }
    },
    
    // 工具方法
    readFile(file) {
      return new Promise((resolve, reject) => {
        const reader = new FileReader()
        reader.onload = (e) => resolve(e.target.result)
        reader.onerror = (e) => reject(e)
        reader.readAsText(file)
      })
    },
    
    formatKey(key) {
      return key.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')
    },
    
    formatValue(value) {
      if (Array.isArray(value)) {
        return value.join(', ')
      }
      return value
    },
    
    showSuccess(message) {
      // 简单的成功提示，可以后续集成更好的通知组件
      alert('成功: ' + message)
    }
  }
}
</script>

<style scoped>
.module {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  background-color: #f8f9fa;
  min-height: 100vh;
}

h1 {
  color: #2c3e50;
  text-align: center;
  margin-bottom: 2rem;
  font-size: 2.5rem;
  font-weight: 700;
}

/* 选项卡样式 */
.tabs {
  display: flex;
  justify-content: center;
  background-color: #ffffff;
  border-radius: 12px;
  padding: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
}

.tab-button {
  padding: 12px 24px;
  margin: 0 4px;
  background-color: transparent;
  color: #6c757d;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
}

.tab-button.active {
  background-color: #007bff;
  color: white;
  box-shadow: 0 2px 8px rgba(0, 123, 255, 0.3);
}

.tab-button:hover:not(.active) {
  background-color: #e9ecef;
  color: #495057;
}

/* 内容区域 */
.content {
  background-color: #ffffff;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  margin-top: 2rem;
}

.content h2 {
  color: #2c3e50;
  margin-bottom: 1.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #e9ecef;
}

/* 上传区域样式 */
.upload-section {
  margin-bottom: 2rem;
  display: flex;
  gap: 1rem;
  align-items: center;
  flex-wrap: wrap;
}

.upload-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.upload-item label {
  font-weight: 600;
  color: #495057;
  margin-bottom: 0.5rem;
}

.file-upload-group {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  margin-bottom: 1.5rem;
}

.file-name {
  color: #28a745;
  font-size: 0.9rem;
  font-style: italic;
}

input[type="file"] {
  padding: 8px 12px;
  border: 2px dashed #dee2e6;
  border-radius: 8px;
  background-color: #f8f9fa;
  cursor: pointer;
  transition: border-color 0.3s ease;
}

input[type="file"]:hover {
  border-color: #007bff;
}

input[type="text"], select {
  padding: 12px 16px;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.3s ease;
}

input[type="text"]:focus, select:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
}

/* 按钮样式 */
.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  font-size: 1rem;
  transition: all 0.3s ease;
  margin: 0.25rem;
}

.btn-primary {
  background-color: #007bff;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #0056b3;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 123, 255, 0.3);
}

.btn-success {
  background-color: #28a745;
  color: white;
}

.btn-success:hover:not(:disabled) {
  background-color: #1e7e34;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(40, 167, 69, 0.3);
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #545b62;
}

.btn:disabled {
  background-color: #e9ecef;
  color: #6c757d;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* 检测类型选择 */
.detection-type {
  margin-bottom: 2rem;
  padding: 1rem;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.detection-type label {
  font-weight: 600;
  margin-right: 1rem;
  color: #495057;
}

.detection-type select {
  min-width: 200px;
}

/* 结果显示区域 */
.detection-result, .analysis-result {
  margin-top: 2rem;
  padding: 1.5rem;
  background-color: #f8f9fa;
  border-radius: 12px;
  border: 1px solid #e9ecef;
}

.detection-result h3, .analysis-result h3 {
  color: #2c3e50;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #dee2e6;
}

.result-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  margin: 0.5rem 0;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.result-status {
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 600;
  text-align: center;
  margin: 1rem 0;
}

.result-status.normal {
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.result-status.anomaly {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.result-description {
  padding: 1rem;
  background-color: white;
  border-radius: 8px;
  border-left: 4px solid #007bff;
  margin-top: 1rem;
}

.fault-type {
  color: #dc3545;
  font-weight: 600;
}

/* 匹配结果 */
.top-matches {
  margin-top: 1rem;
}

.top-matches h4 {
  color: #495057;
  margin-bottom: 0.75rem;
}

.match-item {
  display: flex;
  align-items: center;
  padding: 0.5rem 1rem;
  margin: 0.25rem 0;
  background-color: white;
  border-radius: 6px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.rank {
  font-weight: 600;
  color: #007bff;
  margin-right: 0.75rem;
  min-width: 20px;
}

.fault-name {
  flex: 1;
  color: #495057;
}

.similarity {
  color: #6c757d;
  font-size: 0.9rem;
}

/* 故障库管理 */
.fault-database {
  display: grid;
  gap: 2rem;
}

.add-fault-section, .fault-info-section, .fault-types-section {
  padding: 1.5rem;
  background-color: #f8f9fa;
  border-radius: 12px;
  border: 1px solid #e9ecef;
}

.add-fault-section h3, .fault-info-section h3, .fault-types-section h3 {
  color: #2c3e50;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #dee2e6;
}

.form-group {
  margin: 1rem 0;
}

.form-group label {
  display: block;
  font-weight: 600;
  color: #495057;
  margin-bottom: 0.5rem;
}

.form-group input {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #dee2e6;
  border-radius: 8px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin: 1rem 0;
}

.info-item {
  background-color: white;
  padding: 1rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  text-align: center;
}

.info-item .label {
  display: block;
  font-weight: 600;
  color: #6c757d;
  margin-bottom: 0.5rem;
}

.info-item .value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #007bff;
}

.fault-types-list {
  display: grid;
  gap: 0.5rem;
}

.fault-type-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.type-name {
  font-weight: 600;
  color: #495057;
}

.type-count {
  color: #6c757d;
  font-size: 0.9rem;
}

/* 加载状态 */
.loading {
  text-align: center;
  padding: 2rem;
  color: #666;
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.loading-spinner {
  background-color: white;
  padding: 2rem;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 错误提示 */
.error {
  color: #721c24;
  padding: 1rem 1.5rem;
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
  border-radius: 8px;
  margin: 1rem 0;
  border-left: 4px solid #dc3545;
}

/* 流程分析结果样式 */
.summary-section {
  background-color: #f8f9fa;
  padding: 1.5rem;
  border-radius: 12px;
  margin-bottom: 2rem;
  border: 1px solid #e9ecef;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.summary-item {
  background-color: white;
  padding: 1rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  text-align: center;
}

.summary-item .label {
  display: block;
  font-weight: 600;
  color: #6c757d;
  margin-bottom: 0.5rem;
}

.summary-item .value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #007bff;
}

.error-section, .in-progress-section, .problematic-section {
  margin-top: 2rem;
  padding: 1.5rem;
  background-color: #f8f9fa;
  border-radius: 12px;
  border: 1px solid #e9ecef;
}

.flow-item {
  background-color: white;
  padding: 1rem;
  margin: 1rem 0;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.flow-item h5 {
  margin: 0 0 0.5rem 0;
  color: #2c3e50;
  font-weight: 600;
}

.error-details {
  background-color: white;
  padding: 1rem;
  border-radius: 8px;
  margin-top: 1rem;
  border-left: 4px solid #dc3545;
}

ul {
  margin: 0.5rem 0;
  padding-left: 1.5rem;
}

li {
  margin: 0.25rem 0;
  color: #495057;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .module {
    padding: 1rem;
  }
  
  .file-upload-group {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .tabs {
    flex-direction: column;
  }
  
  .tab-button {
    margin: 2px 0;
  }
  
  .summary-grid, .info-grid {
    grid-template-columns: 1fr;
  }
}
</style> 