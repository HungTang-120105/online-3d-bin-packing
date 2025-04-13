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

        - Box không vượt ngoài kích thước bin.
        - Box không va chạm với các box đã đặt.
        - Box phải được đỡ từ dưới nếu không nằm trên đáy.
        - Phần đỡ (diện tích tiếp xúc) phải chiếm ít nhất 50% diện tích đáy box.
        - Không có box nào đã đặt nằm phía trên (theo trục Z) box mới.
        """

        # 1. Kiểm tra vượt quá kích thước bin
        if x + box.w > self.W or y + box.h > self.H or z + box.d > self.D:
            return False

        # 2. Kiểm tra va chạm với các box đã đặt
        for placed in self.boxes:
            bx1, bx2, by1, by2, bz1, bz2 = placed.get_bounds()

            if not (x + box.w <= bx1 or x >= bx2 or
                    y + box.h <= by1 or y >= by2 or
                    z + box.d <= bz1 or z >= bz2):
                return False

        # 3. Kiểm tra không có box nào đã đặt nằm phía trên box mới (theo trục Z)
        for placed in self.boxes:
            bx1, bx2, by1, by2, bz1, bz2 = placed.get_bounds()

            # Nếu box đã đặt giao với vùng phía trên box mới
            if not (x + box.w <= bx1 or x >= bx2 or
                    y + box.h <= by1 or y >= by2 ) and (z <= bz1):  # Giao với vùng z > z + box.d
                return False

        # 4. Kiểm tra nếu box được đỡ từ dưới (nếu không đặt trên đáy)
        if z > 0:  # z là trục chiều cao
            supported_area = 0
            base_area = box.w * box.h  # vì mặt đáy nằm trên mặt phẳng XY

            for placed in self.boxes:
                px1, px2, py1, py2, pz1, pz2 = placed.get_bounds()

                if z == pz2:
                    overlap_x = max(0, min(x + box.w, px2) - max(x, px1))
                    overlap_y = max(0, min(y + box.h, py2) - max(y, py1))
                    supported_area += overlap_x * overlap_y

            if supported_area < 0.5 * base_area:
                return False

        return True




    def place(self, box, x, y, z) -> PlacedBox:
        """Nếu hợp lệ, đặt box vào bin tại vị trí (x, y, z)"""
        new_box = PlacedBox(box.w, box.h, box.d, x, y, z, id=box.id)
        self.boxes.append(new_box)
        return new_box
