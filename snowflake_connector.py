"""
Snowflake database connector
"""
import os
import snowflake.connector
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()


class SnowflakeConnector:
    """Manages Snowflake database connections and queries"""
    
    def __init__(self):
        self.config = {
            'account': os.getenv('JAPFA_ACCOUNT'),
            'user': os.getenv('JAPFA_USER'),
            'password': os.getenv('JAPFA_PASSWORD'),
            'database': os.getenv('JAPFA_DATABASE'),
            'schema': os.getenv('JAPFA_SCHEMA'),
            'warehouse': os.getenv('JAPFA_WAREHOUSE'),
            'role': os.getenv('JAPFA_ROLE', 'PUBLIC')
        }
        
        # Validate configuration
        missing = [k for k, v in self.config.items() if not v and k != 'role']
        if missing:
            raise ValueError(f"Missing Snowflake configuration: {', '.join(missing)}")
    
    def execute_query(self, sql_query: str) -> List[Dict[str, Any]]:
        """
        Execute SQL query and return results
        
        Args:
            sql_query: SQL SELECT query
            
        Returns:
            List of dictionaries representing rows
            
        Raises:
            RuntimeError: If query execution fails
        """
        conn = None
        cursor = None
        
        try:
            print(f"📊 Connecting to Snowflake...")
            conn = snowflake.connector.connect(**self.config)
            
            print(f"🔍 Executing query...")
            cursor = conn.cursor(snowflake.connector.DictCursor)
            cursor.execute(sql_query)
            
            results = cursor.fetchall()
            print(f"✅ Query returned {len(results)} rows")
            
            return results
        
        except snowflake.connector.errors.ProgrammingError as e:
            error_msg = f"SQL Error: {str(e)}"
            print(f"❌ {error_msg}")
            raise RuntimeError(error_msg)
        
        except Exception as e:
            error_msg = f"Database error: {str(e)}"
            print(f"❌ {error_msg}")
            raise RuntimeError(error_msg)
        
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
                print("🔌 Snowflake connection closed")


# Singleton instance
_snowflake_connector = None

def get_snowflake_connector() -> SnowflakeConnector:
    """Get or create Snowflake connector instance"""
    global _snowflake_connector
    if _snowflake_connector is None:
        _snowflake_connector = SnowflakeConnector()
    return _snowflake_connector