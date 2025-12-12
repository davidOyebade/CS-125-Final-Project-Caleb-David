# Westmont College CS 125 Database Design Fall 2025
# Final Project
# Assistant Professor Mike Ryu
#Caleb Song & David Oyebade

"""
FastAPI integration for GraphQL schema

This file integrates the GraphQL schema with FastAPI using Strawberry.
"""

from strawberry.fastapi import GraphQLRouter

# Import schema and connection setter
from graphql_schema import schema, set_database_connections

# This function will be called from api_implement.py to set up connections
def init_graphql(db_pool_conn, redis_conn, mongo_conn):
    """Initialize GraphQL with database connections."""
    set_database_connections(db_pool_conn, redis_conn, mongo_conn)

# Create GraphQL router
graphql_app = GraphQLRouter(schema)