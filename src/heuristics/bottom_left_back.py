from src.core.bin import Bin
from src.core.box import Box
import copy
from src.utils.visualization import animate_bin_packing

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
                for z in range(0, bin.D - box.d + 1):
                    if self.bin.can_place(box, x, y, z):
                        if best_position is None:
                            best_position = (x, y, z)
                        else:
                            xb, yb, zb = best_position
                            if x < xb or (x == xb and y < yb) or (x == xb and y == yb and z < zb):
                                best_position = (x, y, z)
        if best_position:
            x, y, z = best_position
            self.bin.place(box, x, y, z)
            print(f" Box {box.id} placed at ({x}, {y}, {z})")
            # Lưu trạng thái hiện tại (deepcopy để tránh bị thay đổi sau)
            self.frames.append(copy.deepcopy(self.bin.boxes))
            return True
        
        print(f" Box {box.id} cannot be placed")
        return False
    
    def get_placed_boxes(self):
        return self.bin.boxes

    def animate(self):
        animate_bin_packing(self.frames, self.W, self.H, self.D)

    def utilization(self):
        total_volume = self.W * self.H * self.D
        used_volume = sum(box.w * box.h * box.d for box in self.bin.boxes)
        return used_volume / total_volume if total_volume > 0 else 0.0
        
