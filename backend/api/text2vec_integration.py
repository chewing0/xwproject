"""
Text2Vec日志分析集成模块
将text2vec_v1.py的核心功能集成到Django后端
保留原始的日志清洗算法和向量化方法
"""

import os
import csv
import re
import logging
from typing import List, Tuple, Optional, Dict, Any
from pathlib import Path
import numpy as np
import pandas as pd
from django.conf import settings


class LogAnalysisConfig:
    """日志分析配置类"""
    
    # 数据库路径
    DATABASE_PATH = os.path.join(settings.BASE_DIR, 'fault_database', 'fault_records.csv')
    
    # 异常检测阈值
    ANOMALY_THRESHOLD = 0.8
    
    # 日志清洗正则表达式
    LOG_PATTERNS = {
        'timestamp': r'\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}',
        'level': r'(DEBUG|INFO|WARN|WARNING|ERROR|FATAL|CRITICAL)',
        'message': r'.*'
    }


class LogProcessor:
    """日志处理器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def clean_log_text(self, text_lines: List[str]) -> Optional[str]:
        """
        清洗日志文本（针对9005日志格式）- 保留原始算法
        
        Args:
            text_lines: 原始日志行列表
            
        Returns:
            清洗后的文本字符串，失败返回None
        """
        try:
            if not text_lines:
                raise ValueError("输入的日志文本为空")
            
            # 第一步：过滤掉包含 'systemInformationBlockType' 的行
            filtered_lines = []
            for i in range(len(text_lines) - 1):
                line1_parts = text_lines[i].split()
                line2_parts = text_lines[i + 1].split()
                
                if line1_parts and line1_parts[-1] != 'systemInformationBlockType':
                    filtered_lines.append(line1_parts)
            
            # 添加最后一行
            if text_lines:
                filtered_lines.append(text_lines[-1].split())
            
            # 第二步：提取有效内容（从第11个字段开始）
            processed_text = []
            for i in range(len(filtered_lines) - 1):
                line1 = filtered_lines[i]
                line2 = filtered_lines[i + 1]
                
                # 检查最后一个字段是否不同
                if line1 and line2 and len(line1) > 10 and len(line2) > 10:
                    if line1[-1] != line2[-1]:
                        processed_text.extend(line1[10:])
            
            # 添加最后一行的内容
            if filtered_lines and len(filtered_lines[-1]) > 10:
                processed_text.extend(filtered_lines[-1][10:])
            
            result = ' '.join(processed_text)
            
            if not result.strip():
                raise ValueError("处理后的文本为空，可能不是有效的9005日志格式")
            
            self.logger.info(f"日志清洗完成，输出长度: {len(result)}")
            return result
            
        except Exception as e:
            self.logger.error(f"日志清洗失败: {e}")
            return None
    
    def clean_log_text_simple(self, log_content: str) -> str:
        """
        简单的日志清洗方法（用于非9005格式日志）
        
        Args:
            log_content: 原始日志内容
            
        Returns:
            清洗后的文本
        """
        try:
            lines = log_content.strip().split('\n')
            processed_text = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # 移除时间戳
                line = re.sub(LogAnalysisConfig.LOG_PATTERNS['timestamp'], '', line)
                
                # 移除日志级别标识
                line = re.sub(LogAnalysisConfig.LOG_PATTERNS['level'], '', line)
                
                # 移除多余空格
                line = re.sub(r'\s+', ' ', line).strip()
                
                if line and len(line) > 3:  # 过滤过短的行
                    processed_text.append(line)
            
            result = ' '.join(processed_text)
            return result if result.strip() else log_content
            
        except Exception as e:
            self.logger.error(f"日志清洗失败: {e}")
            return log_content
    
    def auto_clean_log_text(self, log_content: str) -> str:
        """
        自动选择清洗方法
        
        Args:
            log_content: 原始日志内容
            
        Returns:
            清洗后的文本
        """
        try:
            # 将字符串转为行列表
            text_lines = [line.strip() for line in log_content.split('\n') if line.strip()]
            
            # 检查是否为9005格式（简单判断：是否包含特定关键词）
            is_9005_format = any('9005' in line or 'systemInformationBlockType' in line for line in text_lines)
            
            if is_9005_format and len(text_lines) > 0:
                # 使用原始的9005清洗算法
                result = self.clean_log_text(text_lines)
                if result:
                    return result
            
            # 使用简单清洗方法作为备选
            return self.clean_log_text_simple(log_content)
            
        except Exception as e:
            self.logger.error(f"自动日志清洗失败: {e}")
            return log_content


class VectorEngine:
    """向量化引擎，负责文本向量化和相似度计算（保留原始方法）"""
    
    def __init__(self, model_path: str = None):
        """
        初始化向量化引擎
        
        Args:
            model_path: SentenceTransformer模型路径
        """
        self.logger = logging.getLogger(__name__)
        self.model = None
        self.model_path = model_path
        self.use_sentence_transformer = False
        
        # 尝试加载SentenceTransformer模型
        if model_path and os.path.exists(model_path):
            self._load_sentence_transformer(model_path)
        else:
            self.logger.info("未找到SentenceTransformer模型，使用备用向量化方法")
    
    def _load_sentence_transformer(self, model_path: str) -> None:
        """加载Sentence Transformer模型（原始方法）"""
        try:
            from sentence_transformers import SentenceTransformer
            
            self.logger.info("正在加载SentenceTransformer模型...")
            self.model = SentenceTransformer(model_path)
            self.use_sentence_transformer = True
            self.logger.info("SentenceTransformer模型加载成功")
            
        except ImportError:
            self.logger.warning("sentence-transformers库未安装，使用备用方法")
        except Exception as e:
            self.logger.error(f"SentenceTransformer模型加载失败: {e}")
    
    def text_to_vector(self, text: str) -> Optional[np.ndarray]:
        """
        将文本转换为向量（优先使用SentenceTransformer）
        
        Args:
            text: 输入文本
            
        Returns:
            文本向量，失败返回None
        """
        try:
            if not text.strip():
                raise ValueError("输入文本为空")
            
            if self.use_sentence_transformer and self.model is not None:
                # 使用SentenceTransformer（原始方法）
                vector = self.model.encode([text], convert_to_numpy=True)[0]
                self.logger.debug(f"SentenceTransformer向量化完成，维度: {vector.shape}")
                return vector
            else:
                # 使用备用方法
                return self._fallback_vectorization(text)
                
        except Exception as e:
            self.logger.error(f"文本向量化失败: {e}")
            return None
    
    def _fallback_vectorization(self, text: str) -> np.ndarray:
        """备用向量化方法"""
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            
            # 使用字符级别的TF-IDF
            vectorizer = TfidfVectorizer(
                analyzer='char_wb', 
                ngram_range=(2, 4), 
                max_features=384  # 与SentenceTransformer维度保持一致
            )
            
            # 训练并转换文本
            vector = vectorizer.fit_transform([text]).toarray()[0]
            self.logger.debug(f"TF-IDF向量化完成，维度: {vector.shape}")
            return vector
            
        except ImportError:
            # 如果sklearn不可用，使用简单的哈希方法
            self.logger.warning("sklearn不可用，使用简单哈希向量化")
            return self._simple_hash_vector(text, 384)
    
    def _simple_hash_vector(self, text: str, vector_size: int = 384) -> np.ndarray:
        """简单的哈希向量化方法"""
        words = text.lower().split()
        vector = np.zeros(vector_size)
        
        for word in words:
            hash_val = hash(word) % vector_size
            vector[hash_val] += 1
        
        # 归一化
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
        
        return vector
    
    def calculate_similarity(self, vector1: np.ndarray, vector2: np.ndarray) -> float:
        """
        计算两个向量的余弦相似度（原始方法）
        
        Args:
            vector1: 向量1
            vector2: 向量2
            
        Returns:
            余弦相似度值
        """
        try:
            from sklearn.metrics.pairwise import cosine_similarity
            similarity = cosine_similarity(
                vector1.reshape(1, -1), 
                vector2.reshape(1, -1)
            )[0][0]
            return float(similarity)
        except ImportError:
            # 手动计算余弦相似度
            dot_product = np.dot(vector1, vector2)
            norm1 = np.linalg.norm(vector1)
            norm2 = np.linalg.norm(vector2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return float(dot_product / (norm1 * norm2))


class SimpleVectorEngine:
    """简化的向量化引擎（保持向后兼容）"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def text_to_vector(self, text: str) -> np.ndarray:
        """
        将文本转换为向量（使用简单的TF-IDF方法）
        
        Args:
            text: 输入文本
            
        Returns:
            文本向量
        """
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            
            # 使用字符级别的TF-IDF
            vectorizer = TfidfVectorizer(
                analyzer='char_wb', 
                ngram_range=(2, 4), 
                max_features=100
            )
            
            # 训练并转换文本
            vector = vectorizer.fit_transform([text]).toarray()[0]
            return vector
            
        except ImportError:
            # 如果sklearn不可用，使用简单的哈希方法
            return self._simple_hash_vector(text)
    
    def _simple_hash_vector(self, text: str, vector_size: int = 100) -> np.ndarray:
        """简单的哈希向量化方法"""
        words = text.lower().split()
        vector = np.zeros(vector_size)
        
        for word in words:
            hash_val = hash(word) % vector_size
            vector[hash_val] += 1
        
        # 归一化
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
        
        return vector
    
    def calculate_similarity(self, vector1: np.ndarray, vector2: np.ndarray) -> float:
        """计算两个向量的余弦相似度"""
        try:
            from sklearn.metrics.pairwise import cosine_similarity
            return cosine_similarity([vector1], [vector2])[0][0]
        except ImportError:
            # 手动计算余弦相似度
            dot_product = np.dot(vector1, vector2)
            norm1 = np.linalg.norm(vector1)
            norm2 = np.linalg.norm(vector2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return dot_product / (norm1 * norm2)


class FaultDatabase:
    """故障数据库管理器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.database_path = LogAnalysisConfig.DATABASE_PATH
        self._ensure_database_exists()
    
    def _ensure_database_exists(self):
        """确保数据库目录和文件存在"""
        os.makedirs(os.path.dirname(self.database_path), exist_ok=True)
        
        if not os.path.exists(self.database_path):
            # 创建空的CSV文件
            with open(self.database_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['vector', 'fault_type', 'timestamp', 'log_sample', 'vector_dim', 'vector_method'])
    
    def add_fault_record(self, vector: np.ndarray, fault_type: str, 
                        log_content: str, timestamp: str = None, vector_method: str = None) -> bool:
        """添加故障记录"""
        try:
            if timestamp is None:
                from datetime import datetime
                timestamp = datetime.now().isoformat()
            
            if vector_method is None:
                vector_method = "unknown"
            
            # 将向量转换为字符串
            vector_str = ','.join(map(str, vector))
            
            # 截取日志样本
            log_sample = log_content[:200] + '...' if len(log_content) > 200 else log_content
            
            with open(self.database_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([vector_str, fault_type, timestamp, log_sample, len(vector), vector_method])
            
            self.logger.info(f"故障记录添加成功: {fault_type}, 维度: {len(vector)}, 方法: {vector_method}")
            return True
            
        except Exception as e:
            self.logger.error(f"添加故障记录失败: {e}")
            return False
    
    def load_fault_records(self, target_dim: int = None, vector_method: str = None) -> Tuple[List[np.ndarray], List[str]]:
        """加载所有故障记录，支持维度过滤"""
        vectors = []
        fault_types = []
        
        try:
            if not os.path.exists(self.database_path):
                return vectors, fault_types
            
            with open(self.database_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader, None)  # 读取标题行
                
                for row in reader:
                    if len(row) >= 2:
                        try:
                            # 解析向量
                            vector_str = row[0]
                            vector = np.array([float(x) for x in vector_str.split(',')])
                            fault_type = row[1]
                            
                            # 检查维度匹配
                            if target_dim is not None and len(vector) != target_dim:
                                self.logger.debug(f"跳过维度不匹配的记录: {len(vector)} != {target_dim}")
                                continue
                            
                            # 检查向量化方法匹配（如果有的话）
                            if len(row) >= 6 and vector_method is not None:
                                record_method = row[5]
                                if record_method != vector_method:
                                    self.logger.debug(f"跳过方法不匹配的记录: {record_method} != {vector_method}")
                                    continue
                            
                            vectors.append(vector)
                            fault_types.append(fault_type)
                            
                        except (ValueError, IndexError) as e:
                            self.logger.warning(f"跳过无效记录: {e}")
                            continue
            
            self.logger.info(f"成功加载 {len(vectors)} 条故障记录 (目标维度: {target_dim})")
            return vectors, fault_types
            
        except Exception as e:
            self.logger.error(f"加载故障记录失败: {e}")
            return vectors, fault_types
    
    def get_database_info(self) -> Dict[str, Any]:
        """获取数据库统计信息"""
        try:
            from collections import Counter
            
            if not os.path.exists(self.database_path):
                return {'total_records': 0, 'fault_types': [], 'dimensions': {}}
            
            fault_type_counts = Counter()
            dimension_counts = Counter()
            total_records = 0
            
            with open(self.database_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader, None)  # 跳过标题行
                
                for row in reader:
                    if len(row) >= 2:
                        fault_type_counts[row[1]] += 1
                        total_records += 1
                        
                        # 统计维度信息
                        if len(row) >= 5:
                            try:
                                dim = int(row[4])
                                dimension_counts[dim] += 1
                            except (ValueError, IndexError):
                                pass
            
            fault_types = [
                {'name': fault_type, 'count': count}
                for fault_type, count in fault_type_counts.items()
            ]
            
            dimensions = [
                {'dim': dim, 'count': count}
                for dim, count in dimension_counts.items()
            ]
            
            return {
                'total_records': total_records,
                'fault_types': fault_types,
                'dimensions': dimensions
            }
            
        except Exception as e:
            self.logger.error(f"获取数据库信息失败: {e}")
            return {'total_records': 0, 'fault_types': [], 'dimensions': {}}


class LogAnalysisEngine:
    """日志分析引擎主类"""
    
    def __init__(self, model_path: str = None):
        """
        初始化日志分析引擎
        
        Args:
            model_path: SentenceTransformer模型路径（可选）
        """
        self.logger = logging.getLogger(__name__)
        self.log_processor = LogProcessor()
        
        # 尝试使用高级向量化引擎，失败则使用简单版本
        try:
            # 检查是否有SentenceTransformer模型路径配置
            if model_path is None:
                # 使用项目中的SentenceTransformer模型路径
                project_model_path = os.path.join(
                    settings.BASE_DIR, 'api', 'hugface-model', 
                    'models--sentence-transformers--all-MiniLM-L6-v2', 
                    'snapshots', 'c9745ed1d9f207416be6d2e6f8de32d1f16199bf'
                )
                if os.path.exists(project_model_path):
                    model_path = project_model_path
                    self.logger.info(f"找到项目中的SentenceTransformer模型: {model_path}")
                else:
                    self.logger.warning(f"SentenceTransformer模型未找到: {project_model_path}")
            
            self.vector_engine = VectorEngine(model_path)
            self.logger.info(f"使用高级向量化引擎，SentenceTransformer: {self.vector_engine.use_sentence_transformer}")
        except Exception as e:
            self.vector_engine = SimpleVectorEngine()
            self.logger.warning(f"使用简单向量化引擎: {e}")
        
        self.fault_db = FaultDatabase()
        
        # 记录当前向量化方法信息
        self.vector_method = self._get_vector_method()
        self.vector_dim = self._get_vector_dimension()
    
    def _get_vector_method(self) -> str:
        """获取当前使用的向量化方法"""
        if hasattr(self.vector_engine, 'use_sentence_transformer') and self.vector_engine.use_sentence_transformer:
            return "sentence_transformer"
        elif isinstance(self.vector_engine, SimpleVectorEngine):
            return "simple_tfidf"
        else:
            return "advanced_tfidf"
    
    def _get_vector_dimension(self) -> int:
        """获取向量维度"""
        # 测试向量化以确定维度
        test_vector = self.vector_engine.text_to_vector("test")
        return len(test_vector) if test_vector is not None else 100
    
    def detect_anomaly(self, normal_log: str, test_log: str, 
                      threshold: float = None) -> Dict[str, Any]:
        """异常检测"""
        if threshold is None:
            threshold = LogAnalysisConfig.ANOMALY_THRESHOLD
        
        try:
            # 预处理日志 - 使用自动清洗方法
            normal_text = self.log_processor.auto_clean_log_text(normal_log)
            test_text = self.log_processor.auto_clean_log_text(test_log)
            
            # 向量化
            normal_vector = self.vector_engine.text_to_vector(normal_text)
            test_vector = self.vector_engine.text_to_vector(test_text)
            
            if normal_vector is None or test_vector is None:
                raise ValueError("向量化失败")
            
            # 确保向量维度一致
            if len(normal_vector) != len(test_vector):
                raise ValueError(f"向量维度不匹配: {len(normal_vector)} != {len(test_vector)}")
            
            # 计算相似度
            similarity = self.vector_engine.calculate_similarity(normal_vector, test_vector)
            
            is_anomaly = similarity < threshold
            
            description = f"日志相似度为 {similarity:.4f}，"
            if is_anomaly:
                description += f"低于阈值 {threshold}，检测到异常。"
            else:
                description += f"高于阈值 {threshold}，日志正常。"
            
            return {
                'similarity': similarity,
                'threshold': threshold,
                'is_anomaly': is_anomaly,
                'description': description
            }
            
        except Exception as e:
            self.logger.error(f"异常检测失败: {e}")
            raise
    
    def identify_fault_type(self, log_content: str) -> Dict[str, Any]:
        """故障类型识别"""
        try:
            # 预处理日志 - 使用自动清洗方法
            test_text = self.log_processor.auto_clean_log_text(log_content)
            test_vector = self.vector_engine.text_to_vector(test_text)
            
            if test_vector is None:
                raise ValueError("向量化失败")
            
            # 加载匹配维度的故障记录
            fault_vectors, fault_types = self.fault_db.load_fault_records(
                target_dim=len(test_vector),
                vector_method=self.vector_method
            )
            
            if not fault_vectors:
                # 如果没有匹配维度的记录，尝试加载所有记录并进行维度转换
                all_vectors, all_types = self.fault_db.load_fault_records()
                
                if not all_vectors:
                    return {
                        'predicted_fault': '故障库为空',
                        'confidence': 0.0,
                        'top_matches': [],
                        'warning': '故障库中没有记录，请先添加故障样本'
                    }
                
                # 尝试重新向量化已有记录以匹配当前维度
                self.logger.warning(f"故障库中没有匹配维度({len(test_vector)})的记录，总记录数: {len(all_vectors)}")
                return {
                    'predicted_fault': '维度不匹配',
                    'confidence': 0.0,
                    'top_matches': [],
                    'warning': f'故障库中的向量维度与当前不匹配。请清空故障库后重新添加记录，或确保使用相同的向量化方法。'
                }
            
            # 计算与每个故障记录的相似度
            similarities = []
            for fault_vector in fault_vectors:
                if len(fault_vector) == len(test_vector):
                    similarity = self.vector_engine.calculate_similarity(test_vector, fault_vector)
                    similarities.append(similarity)
                else:
                    # 跳过维度不匹配的向量
                    similarities.append(0.0)
            
            if not any(similarities):
                return {
                    'predicted_fault': '无匹配记录',
                    'confidence': 0.0,
                    'top_matches': [],
                    'warning': '没有找到维度匹配的故障记录'
                }
            
            # 找到最相似的故障类型
            max_similarity_idx = np.argmax(similarities)
            predicted_fault = fault_types[max_similarity_idx]
            max_similarity = similarities[max_similarity_idx]
            
            # 生成排名
            sorted_indices = np.argsort(similarities)[::-1]
            top_matches = []
            
            seen_types = set()
            for idx in sorted_indices[:5]:  # 前5个结果
                if similarities[idx] > 0:  # 只包含有效相似度的结果
                    fault_type = fault_types[idx]
                    if fault_type not in seen_types:
                        top_matches.append({
                            'fault_type': fault_type,
                            'similarity': similarities[idx]
                        })
                        seen_types.add(fault_type)
                        if len(top_matches) >= 3:  # 只保留前3个不同类型
                            break
            
            return {
                'predicted_fault': predicted_fault,
                'confidence': max_similarity,
                'top_matches': top_matches
            }
            
        except Exception as e:
            self.logger.error(f"故障类型识别失败: {e}")
            raise
    
    def add_fault_record(self, log_content: str, fault_type: str) -> bool:
        """添加故障记录到数据库"""
        try:
            # 预处理日志 - 使用自动清洗方法
            processed_text = self.log_processor.auto_clean_log_text(log_content)
            
            # 向量化
            vector = self.vector_engine.text_to_vector(processed_text)
            
            if vector is None:
                raise ValueError("向量化失败")
            
            # 添加到数据库，包含向量化方法信息
            return self.fault_db.add_fault_record(
                vector, fault_type, log_content, 
                vector_method=self.vector_method
            )
            
        except Exception as e:
            self.logger.error(f"添加故障记录失败: {e}")
            return False
    
    def get_fault_database_info(self) -> Dict[str, Any]:
        """获取故障库信息"""
        info = self.fault_db.get_database_info()
        
        # 添加当前引擎信息
        info['current_engine'] = {
            'vector_method': self.vector_method,
            'vector_dimension': self.vector_dim,
            'engine_type': type(self.vector_engine).__name__
        }
        
        return info
