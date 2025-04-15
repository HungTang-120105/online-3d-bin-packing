from src.core.bin import Bin
from src.core.box import Box
from src.utils.visualization import animate_bin_packing
import copy
import itertools
import numpy as np

class FirstFitBufferPacker:
    def __init__(self, binsize=(1.0, 1.0, 1.0), buffer_size=5, boxes=[]):
        self.W, self.H, self.D = binsize
        self.bin = Bin(self.W, self.H, self.D, id=0)
        self.frames = []           # Lưu các trạng thái của bin sau mỗi lần đặt box
        self.buffer = []           # Buffer chứa các box không đặt được
        self.buffer_size = buffer_size
        self.boxes = boxes         # Danh sách các box cần đặt

    def get_all_rotations(self, box: Box):
        """
        Trả về tất cả các hoán vị (w, h, d) không trùng nhau của box.
        """
        dims = [box.w, box.h, box.d]
        return list(set(itertools.permutations(dims)))

    def try_place_box(self, box: Box):
        """
        Cố gắng đặt box vào bin sử dụng tất cả các vị trí (x, y) và các hướng xoay.
        Nếu đặt thành công, cập nhật heightmap của bin, lưu trạng thái và trả về True.
        Nếu không đặt được, trả về False.
        """
        for y in range(self.H):
            for x in range(self.W):
                for rotation in self.get_all_rotations(box):
                    if self.bin.can_place(box, x, y, rotation=rotation):
                        placed_box = self.bin.place(box, x, y, rotation=rotation)
                        self.frames.append(copy.deepcopy(self.bin.boxes))
                        return True
        return False

    def place_box(self, box: Box):
        """
        Cố gắng đặt box vào bin.
        Nếu đặt được, sau đó kiểm tra và cố gắng đặt lại các box trong buffer.
        Nếu không đặt được, thêm box vào buffer (nếu còn chỗ).
        Nếu buffer đầy và không thể đặt box nào thì in ra thông báo.
        """
        placed = self.try_place_box(box)
        if placed:
            # Sau khi đặt box thành công, thử đặt lại các box trong buffer (theo FIFO)
            new_buffer = []
            for buffered_box in self.buffer:
                if not self.try_place_box(buffered_box):
                    new_buffer.append(buffered_box)
            self.buffer = new_buffer
            return True
        else:
            # Nếu không đặt được, thêm vào buffer nếu có chỗ trống
            if len(self.buffer) < self.buffer_size:
                self.buffer.append(box)
                return False
            else:
                # print(f"Buffer đầy, không thể đặt box {box.id}")
                return False

    def pack_all_boxes(self):
        """
        Đặt toàn bộ các box trong self.boxes vào bin.
        Mỗi lần đặt, sau đó kiểm tra lại buffer để cố gắng đặt các box bị treo.
        Thuật toán dừng lại khi buffer đã đầy và không thể đặt được thêm bất kỳ box nào.
        """
        i = 0
        while i < len(self.boxes):
            box = self.boxes[i]
            placed = self.place_box(box)

            if placed:
                # Nếu box hiện tại được đặt thành công, chuyển sang box tiếp theo
                i += 1
            else:
                # Nếu không đặt được và buffer đã đầy, hãy thử một lượt lại toàn bộ buffer
                if len(self.buffer) >= self.buffer_size:
                    any_placed = False
                    new_buffer = []
                    for buf_box in self.buffer:
                        if self.try_place_box(buf_box):
                            any_placed = True
                        else:
                            new_buffer.append(buf_box)
                    self.buffer = new_buffer
                    if not any_placed:
                        # print("Dừng lại: Buffer đầy và không thể đặt được thêm box nào.")
                        break
                else:
                    # Nếu không đặt được nhưng buffer chưa đầy, chuyển sang box tiếp theo
                    i += 1

    def get_placed_boxes(self):
        """
        Trả về danh sách các box đã được đặt thành công trong bin.
        """
        return self.bin.boxes

    def get_buffered_boxes(self):
        """
        Trả về danh sách các box đang chờ trong buffer.
        """
        return self.buffer

    def animate(self):
        """
        Sử dụng hàm animate_bin_packing để trực quan hóa quá trình đặt box.
        """
        animate_bin_packing(self.frames, self.W, self.H, self.D)

    def utilization(self):
        """
        Tính phần trăm thể tích của bin đã được sử dụng.
        """
        total_volume = self.W * self.H * self.D
        used_volume = sum(box.w * box.h * box.d for box in self.bin.boxes)
        return used_volume / total_volume if total_volume > 0 else 0.0
