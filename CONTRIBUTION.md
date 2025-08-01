# 贡献指南（Contributing Guide）

我们欢迎社区的贡献！无论是修复 bug、改进文档还是提出新功能建议，都非常感谢。请花一点时间阅读以下贡献指南，以确保贡献流程顺利。

## 🛠 如何贡献

1. **Fork 本仓库**
   在 GitHub 上点击 "Fork" 按钮，将项目复制到你的账户下。

2. **创建分支**
   创建一个新的特性分支用于开发：
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **编写代码并测试**
   实现你的功能或修复，并确保所有测试通过。如果添加了新功能，请补充相应的单元测试。

4. **格式化代码**
   使用项目配置的格式工具（如 `ruff`等）对代码进行格式化：
   ```bash
   ruff format .
   ruff check .
   ```

5. **提交更改**
   使用清晰、简洁的提交信息描述你的更改：
   ```bash
   git commit -m "Fix bug in login flow"
   ```

6. **推送分支**
   将你的本地分支推送到你的 fork 仓库：
   ```bash
   git push origin feature/your-feature-name
   ```

7. **创建 Pull Request (PR)**
   前往 GitHub 页面，发起一个 Pull Request 到主仓库的 `main` 或 `develop` 分支。

## 📝 PR 提交要求

- 描述清楚你修改的内容和目的。
- 如果修复了一个 issue，请在描述中加入 `Fixes #issue-number`。
- 确保 CI 构建通过（如自动运行的测试、格式检查等）。
- 遵守项目的编码规范（见 `pyproject.toml` 中的配置）。
- 保持提交历史清晰，避免不必要的合并提交。

## 🐞 报告 Bug

如果你发现了 bug，请先查看 [Issues](https://https://github.com/BiManuRobo/BiManuRobo/issues) 是否已有相关报告。如果没有，请新建一个 issue 并提供以下信息：

- 操作系统和 Python 版本
- 完整的错误日志
- 复现步骤
- 期望行为与实际行为的差异

## 💡 提出新功能

我们非常欢迎新功能的建议！请先在 Issues 中发起讨论，说明你的想法和使用场景。我们会评估可行性并与你协作完善方案。

## 🧑‍💻 开发者环境设置

安装开发依赖：
```bash
uv install -e . --dev
```

运行测试：
```bash
pytest tests/
```

格式化与检查：
```bash
ruff format .
ruff check .
```

---

再次感谢你的贡献！开源因你而精彩 🎉
