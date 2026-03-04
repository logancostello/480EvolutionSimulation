import math
from collections import defaultdict


class SpatialHashGrid:
    def __init__(self, cell_size: float):
        self.cell_size = float(cell_size)  # How many px are in each grid cell
        self.inv = 1.0 / self.cell_size  # used to multiply instead of divide
        self.cells = defaultdict(list)  # list of creatures in grid cell
        self.touched = []  # list of keys used this frame
        self._touched_set = set()  # prevents duplicates

    def _cell_coords(self, x: float, y: float):
        """Accepts a world position and returns a grid cell coordinate."""
        return math.floor(x * self.inv), math.floor(y * self.inv)

    def _key(self, cx: int, cy: int):
        return cx, cy

    def clear_frame(self):
        """Clears all cells used last frame."""
        for k in self.touched:
            self.cells[k].clear()
        self.touched.clear()
        self._touched_set.clear()

    def insert(self, creature, x: float, y: float):
        """Accepts a creature object and places it in a grid cell."""
        cx, cy = self._cell_coords(x, y)
        k = self._key(cx, cy)

        if k not in self._touched_set:
            self._touched_set.add(k)
            self.touched.append(k)

        self.cells[k].append(creature)

    def query_rectangle(self, min_x: float, min_y: float, max_x: float, max_y: float):
        """Accepts a rectangular area and returns all creatures inside."""
        cell_min_x, cell_min_y = self._cell_coords(min_x, min_y)
        cell_max_x, cell_max_y = self._cell_coords(max_x, max_y)

        out = []
        for cy in range(cell_min_y, cell_max_y + 1):
            for cx in range(cell_min_x, cell_max_x + 1):
                out.extend(self.cells.get((cx, cy), ()))
        return out
