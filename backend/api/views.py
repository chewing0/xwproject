from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .protocol_analyzer import ProtocolAnalyzer
from .knowledge_graph import KnowledgeGraphService
import traceback

@csrf_exempt
@require_http_methods(["POST"])
def analyze_protocol(request):
    try:
        # 获取请求体中的日志内容
        data = json.loads(request.body)
        log_content = data.get('log_content', '')
        
        if not log_content:
            return JsonResponse({
                'error': 'No log content provided'
            }, status=400)
        
        # 创建分析器实例
        analyzer = ProtocolAnalyzer()
        
        # 解析日志
        logs = analyzer.parse_log(log_content)
        
        # 分析流程完整性
        analyzer.analyze_flow_completeness(logs)
        
        # 生成分析报告
        report = analyzer.generate_analysis_report()
        
        # 获取流程顺序
        flow_order = list(analyzer.flow_definitions.keys())
        
        # 获取第一个错误信息
        first_error = analyzer.print_first_error(report, flow_order)
        
        return JsonResponse({
            'report': report,
            'first_error': first_error
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Invalid JSON in request body'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def get_nodes(request):
    """获取所有节点或特定标签的节点"""
    try:
        label = request.GET.get('label', '')
        search_field = request.GET.get('search_field', '')
        search_value = request.GET.get('search_value', '')
        
        with KnowledgeGraphService() as kg:
            if search_field and search_value:
                # 模糊搜索
                nodes = kg.nodes.fuzzy_find(label, search_field, search_value)
            elif label:
                # 按标签查询
                nodes = kg.nodes.find(label)
            else:
                # 获取所有标签的节点
                valid_labels = ['type', 'reason', 'solution']
                all_nodes = []
                for lbl in valid_labels:
                    nodes_of_label = kg.nodes.find(lbl)
                    all_nodes.extend(nodes_of_label)
                nodes = all_nodes
        
        # 处理节点数据，将标签信息添加到节点对象中
        processed_nodes = []
        for item in nodes:
            node_data = item['n']
            if 'node_labels' in item:
                node_data['__labels__'] = item['node_labels']
            processed_nodes.append({'n': node_data})
        
        return JsonResponse({
            'success': True,
            'data': processed_nodes
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def create_node(request):
    """创建新节点"""
    try:
        data = json.loads(request.body)
        label = data.get('label', '')
        properties = data.get('properties', {})
        
        # 验证节点类型
        valid_labels = ['type', 'reason', 'solution']
        if label not in valid_labels:
            return JsonResponse({
                'success': False,
                'error': f'Invalid label. Must be one of: {valid_labels}'
            }, status=400)
        
        with KnowledgeGraphService() as kg:
            result = kg.nodes.create(label, properties)
        
        return JsonResponse({
            'success': True,
            'data': result
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON in request body'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["PUT"])
def update_node(request):
    """更新节点"""
    try:
        data = json.loads(request.body)
        label = data.get('label', '')
        match_properties = data.get('match_properties', {})
        update_properties = data.get('update_properties', {})
        
        # 验证节点类型
        valid_labels = ['type', 'reason', 'solution']
        if label not in valid_labels:
            return JsonResponse({
                'success': False,
                'error': f'Invalid label. Must be one of: {valid_labels}'
            }, status=400)
        
        with KnowledgeGraphService() as kg:
            result = kg.nodes.update(label, match_properties, update_properties)
        
        return JsonResponse({
            'success': True,
            'data': result
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON in request body'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["DELETE"])
def delete_node(request):
    """删除节点"""
    try:
        data = json.loads(request.body)
        label = data.get('label', '')
        properties = data.get('properties', {})
        
        # 验证节点类型
        valid_labels = ['type', 'reason', 'solution']
        if label not in valid_labels:
            return JsonResponse({
                'success': False,
                'error': f'Invalid label. Must be one of: {valid_labels}'
            }, status=400)
        
        with KnowledgeGraphService() as kg:
            result = kg.nodes.delete(label, properties)
        
        return JsonResponse({
            'success': True,
            'data': result
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON in request body'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_relationships(request):
    """获取关系"""
    try:
        from_label = request.GET.get('from_label', '')
        to_label = request.GET.get('to_label', '')
        rel_type = request.GET.get('rel_type', '')
        
        with KnowledgeGraphService() as kg:
            if from_label and to_label and rel_type:
                relationships = kg.relationships.find(from_label, to_label, rel_type)
            else:
                # 获取所有有效的关系
                all_relationships = []
                valid_rels = [
                    ('type', 'reason', 'BECAUSE'),
                    ('reason', 'solution', 'DEAL')
                ]
                for from_lbl, to_lbl, rel_tp in valid_rels:
                    rels = kg.relationships.find(from_lbl, to_lbl, rel_tp)
                    all_relationships.extend(rels)
                relationships = all_relationships
        
        # 处理关系数据，将标签信息添加到节点对象中
        processed_relationships = []
        for item in relationships:
            # 处理起始节点
            from_node = item['a']
            if 'a_labels' in item:
                from_node['__labels__'] = item['a_labels']
            
            # 处理目标节点
            to_node = item['b']
            if 'b_labels' in item:
                to_node['__labels__'] = item['b_labels']
            
            processed_relationships.append({
                'a': from_node,
                'r': item['r'],
                'b': to_node
            })
        
        return JsonResponse({
            'success': True,
            'data': processed_relationships
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def create_relationship(request):
    """创建关系"""
    try:
        data = json.loads(request.body)
        from_label = data.get('from_label', '')
        from_properties = data.get('from_properties', {})
        to_label = data.get('to_label', '')
        to_properties = data.get('to_properties', {})
        rel_type = data.get('rel_type', '')
        rel_properties = data.get('rel_properties', {})
        
        # 验证关系类型
        valid_relationships = {
            ('type', 'reason'): 'BECAUSE',
            ('reason', 'solution'): 'DEAL'
        }
        
        if (from_label, to_label) not in valid_relationships:
            return JsonResponse({
                'success': False,
                'error': f'Invalid relationship. Valid relationships: {list(valid_relationships.keys())}'
            }, status=400)
        
        if rel_type != valid_relationships[(from_label, to_label)]:
            return JsonResponse({
                'success': False,
                'error': f'Invalid relationship type for {from_label}->{to_label}. Expected: {valid_relationships[(from_label, to_label)]}'
            }, status=400)
        
        with KnowledgeGraphService() as kg:
            result = kg.relationships.create(
                from_label, from_properties,
                to_label, to_properties,
                rel_type, rel_properties
            )
        
        return JsonResponse({
            'success': True,
            'data': result
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON in request body'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["DELETE"])
def delete_relationship(request):
    """删除关系"""
    try:
        data = json.loads(request.body)
        from_label = data.get('from_label', '')
        from_properties = data.get('from_properties', {})
        to_label = data.get('to_label', '')
        to_properties = data.get('to_properties', {})
        rel_type = data.get('rel_type', '')
        
        # 验证关系类型
        valid_relationships = {
            ('type', 'reason'): 'BECAUSE',
            ('reason', 'solution'): 'DEAL'
        }
        
        if (from_label, to_label) not in valid_relationships:
            return JsonResponse({
                'success': False,
                'error': f'Invalid relationship. Valid relationships: {list(valid_relationships.keys())}'
            }, status=400)
        
        with KnowledgeGraphService() as kg:
            result = kg.relationships.delete(
                from_label, from_properties,
                to_label, to_properties,
                rel_type
            )
        
        return JsonResponse({
            'success': True,
            'data': result
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON in request body'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_knowledge_graph_schema(request):
    """获取知识图谱的架构信息"""
    try:
        schema = {
            'node_types': [
                {
                    'label': 'type',
                    'description': '故障类型节点',
                    'required_fields': ['name'],
                    'optional_fields': ['description']
                },
                {
                    'label': 'reason',
                    'description': '故障原因节点',
                    'required_fields': ['name'],
                    'optional_fields': ['description', 'probability']
                },
                {
                    'label': 'solution',
                    'description': '解决方案节点',
                    'required_fields': ['name'],
                    'optional_fields': ['description', 'steps', 'difficulty']
                }
            ],
            'relationship_types': [
                {
                    'type': 'BECAUSE',
                    'from': 'type',
                    'to': 'reason',
                    'description': '故障类型导致原因'
                },
                {
                    'type': 'DEAL',
                    'from': 'reason',
                    'to': 'solution',
                    'description': '原因对应的解决方案'
                }
            ]
        }
        
        return JsonResponse({
            'success': True,
            'data': schema
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def anomaly_detection(request):
    """异常检测API - 通过与正常日志对比检测异常"""
    try:
        data = json.loads(request.body)
        normal_log = data.get('normal_log', '')
        test_log = data.get('test_log', '')
        
        if not normal_log or not test_log:
            return JsonResponse({
                'error': 'Normal log and test log content are required'
            }, status=400)
        
        # 使用集成的text2vec功能
        from .text2vec_integration import LogAnalysisEngine
        
        engine = LogAnalysisEngine()
        result = engine.detect_anomaly(normal_log, test_log)
        
        return JsonResponse(result)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Invalid JSON in request body'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def fault_identification(request):
    """故障类型识别API"""
    try:
        data = json.loads(request.body)
        log_content = data.get('log_content', '')
        
        if not log_content:
            return JsonResponse({
                'error': 'Log content is required'
            }, status=400)
          # 使用集成的text2vec功能
        from .text2vec_integration import LogAnalysisEngine
        
        engine = LogAnalysisEngine()
        result = engine.identify_fault_type(log_content)
        
        return JsonResponse(result)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Invalid JSON in request body'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def add_fault_record(request):
    """添加故障记录到故障库"""
    try:
        data = json.loads(request.body)
        log_content = data.get('log_content', '')
        fault_type = data.get('fault_type', '')
        
        if not log_content or not fault_type:
            return JsonResponse({
                'error': 'Log content and fault type are required'
            }, status=400)
        
        # 使用集成的text2vec功能
        from .text2vec_integration import LogAnalysisEngine
        
        engine = LogAnalysisEngine()
        success = engine.add_fault_record(log_content, fault_type)
        
        if success:
            return JsonResponse({
                'success': True,
                'message': f'故障记录已添加: {fault_type}'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': '添加故障记录失败'
            }, status=500)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Invalid JSON in request body'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def fault_database_info(request):
    """获取故障库信息"""
    try:
        # 使用集成的text2vec功能
        from .text2vec_integration import LogAnalysisEngine
        
        engine = LogAnalysisEngine()
        result = engine.get_fault_database_info()
        
        return JsonResponse(result)
        
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)
