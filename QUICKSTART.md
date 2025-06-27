# 快速开始指南

## 环境准备

### 1. 安装Neo4j数据库
1. 下载并安装 [Neo4j Desktop](https://neo4j.com/download/) 或 Neo4j Community Edition
2. 创建一个新的数据库项目
3. 启动数据库服务，确保运行在默认端口 7687
4. 设置密码（配置文件中默认为 `12345678`）

### 2. 安装Python依赖
```bash
cd backend
pip install Django neo4j django-cors-headers
```

### 3. 安装Node.js依赖
```bash
cd frontend
npm install
```

## 启动服务

### 方法一：使用启动脚本（Windows）
```bash
# 在项目根目录运行
start_services.bat
```

### 方法二：手动启动

1. 启动后端服务：
```bash
cd backend
python manage.py runserver 8000
```

2. 启动前端服务：
```bash
cd frontend
npm run serve
```


## 访问应用

- 前端界面: http://localhost:8080
- 后端API: http://localhost:8000/api/

## 常见问题

### 1. Neo4j连接失败
- 检查Neo4j服务是否启动
- 验证连接配置（uri, user, password）
- 确保防火墙没有阻止7687端口

### 2. 前端编译错误
- 删除 node_modules 文件夹
- 重新运行 `npm install`
- 检查Node.js版本是否兼容

### 3. 后端服务启动失败
- 检查Python版本（推荐3.8+）
- 确保所有依赖已正确安装
- 检查端口8000是否被占用

### 4. CORS跨域问题
- 确保后端已配置CORS
- 检查前端请求的URL是否正确

## 功能特性

### 节点管理
- ✅ 创建节点（故障类型、原因、解决方案）
- ✅ 查询节点（支持筛选和搜索）
- ✅ 更新节点属性
- ✅ 删除节点（自动删除关联关系）

### 关系管理
- ✅ 创建关系（BECAUSE、DEAL）
- ✅ 查询关系
- ✅ 删除关系

### 图谱预览
- ✅ 显示统计信息
- ✅ 架构说明
- 🔄 可视化图谱（待扩展）

## 下一步

1. **可视化图谱**: 集成D3.js或Cytoscape.js
2. **智能推荐**: 基于图谱的故障诊断推荐
3. **批量操作**: 支持批量导入/导出
4. **权限管理**: 用户权限控制
5. **数据验证**: 增强的数据校验和约束

祝你使用愉快！🚀
