<template>  <div class="module">
    <div class="module-header">
      <h1>知识图谱管理</h1>
      <div class="connection-status" :class="connectionStatus.class">
        <span class="status-dot"></span>
        {{ connectionStatus.text }}
      </div>
    </div>
    
    <!-- 操作选项卡 -->
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

    <!-- 节点管理 -->
    <div v-if="activeTab === 'nodes'" class="content">
      <div class="operations-panel">
        <h3>节点操作</h3>
        
        <!-- 搜索区域 -->
        <div class="search-section">
          <div class="form-group">
            <label>节点类型:</label>
            <select v-model="nodeFilter.label">
              <option value="">全部</option>
              <option value="type">故障类型</option>
              <option value="reason">故障原因</option>
              <option value="solution">解决方案</option>
            </select>
          </div>
          <div class="form-group">
            <label>搜索字段:</label>
            <input v-model="nodeFilter.searchField" placeholder="如: name">
          </div>
          <div class="form-group">
            <label>搜索值:</label>
            <input v-model="nodeFilter.searchValue" placeholder="搜索内容">
          </div>
          <button @click="loadNodes" class="btn btn-primary">搜索节点</button>
        </div>

        <!-- 创建节点区域 -->
        <div class="create-section">
          <h4>创建新节点</h4>
          <div class="form-group">
            <label>节点类型:</label>
            <select v-model="newNode.label" required>
              <option value="">请选择</option>
              <option value="type">故障类型</option>
              <option value="reason">故障原因</option>
              <option value="solution">解决方案</option>
            </select>
          </div>
          <div class="form-group">
            <label>名称:</label>
            <input v-model="newNode.properties.name" required placeholder="节点名称">
          </div>
          <div class="form-group">
            <label>描述:</label>
            <textarea v-model="newNode.properties.description" placeholder="节点描述"></textarea>
          </div>
          <div v-if="newNode.label === 'reason'" class="form-group">
            <label>概率:</label>
            <input v-model="newNode.properties.probability" type="number" step="0.1" min="0" max="1" placeholder="0.0-1.0">
          </div>
          <div v-if="newNode.label === 'solution'" class="form-group">
            <label>难度:</label>
            <select v-model="newNode.properties.difficulty">
              <option value="">请选择</option>
              <option value="easy">简单</option>
              <option value="medium">中等</option>
              <option value="hard">困难</option>
            </select>
          </div>
          <button @click="createNode" :disabled="!newNode.label || !newNode.properties.name" class="btn btn-success">创建节点</button>
        </div>
      </div>

      <!-- 节点列表 -->
      <div class="nodes-list">
        <h4>节点列表 ({{ nodes.length }} 个)</h4>
        <div v-if="loading" class="loading">加载中...</div>
        <div v-else-if="nodes.length === 0" class="no-data">暂无数据</div>
        <div v-else class="node-cards">
          <div v-for="(node, index) in nodes" :key="index" class="node-card">
            <div class="node-header">
              <span class="node-type" :class="getNodeTypeClass(node.n)">{{ getNodeTypeLabel(node.n) }}</span>
              <div class="node-actions">
                <button @click="editNode(node.n)" class="btn btn-sm btn-warning">编辑</button>
                <button @click="deleteNode(node.n)" class="btn btn-sm btn-danger">删除</button>
              </div>
            </div>
            <div class="node-content">
              <h5>{{ node.n.name }}</h5>
              <p v-if="node.n.description">{{ node.n.description }}</p>
              <div v-if="node.n.probability" class="node-meta">概率: {{ node.n.probability }}</div>
              <div v-if="node.n.difficulty" class="node-meta">难度: {{ node.n.difficulty }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 关系管理 -->
    <div v-if="activeTab === 'relationships'" class="content">
      <div class="operations-panel">
        <h3>关系操作</h3>
        
        <!-- 创建关系区域 -->
        <div class="create-section">
          <h4>创建新关系</h4>
          <div class="form-group">
            <label>关系类型:</label>
            <select v-model="newRelationship.type" @change="onRelationshipTypeChange">
              <option value="">请选择</option>
              <option value="BECAUSE">故障类型 → 故障原因</option>
              <option value="DEAL">故障原因 → 解决方案</option>
            </select>
          </div>
          
          <div v-if="newRelationship.type" class="relationship-nodes">
            <div class="form-group">
              <label>起始节点 ({{ newRelationship.fromLabel }}):</label>
              <select v-model="newRelationship.fromNode">
                <option value="">请选择</option>
                <option v-for="node in getNodesForLabel(newRelationship.fromLabel)" :key="node.id" :value="node">
                  {{ node.name }}
                </option>
              </select>
            </div>
            
            <div class="form-group">
              <label>目标节点 ({{ newRelationship.toLabel }}):</label>
              <select v-model="newRelationship.toNode">
                <option value="">请选择</option>
                <option v-for="node in getNodesForLabel(newRelationship.toLabel)" :key="node.id" :value="node">
                  {{ node.name }}
                </option>
              </select>
            </div>
          </div>
          
          <button @click="createRelationship" 
                  :disabled="!newRelationship.fromNode || !newRelationship.toNode" 
                  class="btn btn-success">创建关系</button>
        </div>
      </div>

      <!-- 关系列表 -->
      <div class="relationships-list">
        <h4>关系列表 ({{ relationships.length }} 个)</h4>
        <button @click="loadRelationships" class="btn btn-primary">刷新关系</button>
        
        <div v-if="loading" class="loading">加载中...</div>
        <div v-else-if="relationships.length === 0" class="no-data">暂无数据</div>
        <div v-else class="relationship-cards">
          <div v-for="(rel, index) in relationships" :key="index" class="relationship-card">
            <div class="relationship-flow">
              <div class="relationship-node start">
                <span class="node-type" :class="getNodeTypeClass(rel.a)">{{ getNodeTypeLabel(rel.a) }}</span>
                <span class="node-name">{{ rel.a.name }}</span>
              </div>
              <div class="relationship-arrow">
                <span class="arrow">→</span>
                <span class="relationship-type">{{ rel.r.type || 'UNKNOWN' }}</span>
              </div>
              <div class="relationship-node end">
                <span class="node-type" :class="getNodeTypeClass(rel.b)">{{ getNodeTypeLabel(rel.b) }}</span>
                <span class="node-name">{{ rel.b.name }}</span>
              </div>
              <div class="relationship-actions">
                <button @click="deleteRelationship(rel)" class="btn btn-sm btn-danger">删除</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 图谱预览 -->
    <div v-if="activeTab === 'preview'" class="content">
      <h3>知识图谱预览</h3>
      <div class="graph-preview">
        <p>这里可以展示知识图谱的可视化内容</p>
        <p>节点总数: {{ totalNodes }}</p>
        <p>关系总数: {{ totalRelationships }}</p>
        
        <div class="schema-info">
          <h4>图谱架构</h4>
          <div class="schema-section">
            <h5>节点类型</h5>
            <ul>
              <li><strong>type (故障类型)</strong>: 描述各种故障类型</li>
              <li><strong>reason (故障原因)</strong>: 描述故障产生的原因</li>
              <li><strong>solution (解决方案)</strong>: 描述解决故障的方法</li>
            </ul>
          </div>
          <div class="schema-section">
            <h5>关系类型</h5>
            <ul>
              <li><strong>BECAUSE</strong>: 故障类型 → 故障原因</li>
              <li><strong>DEAL</strong>: 故障原因 → 解决方案</li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <!-- 编辑节点模态框 -->
    <div v-if="editingNode" class="modal-overlay" @click="closeEditModal">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>编辑节点</h3>
          <button @click="closeEditModal" class="btn btn-sm btn-secondary">×</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>名称:</label>
            <input v-model="editingNode.name" required>
          </div>
          <div class="form-group">
            <label>描述:</label>
            <textarea v-model="editingNode.description"></textarea>
          </div>
          <div v-if="editingNode.probability !== undefined" class="form-group">
            <label>概率:</label>
            <input v-model="editingNode.probability" type="number" step="0.1" min="0" max="1">
          </div>
          <div v-if="editingNode.difficulty !== undefined" class="form-group">
            <label>难度:</label>
            <select v-model="editingNode.difficulty">
              <option value="">请选择</option>
              <option value="easy">简单</option>
              <option value="medium">中等</option>
              <option value="hard">困难</option>
            </select>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="updateNode" class="btn btn-primary">保存</button>
          <button @click="closeEditModal" class="btn btn-secondary">取消</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'ModuleThreeView',  data() {
    return {
      activeTab: 'nodes',
      loading: false,
      nodes: [],
      relationships: [],
      
      // 连接状态
      connectionStatus: {
        text: '未连接',
        class: 'disconnected'
      },
      
      // 搜索和过滤
      nodeFilter: {
        label: '',
        searchField: '',
        searchValue: ''
      },
      
      // 新建节点
      newNode: {
        label: '',
        properties: {
          name: '',
          description: '',
          probability: '',
          difficulty: ''
        }
      },
      
      // 新建关系
      newRelationship: {
        type: '',
        fromLabel: '',
        toLabel: '',
        fromNode: null,
        toNode: null
      },
      
      // 编辑节点
      editingNode: null,
      originalEditingNode: null,
      
      // 选项卡配置
      tabs: [
        { key: 'nodes', label: '节点管理' },
        { key: 'relationships', label: '关系管理' },
        { key: 'preview', label: '图谱预览' }
      ]
    }
  },
  
  computed: {
    totalNodes() {
      return this.nodes.length
    },
    
    totalRelationships() {
      return this.relationships.length
    }
  },
    mounted() {
    this.checkConnection()
    this.loadNodes()
    this.loadRelationships()
  },
    methods: {
    // 检查连接状态
    async checkConnection() {
      try {
        const response = await this.apiCall('kg/schema/')
        if (response.success) {
          this.connectionStatus = {
            text: '已连接',
            class: 'connected'
          }
        } else {
          this.connectionStatus = {
            text: '连接异常',
            class: 'error'
          }
        }
      } catch (error) {
        this.connectionStatus = {
          text: '连接失败',
          class: 'disconnected'
        }
      }
    },
    
    // API调用基础方法
    async apiCall(url, method = 'GET', data = null) {
      try {
        const config = {
          method,
          url: `http://localhost:8000/api/${url}`,
          headers: {
            'Content-Type': 'application/json',
          }
        }
        
        if (data) {
          config.data = JSON.stringify(data)
        }
        
        const response = await axios(config)
        return response.data
      } catch (error) {
        console.error('API Error:', error)
        this.showError(error.response?.data?.error || '请求失败')
        throw error
      }
    },
    
    // 加载节点
    async loadNodes() {
      this.loading = true
      try {
        let url = 'kg/nodes/'
        const params = new URLSearchParams()
        
        if (this.nodeFilter.label) {
          params.append('label', this.nodeFilter.label)
        }
        if (this.nodeFilter.searchField && this.nodeFilter.searchValue) {
          params.append('search_field', this.nodeFilter.searchField)
          params.append('search_value', this.nodeFilter.searchValue)
        }
        
        if (params.toString()) {
          url += '?' + params.toString()
        }
        
        const response = await this.apiCall(url)
        if (response.success) {
          this.nodes = response.data
        }
      } catch (error) {
        console.error('Failed to load nodes:', error)
      } finally {
        this.loading = false
      }
    },
    
    // 加载关系
    async loadRelationships() {
      this.loading = true
      try {
        const response = await this.apiCall('kg/relationships/')
        if (response.success) {
          this.relationships = response.data
        }
      } catch (error) {
        console.error('Failed to load relationships:', error)
      } finally {
        this.loading = false
      }
    },
    
    // 创建节点
    async createNode() {
      if (!this.newNode.label || !this.newNode.properties.name) {
        this.showError('请填写必要信息')
        return
      }
      
      try {
        // 清理空值
        const properties = {}
        Object.keys(this.newNode.properties).forEach(key => {
          if (this.newNode.properties[key] !== '') {
            properties[key] = this.newNode.properties[key]
          }
        })
        
        const response = await this.apiCall('kg/nodes/create/', 'POST', {
          label: this.newNode.label,
          properties
        })
        
        if (response.success) {
          this.showSuccess('节点创建成功')
          this.resetNewNode()
          this.loadNodes()
        }
      } catch (error) {
        console.error('Failed to create node:', error)
      }
    },
    
    // 编辑节点
    editNode(node) {
      this.editingNode = { ...node }
      this.originalEditingNode = { ...node }
    },
    
    // 更新节点
    async updateNode() {
      if (!this.editingNode.name) {
        this.showError('节点名称不能为空')
        return
      }
      
      try {
        // 获取节点标签
        const nodeLabel = this.getNodeLabel(this.editingNode)
        
        // 清理空值
        const updateProperties = {}
        Object.keys(this.editingNode).forEach(key => {
          if (this.editingNode[key] !== '' && this.editingNode[key] !== null) {
            updateProperties[key] = this.editingNode[key]
          }
        })
        
        const response = await this.apiCall('kg/nodes/update/', 'PUT', {
          label: nodeLabel,
          match_properties: { name: this.originalEditingNode.name },
          update_properties: updateProperties
        })
        
        if (response.success) {
          this.showSuccess('节点更新成功')
          this.closeEditModal()
          this.loadNodes()
        }
      } catch (error) {
        console.error('Failed to update node:', error)
      }
    },
    
    // 删除节点
    async deleteNode(node) {
      if (!confirm(`确定要删除节点 "${node.name}" 吗？`)) {
        return
      }
      
      try {
        const nodeLabel = this.getNodeLabel(node)
        const response = await this.apiCall('kg/nodes/delete/', 'DELETE', {
          label: nodeLabel,
          properties: { name: node.name }
        })
        
        if (response.success) {
          this.showSuccess('节点删除成功')
          this.loadNodes()
          this.loadRelationships() // 重新加载关系，因为可能有关联关系被删除
        }
      } catch (error) {
        console.error('Failed to delete node:', error)
      }
    },
    
    // 创建关系
    async createRelationship() {
      if (!this.newRelationship.fromNode || !this.newRelationship.toNode) {
        this.showError('请选择起始节点和目标节点')
        return
      }
      
      try {
        const response = await this.apiCall('kg/relationships/create/', 'POST', {
          from_label: this.newRelationship.fromLabel,
          from_properties: { name: this.newRelationship.fromNode.name },
          to_label: this.newRelationship.toLabel,
          to_properties: { name: this.newRelationship.toNode.name },
          rel_type: this.newRelationship.type,
          rel_properties: {}
        })
        
        if (response.success) {
          this.showSuccess('关系创建成功')
          this.resetNewRelationship()
          this.loadRelationships()
        }
      } catch (error) {
        console.error('Failed to create relationship:', error)
      }
    },
    
    // 删除关系
    async deleteRelationship(relationship) {
      if (!confirm('确定要删除这个关系吗？')) {
        return
      }
      
      try {
        const fromLabel = this.getNodeLabel(relationship.a)
        const toLabel = this.getNodeLabel(relationship.b)
        
        const response = await this.apiCall('kg/relationships/delete/', 'DELETE', {
          from_label: fromLabel,
          from_properties: { name: relationship.a.name },
          to_label: toLabel,
          to_properties: { name: relationship.b.name },
          rel_type: relationship.r.type || 'UNKNOWN'
        })
        
        if (response.success) {
          this.showSuccess('关系删除成功')
          this.loadRelationships()
        }
      } catch (error) {
        console.error('Failed to delete relationship:', error)
      }
    },
    
    // 工具方法
    resetNewNode() {
      this.newNode = {
        label: '',
        properties: {
          name: '',
          description: '',
          probability: '',
          difficulty: ''
        }
      }
    },
    
    resetNewRelationship() {
      this.newRelationship = {
        type: '',
        fromLabel: '',
        toLabel: '',
        fromNode: null,
        toNode: null
      }
    },
    
    closeEditModal() {
      this.editingNode = null
      this.originalEditingNode = null
    },
    
    onRelationshipTypeChange() {
      const typeMap = {
        'BECAUSE': { from: 'type', to: 'reason' },
        'DEAL': { from: 'reason', to: 'solution' }
      }
      
      if (this.newRelationship.type && typeMap[this.newRelationship.type]) {
        this.newRelationship.fromLabel = typeMap[this.newRelationship.type].from
        this.newRelationship.toLabel = typeMap[this.newRelationship.type].to
        this.newRelationship.fromNode = null
        this.newRelationship.toNode = null
      }
    },
    
    getNodesForLabel(label) {
      return this.nodes
        .filter(node => this.getNodeLabel(node.n) === label)
        .map(node => node.n)
    },    getNodeLabel(node) {
      // 从节点的node_labels属性获取标签
      if (node.node_labels && node.node_labels.length > 0) {
        return node.node_labels[0]
      }
      
      // 从节点的__labels__属性或其他方式推断标签
      if (node.__labels__ && node.__labels__.length > 0) {
        return node.__labels__[0]
      }
      
      // 根据节点属性推断
      if (node.probability !== undefined) return 'reason'
      if (node.difficulty !== undefined) return 'solution'
      
      // 如果无法推断，检查节点的其他特征
      if (Object.prototype.hasOwnProperty.call(node, 'probability')) return 'reason'
      if (Object.prototype.hasOwnProperty.call(node, 'difficulty')) return 'solution'
      
      return 'type' // 默认为故障类型
    },
    
    getNodeTypeClass(node) {
      const label = this.getNodeLabel(node)
      return `node-type-${label}`
    },
    
    getNodeTypeLabel(node) {
      const label = this.getNodeLabel(node)
      const labelMap = {
        'type': '故障类型',
        'reason': '故障原因',
        'solution': '解决方案'
      }
      return labelMap[label] || '未知'
    },
    
    showSuccess(message) {
      // 这里可以集成一个通知组件
      alert('成功: ' + message)
    },
    
    showError(message) {
      // 这里可以集成一个通知组件
      alert('错误: ' + message)
    }
  }
}
</script>

