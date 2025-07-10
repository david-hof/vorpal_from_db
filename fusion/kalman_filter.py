import numpy as np

class KalmanFilterCV2D:
    def __init__(self, init_pos, init_vel=(0.0, 0.0), q=1.0, r=10.0, p0=1000.0):
        self.x = np.array([init_pos[0], init_pos[1], init_vel[0], init_vel[1]], dtype=float)
        self.P = np.eye(4) * p0
        self.q = q
        self.r = r
        self.F = np.eye(4)
        self.H = np.array([[1, 0, 0, 0],
                           [0, 1, 0, 0]])
        self.Q = np.eye(4) * q
        self.R = np.eye(2) * r

    def predict(self, dt):
        self.F = np.array([[1, 0, dt, 0],
                           [0, 1, 0, dt],
                           [0, 0, 1,  0],
                           [0, 0, 0,  1]])

        self.Q = self.q * np.array([
            [dt**4/4, 0,     dt**3/2, 0],
            [0,     dt**4/4, 0,     dt**3/2],
            [dt**3/2, 0,     dt**2,   0],
            [0,     dt**3/2, 0,     dt**2]
        ])

        self.x = self.F @ self.x
        self.P = self.F @ self.P @ self.F.T + self.Q

    def update(self, z):
        z = np.asarray(z)
        y = z - self.H @ self.x
        S = self.H @ self.P @ self.H.T + self.R
        K = self.P @ self.H.T @ np.linalg.inv(S)

        self.x = self.x + K @ y
        self.P = (np.eye(4) - K @ self.H) @ self.P

    def get_predicted_position(self, dt):
        return self.x[:2] + self.x[2:] * dt

    def get_state(self):
        return self.x.copy()

    def get_position(self):
        return self.x[:2].copy()

    def get_velocity(self):
        return self.x[2:].copy()
