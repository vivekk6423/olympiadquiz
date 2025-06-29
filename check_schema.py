#!/usr/bin/env python3
"""
Check the actual database schema
"""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

def check_schema():
    """Check the actual database schema"""
    database_url = os.getenv('DATABASE_URL')
    
    try:
        engine = create_engine(
            database_url, 
            echo=False,
            connect_args={"options": "-csearch_path=olympiadquiz,public"}
        )
        
        with engine.connect() as conn:
            # Check user table structure
            result = conn.execute(text("""
                SELECT column_name, data_type, character_maximum_length, is_nullable
                FROM information_schema.columns 
                WHERE table_schema = 'olympiadquiz' AND table_name = 'user'
                ORDER BY ordinal_position
            """))
            
            print("User table structure:")
            columns = result.fetchall()
            for col in columns:
                print(f"  {col[0]}: {col[1]}" + (f"({col[2]})" if col[2] else "") + f" {'NULL' if col[3] == 'YES' else 'NOT NULL'}")
                
            return True
            
    except Exception as e:
        print(f"Error checking schema: {e}")
        return False

if __name__ == "__main__":
    check_schema()
