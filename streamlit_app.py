import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# ====== 입력 ======
A = np.array([[1, 2],
              [3, 4]])

B = np.array([[5, 6],
              [7, 8]])

# ====== 결과 행렬 ======
C = np.zeros((A.shape[0], B.shape[1]))

fig, ax = plt.subplots(figsize=(6, 6))
ax.axis('off')

# 텍스트 저장용
texts = []

def draw_matrix(matrix, x_offset, label):
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            txt = ax.text(j + x_offset, -i, str(matrix[i, j]),
                          ha='center', va='center', fontsize=14)
            texts.append(txt)
    ax.text(x_offset, 1, label, fontsize=14)

def update(frame):
    ax.clear()
    ax.axis('off')

    i = frame // B.shape[1]
    j = frame % B.shape[1]

    draw_matrix(A, 0, "A")
    draw_matrix(B, 3, "B")
    draw_matrix(C, 6, "C")

    # 계산 과정 시각화
    result = 0
    for k in range(A.shape[1]):
        a = A[i, k]
        b = B[k, j]
        result += a * b

        ax.text(1.5, -3 - k, f"{a} × {b} = {a*b}", fontsize=12)

    C[i, j] = result
    ax.text(1.5, -5, f"Sum = {result}", fontsize=14, color='red')

ani = FuncAnimation(fig, update,
                    frames=A.shape[0] * B.shape[1],
                    interval=1000, repeat=False)

plt.show()