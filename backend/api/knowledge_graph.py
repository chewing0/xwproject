from neo4j import GraphDatabase
from typing import Dict, Optional, List, Tuple, Any
import logging
from .kg_config import NEO4J_CONFIG

logger = logging.getLogger(__name__)

class Neo4jClient:
    def __init__(self, uri: str = None, user: str = None, password: str = None):
        # 使用配置文件中的默认值
        self.uri = uri or NEO4J_CONFIG['uri']
        self.user = user or NEO4J_CONFIG['user']
        self.password = password or NEO4J_CONFIG['password']
        
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            # 测试连接
            with self.driver.session() as session:
                session.run("RETURN 1")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise

    def close(self):
        if hasattr(self, 'driver'):
            self.driver.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def run(self, query: str, parameters: Optional[Dict] = None) -> List[Dict]:
        try:
            with self.driver.session() as session:
                records = session.run(query, parameters or {})
                return self._format_records(records)
        except Exception as e:
            logger.error(f"Neo4j Query Error: {e}")
            return []

    @staticmethod
    def _format_records(records) -> List[Dict]:
        result = []
        for record in records:
            item = {}
            for key in record.keys():
                val = record[key]
                item[key] = dict(val) if hasattr(val, "items") else val
            result.append(item)
        return result


class CypherUtils:
    @staticmethod
    def build_where_and_params(var: str, props: Dict, prefix: str = "") -> Tuple[str, Dict]:
        clause = " AND ".join([f"{var}.{k} = ${prefix + k}" for k in props])
        params = {f"{prefix}{k}": v for k, v in props.items()}
        return clause, params

    @staticmethod
    def build_set_clause_and_params(var: str, props: Dict, prefix: str = "") -> Tuple[str, Dict]:
        clause = ", ".join([f"{var}.{k} = ${prefix + k}" for k in props])
        params = {f"{prefix}{k}": v for k, v in props.items()}
        return clause, params


class NodeManager:
    def __init__(self, client: Neo4jClient):
        self.client = client

    def create(self, label: str, props: Dict):
        query = f"CREATE (n:{label} $props) RETURN n, labels(n) as node_labels"
        return self.client.run(query, {"props": props})

    def find(self, label: str, conditions: Optional[Dict] = None):
        if conditions:
            where, params = CypherUtils.build_where_and_params("n", conditions)
            query = f"MATCH (n:{label}) WHERE {where} RETURN n, labels(n) as node_labels"
        else:
            query, params = f"MATCH (n:{label}) RETURN n, labels(n) as node_labels", {}
        return self.client.run(query, params)

    def update(self, label: str, match_props: Dict, update_props: Dict):
        where, where_params = CypherUtils.build_where_and_params("n", match_props, "m_")
        set_clause, set_params = CypherUtils.build_set_clause_and_params("n", update_props, "u_")
        query = f"MATCH (n:{label}) WHERE {where} SET {set_clause} RETURN n, labels(n) as node_labels"
        return self.client.run(query, {**where_params, **set_params})

    def delete(self, label: str, conditions: Dict):
        where, params = CypherUtils.build_where_and_params("n", conditions)
        query = f"MATCH (n:{label}) WHERE {where} DETACH DELETE n"
        return self.client.run(query, params)

    def fuzzy_find(self, label: str, field: str, pattern: str):
        query = f"MATCH (n:{label}) WHERE n.{field} CONTAINS $value RETURN n, labels(n) as node_labels"
        return self.client.run(query, {"value": pattern})

    def get_all_labels(self):
        query = "CALL db.labels()"
        return self.client.run(query)


class RelationshipManager:
    def __init__(self, client: Neo4jClient):
        self.client = client

    def create(self, from_label: str, from_props: Dict,
                     to_label: str, to_props: Dict,
                     rel_type: str, rel_props: Optional[Dict] = None):
        where_from, params_from = CypherUtils.build_where_and_params("a", from_props, "f_")
        where_to, params_to = CypherUtils.build_where_and_params("b", to_props, "t_")
        query = (
            f"MATCH (a:{from_label}), (b:{to_label}) "
            f"WHERE {where_from} AND {where_to} "
            f"CREATE (a)-[r:{rel_type} $rel_props]->(b) "
            f"RETURN a, labels(a) as a_labels, r, b, labels(b) as b_labels"
        )
        params = {**params_from, **params_to, "rel_props": rel_props or {}}
        return self.client.run(query, params)

    def find(self, from_label: str, to_label: str, rel_type: str, rel_props: Optional[Dict] = None):
        query = f"MATCH (a:{from_label})-[r:{rel_type}]->(b:{to_label})"
        params = {}
        if rel_props:
            where_rel, rel_params = CypherUtils.build_where_and_params("r", rel_props)
            query += f" WHERE {where_rel}"
            params.update(rel_params)
        query += " RETURN a, labels(a) as a_labels, r, b, labels(b) as b_labels"
        return self.client.run(query, params)

    def delete(self, from_label: str, from_props: Dict,
                     to_label: str, to_props: Dict,
                     rel_type: str):
        where_from, params_from = CypherUtils.build_where_and_params("a", from_props, "f_")
        where_to, params_to = CypherUtils.build_where_and_params("b", to_props, "t_")
        query = (
            f"MATCH (a:{from_label})-[r:{rel_type}]->(b:{to_label}) "
            f"WHERE {where_from} AND {where_to} "
            f"DELETE r"
        )
        params = {**params_from, **params_to}
        return self.client.run(query, params)

    def get_all_relationship_types(self):
        query = "CALL db.relationshipTypes()"
        return self.client.run(query)


class KnowledgeGraphService:
    def __init__(self):
        # 可以从Django settings中获取连接配置
        self.client = Neo4jClient()
        self.nodes = NodeManager(self.client)
        self.relationships = RelationshipManager(self.client)

    def close(self):
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
