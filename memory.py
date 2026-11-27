import sqlite3
import networkx as nx
from datetime import datetime


class EpisodicMemory:

    def __init__(self, db_path="memory.db"):

        self.db = sqlite3.connect(
            db_path,
            check_same_thread=False
        )

        self.graph = nx.Graph()

        self.create_table()
        self.load_graph()


    def create_table(self):

        self.db.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                event TEXT,
                location TEXT,
                activity TEXT,
                cognitive_state TEXT,
                accel_x REAL DEFAULT 0,
                accel_y REAL DEFAULT 0,
                accel_z REAL DEFAULT 0,
                image_path TEXT
            )
        """)

        # Handle your existing database
        columns = self.db.execute(
            "PRAGMA table_info(memories)"
        ).fetchall()

        column_names = [column[1] for column in columns]

        if "accel_x" not in column_names:
            self.db.execute(
                "ALTER TABLE memories ADD COLUMN accel_x REAL DEFAULT 0"
            )

        if "accel_y" not in column_names:
            self.db.execute(
                "ALTER TABLE memories ADD COLUMN accel_y REAL DEFAULT 0"
            )

        if "accel_z" not in column_names:
            self.db.execute(
                "ALTER TABLE memories ADD COLUMN accel_z REAL DEFAULT 0"
            )

        if "image_path" not in column_names:
            self.db.execute(
                "ALTER TABLE memories ADD COLUMN image_path TEXT"
            )

        self.db.commit()


    def add_memory(
        self,
        event,
        location="Unknown",
        activity="Unknown",
        cognitive_state="Unknown",
        accel_x=0,
        accel_y=0,
        accel_z=0,
        image_path=None
    ):

        timestamp = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        cursor = self.db.execute("""
            INSERT INTO memories
            (
                timestamp,
                event,
                location,
                activity,
                cognitive_state,
                accel_x,
                accel_y,
                accel_z,
                image_path
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            timestamp,
            event,
            location,
            activity,
            cognitive_state,
            accel_x,
            accel_y,
            accel_z,
            image_path
        ))

        memory_id = cursor.lastrowid

        self.db.commit()

        memory_node = f"memory_{memory_id}"
        location_node = f"location_{location}"
        activity_node = f"activity_{activity}"

        self.graph.add_node(
            memory_node,
            type="memory",
            label=event,
            timestamp=timestamp
        )

        self.graph.add_node(
            location_node,
            type="location",
            label=location
        )

        self.graph.add_node(
            activity_node,
            type="activity",
            label=activity
        )

        self.graph.add_edge(
            memory_node,
            location_node,
            relation="occurred_at"
        )

        self.graph.add_edge(
            memory_node,
            activity_node,
            relation="involved"
        )

        return memory_id


    def get_memories(self):

        cursor = self.db.execute("""
            SELECT
                id,
                timestamp,
                event,
                location,
                activity,
                cognitive_state,
                accel_x,
                accel_y,
                accel_z,
                image_path
            FROM memories
            ORDER BY timestamp DESC
        """)

        return cursor.fetchall()


    def search(self, query):

        query = f"%{query}%"

        cursor = self.db.execute("""
            SELECT
                timestamp,
                event,
                location,
                activity,
                cognitive_state,
                accel_x,
                accel_y,
                accel_z,
                image_path
            FROM memories
            WHERE
                event LIKE ?
                OR location LIKE ?
                OR activity LIKE ?
                OR cognitive_state LIKE ?
            ORDER BY timestamp DESC
        """, (
            query,
            query,
            query,
            query
        ))

        return cursor.fetchall()


    def load_graph(self):

        memories = self.get_memories()

        for memory in memories:

            memory_id = memory[0]
            timestamp = memory[1]
            event = memory[2]
            location = memory[3]
            activity = memory[4]

            memory_node = f"memory_{memory_id}"
            location_node = f"location_{location}"
            activity_node = f"activity_{activity}"

            self.graph.add_node(
                memory_node,
                type="memory",
                label=event,
                timestamp=timestamp
            )

            self.graph.add_node(
                location_node,
                type="location",
                label=location
            )

            self.graph.add_node(
                activity_node,
                type="activity",
                label=activity
            )

            self.graph.add_edge(
                memory_node,
                location_node,
                relation="occurred_at"
            )

            self.graph.add_edge(
                memory_node,
                activity_node,
                relation="involved"
            )