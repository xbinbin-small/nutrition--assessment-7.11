# 代码风格和模式

请遵循以下代码风格和常用模式：

- **组件命名**: React 组件应使用 **PascalCase** 命名 (例如，`VocabularyCard`, `WordInput`)。
- **函数命名**: 辅助函数应使用 **camelCase** 命名 (例如，`formatWord`, `generateStory`)。
- **变量命名**: 变量应使用 **camelCase** 命名 (例如，`userWords`, `generatedText`)。常量可以使用 **UPPER_SNAKE_CASE** (例如，`MAX_WORDS`)。
- **组件类型**: 除非有特殊理由，否则优先使用**函数式组件**和**箭头函数**语法。
- **状态管理**: 优先考虑使用 React 的 `useState` 和 `useEffect` 进行组件级别的状态管理。如果需要更复杂的状态管理，请根据具体情况考虑 `useContext` 或其他的轻量级状态管理库。
- **错误处理**: 在进行 API 调用和处理用户输入时，务必进行适当的错误处理。
