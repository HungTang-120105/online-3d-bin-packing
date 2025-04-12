from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Đọc các dependencies từ requirements.txt (nếu có)
with open(path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    all_reqs = f.read().splitlines()

install_requires = [x.strip() for x in all_reqs if 'git+' not in x]

setup(
    name="online-3d-bin-packing",
    version="0.1.0",
    author="Hưng Tăng",
    author_email="hung.ttm230037@sis.hust.edu.vn",
    description="Online 3D Bin Packing algorithms implementation",
    long_description=open(path.join(here, "README.md"), encoding='utf-8').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/HungTang-120105/online-3d-bin-packing",  # cập nhật nếu có
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    install_requires=install_requires,  # Thêm phần dependencies vào đây
)
