---
name: 主题修改
description: 针对主题样式进行整体调整，涉及各种包含组件，修改样式，不修改逻辑。
---
# 智能体广场（右侧主内容区）科技蓝玻璃拟态风格

本规范用于把页面的**主内容区（通常是左侧菜单右边的区域）**统一为“科技深蓝 + 玻璃拟态 + 发光描边”风格。  
原则：**只改样式，不改业务逻辑与 DOM 结构**；变量**作用域限制**在页面根容器，避免污染其它页面。

---

## 一、页面改造步骤（推荐顺序）

按以下步骤依次改造，每步所需的具体样式代码见 **二、样式规范与参考** 中对应小节。

| 步骤 | 改造项 | 说明 | 参考小节 |
|------|--------|------|----------|
| **1** | 确定页面根容器并添加变量 | 在页面最外层容器（如 `.xxxWrapper`）的样式里定义科技蓝相关 CSS 变量，后续所有子元素都依赖这些变量。 | § 1 样式变量 |
| **2** | 设置页面背景 | 根容器使用统一背景图或 CSS 渐变，并设置主文字颜色。 | § 2 背景 |
| **3** | 顶栏 / 内容区面板 | 顶部标题栏、主内容区外层等容器改为玻璃拟态面板（背景、边框、圆角、内阴影、毛玻璃）。 | § 3 面板 |
| **4** | Tabs（若有） | 顶部分类 Tab 的默认 / hover / 激活态改为深色背景 + 强调色高亮。 | § 5 Tabs |
| **5** | 搜索框 / 输入框 | 搜索框、筛选输入框改为深色玻璃面板，输入文字与占位符为浅色，图标统一次要色。 | § 6 输入框 |
| **6** | 下拉框 Select（若有） | 触发器与展开菜单均改为与输入框一致的深色玻璃；建议使用 `styles` + `rootClassName` 双保险。 | § 6.1 下拉框 |
| **7** | 卡片列表（若有） | 列表项卡片改为玻璃拟态，标题主色、描述次要色，hover 时发光描边。 | § 4 卡片 |
| **8** | 空状态 Empty（若有） | 空状态文案使用次要色，hover/可点击时强调色 + 发光。 | § 7 空状态 |

**操作建议：**

- 先给页面根容器加上 **步骤 1（变量）** 和 **步骤 2（背景）**，确认整页底色和主文字颜色正确。
- 再按页面实际存在的模块，依次做 **步骤 3～8**（没有的模块可跳过）。
- 若存在全局样式覆盖（如输入框、Select 白底），选择器需带**页面根 class**（如 `.plugin-store-page`），必要时使用 `!important` 或 Ant Design 的 `styles` 覆盖。

---

## 二、样式规范与参考

### 1. 样式变量（建议放在页面根容器）

**改造步骤 1**：在页面根容器的样式块中（例如 `.homeWrapper` 或 `.plugin-store-page`）最先定义以下变量，后续背景、面板、输入框等都会引用它们。

```scss
/* 科技背景与玻璃拟态（建议仅在当前页面作用域内定义） */
--as-bg-color: #031931;
--as-panel-bg-color: rgba(15, 30, 60, 0.5);
--as-primary-text-color: #e5e9f0;
--as-secondary-text-color: #8892b0;

/* 强调色：推荐直接复用系统主题色 */
--as-accent-color: var(--primary-color);
--as-border-color: color-mix(in srgb, var(--as-accent-color) 30%, transparent);
--as-glow-shadow: 0 0 8px color-mix(in srgb, var(--as-accent-color) 85%, transparent),
  0 0 12px color-mix(in srgb, var(--as-accent-color) 55%, transparent);
```

> 说明：`demo.html` 的强调色是 `#00E5FF`，这里用 `var(--primary-color)` 兼容系统主题。

---

### 2. 背景（科技感高光 + 渐变）

**改造步骤 2**：在页面根容器上设置背景与主文字颜色。

**统一背景图**：智能体广场与插件广场共用一张背景图，路径为 **`console/frontend/src/assets/imgs/upload/tech-square-bg.svg`**。替换该文件即可同时更换两处页面背景（支持 SVG 或 PNG/JPG 等，保持文件名 `tech-square-bg.svg` 或同步修改两处引用）。

```scss
/* 科技感背景：使用统一背景图 */
background-color: var(--as-bg-color);
background-image: url('@/assets/imgs/upload/tech-square-bg.svg');
background-size: cover;
background-position: center;
background-repeat: no-repeat;
color: var(--as-primary-text-color);
```

若需恢复为 CSS 渐变写法（不依赖图片），可改为：

```scss
background-image:
  radial-gradient(circle at 20% 0%, rgba(0, 229, 255, 0.22), transparent 55%),
  radial-gradient(circle at 80% 100%, rgba(88, 101, 242, 0.2), transparent 60%),
  linear-gradient(135deg, rgba(0, 0, 0, 0.35), transparent 55%);
background-size: 100% 100%, 100% 100%, 100% 100%;
```

