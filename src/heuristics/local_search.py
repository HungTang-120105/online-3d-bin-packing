import numpy as np
import itertools
import random
from src.core.bin import Bin
from src.core.box import Box, PlacedBox
from src.utils.visualization import animate_bin_packing

class LocalSearchRepacker:
    def __init__(self, binsize=(10, 10, 10), buffer_size=5, boxes=[]):
        """
        binsize: Kích thước của bin (W, H, D).
        buffer_size: Số lượng tối đa box có thể đưa vào buffer.
        boxes: Danh sách các box ban đầu (đối tượng Box).
        """
        self.W, self.H, self.D = binsize
        self.buffer_size = buffer_size
        self.initial_boxes = boxes[:]  # lưu danh sách box ban đầu
        # Lưu các trạng thái của bin để visualize nếu cần.
        self.frames = []  

    def get_all_rotations(self, box):
        """Trả về tất cả các hoán vị (w, h, d) không trùng nhau của box."""
        dims = [box.w, box.h, box.d]
        return list(set(itertools.permutations(dims)))

    def pack_solution(self, sequence):
        """
        Xếp các box theo thứ tự của sequence sử dụng thuật toán BLB.
        Quét theo thứ tự từ trên xuống và trái sang phải.
        Nếu không thể đặt box nào đó, cho box đó vào buffer.
        Trả về đối tượng bin đã xếp và danh sách buffer.
        """
        bin_instance = Bin(self.W, self.H, self.D, id=0)
        buffer = []
        # Đặt lại các frame để lưu lại trạng thái của bin nếu cần visualize.
        self.frames = []
        for box in sequence:
            placed = False
            # Quét qua các vị trí (x, y) trên bin
            for y in range(self.H):
                for x in range(self.W):
                    for rotation in self.get_all_rotations(box):
                        if bin_instance.can_place(box, x, y, rotation=rotation):
                            bin_instance.place(box, x, y, rotation=rotation)
                            placed = True
                            self.frames.append(bin_instance.heightmap.copy())
                            break
                    if placed:
                        break
                if placed:
                    break
            if not placed:
                buffer.append(box)
        return bin_instance, buffer

    def utilization(self, bin_instance):
        """Tính toán tỷ lệ sử dụng không gian của bin."""
        vol_box = sum(p.w * p.h * p.d for p in bin_instance.boxes)
        vol_bin = self.W * self.H * self.D
        return vol_box / vol_bin

    def evaluate_solution(self, sequence):
        """
        Đánh giá một solution bằng cách xếp box theo sequence 
        và tính tỷ lệ sử dụng (utilization).
        """
        bin_instance, _ = self.pack_solution(sequence)
        return self.utilization(bin_instance)

    def is_accessible(self, placed_box, bin_instance):
        """
        Kiểm tra liệu box đã được đặt (placed_box) có "accessible" 
        theo điều kiện của robot không.
        Điều kiện mẫu: box được xem là accessible nếu vị trí z của box
        bằng giá trị cao nhất (max) trong vùng heightmap mà box chiếm.
        """
        x, y, z = placed_box.x, placed_box.y, placed_box.z
        w, h, d = placed_box.w, placed_box.h, placed_box.d
        region = bin_instance.heightmap[y:y+h, x:x+w]
        # Nếu box có z bằng max của khu vực đó, ta coi nó có thể lấy ra được.
        if z == np.max(region):
            return True
        return False

    def get_accessible_indices(self, sequence):
        """
        Xếp lại solution hiện tại, sau đó trả về danh sách các chỉ số
        của box mà cánh tay robot có thể dễ dàng lấy ra (accessible).
        Để kiểm tra, ta xếp solution hiện tại và duyệt qua từng box đã đặt.
        """
        bin_instance, _ = self.pack_solution(sequence)
        accessible_indices = []
        # Ta duyệt theo thứ tự của sequence và đối chiếu với các box đã được đặt.
        # Giả sử thứ tự box trong bin_instance.boxes tương ứng với sequence.
        for i, box in enumerate(bin_instance.boxes):
            if self.is_accessible(box, bin_instance):
                accessible_indices.append(i)
        return accessible_indices

    def local_search(self, max_iter=50):
        """
        Áp dụng Local Search dựa trên thao tác: sau mỗi bước đặt,
        tìm những box accessible, loại bỏ chúng ra (cho vào buffer) rồi 
        tái xếp lại để tối ưu hóa packing hiện tại.
        Trả về solution (sequence) tốt nhất và utilization tương ứng.
        """
        # Bắt đầu từ solution ban đầu
        best_sequence = self.initial_boxes[:]
        best_util = self.evaluate_solution(best_sequence)
        print(f"Initial utilization: {best_util:.3f}")
        
        for iter in range(max_iter):
            # Xếp solution hiện tại để có đối tượng bin
            current_bin, _ = self.pack_solution(best_sequence)
            # Lấy ra danh sách các box có thể lấy ra (accessible)
            accessible_indices = self.get_accessible_indices(best_sequence)
            
            # Nếu không có box nào accessible, dừng tìm kiếm (hoặc có thể perturb toàn bộ sequence)
            if not accessible_indices:
                print("Không tìm thấy box accessible trong iteration", iter)
                break
            
            # Chọn ngẫu nhiên một vài box từ accessible_indices để loại bỏ, số lượng không vượt quá buffer_size
            num_to_remove = min(len(accessible_indices), self.buffer_size)
            indices_to_remove = random.sample(accessible_indices, k=num_to_remove)
            
            # Tạo solution candidate: loại bỏ các box được chọn
            candidate_sequence = [box for i, box in enumerate(best_sequence) if i not in indices_to_remove]
            removed_boxes = [best_sequence[i] for i in indices_to_remove]
            
            # Sau đó, sắp xếp lại removed_boxes (ví dụ: trộn ngẫu nhiên) và chèn vào đầu solution candidate
            new_order_removed = random.sample(removed_boxes, k=len(removed_boxes))
            # Tùy thuộc vào chiến lược, ta có thể chèn vào đầu, cuối hoặc xen kẽ
            new_candidate_sequence = new_order_removed + candidate_sequence
            
            # Đánh giá giải pháp candidate mới
            candidate_util = self.evaluate_solution(new_candidate_sequence)
            print(f"Iteration {iter}: candidate utilization = {candidate_util:.3f}")
            
            if candidate_util > best_util:
                best_util = candidate_util
                best_sequence = new_candidate_sequence
                print(f"--> Cải thiện utilization thành {best_util:.3f} tại iteration {iter}")
            # Nếu không cải thiện, có thể tiếp tục với vòng lặp tiếp theo để thử perturb khác
        
        return best_sequence, best_util

    def visualize_solution(self, sequence):
        """Trực quan hóa quá trình đóng gói dựa trên solution cho trước."""
        bin_instance, _ = self.pack_solution(sequence)
        animate_bin_packing(self.frames)
        

# --- Ví dụ sử dụng ---
# Tạo một số box mẫu (w, h, d) và gán id
boxes = [
    Box(3, 2, 2, id=1),
    Box(5, 3, 1, id=2),
    Box(4, 3, 3, id=3),
    Box(2, 2, 2, id=4),
    Box(3, 3, 2, id=5),
    Box(2, 4, 1, id=6)
]

# Khởi tạo Local Search Repacker với bin kích thước (10, 10, 10)
repacker = LocalSearchRepacker(binsize=(10, 10, 10), buffer_size=2, boxes=boxes)

# Thực hiện local search
best_seq, best_util = repacker.local_search(max_iter=50)
print(f"Best utilization after Local Search: {best_util:.3f}")

# Visualize solution (nếu animate_bin_packing đã được cài đặt)
# repacker.visualize_solution(best_seq)
