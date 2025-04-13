from src.core.bin import Bin
from src.core.box import Box
import copy
from src.utils.visualization import animate_bin_packing

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

    def fit_score_1(self, box: Box, x: float, y: float, z: float) -> float:
        return (self.W - (x + box.w)) * (self.H - (y + box.h)) * (self.D - (z + box.d))
    
    def fit_score_2(self, box: Box, x: float, y: float, z: float) -> float:
        return max([b.z + b.d for b in self.bin.boxes]) + (z + box.d) if self.bin.boxes else 0
    
    def evaluate_fit_score(self, box: Box, x: float, y: float, z: float, lamda) -> float:
        # Tính toán điểm cho vị trí (x, y, z) dựa trên kích thước của box
        return lamda * self.fit_score_1(box, x, y, z) + (1 - lamda) * self.fit_score_2(box, x, y, z)
    
    def place_box(self, box: Box, lamda=0.5):
        candidate_positions = [(0, 0, 0)]
            
        for placed in self.bin.boxes:
            candidate_positions.extend([
                (placed.x + placed.w, placed.y, placed.z),
                (placed.x, placed.y + placed.h, placed.z),
                (placed.x, placed.y, placed.z + placed.d),
            ])

        best_position = None
        best_score = float('inf')

        for (x, y, z) in candidate_positions:
            if self.bin.can_place(box, x, y, z):
                score = self.evaluate_fit_score(box, x, y, z, lamda)
                if score < best_score:
                    best_score = score
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

