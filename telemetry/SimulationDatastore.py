import random
import sqlite3
import pandas as pd
import os
from config import SEED, TITLE

AUTOSAVE_INTERVAL = 15 * 60  # save every 15 simulation minutes


class SimulationDatastore:
    def __init__(self):
        self.conn = sqlite3.connect(":memory:")
        self.create_tables()
        self._last_save_time = 0
        self.directory = random.randint(1, 100)
        print("Directory:" + str(self.directory))
        print(TITLE)

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
                energy_for_reproduction REAL,
                time_between_reproduction REAL,
                percent_energy_for_child REAL,
                viewable_distance REAL,
                fov REAL,
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

        cursor.execute("""
            CREATE TABLE collisions (
                time REAL,
                bigger_creature INTEGER,
                smaller_creature INTEGER,
                damage REAL          
            )
        """)

    def add_new_creature(self, c, time):
        self.conn.execute("""
            INSERT INTO creatures (id, parent, generation, birth_time, max_speed, max_turn_rate, radius, energy_for_reproduction, time_between_reproduction, percent_energy_for_child, viewable_distance, fov, num_brain_nodes, num_brain_connections)
            VALUES (:id, :parent, :generation, :birth_time, :max_speed, :max_turn_rate, :radius, :energy_for_reproduction, :time_between_reproduction, :percent_energy_for_child, :viewable_distance, :fov, :num_brain_nodes, :num_brain_connections)""",
            {
                "id": c.id,
                "parent": c.parent,
                "generation": c.generation,
                "birth_time": time,
                "max_speed": c.genome.max_speed,
                "max_turn_rate": c.genome.max_turn_rate,
                "radius": c.genome.radius,
                "energy_for_reproduction": c.genome.energy_for_reproduction,
                "time_between_reproduction": c.genome.time_between_reproduction,
                "percent_energy_for_child": c.genome.percent_energy_for_child,
                "viewable_distance": c.genome.viewable_distance,
                "fov": c.genome.fov,
                "num_brain_nodes": c.num_brain_nodes,
                "num_brain_connections": c.num_brain_connections
            })

    def mark_creature_dead(self, creature_id, time):
        self.conn.execute(
            "UPDATE creatures SET death_time = ? WHERE id = ?",
            (time, creature_id)
        )

    def update_real_time(self, time, num_creatures, num_food):
        self.conn.execute(
            "INSERT INTO real_time_stats VALUES (?, ?, ?)",
            (time, num_creatures, num_food)
        )
        self._autosave(time)

    def update_collisions(self, time, bigger_creature_id, smaller_creature_id, damage):
        self.conn.execute(
            "INSERT INTO collisions VALUES (?, ?, ?, ?)",
            (time, bigger_creature_id, smaller_creature_id, damage)
        )

    def _autosave(self, time):
        if time - self._last_save_time >= AUTOSAVE_INTERVAL:
            self.save()
            self._last_save_time = time

    def save(self):
        os.makedirs("data", exist_ok=True)
        pd.read_sql("SELECT * FROM creatures", self.conn).to_csv("data/creatures" + TITLE + str(SEED) + ".csv")
        pd.read_sql("SELECT * FROM real_time_stats", self.conn).to_csv("data/real_time_stats" + TITLE + str(SEED) + ".csv")
        pd.read_sql("SELECT * FROM collisions", self.conn).to_csv("data/collisions" + TITLE + str(SEED) + ".csv")

    def close(self):
        self.save()
        self.conn.close()