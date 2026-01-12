"""
Database Package - Schema Designs and Database Management

Document 09: Database Schema Designs
Implements the three-database architecture:
1. V3 Combined Logic DB (zepix_combined.db)
2. V6 Price Action DB (zepix_price_action.db)
3. Central System DB (zepix_bot.db)

Modules:
- schemas: Base schema definitions and utilities
- v3_database: V3 Combined Logic database schema
- v6_database: V6 Price Action database schema
- central_database: Central System database schema
- sync_manager: Database synchronization manager
"""

from .schemas import (
    BaseSchema,
    SchemaManager,
    create_all_databases,
    get_database_info
)
from .v3_database import V3Database, V3Schema
from .v6_database import V6Database, V6Schema
from .central_database import CentralDatabase, CentralSchema
from .sync_manager import DatabaseSyncManager

__all__ = [
    'BaseSchema',
    'SchemaManager',
    'create_all_databases',
    'get_database_info',
    'V3Database',
    'V3Schema',
    'V6Database',
    'V6Schema',
    'CentralDatabase',
    'CentralSchema',
    'DatabaseSyncManager'
]
