"""
MongoDB client for the worker service.
"""
import logging
from typing import Dict, Any, List, Optional
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure, PyMongoError

from worker.config import config

# Configure logging
logger = logging.getLogger(__name__)


class MongoDBClient:
    """
    Client for interacting with MongoDB.
    """

    def __init__(self) -> None:
        """
        Initialize the MongoDB client.
        """
        self.uri = config.MONGODB.URI
        self.db_name = config.MONGODB.DB
        self.collection_name = config.MONGODB.COLLECTION
        self.client = None
        self.db = None
        self.collection = None

    def connect(self) -> None:
        """
        Connect to MongoDB.
        
        Raises:
            ConnectionFailure: If connection to MongoDB fails
        """
        try:
            # Connect to MongoDB
            self.client = MongoClient(self.uri)

            # Check connection
            self.client.admin.command('ping')

            # Get database and collection
            self.db = self.client[self.db_name]
            self.collection = self.db[self.collection_name]

            logger.info("Connected to MongoDB at %s", self.uri)
        except ConnectionFailure as e:
            logger.error("Failed to connect to MongoDB: %s", e)
            raise

    def insert_one(self, document: Dict[str, Any]) -> str:
        """
        Insert a document into the collection.
        
        Args:
            document: Document to insert
            
        Returns:
            ID of the inserted document
            
        Raises:
            ConnectionFailure: If connection to MongoDB fails
            OperationFailure: If the insert operation fails
        """
        if not self.client:
            self.connect()

        try:
            result = self.collection.insert_one(document)
            logger.info("Inserted document with ID: %s", result.inserted_id)
            return str(result.inserted_id)
        except ConnectionFailure as e:
            logger.error("Connection to MongoDB failed during insert: %s", e)
            raise
        except OperationFailure as e:
            logger.error("Failed to insert document: %s", e)
            raise
        except PyMongoError as e:
            logger.error("Unexpected MongoDB error during insert: %s", e)
            raise

    def find_one(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Find a document in the collection.
        
        Args:
            query: Query to find document
            
        Returns:
            Document or None if not found
            
        Raises:
            ConnectionFailure: If connection to MongoDB fails
            OperationFailure: If the find operation fails
        """
        if not self.client:
            self.connect()

        try:
            result = self.collection.find_one(query)
            return result
        except ConnectionFailure as e:
            logger.error("Connection to MongoDB failed during find: %s", e)
            raise
        except OperationFailure as e:
            logger.error("Failed to find document: %s", e)
            raise
        except PyMongoError as e:
            logger.error("Unexpected MongoDB error during find: %s", e)
            raise

    def find_many(self, query: Dict[str, Any], limit: int = 100) -> List[Dict[str, Any]]:
        """
        Find multiple documents in the collection.
        
        Args:
            query: Query to find documents
            limit: Maximum number of documents to return
            
        Returns:
            List of documents
            
        Raises:
            ConnectionFailure: If connection to MongoDB fails
            OperationFailure: If the find operation fails
        """
        if not self.client:
            self.connect()

        try:
            cursor = self.collection.find(query).limit(limit)
            return list(cursor)
        except ConnectionFailure as e:
            logger.error("Connection to MongoDB failed during find_many: %s", e)
            raise
        except OperationFailure as e:
            logger.error("Failed to find documents: %s", e)
            raise
        except PyMongoError as e:
            logger.error("Unexpected MongoDB error during find_many: %s", e)
            raise

    def close(self) -> None:
        """
        Close the connection to MongoDB.
        """
        if self.client:
            self.client.close()
            self.client = None
            self.db = None
            self.collection = None
            logger.info("Closed connection to MongoDB")


# Create a singleton instance
mongodb_client = MongoDBClient()
