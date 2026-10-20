import streamlit as st
import numpy as np

# ============ 页面配置 ============
st.set_page_config(page_title="线性代数AI助教", layout="wide")
st.title("线性代数动态讲解AI Agent")
st.caption("矩阵乘法 · Cramer法则 · 逆矩阵求法  三步教学")

mode = st.sidebar.radio(
    "选择讲解功能",
    ["矩阵乘法动态讲解", "Cramer法则动态讲解", "逆矩阵求法动态讲解"]
)

EPS = 1e-10

def fmt(x):
    """格式化数字：整数显示整数，否则保留2位小数"""
    if abs(x - round(x)) < EPS:
        return str(int(round(x)))
    return f"{x:.2f}"

def latex_matrix(M, name=None):
    rows = []
    for row in M:
        rows.append(" & ".join(fmt(v) for v in row))
    body = r" \\ ".join(rows)
    if name:
        return f"{name} = \\begin{{bmatrix}} {body} \\end{{bmatrix}}"
    return f"\\begin{{bmatrix}} {body} \\end{{bmatrix}}"

# ============================================================
# 模块一：矩阵乘法
# ============================================================
if mode == "矩阵乘法动态讲解":
    st.header("矩阵乘法分步讲解")

    if "mat_step" not in st.session_state:
        st.session_state.mat_step = 0

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("矩阵 A")
        rows_a = st.number_input("行数", min_value=1, max_value=4, value=2, key="rows_a")
        cols_a = st.number_input("列数", min_value=1, max_value=4, value=2, key="cols_a")
    with col2:
        st.subheader("矩阵 B")
        rows_b = st.number_input("行数", min_value=1, max_value=4, value=2, key="rows_b")
        cols_b = st.number_input("列数", min_value=1, max_value=4, value=2, key="cols_b")

    st.subheader("输入元素")
    colA, colB = st.columns(2)
    A = np.zeros((rows_a, cols_a))
    B = np.zeros((rows_b, cols_b))
    with colA:
        st.write("**矩阵 A**")
        for i in range(rows_a):
            cs = st.columns(cols_a)
            for j in range(cols_a):
                A[i][j] = cs[j].number_input(f"A[{i+1},{j+1}]", value=0.0, key=f"mA_{i}_{j}")
    with colB:
        st.write("**矩阵 B**")
        for i in range(rows_b):
            cs = st.columns(cols_b)
            for j in range(cols_b):
                B[i][j] = cs[j].number_input(f"B[{i+1},{j+1}]", value=0.0, key=f"mB_{i}_{j}")

    if st.button("开始分步讲解", type="primary", key="mat_start"):
        if cols_a != rows_b:
            st.error("❌ 不可相乘：左矩阵列数 ≠ 右矩阵行数")
            st.session_state.mat_step = 0
        else:
            st.session_state.mat_A = A.copy()
            st.session_state.mat_B = B.copy()
            st.session_state.mat_result = A @ B
            st.session_state.mat_step = 1
            st.success("✅ 可相乘，开始讲解")

    if st.session_state.mat_step > 0:
        A = st.session_state.mat_A
        B = st.session_state.mat_B
        result = st.session_state.mat_result
        elem_count = rows_a * cols_b
        total_steps = elem_count + 2

        st.markdown("---")
        c1, c2, c3 = st.columns([1, 3, 1])
        with c1:
            if st.button("⬅ 上一步", key="mat_prev") and st.session_state.mat_step > 1:
                st.session_state.mat_step -= 1
        with c2:
            st.progress((st.session_state.mat_step - 1) / max(total_steps - 1, 1))
            st.caption(f"步骤 {st.session_state.mat_step} / {total_steps}")
        with c3:
            if st.button("下一步 ➡", key="mat_next") and st.session_state.mat_step < total_steps:
                st.session_state.mat_step += 1
        st.markdown("---")

        step = st.session_state.mat_step
        if step == 1:
            st.subheader("步骤1：判断条件与结果维度")
            st.success(f"✅ 左A列数({cols_a}) = 右B行数({rows_b})，可乘\n"
                       f"📐 结果 C = A×B 维度：{rows_a}行 × {cols_b}列")
            st.latex(latex_matrix(A, "A") + r",\quad " + latex_matrix(B, "B") +
                     r",\quad C_{" + f"{rows_a}×{cols_b}" + "}")
        elif 2 <= step <= elem_count + 1:
            idx = step - 2
            ri = idx // cols_b
            ci = idx % cols_b
            st.subheader(f"步骤{step}：计算 C[{ri+1},{ci+1}]")
            st.info("规则：A 的第 " + str(ri+1) + " 行 × B 的第 " + str(ci+1) + " 列，对应相乘再求和")
            r1, r2 = st.columns(2)
            with r1:
                st.write("A 的第 " + str(ri+1) + " 行：")
                st.latex(r"\begin{bmatrix} " + " & ".join(fmt(v) for v in A[ri]) + r" \end{bmatrix}")
            with r2:
                st.write("B 的第 " + str(ci+1) + " 列：")
                st.latex(r"\begin{bmatrix} " + r" \\ ".join(fmt(v) for v in B[:, ci]) + r" \end{bmatrix}")
            terms, s = [], 0.0
            for k in range(cols_a):
                terms.append(f"{fmt(A[ri][k])} \\times {fmt(B[k][ci])}")
                s += A[ri][k] * B[k][ci]
            st.latex(f"C_{{{ri+1}{ci+1}}} = " + " + ".join(terms) + f" = {fmt(s)}")

            st.write("结果矩阵进度（蓝色=已算出，?=待算）：")
            res_latex = r"\begin{bmatrix}"
            for i in range(rows_a):
                es = []
                for j in range(cols_b):
                    if i < ri or (i == ri and j <= ci):
                        es.append(f"\\color{{blue}} {fmt(result[i][j])}")
                    else:
                        es.append("?")
                res_latex += " & ".join(es)
                if i < rows_a - 1:
                    res_latex += r" \\ "
            res_latex += r" \end{bmatrix}"
            st.latex(res_latex)
        else:
            st.subheader("✅ 最终结果与性质")
            st.latex("C = " + latex_matrix(result))
            st.info("📌 性质：\n1. 一般 **AB ≠ BA**（不满足交换律）\n"
                     "2. 满足结合律 (AB)C = A(BC)\n"
                     "3. 满足分配律 A(B+C) = AB + AC")

