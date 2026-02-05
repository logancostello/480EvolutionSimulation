import sqlite3
import pandas as pd
import os

class SimulationDatastore:
    """ Place for simulation data to be stored """

    def __init__(self):
        self.conn = sqlite3.connect(":memory:")
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()

        cursor.execute("""
            CREATE TABLE creatures (
                id INTEGER PRIMARY KEY,
                parent INTEGER,
                generation INTEGER,
                birth_time REAL,
                death_time REAL,
                max_speed REAL,
                max_turn_rate REAL,
                radius REAL,
                min_energy_to_reproduce REAL,
                min_time_between_reproducing REAL,
                viewable_distance REAL,
                viewable_angle REAL,
                num_brain_nodes INTEGER,
                num_brain_connections INTEGER
            )
        """)

        cursor.execute("""
            CREATE TABLE real_time_stats (
                time REAL PRIMARY KEY,
                num_creatures INTEGER,
                num_food INTEGER
            )
        """)

    def add_new_creature(self, c, time):
        self.conn.execute("""
            INSERT INTO creatures (id, parent, generation, birth_time, max_speed, max_turn_rate, radius, min_energy_to_reproduce, min_time_between_reproducing, viewable_distance, viewable_angle, num_brain_nodes, num_brain_connections)
            VALUES (:id, :parent, :generation, :birth_time, :max_speed, :max_turn_rate, :radius, :min_energy_to_reproduce, :min_time_between_reproducing, :viewable_distance, :viewable_angle, :num_brain_nodes, :num_brain_connections)""",
            {
                "id": c.id,
                "parent": c.parent,
                "generation": c.generation,
                "birth_time": time,
                "max_speed": c.max_speed,
                "max_turn_rate": c.max_turn_rate,
                "radius": c.radius,
                "min_energy_to_reproduce": c.min_energy_to_reproduce,
                "min_time_between_reproducing": c.min_time_between_reproducing,
                "viewable_distance": c.viewable_distance,
                "viewable_angle": c.viewable_angle,
                "num_brain_nodes": len(c.brain.nodes),
                "num_brain_connections": len(c.brain.connections.keys())
        })

    def mark_creature_dead(self, creature_id, time):
        self.conn.execute(
            """ UPDATE creatures SET death_time = ? WHERE id = ? """,
            (time, creature_id)
        )

    def update_real_time(self, time, num_creatures, num_food):
        self.conn.execute(
            """ INSERT INTO real_time_stats VALUES (?, ?, ?) """,
            (time, num_creatures, num_food)
        )

    def save(self):
        os.makedirs("data", exist_ok=True)  

        creatures_df = pd.read_sql("SELECT * FROM creatures", self.conn)
        creatures_df.to_csv("data/creatures.csv")

        real_time_stats_df = pd.read_sql("SELECT * FROM real_time_stats", self.conn)
        real_time_stats_df.to_csv("data/real_time_stats.csv")

    def close(self):
        self.save()
        self.conn.close()