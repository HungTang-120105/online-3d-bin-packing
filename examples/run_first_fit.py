from src.heuristics.first_fit import FirstFitPacker
from src.core.box import Box
from src.utils.generatorBPP import generatorBPP

generator = generatorBPP()
generator._generator_1(numOfBox=100, bin_size=[10, 10, 10], seed=42)

packer = FirstFitPacker(tuple(generator.bin_size))


boxes = [ Box(*(box_size)) for box_size in generator.box_size ]

for box in boxes:
    if not packer.place_box(box):
        break


print(f" Utilization: {packer.utilization()}") # Tính toán tỷ lệ sử dụng không gian

packer.animate()  # Tạo animation
