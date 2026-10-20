import streamlit as st
import numpy as np

# ============ 页面配置 ============
st.set_page_config(page_title="线性代数AI助教", layout="wide")
st.title("线性代数动态讲解AI Agent")
st.caption("矩阵乘法 · Cramer法则 · 逆矩阵求法  三步教学")

mode = st.sidebar.radio(
    "选择讲解功能",
    ["矩阵乘法动态讲解", "Cramer法则动态讲解", "逆矩阵求法动态讲解",
     "💬 线性代数AI问答"]
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

# ============================================================
# 模块四：本地AI问答（内置知识库，关键词匹配）
# ============================================================
elif mode == "💬 线性代数AI问答":
    st.header("💬 线性代数AI助教问答")
    st.caption("本地知识库 · 回答线性代数基础概念问题 · 不调用外部API")

    # ---------- 内置知识库 ----------
    # 每条 = (关键词列表, 回答内容, 可选公式)
    KB = [
        {
            "kw": ["矩阵乘法", "矩阵相乘", "怎么乘", "乘法规则", "ab不等于ba", "交换律"],
            "ans": "**矩阵乘法规则**：只有当左矩阵的列数 = 右矩阵的行数时才能相乘。\n"
                   "结果 C[i][j] = A的第i行 与 B的第j列 对应元素相乘再求和。\n\n"
                   "⚠️ **最重要的性质：一般情况下 AB ≠ BA**（不满足交换律），"
                   "甚至当 AB 有定义时，BA 可能根本不存在。",
            "latex": r"C_{ij} = \sum_{k} A_{ik} B_{kj}"
        },
        {
            "kw": ["逆矩阵", "逆矩阵存在", "什么时候可逆", "不可逆", "奇异", "非奇异", "det=0", "行列式为0"],
            "ans": "**逆矩阵存在的充要条件**：A 是方阵，且 det(A) ≠ 0（非奇异矩阵）。\n\n"
                   "如果 det(A) = 0，A 叫**奇异矩阵**，不存在逆矩阵，对应的线性方程组 "
                   "Ax = b 要么无解、要么有无穷多解。\n\n"
                   "求法：二阶直接用公式；三阶以上推荐初等行变换法 [A|I] → [I|A⁻¹]。",
            "latex": r"A A^{-1} = A^{-1} A = I \quad\Longleftrightarrow\quad \det(A) \neq 0"
        },
        {
            "kw": ["伴随矩阵", "伴随", "adj"],
            "ans": "**伴随矩阵 adj(A)**：是 A 的所有代数余子式矩阵的转置。\n"
                   "二阶时特别简单：主对角线元素互换，副对角线元素变号。\n"
                   "逆矩阵公式：A⁻¹ = adj(A) / det(A)。",
            "latex": r"A^{-1} = \frac{1}{\det(A)} \cdot \mathrm{adj}(A)"
        },
        {
            "kw": ["cramer", "克莱姆", "克拉默", "cramer法则", "适用条件"],
            "ans": "**Cramer法则适用条件**：\n"
                   "1. 方程个数 = 未知数个数（系数矩阵是方阵）\n"
                   "2. 系数行列式 D ≠ 0\n\n"
                   "满足时，解为 xᵢ = Dᵢ / D，其中 Dᵢ 是把 D 的第 i 列换成常数项得到的行列式。\n\n"
                   "⚠️ 缺点：n 较大时计算量爆炸，工程上一般用高斯消元；本法则主要用于理论推导。",
            "latex": r"x_i = \frac{D_i}{D}, \quad D_i = \det(A_{\leftarrow b})"
        },
        {
            "kw": ["行列式", "det", "行列式定义", "几何意义"],
            "ans": "**行列式 det(A)**：是方阵对应的一个标量。\n\n"
                   "几何意义：它表示矩阵对应的线性变换对**面积/体积的缩放倍数**。\n"
                   "- det > 0：保持定向\n"
                   "- det < 0：翻转定向（镜像）\n"
                   "- det = 0：线性变换把空间降维了（面积/体积被压成 0）",
            "latex": r"|\det(A)| = \text{平行六面体体积}"
        },
        {
            "kw": ["秩", "rank", "矩阵的秩"],
            "ans": "**矩阵的秩 rank(A)**：矩阵中线性无关的行（或列）的最大个数。\n\n"
                   "它决定了线性方程组解的情况：\n"
                   "- rank(A) = rank(A|b) = n：唯一解\n"
                   "- rank(A) = rank(A|b) < n：无穷多解\n"
                   "- rank(A) < rank(A|b)：无解",
            "latex": r"\mathrm{rank}(A) \leq \min(m, n)"
        },
        {
            "kw": ["单位矩阵", "单位阵", "identity", "eye"],
            "ans": "**单位矩阵 I**：主对角线全是 1，其余全是 0 的方阵。\n"
                   "性质：I 乘任何矩阵等于那个矩阵本身，即 AI = IA = A。\n"
                   "求逆矩阵时构造的 [A|I] 就是从单位阵出发做行变换。",
            "latex": r"I_n = \begin{bmatrix} 1 & & \\ & \ddots & \\ & & 1 \end{bmatrix}"
        },
        {
            "kw": ["转置", "transpose", "AT"],
            "ans": "**矩阵转置 Aᵀ**：把 A 的行和列互换，即 (Aᵀ)[i][j] = A[j][i]。\n\n"
                   "常用性质：\n"
                   "- (Aᵀ)ᵀ = A\n"
                   "- (AB)ᵀ = Bᵀ Aᵀ（注意顺序反过来）\n"
                   "- (A⁻¹)ᵀ = (Aᵀ)⁻¹",
            "latex": r"(AB)^T = B^T A^T"
        },
        {
            "kw": ["线性方程组", "方程组解", "解的情况", "无解", "无穷多解", "唯一解"],
            "ans": "**线性方程组 Ax = b 解的判定**（用秩判断）：\n\n"
                   "1. rank(A) = rank(A|b) = n（未知数个数）→ **唯一解**\n"
                   "2. rank(A) = rank(A|b) < n → **无穷多解**\n"
                   "3. rank(A) < rank(A|b) → **无解**\n\n"
                   "其中 A|b 是把常数项 b 拼在 A 右边的增广矩阵。",
            "latex": r"\text{唯一解} \iff \mathrm{rank}(A) = n"
        },
        {
            "kw": ["高斯消元", "消元法", "初等行变换"],
            "ans": "**初等行变换**包括三种操作：\n"
                   "1. 交换两行\n"
                   "2. 某一行乘一个非零常数\n"
                   "3. 某一行加上另一行的若干倍\n\n"
                   "初等行变换**不改变方程组的解**，也**不改变矩阵的秩**。\n"
                   "求逆矩阵、解方程组、求秩都靠它。",
            "latex": r"[A | I] \xrightarrow{\text{行变换}} [I | A^{-1}]"
        },
        {
            "kw": ["加法", "矩阵加法", "矩阵相减"],
            "ans": "**矩阵加减法**：要求两个矩阵**维度完全相同**，对应位置元素直接加减。\n\n"
                   "⚠️ 维度不同的矩阵不能加减，但可以用广播（broadcast）做标量乘、数乘。",
            "latex": r"(A \pm B)_{ij} = A_{ij} \pm B_{ij}"
        },
        {
            "kw": ["数乘", "标量乘", "矩阵乘常数"],
            "ans": "**数乘 kA**：常数 k 乘到矩阵的每一个元素上。\n\n"
                   "注意和矩阵乘法区分：\n"
                   "- 数乘：k·A，每个元素都乘 k\n"
                   "- 矩阵乘法：A·B，按行×列规则，不是对应位置相乘",
            "latex": r"(kA)_{ij} = k \cdot A_{ij}"
        },
        {
            "kw": ["hello", "你好", "hi", "在吗"],
            "ans": "你好！我是线性代数AI助教。\n"
                   "你可以问我：\n"
                   "- 矩阵乘法怎么算？\n"
                   "- 逆矩阵什么时候不存在？\n"
                   "- Cramer法则适用条件？\n"
                   "- 行列式的几何意义是什么？\n"
                   "- 线性方程组怎么判断有没有解？",
            "latex": None
        },
    ]

    FALLBACK = ("这个问题我暂时没覆盖到，试试换个问法，或者参考下面这些我能回答的话题：\n"
                "- 矩阵乘法规则与交换律\n"
                "- 逆矩阵存在条件、伴随矩阵\n"
                "- Cramer法则适用条件\n"
                "- 行列式定义与几何意义\n"
                "- 矩阵的秩、线性方程组解的判定\n"
                "- 初等行变换、高斯消元\n"
                "- 单位矩阵、转置、数乘")

    # ---------- 回答匹配函数 ----------
    def answer(q: str):
        q_low = q.lower()
        best, best_score = None, 0
        for item in KB:
            score = sum(1 for kw in item["kw"] if kw.lower() in q_low)
            if score > best_score:
                best, best_score = item, score
        if best and best_score > 0:
            return best["ans"], best.get("latex")
        return FALLBACK, None

    # ---------- 对话历史 ----------
    if "chat_hist" not in st.session_state:
        st.session_state.chat_hist = [
            {"role": "assistant",
             "content": "👋 你好，我是线性代数AI助教。你可以问我矩阵乘法、逆矩阵、Cramer法则、行列式、秩、方程组解的判定等基础问题。",
             "latex": None}
        ]

    # 渲染历史
    for msg in st.session_state.chat_hist:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("latex"):
                st.latex(msg["latex"])

    # 推荐问题
    st.markdown("**试试问我：**")
    sugg = ["矩阵乘法为什么不满足交换律？",
            "逆矩阵什么时候不存在？",
            "Cramer法则的适用条件是什么？",
            "行列式的几何意义？",
            "线性方程组怎么判断有没有解？"]
    cols = st.columns(len(sugg))
    for i, s in enumerate(sugg):
        if cols[i].button(s, key=f"sug_{i}"):
            user_q = s
            st.session_state.chat_hist.append({"role": "user", "content": user_q, "latex": None})
            with st.chat_message("user"):
                st.markdown(user_q)
            ans, latex = answer(user_q)
            st.session_state.chat_hist.append({"role": "assistant", "content": ans, "latex": latex})
            with st.chat_message("assistant"):
                st.markdown(ans)
                if latex:
                    st.latex(latex)
            st.rerun()

    # 输入框
    user_input = st.chat_input("输入你的线性代数问题...")
    if user_input:
        st.session_state.chat_hist.append({"role": "user", "content": user_input, "latex": None})
        with st.chat_message("user"):
            st.markdown(user_input)
        ans, latex = answer(user_input)
        st.session_state.chat_hist.append({"role": "assistant", "content": ans, "latex": latex})
        with st.chat_message("assistant"):
            st.markdown(ans)
            if latex:
                st.latex(latex)

# 页脚
st.markdown("---")
st.caption("线性代数AI Agent | 矩阵乘法 · Cramer法则 · 逆矩阵 · 本地AI问答")
