# BiManuRobo

> 🤖 面向具身双臂操作学习的大规模开放数据集

**BiManuRobo** 是一个致力于推动具身智能发展的开放数据集，专注于提供高质量、多模态、跨形态的双臂操作数据。我们旨在打破当前双臂数据集在机器人本体上的限制，构建一个支持多样化机器人结构、促进策略迁移与泛化能力研究的统一数据生态。

本项目不仅开放数据集供研究使用，更鼓励全球机器人厂商、研究机构、开发者共同贡献数据，形成“双向开放”的协作网络。平台将为所有贡献数据提供标准化处理、高质量标注与多模态融合支持，打造下一代具身学习的基础设施。

该数据集具备如下核心特点，并由本代码仓库提供完整的功能实现支持：

1. **模块化数据组织**：数据集由大量基于任务划分的子数据集构成，并支持基于标签的高效检索，以及基于大语言模型（LLM）的语义化子数据集搜索(Clip合作者ES)；
2. **双平台兼容**：原生支持 [Hugging Face Datasets Hub](https://huggingface.co/datasets) 与 [ModelScope](https://modelscope.cn) 两大开源数据平台，便于全球用户访问与集成；
3. **批量下载功能**：提供命令行与 API 接口，支持按任务、场景或多模态类型批量下载子数据集；
4. **一键上传支持**：支持将自采集的双臂操作数据集批量上传至 Hugging Face 或 ModelScope，助力社区共建；（简单的网页，提交数据集）
5. **开箱即用的算法支持**：为所有子数据集提供基于主流模仿学习与扩散策略的训练、推理与部署代码，包括：
   - [ACT (Action Chunking with Transformers)](https://arxiv.org/abs/2304.13705)
   - [Diffusion Policy](https://arxiv.org/abs/2304.13687)
   - [Pi0 / Pi-Fast](https://arxiv.org/abs/2402.15349) 等先进策略

通过本仓库，研究人员可快速完成“数据检索 → 下载 → 训练 → 部署”的完整闭环，极大提升双臂操作学习的研究效率。

## 克隆仓库
```bash
git clone https://github.com/BiManuRobo/BiManuRobo.git
cd BiManuRobo
```

## 🛠 使用 uv 管理项目

[`uv`](https://github.com/astral-sh/uv) 是一个超快的 Python 包安装器和虚拟环境管理器，兼容 `pyproject.toml` 和 `pip` 生态，是替代 `pip`, `poetry`, `pipenv` 的现代化选择。

### 安装 uv（如尚未安装）

```bash
pip install uv
```
### 创建和激活uv环境
```bash
uv venv
source .venv/bin/activate
uv pip install .
uv sync
```

---
## 📦 仓库使用方法

### 🔍 1. 搜索和下载子数据集

数据集搜索页面：Refer to https://BiManuRobo.github.io
#### 搜索结果会给出子数据集下载脚本
```bash
python -m bimanurobo.datasets.download --hub huggingface --ds_lists " \
pika_pickplace_cube_100 \
aloha_fold_cloth_200 \
"
# 如果想从modelscope下载数据集，请使用以下脚本
python -m bimanurobo.datasets.download --hub modelscope --ds_lists " \
pika_pickplace_cube_100 \
aloha_fold_cloth_200 \
"
```
数据集会默认保存到~/.cache/huggingface/或者~/.cache/modelscope/
你也可以自定义数据集保存地址
```bash
python -m bimanurobo.download --hub huggingface --ds_lists " \
pika_pickplace_cube_100 \
aloha_fold_cloth_200 \
" --download_path YOUR_DOWNLOAD_PATH
# 如果想从modelscope下载数据集，请使用以下脚本
python -m bimanurobo.download --hub modelscope --ds_lists " \
pika_pickplace_cube_100 \
aloha_fold_cloth_200 \
"  --download_path YOUR_DOWNLOAD_PATH
```

#### 或者搜索结果会列出子数据集列表，例子如下：
```bash
bimanurobo/pika_pickplace_cube_100 
bimanurobo/aloha_fold_cloth_200
```
你可以使用hugginface cli以及modelscope cli批量下载数据集
另外，由于数据集使用lerobot格式，所以你也可以使用lerobot下载数据

### 2. 模型训练、推理、部署
#### 模型训练(基于Lerobot实现)
```bash
python -m bimanurobo.models.train --robot realman --ds_list " \
baai-realman-picktoy-500 \
baai-realman-foldcloth-100 \
" \
--output_path your_model_path
```

#### 模型推理与部署(基于Lerobot实现)
```bash
python -m bimanurobo.models.deploy --robot realman --model your_model_name
```
---

### 3. 贡献你的数据集
#### 采集、制作你的数据集
#### 上传数据集到你的hub
```bash
# 上传到Huggingface或Modelscope
python -m bimanurobo.datasets.upload --config your_config_yaml_path
```
#### 通过邮件通知BiManuRobo项目组
在邮件中标明repo_ids，BiManuRobo项目组将协助对数据集进行整理、标注、测试，并上传到BiManuRobo Hub

## 🧪 标准开发流程（推荐）

以下是开发者常见的工作流程：

### 1. 安装编辑模式依赖

```bash
uv pip install -e .[dev]
```

### 2. 安装 pre-commit 钩子（提交前自动格式化和检查代码）
```
pre-commit install
```

---

## 🔧 常用依赖管理操作

### 添加新依赖

推荐在`pyproject.toml`文件中手动添加依赖项，或使用以下命令。
```bash
uv add requests           # 添加运行时依赖
uv add --test ruff       # 添加开发依赖
```

这些命令会自动更新 `pyproject.toml` 和 `uv.lock` 文件。

### 添加或删除依赖

在pyproject.toml中的相应位置，添加或删除依赖项

### 查看已安装依赖

```bash
uv pip list
```
---

## 🧹 清理与重建环境（可选）

```bash
# 删除虚拟环境
rm -rf .venv/

# 重新创建和安装
uv venv
uv pip install -e .[dev]
```
---
