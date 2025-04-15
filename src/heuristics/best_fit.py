import itertools
import copy
import numpy as np
from src.core.bin import Bin
from src.core.box import Box
from src.utils.visualization import animate_bin_packing

class BestFitBufferPacker:
    def __init__(self, binsize=(1.0, 1.0, 1.0), buffer_size=5, boxes=[]):
        self.W, self.H, self.D = binsize
        self.bin = Bin(self.W, self.H, self.D, id=0)
        self.frames = []          # Lưu trạng thái (danh sách các box đã đặt) sau mỗi bước
        self.buffer = []          # Buffer chứa các box không đặt được ngay
        self.buffer_size = buffer_size
        self.boxes = boxes        # Danh sách các box cần đặt

    def get_all_rotations(self, box: Box):
        """
        Trả về tất cả các hoán vị (w, h, d) không trùng nhau của box.
        """
        dims = [box.w, box.h, box.d]
        return list(set(itertools.permutations(dims)))

    def evaluate_fit_score(self, w, h, d, x, y, z, lamda) -> float:
        """
        Điểm đánh giá vị trí đặt box với kích thước (w,h,d) tại vị trí (x,y) với z-base = z.
        Sử dụng trọng số lamda để kết hợp hai tiêu chí:
         - Không gian trống còn lại.
         - Chiều cao của bề mặt hiện tại.
        """
        score1 = (self.W - (x + w)) * (self.H - (y + h)) * (self.D - (z + d))
        score2 = np.max(self.bin.heightmap) + (z + d)
        return lamda * score1 + (1 - lamda) * score2

    def evaluate_candidate(self, box: Box, lamda=0.5):
        """
        Với một box cho trước, duyệt qua tất cả các hướng xoay và vị trí (x,y)
        để tìm vị trí đặt khả thi với điểm đánh giá tốt nhất.
        Nếu box có thể được đặt, trả về tuple:
            (best_score, (x, y, z, rotation))
        Nếu không box nào khả thi, trả về None.
        """
        best_score = float('inf')
        best_params = None

        for rotation in self.get_all_rotations(box):
            rw, rh, rd = rotation
            for x in range(0, self.W - rw + 1):
                for y in range(0, self.H - rh + 1):
                    region = self.bin.heightmap[y:y+rh, x:x+rw]
                    z = float(np.max(region))
                    # Kiểm tra khả năng đặt dựa trên heightmap và rotation
                    if self.bin.can_place(box, x, y, rotation=rotation):
                        score = self.evaluate_fit_score(rw, rh, rd, x, y, z, lamda)
                        if score < best_score:
                            best_score = score
                            best_params = (x, y, z, rotation)
        if best_params is not None:
            return best_score, best_params
        else:
            return None

    def place_box(self, incoming_box: Box, lamda=0.5):
        """
        Ở mỗi bước, thuật toán xem xét **tất cả** các box bao gồm:
          - Box hiện tại (incoming_box)
          - Các box đang trong buffer
        Sau đó, chọn ra candidate box có điểm đánh giá (best fit score) thấp nhất để đặt.
        Nếu một candidate được tìm thấy, đặt box đó và xóa khỏi buffer (nếu có).
        Nếu incoming_box không được chọn và không thể đặt được, thêm vào buffer (nếu còn chỗ).
        """
        candidates = []  # Mỗi phần tử: (score, best_params, box)
        # Đánh giá incoming_box
        candidate = self.evaluate_candidate(incoming_box, lamda)
        if candidate is not None:
            candidates.append((candidate[0], candidate[1], incoming_box))

        # Đánh giá các box trong buffer
        new_buffer = []
        for buf_box in self.buffer:
            cand_buf = self.evaluate_candidate(buf_box, lamda)
            if cand_buf is not None:
                candidates.append((cand_buf[0], cand_buf[1], buf_box))
            else:
                new_buffer.append(buf_box)
        # Cập nhật buffer với các box không thể đặt được hiện nay
        self.buffer = new_buffer

        if candidates:
            # Chọn candidate với điểm đánh giá thấp nhất
            candidates.sort(key=lambda c: c[0])
            best_score, (x, y, z, rotation), chosen_box = candidates[0]
            # Đặt box được chọn vào bin
            self.bin.place(chosen_box, x, y, rotation=rotation)
            self.frames.append(copy.deepcopy(self.bin.boxes))
            # Nếu candidate được chọn là từ buffer, loại bỏ nó khỏi buffer
            if chosen_box in self.buffer:
                self.buffer.remove(chosen_box)
            return True
        else:
            # Không có candidate nào có thể đặt được.
            # Nếu incoming_box không được đặt, thử thêm nó vào buffer (nếu chưa có và còn chỗ)
            if incoming_box not in self.buffer and len(self.buffer) < self.buffer_size:
                self.buffer.append(incoming_box)
            # else:
            #     print(f"Buffer đầy, không thể đặt box {incoming_box.id}")
            return False

    def pack_all_boxes(self, lamda=0.5):
        """
        Đặt toàn bộ các box trong danh sách self.boxes vào bin.
        Ở mỗi bước, xét union của (box hiện tại) và các box trong buffer.
        Thuật toán dừng lại nếu buffer đầy và không thể đặt được box nào thêm.
        """
        i = 0
        while i < len(self.boxes):
            box = self.boxes[i]
            placed = self.place_box(box, lamda)
            # Nếu đặt được, chuyển sang box tiếp theo.
            # Nếu không, vẫn tăng chỉ số (một số box sẽ được đưa vào buffer)
            i += 1

            if not placed:
                # Nếu buffer đã đầy và không thể đặt thêm box nào từ buffer, dừng thuật toán.
                if len(self.buffer) >= self.buffer_size:
                    any_placed = False
                    for buf_box in self.buffer[:]:
                        if self.place_box(buf_box, lamda):
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
