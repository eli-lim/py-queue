import logging
import os

from db import create_conn

# Logging
logger = logging.getLogger("init_db")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Task creation parameters
num_tasks = int(os.getenv("TASKS", 20))

def main():

    conn = create_conn()

    # Create db / table if it doesn't exist
    conn.start_transaction(isolation_level="SERIALIZABLE")

    with conn.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Task (
            id INT AUTO_INCREMENT PRIMARY KEY,
            status ENUM('pending', 'complete') NOT NULL DEFAULT 'pending',
            created_at TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP(3),
            updated_at TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3)
        )""")
        cursor.execute(f"""
            INSERT INTO Task VALUES {','.join("()" for _ in range(num_tasks))}
        """)

    conn.commit()
    conn.close()

    print(f"Created {num_tasks} tasks")


if __name__ == "__main__":
    main()