<style scoped>
.module {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

/* 模块头部 */
.module-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.module-header h1 {
  margin: 0;
  color: #495057;
}

/* 连接状态 */
.connection-status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 600;
}

.connection-status.connected {
  background-color: #d4edda;
  color: #155724;
}

.connection-status.disconnected {
  background-color: #f8d7da;
  color: #721c24;
}

.connection-status.error {
  background-color: #fff3cd;
  color: #856404;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: currentColor;
}

/* 选项卡样式 */
.tabs {
  display: flex;
  border-bottom: 2px solid #e1e5e9;
  margin-bottom: 2rem;
}

.tab-button {
  padding: 0.75rem 1.5rem;
  border: none;
  background: none;
  cursor: pointer;
  font-size: 1rem;
  color: #6c757d;
  border-bottom: 2px solid transparent;
  transition: all 0.3s ease;
}

.tab-button:hover {
  color: #007bff;
  background-color: #f8f9fa;
}

.tab-button.active {
  color: #007bff;
  border-bottom-color: #007bff;
  font-weight: 600;
}

/* 内容区域 */
.content {
  margin-top: 2rem;
}

/* 操作面板 */
.operations-panel {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.operations-panel h3 {
  margin: 0 0 1.5rem 0;
  color: #495057;
}

.operations-panel h4 {
  margin: 2rem 0 1rem 0;
  color: #6c757d;
  border-top: 1px solid #dee2e6;
  padding-top: 1rem;
}

.operations-panel h4:first-child {
  margin-top: 0;
  border-top: none;
  padding-top: 0;
}

/* 搜索区域 */
.search-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  align-items: end;
  margin-bottom: 1rem;
}

