# from neo4j import GraphDatabase

# class Neo4jConnection:
    
#     def __init__(self, uri, user, pwd):
#         self.__uri = uri
#         self.__user = user
#         self.__pwd = pwd
#         self.__driver = None
#         try:
#             self.__driver = GraphDatabase.driver(self.__uri, auth=(self.__user, self.__pwd))
#         except Exception as e:
#             print("Failed to create the driver:", e)
        
#     def close(self):
#         if self.__driver is not None:
#             self.__driver.close()
        
#     def query(self, query, parameters=None, db=None):
#         assert self.__driver is not None, "Driver not initialized!"
#         session = None
#         response = None
#         try: 
#             session = self.__driver.session(database=db) if db is not None else self.__driver.session() 
#             response = list(session.run(query, parameters))
#         except Exception as e:
#             print("Query failed:", e)
#         finally: 
#             if session is not None:
#                 session.close()
#         return response

# # Initialize the connection to the Neo4j database
# conn = Neo4jConnection(uri="bolt://localhost:7687", user="neo4j", pwd="fRDotJGu_9Li8FSPvspohtBEYw5Z-FOiqjeRlhlGCQ4")

# # Test the connection
# conn.query("MATCH (n) RETURN n LIMIT 5")

from neo4j import GraphDatabase

# URI examples: "neo4j://localhost", "neo4j+s://xxx.databases.neo4j.io"
URI = "neo4j+s://9be528d2.databases.neo4j.io"
AUTH = ("neo4j", "fRDotJGu_9Li8FSPvspohtBEYw5Z-FOiqjeRlhlGCQ4")

with GraphDatabase.driver(URI, auth=AUTH) as driver:
    driver.verify_connectivity()