---

### 3. 面板（玻璃拟态容器）通用写法

**改造步骤 3**：用于顶栏、右侧内容区容器、Tab 容器、筛选面板、信息块等。

```scss
background: var(--as-panel-bg-color);
border: 1px solid var(--as-border-color);
border-radius: 10px; /* 通常 8~20 之间取值 */
backdrop-filter: blur(10px);
box-shadow: inset 0 0 10px color-mix(in srgb, var(--as-accent-color) 10%, transparent);
```

如果需要更强的“发光卡片”效果（用于 hover / 选中态）：

```scss
box-shadow: var(--as-glow-shadow);
text-shadow: var(--as-glow-shadow);
```

---

### 4. 卡片（列表项）风格

**改造步骤 7**：用于卡片列表、推荐位、资源块等。

**默认态**

```scss
background: var(--as-panel-bg-color);
border: 1px solid var(--as-border-color);
border-radius: 18px; /* 卡片建议更大圆角 */
backdrop-filter: blur(10px);
box-shadow: inset 0 0 10px color-mix(in srgb, var(--as-accent-color) 10%, transparent);
transition: all 0.2s ease;
```

**hover 态**

```scss
&:hover {
  border-color: var(--as-border-color);
  box-shadow: var(--as-glow-shadow);
}
```

**文案颜色**

- 标题：`#ffffff` 或 `var(--as-primary-text-color)`
- 描述/次要信息：`var(--as-secondary-text-color)`

---

### 5. Tabs（顶部分类）风格

**改造步骤 4**：顶栏内 Tab 的容器用“面板”写法（§3）；Tab 项样式如下。

```scss
color: var(--as-secondary-text-color);

&:hover {
  background: color-mix(in srgb, var(--as-accent-color) 8%, transparent);
  color: var(--as-accent-color);
  text-shadow: var(--as-glow-shadow);
}

&.active {
  color: var(--as-accent-color);
  background: color-mix(in srgb, var(--as-accent-color) 12%, transparent);
  border: 1px solid var(--as-border-color);
  box-shadow: var(--as-glow-shadow);
}
```

---

### 6. 搜索框 / 输入框（Ant Design）

**改造步骤 5**：把输入框当做玻璃面板，**边框与图标**需统一：

- **边框**：`border: 1px solid var(--as-border-color)`（与强调色一致的浅紫/青描边）。
- **图标**：前缀/后缀图标使用 `color: var(--as-secondary-text-color)`；若为 `<img>` 图标，可用 `filter: brightness(0) invert(1)` 或配合 `opacity` 做成浅色。

```scss
/* antd Input（带 prefix 时为 affix wrapper） */
.ant-input-outlined,
.ant-input-affix-wrapper {
  border: 1px solid var(--as-border-color);
  background: var(--as-panel-bg-color);
  color: #ffffff !important;
  backdrop-filter: blur(10px);
  box-shadow: inset 0 0 10px color-mix(in srgb, var(--as-accent-color) 10%, transparent);
}

.ant-input-affix-wrapper > input.ant-input,
.ant-input-outlined.ant-input {
  color: #ffffff;
  font-weight: 500;
  text-shadow: 0 0 4px rgba(0, 0, 0, 0.6);
  caret-color: var(--as-accent-color);
}

.ant-input::placeholder {
  color: var(--as-secondary-text-color);
}

.ant-input-prefix,
.ant-input-suffix {
  color: var(--as-secondary-text-color);
}
```

> 注意：若项目中有封装搜索组件（如 `retractable-input-UI`），全局只控制尺寸/内边距，背景与边框在深色页面（智能体广场、插件广场）用页面级样式覆写；输入框外层容器也建议使用相同边框与背景。

---

### 6.1 下拉框 Select（与输入框一致）

**改造步骤 6**：下拉框分两块：**默认展示框（触发器）** 和 **展开后的选项菜单**，二者背景、边框均需与输入框一致。

### 默认展示框（触发器）改动点

- **背景**：`background` 与 `background-color` 均为 `var(--as-panel-bg-color)`（深色玻璃），并用 `!important` 覆盖全局白底（如 `.ant-select-UI .ant-select-selector { background: #fff }`）。
- **边框**：`1px solid var(--as-border-color)`；**聚焦/展开时** 不改为主题色，保持 `var(--as-border-color)`，阴影用内阴影与输入框一致。
- **文字**：`.ant-select-selection-item`、`.ant-select-selection-placeholder` 使用 `var(--as-primary-text-color)`。
- **下拉箭头**：`.ant-select-arrow`、`.anticon` 使用 `var(--as-secondary-text-color)`；若箭头为 `<img>`，可用 `filter: brightness(0) invert(1)` 提亮。

