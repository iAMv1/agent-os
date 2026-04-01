"""
Database MCP Connector

Multi-database connector supporting PostgreSQL, MongoDB, and Redis.
Provides tools for querying, inserting, and managing data across databases.
"""

import os
from typing import Any, Dict, List, Optional

from agentos.mcp.connectors import (
    MCPConnector,
    AuthType,
    ConnectorResult,
    ToolDefinition,
    ConnectorState,
)


class DatabaseConnector(MCPConnector):
    """
    MCP connector for database operations (PostgreSQL, MongoDB, Redis).

    Tools provided:
    - db_query: Execute a query (SQL for PostgreSQL, find for MongoDB)
    - db_insert: Insert data into the database
    - db_update: Update existing records
    - db_delete: Delete records
    - db_list_tables: List tables/collections
    - db_describe: Get schema/collection info
    - redis_get: Get a value from Redis
    - redis_set: Set a value in Redis
    - redis_delete: Delete a key from Redis
    - redis_keys: List keys matching a pattern

    Authentication:
    - PostgreSQL: DATABASE_URL env var or config (postgresql://user:pass@host:port/db)
    - MongoDB: MONGODB_URI env var or config (mongodb://host:port/db)
    - Redis: REDIS_URL env var or config (redis://host:port/db)
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(
            name="database",
            auth_type=AuthType.API_KEY,
            config=config or {},
        )
        self._pg_pool = None
        self._mongo_client = None
        self._mongo_db = None
        self._redis_client = None
        self._enabled_dbs: List[str] = []

    async def connect(self) -> ConnectorResult:
        """Initialize database connections."""
        try:
            self.state = ConnectorState.CONNECTING
            self._enabled_dbs = []

            pg_result = await self._connect_postgresql()
            mongo_result = await self._connect_mongodb()
            redis_result = await self._connect_redis()

            if not any([pg_result.success, mongo_result.success, redis_result.success]):
                self.state = ConnectorState.ERROR
                return ConnectorResult.fail(
                    "No database connections established. Check connection strings."
                )

            self.state = ConnectorState.CONNECTED
            return ConnectorResult.ok(
                output={
                    "connector": "database",
                    "status": "connected",
                    "databases": self._enabled_dbs,
                },
                metadata={
                    "postgresql": pg_result.success,
                    "mongodb": mongo_result.success,
                    "redis": redis_result.success,
                },
            )

        except Exception as e:
            self.state = ConnectorState.ERROR
            return ConnectorResult.fail(f"Failed to connect to databases: {str(e)}")

    async def disconnect(self) -> ConnectorResult:
        """Disconnect all database connections."""
        try:
            if self._pg_pool:
                await self._pg_pool.close()
                self._pg_pool = None

            if self._mongo_client:
                self._mongo_client.close()
                self._mongo_client = None
                self._mongo_db = None

            if self._redis_client:
                await self._redis_client.close()
                self._redis_client = None

            self._enabled_dbs = []
            self._tools = None
            self._tools_loaded = False
            self.state = ConnectorState.DISCONNECTED
            return ConnectorResult.ok(
                output={"connector": "database", "status": "disconnected"}
            )
        except Exception as e:
            return ConnectorResult.fail(
                f"Failed to disconnect from databases: {str(e)}"
            )

    async def _connect_postgresql(self) -> ConnectorResult:
        """Connect to PostgreSQL."""
        try:
            conn_string = self.config.get("postgresql_url") or os.environ.get(
                "DATABASE_URL"
            )
            if not conn_string or not conn_string.startswith("postgresql"):
                return ConnectorResult.fail("PostgreSQL connection string not found.")

            try:
                import asyncpg

                self._pg_pool = await asyncpg.create_pool(dsn=conn_string)
                self._enabled_dbs.append("postgresql")
                return ConnectorResult.ok(
                    output={"database": "postgresql", "status": "connected"}
                )
            except ImportError:
                return ConnectorResult.fail(
                    "asyncpg package not installed. Run: pip install asyncpg"
                )
        except Exception as e:
            return ConnectorResult.fail(f"PostgreSQL connection failed: {str(e)}")

    async def _connect_mongodb(self) -> ConnectorResult:
        """Connect to MongoDB."""
        try:
            uri = self.config.get("mongodb_uri") or os.environ.get("MONGODB_URI")
            if not uri:
                return ConnectorResult.fail("MongoDB URI not found.")

            try:
                from pymongo import MongoClient

                self._mongo_client = MongoClient(uri)
                db_name = (
                    self.config.get("mongodb_db") or uri.split("/")[-1].split("?")[0]
                )
                self._mongo_db = self._mongo_client[db_name]
                self._enabled_dbs.append("mongodb")
                return ConnectorResult.ok(
                    output={"database": "mongodb", "status": "connected"}
                )
            except ImportError:
                return ConnectorResult.fail(
                    "pymongo package not installed. Run: pip install pymongo"
                )
        except Exception as e:
            return ConnectorResult.fail(f"MongoDB connection failed: {str(e)}")

    async def _connect_redis(self) -> ConnectorResult:
        """Connect to Redis."""
        try:
            url = self.config.get("redis_url") or os.environ.get("REDIS_URL")
            if not url:
                return ConnectorResult.fail("Redis URL not found.")

            try:
                import redis.asyncio as redis

                self._redis_client = redis.from_url(url, decode_responses=True)
                await self._redis_client.ping()
                self._enabled_dbs.append("redis")
                return ConnectorResult.ok(
                    output={"database": "redis", "status": "connected"}
                )
            except ImportError:
                return ConnectorResult.fail(
                    "redis package not installed. Run: pip install redis"
                )
        except Exception as e:
            return ConnectorResult.fail(f"Redis connection failed: {str(e)}")

    async def get_tools(self) -> List[ToolDefinition]:
        """Return database tools."""
        tools = []

        if "postgresql" in self._enabled_dbs:
            tools.extend(
                [
                    ToolDefinition(
                        name="db_query",
                        description="Execute a SQL query on PostgreSQL",
                        parameters={
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "SQL query to execute",
                                },
                                "params": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Query parameters",
                                },
                                "database": {
                                    "type": "string",
                                    "description": "Database type",
                                    "default": "postgresql",
                                    "enum": ["postgresql"],
                                },
                            },
                            "required": ["query"],
                        },
                        handler=self._pg_query,
                    ),
                    ToolDefinition(
                        name="db_insert",
                        description="Insert data into PostgreSQL",
                        parameters={
                            "type": "object",
                            "properties": {
                                "table": {
                                    "type": "string",
                                    "description": "Table name",
                                },
                                "data": {
                                    "type": "object",
                                    "description": "Data to insert (key-value pairs)",
                                },
                                "database": {
                                    "type": "string",
                                    "description": "Database type",
                                    "default": "postgresql",
                                },
                            },
                            "required": ["table", "data"],
                        },
                        handler=self._pg_insert,
                    ),
                    ToolDefinition(
                        name="db_update",
                        description="Update records in PostgreSQL",
                        parameters={
                            "type": "object",
                            "properties": {
                                "table": {
                                    "type": "string",
                                    "description": "Table name",
                                },
                                "data": {
                                    "type": "object",
                                    "description": "Data to update",
                                },
                                "where": {
                                    "type": "object",
                                    "description": "WHERE clause conditions",
                                },
                                "database": {
                                    "type": "string",
                                    "description": "Database type",
                                    "default": "postgresql",
                                },
                            },
                            "required": ["table", "data", "where"],
                        },
                        handler=self._pg_update,
                    ),
                    ToolDefinition(
                        name="db_delete",
                        description="Delete records from PostgreSQL",
                        parameters={
                            "type": "object",
                            "properties": {
                                "table": {
                                    "type": "string",
                                    "description": "Table name",
                                },
                                "where": {
                                    "type": "object",
                                    "description": "WHERE clause conditions",
                                },
                                "database": {
                                    "type": "string",
                                    "description": "Database type",
                                    "default": "postgresql",
                                },
                            },
                            "required": ["table", "where"],
                        },
                        handler=self._pg_delete,
                    ),
                    ToolDefinition(
                        name="db_list_tables",
                        description="List all tables in PostgreSQL",
                        parameters={
                            "type": "object",
                            "properties": {
                                "database": {
                                    "type": "string",
                                    "description": "Database type",
                                    "default": "postgresql",
                                },
                            },
                            "required": [],
                        },
                        handler=self._pg_list_tables,
                    ),
                    ToolDefinition(
                        name="db_describe",
                        description="Get table schema in PostgreSQL",
                        parameters={
                            "type": "object",
                            "properties": {
                                "table": {
                                    "type": "string",
                                    "description": "Table name",
                                },
                                "database": {
                                    "type": "string",
                                    "description": "Database type",
                                    "default": "postgresql",
                                },
                            },
                            "required": ["table"],
                        },
                        handler=self._pg_describe,
                    ),
                ]
            )

        if "mongodb" in self._enabled_dbs:
            tools.extend(
                [
                    ToolDefinition(
                        name="db_query",
                        description="Query MongoDB collection",
                        parameters={
                            "type": "object",
                            "properties": {
                                "collection": {
                                    "type": "string",
                                    "description": "Collection name",
                                },
                                "filter": {
                                    "type": "object",
                                    "description": "Query filter",
                                },
                                "limit": {
                                    "type": "integer",
                                    "description": "Max documents to return",
                                    "default": 100,
                                },
                                "sort": {
                                    "type": "object",
                                    "description": "Sort criteria",
                                },
                                "database": {
                                    "type": "string",
                                    "description": "Database type",
                                    "default": "mongodb",
                                },
                            },
                            "required": ["collection"],
                        },
                        handler=self._mongo_query,
                    ),
                    ToolDefinition(
                        name="db_insert",
                        description="Insert documents into MongoDB",
                        parameters={
                            "type": "object",
                            "properties": {
                                "collection": {
                                    "type": "string",
                                    "description": "Collection name",
                                },
                                "documents": {
                                    "type": "array",
                                    "items": {"type": "object"},
                                    "description": "Documents to insert",
                                },
                                "database": {
                                    "type": "string",
                                    "description": "Database type",
                                    "default": "mongodb",
                                },
                            },
                            "required": ["collection", "documents"],
                        },
                        handler=self._mongo_insert,
                    ),
                    ToolDefinition(
                        name="db_update",
                        description="Update documents in MongoDB",
                        parameters={
                            "type": "object",
                            "properties": {
                                "collection": {
                                    "type": "string",
                                    "description": "Collection name",
                                },
                                "filter": {
                                    "type": "object",
                                    "description": "Filter for documents to update",
                                },
                                "update": {
                                    "type": "object",
                                    "description": "Update operations",
                                },
                                "upsert": {
                                    "type": "boolean",
                                    "description": "Insert if not found",
                                    "default": False,
                                },
                                "database": {
                                    "type": "string",
                                    "description": "Database type",
                                    "default": "mongodb",
                                },
                            },
                            "required": ["collection", "filter", "update"],
                        },
                        handler=self._mongo_update,
                    ),
                    ToolDefinition(
                        name="db_delete",
                        description="Delete documents from MongoDB",
                        parameters={
                            "type": "object",
                            "properties": {
                                "collection": {
                                    "type": "string",
                                    "description": "Collection name",
                                },
                                "filter": {
                                    "type": "object",
                                    "description": "Filter for documents to delete",
                                },
                                "database": {
                                    "type": "string",
                                    "description": "Database type",
                                    "default": "mongodb",
                                },
                            },
                            "required": ["collection", "filter"],
                        },
                        handler=self._mongo_delete,
                    ),
                    ToolDefinition(
                        name="db_list_tables",
                        description="List all collections in MongoDB",
                        parameters={
                            "type": "object",
                            "properties": {
                                "database": {
                                    "type": "string",
                                    "description": "Database type",
                                    "default": "mongodb",
                                },
                            },
                            "required": [],
                        },
                        handler=self._mongo_list_collections,
                    ),
                ]
            )

        if "redis" in self._enabled_dbs:
            tools.extend(
                [
                    ToolDefinition(
                        name="redis_get",
                        description="Get a value from Redis",
                        parameters={
                            "type": "object",
                            "properties": {
                                "key": {
                                    "type": "string",
                                    "description": "Redis key",
                                },
                            },
                            "required": ["key"],
                        },
                        handler=self._redis_get,
                    ),
                    ToolDefinition(
                        name="redis_set",
                        description="Set a value in Redis",
                        parameters={
                            "type": "object",
                            "properties": {
                                "key": {
                                    "type": "string",
                                    "description": "Redis key",
                                },
                                "value": {
                                    "type": "string",
                                    "description": "Value to set",
                                },
                                "ex": {
                                    "type": "integer",
                                    "description": "Expiry in seconds",
                                },
                            },
                            "required": ["key", "value"],
                        },
                        handler=self._redis_set,
                    ),
                    ToolDefinition(
                        name="redis_delete",
                        description="Delete a key from Redis",
                        parameters={
                            "type": "object",
                            "properties": {
                                "key": {
                                    "type": "string",
                                    "description": "Redis key to delete",
                                },
                            },
                            "required": ["key"],
                        },
                        handler=self._redis_delete,
                    ),
                    ToolDefinition(
                        name="redis_keys",
                        description="List Redis keys matching a pattern",
                        parameters={
                            "type": "object",
                            "properties": {
                                "pattern": {
                                    "type": "string",
                                    "description": "Key pattern (use * for wildcard)",
                                    "default": "*",
                                },
                            },
                            "required": [],
                        },
                        handler=self._redis_keys,
                    ),
                ]
            )

        return tools

    async def call_tool(
        self, tool_name: str, arguments: Dict[str, Any]
    ) -> ConnectorResult:
        """Execute a database tool."""
        check = self._ensure_connected()
        if not check.success:
            return check

        tools = await self._load_tools_if_needed()
        tool = next((t for t in tools if t.name == tool_name), None)
        if not tool:
            return ConnectorResult.fail(
                f"Unknown database tool: {tool_name}. Available: {[t.name for t in tools]}"
            )

        try:
            result = await tool.handler(**arguments)
            return result
        except Exception as e:
            return ConnectorResult.fail(f"Database tool '{tool_name}' failed: {str(e)}")

    async def _pg_query(
        self, query: str, params: Optional[List[Any]] = None, **kwargs
    ) -> ConnectorResult:
        """Execute a PostgreSQL query."""
        try:
            async with self._pg_pool.acquire() as conn:
                rows = (
                    await conn.fetch(query, *params)
                    if params
                    else await conn.fetch(query)
                )
                results = [dict(r) for r in rows]
            return ConnectorResult.ok(
                output={"rows": results, "count": len(results)},
                metadata={"query": query},
            )
        except Exception as e:
            return ConnectorResult.fail(f"PostgreSQL query failed: {str(e)}")

    async def _pg_insert(
        self, table: str, data: Dict[str, Any], **kwargs
    ) -> ConnectorResult:
        """Insert into PostgreSQL."""
        try:
            columns = ", ".join(data.keys())
            placeholders = ", ".join(f"${i + 1}" for i in range(len(data)))
            query = (
                f"INSERT INTO {table} ({columns}) VALUES ({placeholders}) RETURNING *"
            )
            async with self._pg_pool.acquire() as conn:
                row = await conn.fetch(query, *data.values())
            return ConnectorResult.ok(
                output={"inserted": dict(row[0]) if row else None},
                metadata={"table": table},
            )
        except Exception as e:
            return ConnectorResult.fail(f"PostgreSQL insert failed: {str(e)}")

    async def _pg_update(
        self, table: str, data: Dict[str, Any], where: Dict[str, Any], **kwargs
    ) -> ConnectorResult:
        """Update PostgreSQL records."""
        try:
            set_clause = ", ".join(f"{k} = ${i + 1}" for i, k in enumerate(data.keys()))
            where_clause = " AND ".join(
                f"{k} = ${i + len(data) + 1}" for i, k in enumerate(where.keys())
            )
            query = f"UPDATE {table} SET {set_clause} WHERE {where_clause} RETURNING *"
            params = list(data.values()) + list(where.values())
            async with self._pg_pool.acquire() as conn:
                rows = await conn.fetch(query, *params)
            return ConnectorResult.ok(
                output={"updated": [dict(r) for r in rows], "count": len(rows)},
                metadata={"table": table},
            )
        except Exception as e:
            return ConnectorResult.fail(f"PostgreSQL update failed: {str(e)}")

    async def _pg_delete(
        self, table: str, where: Dict[str, Any], **kwargs
    ) -> ConnectorResult:
        """Delete from PostgreSQL."""
        try:
            where_clause = " AND ".join(
                f"{k} = ${i + 1}" for i, k in enumerate(where.keys())
            )
            query = f"DELETE FROM {table} WHERE {where_clause} RETURNING *"
            async with self._pg_pool.acquire() as conn:
                rows = await conn.fetch(query, *where.values())
            return ConnectorResult.ok(
                output={"deleted": len(rows)},
                metadata={"table": table},
            )
        except Exception as e:
            return ConnectorResult.fail(f"PostgreSQL delete failed: {str(e)}")

    async def _pg_list_tables(self, **kwargs) -> ConnectorResult:
        """List PostgreSQL tables."""
        try:
            query = """
                SELECT table_name FROM information_schema.tables
                WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
                ORDER BY table_name
            """
            async with self._pg_pool.acquire() as conn:
                rows = await conn.fetch(query)
            tables = [r["table_name"] for r in rows]
            return ConnectorResult.ok(
                output={"tables": tables, "count": len(tables)},
                metadata={"database": "postgresql"},
            )
        except Exception as e:
            return ConnectorResult.fail(f"PostgreSQL list tables failed: {str(e)}")

    async def _pg_describe(self, table: str, **kwargs) -> ConnectorResult:
        """Describe PostgreSQL table."""
        try:
            query = """
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = $1 AND table_schema = 'public'
                ORDER BY ordinal_position
            """
            async with self._pg_pool.acquire() as conn:
                rows = await conn.fetch(query, table)
            columns = [dict(r) for r in rows]
            return ConnectorResult.ok(
                output={"table": table, "columns": columns},
                metadata={"database": "postgresql"},
            )
        except Exception as e:
            return ConnectorResult.fail(f"PostgreSQL describe failed: {str(e)}")

    def _mongo_query(
        self,
        collection: str,
        filter: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        sort: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> ConnectorResult:
        """Query MongoDB."""
        try:
            coll = self._mongo_db[collection]
            cursor = coll.find(filter or {})
            if sort:
                cursor = cursor.sort(list(sort.items()))
            cursor = cursor.limit(limit)
            docs = list(cursor)
            for doc in docs:
                doc["_id"] = str(doc["_id"])
            return ConnectorResult.ok(
                output={"documents": docs, "count": len(docs)},
                metadata={"collection": collection},
            )
        except Exception as e:
            return ConnectorResult.fail(f"MongoDB query failed: {str(e)}")

    def _mongo_insert(
        self, collection: str, documents: List[Dict[str, Any]], **kwargs
    ) -> ConnectorResult:
        """Insert into MongoDB."""
        try:
            coll = self._mongo_db[collection]
            result = (
                coll.insert_many(documents)
                if len(documents) > 1
                else coll.insert_one(documents[0])
            )
            ids = (
                [str(id) for id in result.inserted_ids]
                if hasattr(result, "inserted_ids")
                else [str(result.inserted_id)]
            )
            return ConnectorResult.ok(
                output={"inserted_ids": ids, "count": len(ids)},
                metadata={"collection": collection},
            )
        except Exception as e:
            return ConnectorResult.fail(f"MongoDB insert failed: {str(e)}")

    def _mongo_update(
        self,
        collection: str,
        filter: Dict[str, Any],
        update: Dict[str, Any],
        upsert: bool = False,
        **kwargs,
    ) -> ConnectorResult:
        """Update MongoDB documents."""
        try:
            coll = self._mongo_db[collection]
            result = coll.update_many(filter, update, upsert=upsert)
            return ConnectorResult.ok(
                output={
                    "matched": result.matched_count,
                    "modified": result.modified_count,
                    "upserted": str(result.upserted_id) if result.upserted_id else None,
                },
                metadata={"collection": collection},
            )
        except Exception as e:
            return ConnectorResult.fail(f"MongoDB update failed: {str(e)}")

    def _mongo_delete(
        self, collection: str, filter: Dict[str, Any], **kwargs
    ) -> ConnectorResult:
        """Delete MongoDB documents."""
        try:
            coll = self._mongo_db[collection]
            result = coll.delete_many(filter)
            return ConnectorResult.ok(
                output={"deleted": result.deleted_count},
                metadata={"collection": collection},
            )
        except Exception as e:
            return ConnectorResult.fail(f"MongoDB delete failed: {str(e)}")

    def _mongo_list_collections(self, **kwargs) -> ConnectorResult:
        """List MongoDB collections."""
        try:
            collections = self._mongo_db.list_collection_names()
            return ConnectorResult.ok(
                output={"collections": collections, "count": len(collections)},
                metadata={"database": "mongodb"},
            )
        except Exception as e:
            return ConnectorResult.fail(f"MongoDB list collections failed: {str(e)}")

    async def _redis_get(self, key: str, **kwargs) -> ConnectorResult:
        """Get from Redis."""
        try:
            value = await self._redis_client.get(key)
            return ConnectorResult.ok(
                output={"key": key, "value": value},
                metadata={"found": value is not None},
            )
        except Exception as e:
            return ConnectorResult.fail(f"Redis get failed: {str(e)}")

    async def _redis_set(
        self, key: str, value: str, ex: Optional[int] = None, **kwargs
    ) -> ConnectorResult:
        """Set in Redis."""
        try:
            await self._redis_client.set(key, value, ex=ex)
            return ConnectorResult.ok(
                output={"key": key, "set": True},
                metadata={"expiry": ex},
            )
        except Exception as e:
            return ConnectorResult.fail(f"Redis set failed: {str(e)}")

    async def _redis_delete(self, key: str, **kwargs) -> ConnectorResult:
        """Delete from Redis."""
        try:
            count = await self._redis_client.delete(key)
            return ConnectorResult.ok(
                output={"key": key, "deleted": count > 0},
                metadata={"deleted_count": count},
            )
        except Exception as e:
            return ConnectorResult.fail(f"Redis delete failed: {str(e)}")

    async def _redis_keys(self, pattern: str = "*", **kwargs) -> ConnectorResult:
        """List Redis keys."""
        try:
            keys = await self._redis_client.keys(pattern)
            return ConnectorResult.ok(
                output={"keys": keys, "count": len(keys)},
                metadata={"pattern": pattern},
            )
        except Exception as e:
            return ConnectorResult.fail(f"Redis keys failed: {str(e)}")
