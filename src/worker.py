import logging
import mysql.connector.errors
import uuid
from random import random
from time import sleep
from collections import namedtuple

from db import create_conn

# Task class
Task = namedtuple("Task", ["id", "status"])

# Logging
logger = logging.getLogger("worker-" + str(uuid.uuid4())[:8])
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


def process_task(cursor, task: Task):
    """
    A task is processed by incrementing its count by 1, each taking several milliseconds.
    If the count reaches 3, the task is considered complete.
    """
    logger.info(f"Task {task.id} processing")

    sleep(random() / 2)  # Sleep for 0 to 500ms

    cursor.execute("""
        UPDATE Task SET status = 'complete' WHERE id = %s
    """, (task.id,))

    logger.info(f"Task {task.id} complete")


def main():
    conn = create_conn()
    conn.autocommit = True

    # Wait for table to be created
    while True:
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id FROM Task LIMIT 1
                """)
                result = cursor.fetchone()
                if result:
                    break
        except mysql.connector.errors.ProgrammingError as e:
            # Table doesn't exist yet
            pass

        sleep(1)

    while True:
        # Pick up 1 task at a time and process them
        with conn.cursor() as cursor:
            # Start transaction
            conn.start_transaction(isolation_level="READ COMMITTED")
            cursor.execute("""
                SELECT id, status FROM Task 
                WHERE status = 'pending' 
                LIMIT 1
                FOR UPDATE SKIP LOCKED
            """)
            task = cursor.fetchone()
            if task:
                process_task(cursor, Task(*task))
            else:
                logger.info("No pending tasks found")
                sleep(10)
            conn.commit()


if __name__ == "__main__":
    main()
