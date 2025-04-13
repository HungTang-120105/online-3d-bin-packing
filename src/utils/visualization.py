import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import matplotlib.animation as animation

def plot_bin(bin, title="Bin Visualization"):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    ax.set_xlim([0, bin.W])
    ax.set_ylim([0, bin.H])
    ax.set_zlim([0, bin.D])

    # Vẽ tất cả các box đã được đặt trong bin
    for box in bin.boxes:
        ax.bar3d(box.x, box.y, box.z, box.w, box.h, box.d, color="cyan", edgecolor="black")

    ax.set_title(title)
    ax.set_xlabel('X axis')
    ax.set_ylabel('Y axis')
    ax.set_zlabel('Z axis')
    
    plt.show()



def plot_bin_snapshot(ax, boxes, W, H, D):
    ax.cla()
    ax.set_xlim([0, W])
    ax.set_ylim([0, H])
    ax.set_zlim([0, D])

    for box in boxes:
        ax.bar3d(box.x, box.y, box.z, box.w, box.h, box.d, color="cyan", edgecolor="black")

    ax.set_title("Bin Packing Animation")
    ax.set_xlabel('X axis')
    ax.set_ylabel('Y axis')
    ax.set_zlabel('Z axis')


def animate_bin_packing(frames, W, H, D):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    def update(frame):
        plot_bin_snapshot(ax, frame, W, H, D)

    ani = animation.FuncAnimation(fig, update, frames=frames, interval=1000, repeat=False)
    plt.show()

