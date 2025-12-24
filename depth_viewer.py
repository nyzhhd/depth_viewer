import streamlit as st          # ← 原来是 as plt
import numpy as np
import cv2
from matplotlib import cm

st.set_page_config(page_title="Depth Viewer", layout="centered")
st.title("🔵 16-bit 深度图可视化")

# 1. 文件上传（支持 .png / .tiff / .tif）
uploaded = st.file_uploader("上传 16-bit 深度图", type=["png", "tiff", "tif"])
if uploaded is not None:
    file_bytes = np.asarray(bytearray(uploaded.read()), dtype=np.uint8)
    raw = cv2.imdecode(file_bytes, cv2.IMREAD_ANYDEPTH)  # 保持 16-bit
    if raw is None:
        st.error("无法解码，请确认是 16-bit 单通道图像")
        st.stop()

    # 2. 自动计算 2-98 百分位
    mask = raw > 0
    if mask.sum() == 0:
        st.warning("图像全黑，无有效深度")
        st.stop()
    lo, hi = np.percentile(raw[mask], [2, 98])

    # 3. 伪彩色映射（可换 colormap）
    cmap_name = st.selectbox("选择 colormap", ["jet", "viridis", "plasma", "turbo"], index=0)
    cmap = cm.get_cmap(cmap_name)

    # 归一化 + 伪彩
    norm = np.clip((raw.astype(float) - lo) / (hi - lo), 0, 1)
    colored = (cmap(norm)[:, :, :3] * 255).astype(np.uint8)

    # 4. 左右布局
    col1, col2 = st.columns(2)
    with col1:
        st.write("**伪彩色图**")
        st.image(colored, channels="RGB", use_column_width=True)
    with col2:
        st.write("**原始 16-bit 灰度**")
        st.image(raw, channels="GRAY", use_column_width=True,
                 clamp=True)  # clamp 自动 0-255 映射

    # 5. 统计信息
    st.write(f"有效像素 {mask.sum():,}  |  深度范围 {lo:.0f} – {hi:.0f} (单位)")