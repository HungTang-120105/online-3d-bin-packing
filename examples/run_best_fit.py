from src.heuristics.best_fit import BestFitBufferPacker
from src.core.box import Box
from src.utils.generatorBPP import generatorBPP

# Khởi tạo generator và sinh dữ liệu
generator = generatorBPP()
generator._generator_1(numOfBox=100, bin_size=[10, 10, 10], seed=42)

# Tạo danh sách các box từ dữ liệu đã sinh
boxes = [Box(*box_size) for box_size in generator.box_size]

# Khởi tạo packer với buffer_size và danh sách box
packer = BestFitBufferPacker(binsize=tuple(generator.bin_size), buffer_size=6, boxes=boxes)

# Chạy thuật toán đặt box
packer.pack_all_boxes()

# In tỷ lệ sử dụng không gian
print(f"Utilization: {packer.utilization():.2%}")

# Trực quan hóa kết quả
packer.animate()

