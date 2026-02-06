Direct Linear Transform (DLT) is fundamentally connected to triangulation through its ability to solve the intersection of projection rays. Here's how they relate:

**Mathematical Foundation:**

1. **Projection Model**
- A 3D point $X = [X,Y,Z,1]^T$ projects to 2D point $x = [u,v,1]^T$ through:
   $\lambda x = PX$
   where $P$ is the 3×4 projection matrix
   $\lambda$ is the projective depth

2. **DLT Formulation**
- For each image point, we can write:
   $\lambda u = \frac{P_{1}^TX}{P_{3}^TX}$
   $\lambda v = \frac{P_{2}^TX}{P_{3}^TX}$

- This leads to linear equations:
   $uP_{3}^TX - P_{1}^TX = 0$
   $vP_{3}^TX - P_{2}^TX = 0$

3. **Triangulation System**
- For two views with points $x_1=(u_1,v_1)$ and $x_2=(u_2,v_2)$:

$$\begin{bmatrix} 
u_1P_{3,1}^T - P_{1,1}^T \\
v_1P_{3,1}^T - P_{2,1}^T \\
u_2P_{3,2}^T - P_{1,2}^T \\
v_2P_{3,2}^T - P_{2,2}^T
\end{bmatrix} X = 0$$

**Why DLT Works for Triangulation:**

1. **Geometric Interpretation**
- DLT finds the 3D point that minimizes algebraic error
- Each row in the equation system represents a constraint from one coordinate
- The solution is the intersection of projection rays in 3D space

2. **Solution Method**
- The system $AX = 0$ is solved using SVD
- The solution is the eigenvector corresponding to smallest singular value
- This provides the optimal 3D point in a least-squares sense

3. **Implementation Connection**
In your code:

```python
A = [
    point1[1]*P1[2,:] - P1[1,:],
    P1[0,:] - point1[0]*P1[2,:],
    point2[1]*P2[2,:] - P2[1,:],
    P2[0,:] - point2[0]*P2[2,:],
]
```
This directly implements the linear system described above.

**Advantages:**
- Linear solution
- Simple to implement
- Works with multiple views
- Computationally efficient

**Limitations:**
- Sensitive to noise
- Assumes perfect point correspondences
- Minimizes algebraic (not geometric) error
