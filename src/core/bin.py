from src.core.box import PlacedBox
import numpy as np

class Bin:
    def __init__(self, W, H, D, id):
        """
        Khởi tạo bin với kích thước (W, H, D).
        """
        self.W = W
        self.H = H
        self.D = D
        self.id = id
        self.boxes = []

        self.heightmap = np.zeros((self.H, self.W), dtype=np.int32)  # [y][x] = max z tại (x, y)


    def can_place(self, box, x, y):
        if x + box.w > self.W or y + box.h > self.H:
            return False

        # Lấy vùng trên heightmap
        region = self.heightmap[y:y+box.h, x:x+box.w]
        z_base = np.max(region)

        # 1. Vượt quá chiều cao bin?
        if z_base + box.d > self.D:
            return False

        # 2. Kiểm tra support từ dưới: ít nhất 60% diện tích có mặt phẳng đỡ ngay dưới
        if z_base > 0:
            supported = (region == z_base).astype(np.float32)
            support_ratio = supported.sum() / (box.w * box.h)
            if support_ratio < 0.6:
                return False

        return True


    def place(self, box, x, y):
        region = self.heightmap[y:y+box.h, x:x+box.w]
        z_base = np.max(region)

        if z_base + box.d > self.D:
            raise ValueError("Vượt quá chiều cao bin")

        new_box = PlacedBox(box.w, box.h, box.d, x, y, z_base, id=box.id)
        self.boxes.append(new_box)

        # Cập nhật heightmap
        self.heightmap[y:y+box.h, x:x+box.w] = z_base + box.d

        return new_box

    