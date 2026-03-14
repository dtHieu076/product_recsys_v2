import psycopg2
import pickle
from sklearn.preprocessing import LabelEncoder
import os
import sys

DB_URL = "postgresql://neondb_owner:npg_pex1GDbPkA3g@ep-flat-waterfall-a451aj2o-pooler.us-east-1.aws.neon.tech/product_recsys_db"

def build_encoders():
    conn = None
    try:
        # Connect to database
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        
        # Get unique user_ids from events
        cur.execute("SELECT DISTINCT user_id FROM events WHERE user_id IS NOT NULL")
        user_ids = [row[0] for row in cur.fetchall()]
        
        # Get unique product_ids from products
        cur.execute("SELECT DISTINCT product_id FROM products WHERE product_id IS NOT NULL")
        product_ids = [row[0] for row in cur.fetchall()]
        
        # Create and fit encoders
        user_encoder = LabelEncoder()
        user_encoder.fit(user_ids)
        
        item_encoder = LabelEncoder()
        item_encoder.fit(product_ids)
        
        # Ensure directories exist
        ml_dir = "app/ml"
        os.makedirs(ml_dir, exist_ok=True)
        
        # Save encoders
        with open(os.path.join(ml_dir, "user_encoder.pkl"), "wb") as f:
            pickle.dump(user_encoder, f)
        
        with open(os.path.join(ml_dir, "item_encoder.pkl"), "wb") as f:
            pickle.dump(item_encoder, f)
        
        # Print statistics
        print(f"Encoders successfully created!")
        print(f"Number of unique users: {len(user_ids)}")
        print(f"Number of unique products: {len(product_ids)}")
        print(f"Files saved to:")
        print(f"  - {os.path.abspath(os.path.join(ml_dir, 'user_encoder.pkl'))}")
        print(f"  - {os.path.abspath(os.path.join(ml_dir, 'item_encoder.pkl'))}")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    build_encoders()

