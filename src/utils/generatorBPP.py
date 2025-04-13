import random

class generatorBPP:
    def __init__(self):
        self.bin_size = None # example: [x : 1, y ]
        self.box_size = [] # example: [w : 1, h : 1, d : 1, id : 1]

    def _generator_1(self, numOfBox = 10, bin_size =[10, 10, 10], seed = 42):
        n = numOfBox
        random.seed(seed)
        self.bin_size = bin_size

        for i in range(n):
            if i % 3 == 0:
                # box dẹt
                w = random.choice([2, 3])
                h = random.choice([2, 3])
                d = 2
            elif i % 3 == 1:
                # box hình khối lớn
                w = h = d = random.choice([3, 4])
            else:
                # box kiểu bất kỳ
                w = random.choice([2, 3, 4,5])
                h = random.choice([2, 3, 4,5])
                d = random.choice([2, 3, 4,5])
            self.box_size.append([w, h, d, i])
        