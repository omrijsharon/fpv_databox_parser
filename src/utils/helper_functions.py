import numpy as np
from ahrs.filters import Madgwick
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from tqdm import tqdm

from ahrs.common.orientation import q2R

from config import GYRO_SCALE, ACC_SCALE, TIME_SCALE

def process_blackbox_data(df):
    num_samples = len(df)
    gyro_data = df[['gyroADC[0]', 'gyroADC[1]', 'gyroADC[2]']].to_numpy() * GYRO_SCALE
    acc_data = df[['accSmooth[0]', 'accSmooth[1]', 'accSmooth[2]']].to_numpy() * ACC_SCALE

    madgwick = Madgwick()
    madgwick.Dt = (df['time'].to_numpy()[1] - df['time'].to_numpy()[0]) * TIME_SCALE

    Q = np.zeros((num_samples, 4))
    Q[0][0] = 1.0
    for t in tqdm(range(1, num_samples), desc="Processing Quaternions"):
        Q[t] = madgwick.updateIMU(Q[t-1], gyr=gyro_data[t], acc=acc_data[t])
    df['quat_w'] = Q[:, 0]
    df['quat_x'] = Q[:, 1]
    df['quat_y'] = Q[:, 2]
    df['quat_z'] = Q[:, 3]
    return df


def plot_3d_arrows(ax, points, arrows,  **kwargs):
    # for i in range(points.shape[0]):
    #     ax.quiver(points[i, 0], points[i, 1], points[i, 2], arrows[i, 0], arrows[i, 1], arrows[i, 2], color=color)
    points = points.reshape(-1, 3)
    arrows = arrows.reshape(-1, 3)
    ax.quiver(points[:, 0], points[:, 1], points[:, 2], arrows[:, 0], arrows[:, 1], arrows[:, 2],  **kwargs)


def plot_3d_rotation_matrix(ax, R, t, scale=1.0,  **kwargs):
    for dim, color in enumerate(['r', 'g', 'b']):
        plot_3d_arrows(ax, t, scale * R[:, dim], color=color, **kwargs)

def plot_orientation(ax, fig, df):
    num_samples = len(df)
    print("Total measurement time: ", df['time'].to_numpy()[-1] * TIME_SCALE, " seconds")
    # Extract quaternions from the DataFrame
    quaternions = df[['quat_w', 'quat_x', 'quat_y', 'quat_z']].to_numpy()

    translation = np.zeros((1, 3))
    dt = (df['time'].to_numpy()[1] - df['time'].to_numpy()[0]) * TIME_SCALE
    print(dt)
    # Compute rotation matrices and extract the axes
    for i in range(num_samples):
        ax.clear()
        R = q2R(quaternions[i])
        plot_3d_rotation_matrix(ax, R, translation, scale=0.8, alpha=0.7)
        show_plot(ax, fig, title='Orientation', equal=True, grid=True, legend=False)
        # add title current time
        ax.set_title("Time: {:.2f} seconds".format(i * dt))
        plt.pause(1e-6)

def show_plot(ax, fig, middle=None, edge=1.0, title=None, xlabel=None, ylabel=None, zlabel=None, equal=True, grid=True, legend=True):
    if middle is None:
        middle = np.array([0.0, 0.0, 0.0])
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.zaxis.set_major_locator(MaxNLocator(integer=True))
    minmax_edges = np.vstack((middle - edge, middle + edge)).T
    ax.set_xlim(*minmax_edges[0])
    ax.set_ylim(*minmax_edges[1])
    ax.set_zlim(*minmax_edges[2])
    fig.tight_layout()
