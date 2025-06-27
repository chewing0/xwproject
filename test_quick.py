#!/usr/bin/env python3
"""
快速测试SentenceTransformer功能
"""

import os
import sys

# 添加Django项目路径
sys.path.append('d:/wby/projectfiles/xwproject/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# 设置Django
import django
django.setup()

def test_simple():
    """简单测试"""
    print("=== 快速测试 ===")
    
    try:
        from api.text2vec_integration import LogAnalysisEngine
        
        # 初始化引擎
        engine = LogAnalysisEngine()
        
        print(f"向量化方法: {engine.vector_method}")
        print(f"向量维度: {engine.vector_dim}")
        
        # 测试向量化
        test_text = "测试日志消息"
        vector = engine.vector_engine.text_to_vector(test_text)
        
        if vector is not None:
            print(f"向量化成功！维度: {len(vector)}")
            return True
        else:
            print("向量化失败！")
            return False
            
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_simple()
    if success:
        print("✅ 测试通过!")
    else:
        print("❌ 测试失败!")
