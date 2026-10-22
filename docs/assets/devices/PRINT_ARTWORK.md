# 印刷说明书背面示意图

2026-10-20 使用内置 imagegen 工具根据用户提供的三款背面建模截图重绘。原图仅为几何参考，保存在被 Git 忽略的 `.work/print-booklets/references/`，不进入发布说明书。

白底灰黑线描，移除建模网格、坐标线、原配色、商标和文字；按原视角保留轮廓、窗口偏置、凹槽和侧面特征。生成图用于位置识别，不作为尺寸、配色或传感器参数图。与原图逐一核对后使用。

## 输出与提示词

按键与接口页使用 `standard-24-controls.png`、`standard-28-controls.png`、`standard-32-controls.png`，来源为用户提供的原始 PDF。通过 Word 原生裁切选择带完整标注的立体视图，保留屏幕朝向和机身各面。上一轮自绘的平面接口简图已撤下，保留在忽略的工作目录供历史对照。背面重绘图保持原有位置识别用途。

### 2.4 寸

文件：[standard-24-rear-manual.png](standard-24-rear-manual.png)

Use case: style-transfer. Asset type: technical rear-view illustration for an A5 printed consumer device manual. Input image 1 is the geometric reference, NOT a style to retain. Redraw this exact single device as clean professional technical line art on a pure white background, charcoal fine outlines, white case surfaces, only very light neutral-gray shading to distinguish recesses. Preserve the input perspective, enclosure silhouette, corner rounding, seams, all visible side features, and exact sensor-window center relative to the case. Remove CAD grid, colored coordinate lines, CAD colors, all logos and all text. No leader lines, no numbers, no dimensions. No extra object, no extra camera, no invented hardware. Full device visible with generous clean white margins. The single exposed circular sensing face must be clearly distinguishable from case fastener holes. This is technical documentation, not a marketing render. This is the 2.4-inch enclosure: rear sensor is strongly offset toward the right side in the given orientation, not centered; preserve this offset exactly. Do not add corner fastener holes absent in this reference. Preserve the controls visible along the near edge.

### 2.8 寸

文件：[standard-28-rear-manual.png](standard-28-rear-manual.png)

Use case: style-transfer. Asset type: technical rear-view illustration for an A5 printed consumer device manual. Input image 1 is the geometric reference, NOT a style to retain. Redraw this exact single device as clean professional technical line art on a pure white background, charcoal fine outlines, white case surfaces, only very light neutral-gray shading to distinguish recesses. Preserve the input perspective, enclosure silhouette, corner rounding, seams, all visible side features, and exact sensor-window center relative to the case. Remove CAD grid, colored coordinate lines, CAD colors, all logos and all text. No leader lines, no numbers, no dimensions. No extra object, no extra camera, no invented hardware. Full device visible with generous clean white margins. The single exposed circular sensing face must be clearly distinguishable from case fastener holes. This is technical documentation, not a marketing render. This is the 2.8-inch enclosure. Preserve the gently recessed single circular sensor opening toward the middle of the back as shown, the four corner fastener recesses, the recessed Type-C port on the near edge, small indicator slot, and the hole in the side. Do not center or move anything for visual symmetry.

### 3.2 寸

文件：[standard-32-rear-manual.png](standard-32-rear-manual.png)

Use case: style-transfer. Asset type: technical rear-view illustration for an A5 printed consumer device manual. Input image 1 is the geometric reference, NOT a style to retain. Redraw this exact single device as clean professional technical line art on a pure white background, charcoal fine outlines, white case surfaces, only very light neutral-gray shading to distinguish recesses. Preserve the input perspective, enclosure silhouette, corner rounding, seams, all visible side features, and exact sensor-window center relative to the case. Remove CAD grid, colored coordinate lines, CAD colors, all logos and all text. No leader lines, no numbers, no dimensions. No extra object, no extra camera, no invented hardware. Full device visible with generous clean white margins. The single exposed circular sensing face must be clearly distinguishable from case fastener holes. This is technical documentation, not a marketing render. This is the 3.2-inch enclosure. Preserve its single deeply recessed circular sensor well, four corner fastener recesses, enclosure seam, and near-edge Type-C opening and indicator slot. Do not replace the deep sensor well with a flat circle.
