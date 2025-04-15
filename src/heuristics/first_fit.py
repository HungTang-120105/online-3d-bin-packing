from src.core.bin import Bin
from src.core.box import Box
from src.utils.visualization import animate_bin_packing
import copy
import itertools


class FirstFitPacker:
    def __init__(self, bin_size=(1.0, 1.0, 1.0)):
        self.W, self.H, self.D = bin_size
        self.bin = Bin(self.W, self.H, self.D, id=0)
        self.frames = []

    def get_all_rotations(self, box: Box):
        # Trả về tất cả hoán vị (w, h, d) không trùng nhau
        dims = [box.w, box.h, box.d]
        return list(set(itertools.permutations(dims)))

    def place_box(self, box: Box):
        for y in range(self.H):
            for x in range(self.W):
                for rotation in self.get_all_rotations(box):
                    if self.bin.can_place(box, x, y, rotation=rotation):
                        placed_box = self.bin.place(box, x, y, rotation=rotation)
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
