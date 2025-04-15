class Box:
    def __init__(self, w, h, d, id=None):
        """
        Khởi tạo box với chiều rộng (w), chiều cao (h), và chiều sâu (d)
        """
        self.w = w
        self.h = h
        self.d = d
        self.id = id
        self.x = None
        self.y = None
        self.z = None
        self.placed = False
        self.original_dim = (w, h, d)

    def get_orientations(self):
        w, h, d = self.original_dim
        return [(w, h, d), (w, d, h), (h, w, d), (h, d, w), (d, w, h), (d, h, w)]


class PlacedBox(Box):
    def __init__(self, w, h, d, x, y, z, id=None):
        """
        PlacedBox kế thừa Box và có thêm thông tin vị trí (x, y, z) trong bin.
        """
        super().__init__(w, h, d, id)
        self.x = x
        self.y = y
        self.z = z

    def get_bounds(self):
        """Trả về tọa độ giới hạn: (x1, x2, y1, y2, z1, z2)"""
        return (self.x, self.x + self.w, self.y, self.y + self.h, self.z, self.z + self.d)
    
    
