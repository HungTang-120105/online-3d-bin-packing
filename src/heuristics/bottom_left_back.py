from src.core.bin import Bin
from src.core.box import Box
import copy
from src.utils.visualization import animate_bin_packing
import numpy as np
import itertools


class BTB:
    def __init__(self, binsize = (1.0, 1.0, 1.0)):
        self.W, self.H, self.D = binsize
        self.bin = Bin(self.W, self.H, self.D, id=0)
        self.frames = []
        self.boxes = []
        self.placed_boxes = []

    def place_box(self, box: Box):
        bin = self.bin
        best_position = None
        best_rotation = None

        # Tạo tất cả các hướng xoay (w, h, d)
        for rotation in set(itertools.permutations([box.w, box.h, box.d])):
            rw, rh, rd = rotation

            # Duyệt các vị trí khả thi trên mặt phẳng XY
            for x in range(0, bin.W - rw + 1):
                for y in range(0, bin.H - rh + 1):
                    # Lấy z-base từ heightmap
                    region = bin.heightmap[y:y+rh, x:x+rw]
                    z_base = region.max()

                    # Kiểm tra có thể đặt box với kích thước đã xoay không
                    if bin.can_place(box, x, y, rotation=rotation):
                        if best_position is None:
                            best_position = (x, y, z_base)
                            best_rotation = rotation
                        else:
                            xb, yb, zb = best_position
                            if z_base < zb or (z_base == zb and x < xb) or (z_base == zb and x == xb and y < yb):
                                best_position = (x, y, z_base)
                                best_rotation = rotation

        if best_position:
            x, y, _ = best_position
            bin.place(box, x, y, rotation=best_rotation)
            self.frames.append(copy.deepcopy(bin.boxes))
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
        
