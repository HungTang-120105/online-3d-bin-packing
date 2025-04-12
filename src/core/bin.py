from src.core.box import PlacedBox

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

    def can_place(self, box, x, y, z):
        """
        Kiểm tra xem có thể đặt box tại vị trí (x, y, z) trong bin không.
        - Kiểm tra xem box có vượt ngoài kích thước của bin không.
        - Kiểm tra va chạm với các box đã đặt.
        """
        if x + box.w > self.W or y + box.h > self.H or z + box.d > self.D:
            return False

        for placed in self.boxes:
            bx1, bx2, by1, by2, bz1, bz2 = placed.get_bounds()
            # Nếu box mới giao nhau với một box đã đặt
            if not (x + box.w <= bx1 or x >= bx2 or
                    y + box.h <= by1 or y >= by2 or
                    z + box.d <= bz1 or z >= bz2):
                return False
        return True

    def place(self, box, x, y, z) -> PlacedBox:
        """Nếu hợp lệ, đặt box vào bin tại vị trí (x, y, z)"""
        new_box = PlacedBox(box.w, box.h, box.d, x, y, z, id=box.id)
        self.boxes.append(new_box)
        return new_box
