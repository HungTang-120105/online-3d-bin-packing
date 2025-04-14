from src.core.bin import Bin
from src.core.box import Box
import copy
from src.utils.visualization import animate_bin_packing
import numpy as np

class BestFit:
    def __init__(self, binsize = (1.0, 1.0, 1.0)):
        self.W, self.H, self.D = binsize
        self.bin = Bin(self.W, self.H, self.D, id=0)
        self.frames = []
        self.boxes = []
        self.placed_boxes = []
    
    """
    step 1: Tạo một danh sách các vị trí có thể đặt box
    step 2: Tìm vị trí tốt nhất cho box mới dựa trên các vị trí đã có
    step 3: Nếu không tìm thấy vị trí nào thì không thể đặt box
    step 4: Nếu tìm thấy vị trí tốt nhất thì đặt box vào vị trí đó
    step 5: Lưu trạng thái hiện tại của bin sau khi đặt box
    step 6: Trả về True nếu đặt thành công, ngược lại trả về False
    """

    def fit_score_1(self, box: Box, x: int, y: int) -> float:
        z = self._get_z_base(box, x, y)
        return (self.W - (x + box.w)) * (self.H - (y + box.h)) * (self.D - (z + box.d))
    
    def fit_score_2(self, box: Box, x: int, y: int) -> float:
        z = self._get_z_base(box, x, y)
        return np.max(self.bin.heightmap) + (z + box.d)
    
    def _get_z_base(self, box: Box, x: int, y: int) -> float:
        region = self.bin.heightmap[y:y+box.h, x:x+box.w]
        return float(np.max(region))

    def evaluate_fit_score(self, box: Box, x: int, y: int, lamda: float) -> float:
        return lamda * self.fit_score_1(box, x, y) + (1 - lamda) * self.fit_score_2(box, x, y)

    def place_box(self, box: Box, lamda=0.5):
        best_position = None
        best_score = float('inf')

        for x in range(0, self.W - box.w + 1):
            for y in range(0, self.H - box.h + 1):
                if self.bin.can_place(box, x, y):
                    score = self.evaluate_fit_score(box, x, y, lamda)
                    if score < best_score:
                        best_score = score
                        best_position = (x, y)

        if best_position:
            x, y = best_position
            z = self._get_z_base(box, x, y)
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

