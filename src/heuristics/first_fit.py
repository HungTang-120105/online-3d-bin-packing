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
        candidate_positions = [(0, 0, 0)]

        for placed in self.bin.boxes:
            candidate_positions.extend([
                (placed.x + placed.w, placed.y, placed.z),
                (placed.x, placed.y + placed.h, placed.z),
                (placed.x, placed.y, placed.z + placed.d),
            ])

        for (x, y, z) in candidate_positions:
            if self.bin.can_place(box, x, y, z):
                self.bin.place(box, x, y, z)
                print(f"✅ Box {box.id} placed at ({x}, {y}, {z})")
                # Lưu trạng thái hiện tại (deepcopy để tránh bị thay đổi sau)
                self.frames.append(copy.deepcopy(self.bin.boxes))
                return True

        print(f"❌ Box {box.id} cannot be placed")
        return False

    def get_placed_boxes(self):
        return self.bin.boxes

    def animate(self):
        animate_bin_packing(self.frames, self.W, self.H, self.D)