选择器需带页面根 class（如 `.plugin-store-page`），且优先级高于全局 `.ant-select-UI`。若全局样式中对 `.ant-select-UI .ant-select-selector` 使用了 `background: #fff !important`，建议在**全局样式文件**（如 `styles/global.scss`）中增加「页面根 + Select」的覆盖规则，并给 `var(--as-panel-bg-color)` 等写上 fallback（如 `var(--as-panel-bg-color, rgba(15,30,60,0.5))`），这样无论样式加载顺序如何，默认展示框都会是深色玻璃。

**推荐（Ant Design 6）：** 在 `<Select>` 上同时使用 **`styles`** 与 **`rootClassName`**，双保险保证触发器深色玻璃不被覆盖：

- **`styles={{ root: { background, border, borderRadius, boxShadow, color }, content: { color } }}`**：内联样式优先级最高，直接作用在 Select 根节点。
- **`rootClassName="你的页面-select-root"`**：在页面 CSS 里用 `.你的页面根 .你的页面-select-root.ant-select .ant-select-selector { ... !important }` 覆盖内部 `.ant-select-selector`（antd 可能把背景写在 selector 上，仅 `styles.root` 有时不够）。

示例（插件广场）：`index.tsx` 中 `rootClassName="plugin-store-select-root"`，`style.css` 中 `.plugin-store-page .plugin-store-select-root.ant-select .ant-select-selector` 写与输入框一致的背景/边框/阴影。

### 展开菜单改动点

- 背景、边框同触发器；选项文字 `var(--as-primary-text-color)`，选中/高亮 `var(--as-accent-color)`。
- 通过 `getPopupContainer` 将弹出层挂到页面根下以继承变量，`popupClassName` 指定展开层 class 并写对应样式。

```scss
/* 默认展示框（触发器）- 必须覆盖全局白底 */
.你的页面根 .ant-select-UI .ant-select-selector {
  border-radius: 10px !important;
  border: 1px solid var(--as-border-color) !important;
  background: var(--as-panel-bg-color) !important;
  background-color: var(--as-panel-bg-color) !important;
  color: var(--as-primary-text-color) !important;
  box-shadow: inset 0 0 10px color-mix(in srgb, var(--as-accent-color) 10%, transparent) !important;
  backdrop-filter: blur(10px) !important;
}
.你的页面根 .ant-select-UI.ant-select-open .ant-select-selector,
.你的页面根 .ant-select-UI.ant-select-focused .ant-select-selector {
  background: var(--as-panel-bg-color) !important;
  background-color: var(--as-panel-bg-color) !important;
  border-color: var(--as-border-color) !important;
  box-shadow: inset 0 0 10px ... !important;
}
.你的页面根 .ant-select-UI .ant-select-selection-item,
.你的页面根 .ant-select-UI .ant-select-selection-placeholder {
  color: var(--as-primary-text-color) !important;
}
.你的页面根 .ant-select-UI .ant-select-arrow { color: var(--as-secondary-text-color) !important; }

/* 展开菜单（getPopupContainer 挂到页面根） */
.你的页面根 .你的popupClassName { background: var(--as-panel-bg-color) !important; border: 1px solid var(--as-border-color) !important; ... }
.你的页面根 .你的popupClassName .ant-select-item { color: var(--as-primary-text-color) !important; }
```

---

### 7. 空状态（Empty）

**改造步骤 8**：空状态提示文字使用次要色，hover/可点击时给强调色 + 发光：

```scss
color: var(--as-secondary-text-color);

&:hover {
  color: var(--as-accent-color);
  text-shadow: var(--as-glow-shadow);
}
```

---

## 三、本项目落地示例（智能体广场 & 插件广场）

按 **一、页面改造步骤** 改造后，当前项目中已套用该风格的文件如下，供对照与复用：

| 改造项 | 文件路径 | 说明 |
|--------|----------|------|
| 统一背景图 | `console/frontend/src/assets/imgs/upload/tech-square-bg.svg` | 智能体广场、插件广场、插件详情页共用；**替换此图即可更换所有广场/详情背景** |
| 智能体广场 | `console/frontend/src/pages/home-page/index.module.scss` | 根容器 `.homeWrapper`：变量、背景、主内容区面板、Tabs、输入框、卡片、空状态等 |
| 插件广场页面 | `console/frontend/src/pages/plugin-store/style.css` | 根容器 `.plugin-store-page`：变量、背景、顶栏、Tabs、搜索框、下拉框、展开菜单等 |
| 插件广场卡片 | `console/frontend/src/pages/plugin-store/components/tool-card/index.module.scss` | 列表卡片玻璃拟态与文案颜色 |
| **插件详情页** | `console/frontend/src/pages/plugin-store/detail/style.css` | 根容器 `.plugin-store-detail-page`：变量、背景、顶栏、主内容玻璃面板、强调色链接/按钮、隐私弹窗、滚动条 |

**在其它页面复用时**：按照 **一、页面改造步骤** 的顺序，从步骤 1 开始做到步骤 8（无对应模块可跳过），每步代码从 **二、样式规范与参考** 中对应小节复制并替换选择器中的「你的页面根」为实际根容器 class 即可。

