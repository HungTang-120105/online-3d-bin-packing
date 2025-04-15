import itertools
import copy
import numpy as np
from src.core.bin import Bin
from src.core.box import Box
from src.utils.visualization import animate_bin_packing

class BottomLeftBackBufferPacker:
    def __init__(self, binsize=(1.0, 1.0, 1.0), buffer_size=5, boxes=[]):
        self.W, self.H, self.D = binsize
        self.bin = Bin(self.W, self.H, self.D, id=0)
        self.frames = []          # Lưu trạng thái của bin sau mỗi lần đặt box
        self.buffer = []          # Buffer chứa các box không đặt được ngay
        self.buffer_size = buffer_size
        self.boxes = boxes        # Danh sách các box cần đặt

    def get_all_rotations(self, box: Box):
        """Trả về tất cả hoán vị (w, h, d) không trùng nhau của box."""
        dims = [box.w, box.h, box.d]
        return list(set(itertools.permutations(dims)))

    def evaluate_candidate(self, box: Box):
        """
        Với một box cho trước, duyệt qua tất cả các hướng xoay và vị trí (x, y)
        để tìm vị trí đặt khả thi với thông số tối ưu theo tiêu chí Bottom-Left-Back.
        Tiêu chí được biểu diễn dưới dạng tuple (z, x, y) – càng nhỏ càng tốt.
        Trả về một tuple:
            ( (z, x, y, rotation), candidate_found )
        Nếu không tìm được candidate khả thi, trả về None.
        """
        best_candidate = None  # candidate: (z, x, y, rotation)
        for rotation in self.get_all_rotations(box):
            rw, rh, rd = rotation
            for x in range(0, self.W - rw + 1):
                for y in range(0, self.H - rh + 1):
                    region = self.bin.heightmap[y:y+rh, x:x+rw]
                    z = float(np.max(region))
                    # Kiểm tra xem box với kích thước (rw, rh, rd) có thể đặt được tại (x, y, z) không
                    if self.bin.can_place(box, x, y, rotation=rotation):
                        candidate = (z, x, y, rotation)
                        if best_candidate is None:
                            best_candidate = candidate
                        else:
                            # So sánh theo tiêu chí: z (bottom), sau đó x (left), sau đó y (back)
                            if (candidate[0] < best_candidate[0] or
                               (candidate[0] == best_candidate[0] and candidate[1] < best_candidate[1]) or
                               (candidate[0] == best_candidate[0] and candidate[1] == best_candidate[1] and candidate[2] < best_candidate[2])):
                                best_candidate = candidate
        return best_candidate

    def place_box(self, incoming_box: Box):
        """
        Ở mỗi bước, xem xét tất cả các box:
           - Box incoming_box (box hiện tại cần đặt)
           - Các box có trong buffer
        Sau đó, chọn ra candidate có thông số Bottom-Left-Back tốt nhất để đặt.
        Nếu candidate được tìm thấy, đặt box đó (với hướng xoay đã chọn).
        Nếu incoming_box không được đặt và chưa có trong buffer, thêm vào buffer (nếu còn chỗ).
        Trả về True nếu có box được đặt ở bước này, ngược lại False.
        """
        candidates = []  # Danh sách candidate: mỗi phần tử là tuple (candidate, box)
        
        # Đánh giá candidate cho incoming_box
        candidate = self.evaluate_candidate(incoming_box)
        if candidate is not None:
            candidates.append((candidate, incoming_box))
        
        # Đánh giá candidate cho các box trong buffer
        new_buffer = []
        for buf_box in self.buffer:
            cand_buf = self.evaluate_candidate(buf_box)
            if cand_buf is not None:
                candidates.append((cand_buf, buf_box))
            else:
                new_buffer.append(buf_box)
        # Cập nhật buffer với những box không có candidate khả thi ngay hiện tại
        self.buffer = new_buffer

        if candidates:
            # Chọn candidate tốt nhất (so sánh theo tuple (z, x, y))
            candidates.sort(key=lambda c: (c[0][0], c[0][1], c[0][2]))
            best_candidate, chosen_box = candidates[0]
            z, x, y, rotation = best_candidate
            self.bin.place(chosen_box, x, y, rotation=rotation)
            self.frames.append(copy.deepcopy(self.bin.boxes))
            # Nếu box được chọn nằm trong buffer, loại bỏ nó khỏi buffer
            if chosen_box in self.buffer:
                self.buffer.remove(chosen_box)
            return True
        else:
            # Không tìm được candidate nào khả thi: thêm incoming_box vào buffer nếu chưa có và còn chỗ
            if incoming_box not in self.buffer and len(self.buffer) < self.buffer_size:
                self.buffer.append(incoming_box)
            # else:
                # print(f"Buffer đầy, không thể đặt box {incoming_box.id}")
            return False

    def pack_all_boxes(self):
        """
        Đặt toàn bộ các box có trong danh sách self.boxes vào bin.
        Ở mỗi bước, thuật toán xét union của (box incoming) và các box trong buffer.
        Dừng khi đã duyệt hết danh sách hoặc khi buffer đã đầy và không thể đặt được box nào thêm.
        """
        i = 0
        while i < len(self.boxes):
            box = self.boxes[i]
            placed = self.place_box(box)
            i += 1  # Chuyển sang box tiếp theo

            if not placed:
                # Nếu buffer đạt kích thước tối đa, thử duyệt lại buffer một lượt:
                if len(self.buffer) >= self.buffer_size:
                    any_placed = False
                    for buf_box in self.buffer[:]:
                        if self.place_box(buf_box):
                            any_placed = True
                    if not any_placed:
                        # print("Dừng lại: Buffer đầy và không thể đặt được thêm box nào.")
                        break

    def get_placed_boxes(self):
        return self.bin.boxes

    def get_buffered_boxes(self):
        return self.buffer

    def animate(self):
        animate_bin_packing(self.frames, self.W, self.H, self.D)

    def utilization(self):
        total_volume = self.W * self.H * self.D
        used_volume = sum(box.w * box.h * box.d for box in self.bin.boxes)
        return used_volume / total_volume if total_volume > 0 else 0.0
