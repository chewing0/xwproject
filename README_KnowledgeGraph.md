# 知识图谱模块使用说明

## 概述

Module3 是一个知识图谱管理模块，基于 Neo4j 图数据库实现故障诊断知识图谱的增删改查功能。

## 功能特性

### 1. 节点管理
- **节点类型**：
  - `type` (故障类型)：描述各种故障类型
  - `reason` (故障原因)：描述故障产生的原因  
  - `solution` (解决方案)：描述解决故障的方法

- **节点操作**：
  - 创建节点：支持添加新的故障类型、原因或解决方案
  - 查询节点：支持按类型查询和模糊搜索
  - 更新节点：修改节点属性信息
  - 删除节点：删除节点及其关联关系

### 2. 关系管理
- **关系类型**：
  - `BECAUSE`：故障类型 → 故障原因
  - `DEAL`：故障原因 → 解决方案

- **关系操作**：
  - 创建关系：建立节点间的关联关系
  - 查询关系：查看所有关系或特定类型关系
  - 删除关系：移除节点间的关联

### 3. 图谱预览
- 显示图谱统计信息
- 展示图谱架构说明
- 提供可视化预览功能

## 技术架构

### 后端 (Django)
- **API接口**：RESTful API设计
- **数据库**：Neo4j 图数据库
- **核心文件**：
  - `knowledge_graph.py`：Neo4j 客户端和数据操作
  - `views.py`：API视图函数
  - `urls.py`：URL路由配置
  - `kg_config.py`：配置文件

### 前端 (Vue.js)
- **组件化设计**：模块化的Vue组件
- **响应式布局**：适配不同屏幕尺寸
- **交互式操作**：友好的用户界面

## 环境要求

### 后端依赖
```
Django>=4.0.0
neo4j>=5.0.0
django-cors-headers>=3.0.0
```

### 前端依赖
```
vue: ^3.2.13
vue-router: ^4.5.1
axios: ^1.10.0
```

## 安装部署

### 1. 安装 Neo4j 数据库
```bash
# 下载并安装 Neo4j Desktop 或 Community Edition
# 启动 Neo4j 服务，默认端口：7687
```

### 2. 配置数据库连接
修改 `backend/api/kg_config.py` 中的连接参数：
```python
NEO4J_CONFIG = {
    'uri': 'bolt://localhost:7687',
    'user': 'neo4j',
    'password': 'your_password'
}
```

### 3. 安装后端依赖
```bash
cd backend
pip install -r requirements.txt
```

### 4. 安装前端依赖
```bash
cd frontend
npm install
```

### 5. 初始化示例数据
```bash
cd backend/api
python init_sample_data.py
```

## API 接口说明

### 节点操作
- `GET /api/kg/nodes/` - 获取节点列表
- `POST /api/kg/nodes/create/` - 创建节点
- `PUT /api/kg/nodes/update/` - 更新节点
- `DELETE /api/kg/nodes/delete/` - 删除节点

### 关系操作
- `GET /api/kg/relationships/` - 获取关系列表
- `POST /api/kg/relationships/create/` - 创建关系
- `DELETE /api/kg/relationships/delete/` - 删除关系

### 架构信息
- `GET /api/kg/schema/` - 获取知识图谱架构

## 使用示例

### 1. 创建故障类型节点
```json
POST /api/kg/nodes/create/
{
  "label": "type",
  "properties": {
    "name": "网络连接故障",
    "description": "设备无法正常连接到网络"
  }
}
```

### 2. 创建故障原因节点
```json
POST /api/kg/nodes/create/
{
  "label": "reason",
  "properties": {
    "name": "网线断开",
    "description": "物理网线连接断开",
    "probability": 0.3
  }
}
```

### 3. 创建解决方案节点
```json
POST /api/kg/nodes/create/
{
  "label": "solution",
  "properties": {
    "name": "检查网线连接",
    "description": "检查并重新连接网线",
    "difficulty": "easy"
  }
}
```

### 4. 创建关系
```json
POST /api/kg/relationships/create/
{
  "from_label": "type",
  "from_properties": {"name": "网络连接故障"},
  "to_label": "reason",
  "to_properties": {"name": "网线断开"},
  "rel_type": "BECAUSE"
}
```

## 注意事项

1. **数据库连接**：确保 Neo4j 服务正常运行
2. **数据验证**：系统会验证节点类型和关系类型的有效性
3. **级联删除**：删除节点时会同时删除相关关系
4. **错误处理**：API 包含完整的错误处理和响应

## 扩展功能

### 可以扩展的功能：
1. **可视化图谱**：集成 D3.js 或 Cytoscape.js 进行图谱可视化
2. **智能推荐**：基于图谱结构进行故障诊断推荐
3. **批量操作**：支持批量导入/导出节点和关系
4. **权限管理**：添加用户权限和访问控制
5. **版本控制**：支持知识图谱的版本管理和回滚

## 故障排除

### 常见问题：
1. **连接失败**：检查 Neo4j 服务状态和连接配置
2. **创建失败**：验证数据格式和必填字段
3. **查询为空**：检查数据库中是否有相应数据
4. **跨域问题**：确保后端配置了 CORS 支持

## 联系支持

如有问题或建议，请联系开发团队。
