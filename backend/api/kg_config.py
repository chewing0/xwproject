"""
Neo4j数据库配置
"""

import os

# Neo4j数据库连接配置
NEO4J_CONFIG = {
    'uri': os.getenv('NEO4J_URI', 'bolt://localhost:7687'),
    'user': os.getenv('NEO4J_USER', 'neo4j'),
    'password': os.getenv('NEO4J_PASSWORD', '12345678')
}

# 验证节点类型
VALID_NODE_LABELS = ['type', 'reason', 'solution']

# 验证关系类型
VALID_RELATIONSHIPS = {
    ('type', 'reason'): 'BECAUSE',
    ('reason', 'solution'): 'DEAL'
}

# 节点属性配置
NODE_SCHEMAS = {
    'type': {
        'required': ['name'],
        'optional': ['description']
    },
    'reason': {
        'required': ['name'],
        'optional': ['description', 'probability']
    },
    'solution': {
        'required': ['name'],
        'optional': ['description', 'steps', 'difficulty']
    }
}