# ============================================================
# 模块二：Cramer 法则
# ============================================================
elif mode == "Cramer法则动态讲解":
    st.header("Cramer法则分步讲解")

    if "cramer_step" not in st.session_state:
        st.session_state.cramer_step = 0

    n = st.number_input("未知数个数 n", min_value=2, max_value=4, value=2, key="cr_n")

    st.subheader("系数矩阵 A 与常数项 b")
    colA, colB = st.columns([3, 1])
    A = np.zeros((n, n))
    b = np.zeros(n)
    with colA:
        st.write("**A (n×n)**")
        for i in range(n):
            cs = st.columns(n)
            for j in range(n):
                A[i][j] = cs[j].number_input(f"A[{i+1},{j+1}]", value=0.0, key=f"crA_{i}_{j}")
    with colB:
        st.write("**b**")
        for i in range(n):
            b[i] = st.number_input(f"b[{i+1}]", value=0.0, key=f"crb_{i}")

    if st.button("开始分步讲解", type="primary", key="cr_start"):
        D = np.linalg.det(A)
        if abs(D) < EPS:
            st.error("❌ 系数行列式 D ≈ 0，Cramer法则不适用（无解或无穷多解）")
            st.session_state.cramer_step = 0
        else:
            st.session_state.cr_A = A.copy()
            st.session_state.cr_b = b.copy()
            st.session_state.cr_D = D
            st.session_state.cramer_step = 1
            st.success(f"✅ D = {fmt(D)} ≠ 0，适用")

    if st.session_state.cramer_step > 0:
        A = st.session_state.cr_A
        b = st.session_state.cr_b
        D = st.session_state.cr_D
        total = n + 2

        st.markdown("---")
        c1, c2, c3 = st.columns([1, 3, 1])
        with c1:
            if st.button("⬅ 上一步", key="cr_prev") and st.session_state.cramer_step > 1:
                st.session_state.cramer_step -= 1
        with c2:
            st.progress((st.session_state.cramer_step - 1) / max(total - 1, 1))
            st.caption(f"步骤 {st.session_state.cramer_step} / {total}")
        with c3:
            if st.button("下一步 ➡", key="cr_next") and st.session_state.cramer_step < total:
                st.session_state.cramer_step += 1
        st.markdown("---")

        step = st.session_state.cramer_step
        if step == 1:
            st.subheader("步骤1：适用条件与系数行列式 D")
            st.success(f"✅ 方程数=未知数数={n}，且 D≠0\n"
                       f"📐 方程组形式：Ax = b")
            st.latex("D = |A| = " + r"\begin{vmatrix} " +
                     r" \\ ".join(" & ".join(fmt(v) for v in row) for row in A) +
                     r" \end{vmatrix} = " + fmt(D))
        elif 2 <= step <= n + 1:
            idx = step - 2
            st.subheader(f"步骤{step}：计算 D_{idx+1}（用 b 替换第 {idx+1} 列）")
            st.info(f"💡 把 A 的第 {idx+1} 列整体换成常数项 b，其余列不动")
            Ai = A.copy()
            Ai[:, idx] = b
            Di = np.linalg.det(Ai)
            st.latex(f"D_{idx+1} = " + r"\begin{vmatrix} " +
                     r" \\ ".join(" & ".join(fmt(v) for v in row) for row in Ai) +
                     r" \end{vmatrix} = " + fmt(Di))
        else:
            st.subheader("✅ 方程组的解")
            sols = []
            for i in range(n):
                Ai = A.copy()
                Ai[:, i] = b
                Di = np.linalg.det(Ai)
                xi = Di / D
                sols.append(xi)
                st.latex(f"x_{{{i+1}}} = \\frac{{D_{{{i+1}}}}}{{D}} = "
                         f"\\frac{{{fmt(Di)}}}{{{fmt(D)}}} = {fmt(xi)}")
            st.success("唯一解：" + "，".join(f"x_{i+1} = {fmt(sols[i])}" for i in range(n)))
            st.info("📌 局限：n 较大时行列式计算量爆炸，工程上用高斯消元；\n"
                    "本法则价值在于理论推导与解的存在性判断。")