/* 创建区域 */
.create-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
  align-items: end;
}

/* 表单组件 */
.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #495057;
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 0.5rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 0.9rem;
  transition: border-color 0.3s ease;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
}

.form-group textarea {
  resize: vertical;
  min-height: 80px;
}

/* 按钮样式 */
.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: none;
  display: inline-block;
  text-align: center;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background-color: #007bff;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #0056b3;
}

.btn-success {
  background-color: #28a745;
  color: white;
}

.btn-success:hover:not(:disabled) {
  background-color: #1e7e34;
}

.btn-warning {
  background-color: #ffc107;
  color: #212529;
}

.btn-warning:hover:not(:disabled) {
  background-color: #e0a800;
}

.btn-danger {
  background-color: #dc3545;
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background-color: #c82333;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #545b62;
}

.btn-sm {
  padding: 0.25rem 0.5rem;
  font-size: 0.8rem;
}

/* 节点列表 */
.nodes-list h4,
.relationships-list h4 {
  color: #495057;
  margin-bottom: 1rem;
}

.loading,
.no-data {
  text-align: center;
  padding: 2rem;
  color: #6c757d;
  font-style: italic;
}

/* 节点卡片 */
.node-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
}

.node-card {
  border: 1px solid #dee2e6;
  border-radius: 8px;
  overflow: hidden;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.node-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.node-header {
  background: #f8f9fa;
  padding: 0.75rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #dee2e6;
}

.node-type {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
}

.node-type-type {
  background-color: #e3f2fd;
  color: #1976d2;
}

.node-type-reason {
  background-color: #fff3e0;
  color: #f57c00;
}

.node-type-solution {
  background-color: #e8f5e8;
  color: #388e3c;
}

.node-actions {
  display: flex;
  gap: 0.5rem;
}

.node-content {
  padding: 1rem;
}

.node-content h5 {
  margin: 0 0 0.5rem 0;
  color: #495057;
}

.node-content p {
  margin: 0.5rem 0;
  color: #6c757d;
  font-size: 0.9rem;
}

.node-meta {
  font-size: 0.8rem;
  color: #6c757d;
  margin-top: 0.5rem;
}

/* 关系列表 */
.relationship-cards {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.relationship-card {
  border: 1px solid #dee2e6;
  border-radius: 8px;
  padding: 1rem;
  background: white;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.relationship-card:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.relationship-flow {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.relationship-node {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 120px;
}

.relationship-node .node-name {
  font-weight: 600;
  color: #495057;
  margin-top: 0.25rem;
  text-align: center;
}

.relationship-arrow {
  display: flex;
  flex-direction: column;
  align-items: center;
  color: #6c757d;
}

.relationship-arrow .arrow {
  font-size: 1.5rem;
  color: #007bff;
}

.relationship-arrow .relationship-type {
  font-size: 0.8rem;
  font-weight: 600;
  margin-top: 0.25rem;
}

.relationship-actions {
  margin-left: auto;
}

/* 关系节点选择 */
.relationship-nodes {
  grid-column: 1 / -1;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

/* 图谱预览 */
.graph-preview {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 2rem;
  text-align: center;
}

.schema-info {
  margin-top: 2rem;
  text-align: left;
}

.schema-section {
  margin-bottom: 1.5rem;
}

.schema-section h5 {
  color: #495057;
  margin-bottom: 0.5rem;
}

.schema-section ul {
  list-style-type: none;
  padding: 0;
}

.schema-section li {
  padding: 0.5rem;
  background: white;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  margin-bottom: 0.5rem;
}

/* 模态框 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #dee2e6;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
  color: #495057;
}

.modal-body {
  padding: 1.5rem;
}

.modal-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid #dee2e6;
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .module {
    padding: 1rem;
  }
  
  .module-header {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }
  
  .search-section,
  .create-section {
    grid-template-columns: 1fr;
  }
  
  .relationship-nodes {
    grid-template-columns: 1fr;
  }
  
  .relationship-flow {
    flex-direction: column;
    text-align: center;
  }
  
  .relationship-arrow .arrow {
    transform: rotate(90deg);
  }
  
  .node-cards {
    grid-template-columns: 1fr;
  }
}
</style>