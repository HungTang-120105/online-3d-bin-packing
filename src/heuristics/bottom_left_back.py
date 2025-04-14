from src.core.bin import Bin
from src.core.box import Box
import copy
from src.utils.visualization import animate_bin_packing
import numpy as np

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

        for x in range(0, bin.W - box.w + 1):
            for y in range(0, bin.H - box.h + 1):
                # Lấy vùng trên heightmap
                region = self.bin.heightmap[y:y+box.h, x:x+box.w]
                z_base = np.max(region)  # Chiều cao tối đa tại vùng này

                if self.bin.can_place(box, x, y):  # Kiểm tra vị trí (x, y) với z_base tính từ heightmap
                    if best_position is None:
                        best_position = (x, y, z_base)
                    else:
                        xb, yb, zb = best_position
                        if z_base < zb or (z_base == zb and x < xb) or (z_base == zb and x == xb and y < yb):
                            best_position = (x, y, z_base)

        if best_position:
            x, y, z_base = best_position
            z = z_base + box.d  # Tính z thực tế từ heightmap
            self.bin.place(box, x, y)
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
        
