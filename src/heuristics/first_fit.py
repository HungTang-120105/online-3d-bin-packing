from src.core.bin import Bin
from src.core.box import Box
from src.utils.visualization import animate_bin_packing
import copy


class FirstFitPacker:
    def __init__(self, bin_size=(1.0, 1.0, 1.0)):
        self.W, self.H, self.D = bin_size
        self.bin = Bin(self.W, self.H, self.D, id=0)
        self.frames = []  # Lưu các trạng thái sau mỗi lần đặt box

    def place_box(self, box: Box):
        # Duyệt tất cả các vị trí khả thi trên mặt phẳng XY
        for y in range(self.H - box.h + 1):
            for x in range(self.W - box.w + 1):
                if self.bin.can_place(box, x, y):
                    placed_box = self.bin.place(box, x, y)
                    # print(f"Box {box.id} placed at ({placed_box.x}, {placed_box.y}, {placed_box.z})")
                    self.frames.append(copy.deepcopy(self.bin.boxes))
                    return True

        # print(f"Box {box.id} cannot be placed")
        return False


    def get_placed_boxes(self):
        return self.bin.boxes

    def animate(self):
        animate_bin_packing(self.frames, self.W, self.H, self.D)

    def utilization(self):
        total_volume = self.W * self.H * self.D
        used_volume = sum(box.w * box.h * box.d for box in self.bin.boxes)
        return used_volume / total_volume if total_volume > 0 else 0.0