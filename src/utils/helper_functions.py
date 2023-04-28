import numpy as np
from ahrs.filters import Madgwick
from ahrs.common.orientation import q2R

from config import GYRO_SCALE, ACC_SCALE

def process_blackbox_data(df):
    num_samples = len(df)
    gyro_data = df[['gyroADC[0]', 'gyroADC[1]', 'gyroADC[2]']].to_numpy() * GYRO_SCALE
    acc_data = df[['accSmooth[0]', 'accSmooth[1]', 'accSmooth[2]']].to_numpy() * ACC_SCALE

    madgwick = Madgwick()
    madgwick.Dt = df['time'].to_numpy()[1] - df['time'].to_numpy()[0]

    Q = np.zeros((num_samples, 4))
    Q[0][0] = 1.0
    for t in range(1, num_samples):
        Q[t] = madgwick.updateIMU(Q[t-1], gyr=gyro_data[t], acc=acc_data[t])
    df['quat_w'] = Q[:, 0]
    df['quat_x'] = Q[:, 1]
    df['quat_y'] = Q[:, 2]
    df['quat_z'] = Q[:, 3]
    return df