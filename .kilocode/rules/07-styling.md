# 样式指南

- **Tailwind CSS 优先**: 在编写组件样式时，**始终优先使用 Tailwind CSS 的工具类**直接在 JSX 中进行样式化。
- **自定义 CSS**: 如果需要自定义 CSS，请尽量通过在 `tailwind.config.js` 中扩展 Tailwind 的配置，或者使用 Tailwind 的 **`@apply` 指令**来组合 Tailwind 的工具类。避免编写大量的完全自定义的 CSS。
- **Tailwind 配置**: 任何对 Tailwind CSS 的自定义（例如，添加新的颜色、字体、断点）都应该在 `tailwind.config.js` 文件中进行。
- **响应式设计**: 在设计页面和组件时，请始终考虑**响应式设计**，并利用 Tailwind CSS 的响应式前缀 (例如，`sm:`, `md:`, `lg:`) 来适配不同的屏幕尺寸。