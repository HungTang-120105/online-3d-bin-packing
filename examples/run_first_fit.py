from src.heuristics.first_fit import FirstFitPacker
from src.core.box import Box

packer = FirstFitPacker(bin_size=(5, 5, 5))

boxes = [
    Box(2, 2, 2, id=0),
    Box(1, 2, 2, id=1),
    Box(3, 3, 1, id=2),
    Box(3, 3, 3, id=3),
    Box(2, 2, 2, id=4),
    Box(5, 5, 5, id=5),
]

for box in boxes:
    packer.place_box(box)

packer.animate()  # Tạo animation
