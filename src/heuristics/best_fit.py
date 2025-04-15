import itertools
import copy
import numpy as np
from src.core.bin import Bin
from src.core.box import Box
from src.utils.visualization import animate_bin_packing

class BestFit:
    def __init__(self, binsize=(1.0, 1.0, 1.0)):
        self.W, self.H, self.D = binsize
        self.bin = Bin(self.W, self.H, self.D, id=0)
        self.frames = []

    def _get_z_base(self, w: int, h: int, x: int, y: int) -> float:
        region = self.bin.heightmap[y:y+h, x:x+w]
        return float(np.max(region))

    def fit_score_1(self, w: int, h: int, d: int, x: int, y: int, z: float) -> float:
        return (self.W - (x + w)) * (self.H - (y + h)) * (self.D - (z + d))

    def fit_score_2(self, d: int, z: float) -> float:
        return np.max(self.bin.heightmap) + (z + d)

    def evaluate_fit_score(self, w, h, d, x, y, z, lamda) -> float:
        return lamda * self.fit_score_1(w, h, d, x, y, z) + (1 - lamda) * self.fit_score_2(d, z)

    def place_box(self, box: Box, lamda=0.5):
        best_position = None
        best_score = float('inf')
        best_rotation = None

        for rotation in set(itertools.permutations([box.w, box.h, box.d])):
            rw, rh, rd = rotation

            for x in range(0, self.W - rw + 1):
                for y in range(0, self.H - rh + 1):
                    z = self._get_z_base(rw, rh, x, y)

                    if self.bin.can_place(box, x, y, rotation=rotation):
                        score = self.evaluate_fit_score(rw, rh, rd, x, y, z, lamda)
                        if score < best_score:
                            best_score = score
                            best_position = (x, y)
                            best_rotation = rotation

        if best_position:
            x, y = best_position
            self.bin.place(box, x, y, rotation=best_rotation)
            self.frames.append(copy.deepcopy(self.bin.boxes))
            return True

        return False

    def get_placed_boxes(self):
        return self.bin.boxes

    def animate(self):
        animate_bin_packing(self.frames, self.W, self.H, self.D)

    def utilization(self):
        total_volume = self.W * self.H * self.D
        used_volume = sum(box.w * box.h * box.d for box in self.bin.boxes)
        return used_volume / total_volume if total_volume > 0 else 0.0