# ============================================================
# 模块三：逆矩阵求法（新增）
# ============================================================
elif mode == "逆矩阵求法动态讲解":
    st.header("逆矩阵求法分步讲解")

    st.write("**适用前提**：A 是 n 阶方阵，且 det(A) ≠ 0（非奇异）。")

    n = st.number_input("矩阵阶数 n", min_value=2, max_value=3, value=2, key="inv_n")

    A = np.zeros((n, n))
    st.write("**输入方阵 A**")
    for i in range(n):
        cs = st.columns(n)
        for j in range(n):
            A[i][j] = cs[j].number_input(f"A[{i+1},{j+1}]", value=0.0, key=f"invA_{i}_{j}")

    method = st.radio("教学方法",
                      ["二阶伴随公式法（仅n=2时推荐）",
                       "初等行变换法（通用，2~3阶）"],
                      key="inv_method")

    if st.button("开始分步讲解", type="primary", key="inv_start"):
        detA = np.linalg.det(A)
        if abs(detA) < EPS:
            st.error("❌ det(A) ≈ 0，矩阵不可逆（奇异矩阵）")
            st.session_state.inv_step = 0
        else:
            st.session_state.inv_A = A.copy()
            st.session_state.inv_det = detA
            st.session_state.inv_step = 1
            st.success(f"✅ det(A) = {fmt(detA)} ≠ 0，可逆")

    if st.session_state.get("inv_step", 0) > 0:
        A = st.session_state.inv_A
        detA = st.session_state.inv_det

        # ---------- 二阶伴随公式法 ----------
        if method.startswith("二阶伴随") and n == 2:
            a, b = A[0][0], A[0][1]
            c, d = A[1][0], A[1][1]
            steps_total = 4

            st.markdown("---")
            c1, c2, c3 = st.columns([1, 3, 1])
            with c1:
                if st.button("⬅ 上一步", key="inv_prev") and st.session_state.inv_step > 1:
                    st.session_state.inv_step -= 1
            with c2:
                st.progress((st.session_state.inv_step - 1) / (steps_total - 1))
                st.caption(f"步骤 {st.session_state.inv_step} / {steps_total}")
            with c3:
                if st.button("下一步 ➡", key="inv_next") and st.session_state.inv_step < steps_total:
                    st.session_state.inv_step += 1
            st.markdown("---")

            step = st.session_state.inv_step
            if step == 1:
                st.subheader("步骤1：写出 A 并算行列式")
                st.latex("A = " + latex_matrix(A))
                st.latex(r"\det(A) = ad - bc = " + fmt(a) + r"\times" + fmt(d) +
                         " - " + fmt(b) + r"\times" + fmt(c) + " = " + fmt(detA))
            elif step == 2:
                st.subheader("步骤2：求伴随矩阵 adj(A)")
                st.info("规则：**主对角线元素互换，副对角线元素变号**")
                st.latex(r"adj(A) = \begin{bmatrix} d & -b \\ -c & a \end{bmatrix} = "
                         r"\begin{bmatrix} " +
                         f"{fmt(d)} & {fmt(-b)} \\\\ {fmt(-c)} & {fmt(a)} " +
                         r"\end{bmatrix}")
            elif step == 3:
                st.subheader("步骤3：套公式 A⁻¹ = adj(A) / det(A)")
                invA = np.array([[d, -b], [-c, a]]) / detA
                st.latex(r"A^{-1} = \frac{1}{" + fmt(detA) + r"} \cdot " +
                         r"\begin{bmatrix} " + f"{fmt(d)} & {fmt(-b)} \\\\ {fmt(-c)} & {fmt(a)}" +
                         r" \end{bmatrix} = " +
                         r"\begin{bmatrix} " +
                         f"{fmt(invA[0][0])} & {fmt(invA[0][1])} \\\\ "
                         f"{fmt(invA[1][0])} & {fmt(invA[1][1])}" +
                         r" \end{bmatrix}")
            else:
                st.subheader("✅ 验证：A · A⁻¹ = I")
                invA = np.array([[d, -b], [-c, a]]) / detA
                product = A @ invA
                st.latex(latex_matrix(A) + r"\cdot" + latex_matrix(invA) + r"=" +
                         latex_matrix(product))
                st.success("✅ 结果是单位阵 I，逆矩阵正确！")

        # ---------- 初等行变换法（通用） ----------
        else:
            # 预先把整个消元过程算出来，每一步存一个 (矩阵, 说明文字)
            n = A.shape[0]
            M = np.hstack([A.copy(), np.eye(n)])  # 增广矩阵 [A | I]
            trail = [(M.copy(), "初始增广矩阵 [A | I]")]

            ops = []  # 记录每一步的文字说明

            # 高斯-约当消元
            for col in range(n):
                # 选主元（部分选主元，选该列绝对值最大的行）
                pivot_row = max(range(col, n), key=lambda r: abs(M[r][col]))
                if abs(M[pivot_row][col]) < EPS:
                    break
                if pivot_row != col:
                    M[[col, pivot_row]] = M[[pivot_row, col]]
                    ops.append(f"交换第 {col+1} 行 ↔ 第 {pivot_row+1} 行（选主元）")

                # 主元行归一化
                pivot_val = M[col][col]
                M[col] = M[col] / pivot_val
                ops.append(f"第 {col+1} 行 ÷ ({fmt(pivot_val)})，使主元 = 1")

                # 消去其他行
                for r in range(n):
                    if r != col and abs(M[r][col]) > EPS:
                        factor = M[r][col]
                        M[r] = M[r] - factor * M[col]
                        ops.append(f"第 {r+1} 行 - ({fmt(factor)}) × 第 {col+1} 行")

                trail.append((M.copy(), f"第 {col+1} 列消元完成"))

            steps_total = len(ops) + 2  # 初始 + 每步操作 + 最后验证

            st.markdown("---")
            c1, c2, c3 = st.columns([1, 3, 1])
            with c1:
                if st.button("⬅ 上一步", key="inv_prev2") and st.session_state.inv_step > 1:
                    st.session_state.inv_step -= 1
            with c2:
                st.progress((st.session_state.inv_step - 1) / max(steps_total - 1, 1))
                st.caption(f"步骤 {st.session_state.inv_step} / {steps_total}")
            with c3:
                if st.button("下一步 ➡", key="inv_next2") and st.session_state.inv_step < steps_total:
                    st.session_state.inv_step += 1
            st.markdown("---")

            step = st.session_state.inv_step

            if step == 1:
                st.subheader("步骤1：构造增广矩阵 [A | I]")
                st.info("把单位阵 I 拼在 A 的右边，对整体做初等行变换；\n"
                        "当左边 A 被化成单位阵 I 时，右边自然就变成 A⁻¹。")
                M0 = np.hstack([A, np.eye(n)])
                body = r" \\ ".join(
                    " & ".join(fmt(v) for v in row[:n]) +
                    r" \mid " +
                    " & ".join(fmt(v) for v in row[n:])
                    for row in M0
                )
                st.latex(r"\left[\begin{array}{" + "c"*n + r"|" + "c"*n + r"} " +
                         body + r" \end{array}\right]")

            elif 2 <= step <= len(ops) + 1:
                op_idx = step - 2
                st.subheader(f"步骤{step}：{ops[op_idx]}")
                # 重现到这一步为止的矩阵状态
                M_cur = np.hstack([A.copy(), np.eye(n)])
                # 重新跑一遍前 op_idx+1 次操作（简化：直接用 trail 里对应位置的快照）
                # trail 长度 = 列数+1；这里我们用更直接的办法：重放所有 ops 直到 op_idx
                # 为简单起见，重新计算：
                M2 = np.hstack([A.copy(), np.eye(n)])
                # 按列处理，重放到 op_idx
                op_counter = 0
                for col in range(n):
                    pivot_row = max(range(col, n), key=lambda r: abs(M2[r][col]))
                    if abs(M2[pivot_row][col]) < EPS:
                        break
                    if pivot_row != col:
                        if op_counter > op_idx:
                            break
                        M2[[col, pivot_row]] = M2[[pivot_row, col]]
                        op_counter += 1
                        if op_counter > op_idx:
                            break
                    pv = M2[col][col]
                    M2[col] = M2[col] / pv
                    op_counter += 1
                    if op_counter > op_idx:
                        break
                    for r in range(n):
                        if r != col and abs(M2[r][col]) > EPS:
                            f = M2[r][col]
                            M2[r] = M2[r] - f * M2[col]
                            op_counter += 1
                            if op_counter > op_idx:
                                break
                    if op_counter > op_idx:
                        break

                body = r" \\ ".join(
                    " & ".join(fmt(v) for v in row[:n]) +
                    r" \mid " +
                    " & ".join(fmt(v) for v in row[n:])
                    for row in M2
                )
                st.latex(r"\left[\begin{array}{" + "c"*n + r"|" + "c"*n + r"} " +
                         body + r" \end{array}\right]")
                st.caption(f"👉 当前操作：{ops[op_idx]}")

            else:
                st.subheader("✅ 最终结果与验证")
                invA = M[:, n:]
                st.write("左边已变成 I，右边即为 A⁻¹：")
                st.latex(r"A^{-1} = " + latex_matrix(invA))
                st.write("验证 A · A⁻¹ = I：")
                product = A @ invA
                st.latex(latex_matrix(A) + r"\cdot" + latex_matrix(invA) + r"=" +
                         latex_matrix(product))
                st.success("✅ 结果为单位阵，逆矩阵正确！")
                st.info("📌 方法对比：\n"
                        "- **伴随法**：公式固定，但 n≥3 时余子式计算量大，易错\n"
                        "- **初等行变换法**：通用，工程上首选，与高斯消元同源\n"
                        "- det(A) = 0 时不可逆，叫奇异矩阵")

# 页脚
st.markdown("---")
st.caption("线性代数AI Agent | 矩阵乘法 · Cramer法则 · 逆矩阵")