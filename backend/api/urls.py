from django.urls import path
from . import views

urlpatterns = [
    # 信令流程分析
    path('analyze-protocol/', views.analyze_protocol, name='analyze_protocol'),
    
    # 日志异常检测和故障识别
    path('anomaly-detection/', views.anomaly_detection, name='anomaly_detection'),
    path('fault-identification/', views.fault_identification, name='fault_identification'),
    path('add-fault-record/', views.add_fault_record, name='add_fault_record'),
    path('fault-database-info/', views.fault_database_info, name='fault_database_info'),
    
    # 知识图谱节点操作
    path('kg/nodes/', views.get_nodes, name='get_nodes'),
    path('kg/nodes/create/', views.create_node, name='create_node'),
    path('kg/nodes/update/', views.update_node, name='update_node'),
    path('kg/nodes/delete/', views.delete_node, name='delete_node'),
    
    # 知识图谱关系操作
    path('kg/relationships/', views.get_relationships, name='get_relationships'),
    path('kg/relationships/create/', views.create_relationship, name='create_relationship'),
    path('kg/relationships/delete/', views.delete_relationship, name='delete_relationship'),
    
    # 知识图谱架构
    path('kg/schema/', views.get_knowledge_graph_schema, name='get_knowledge_graph_schema'),
]