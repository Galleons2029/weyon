# AI Open Platform

WeYon AI 开发平台，提供各种开发能力，包括：

- [x] WeYon 知识库

## 依赖

- **Python3.10+** 的平台
- **Qdrant** 向量数据库
- 外部平台提供的**Embedding**接口

> [!Important]
>
> 相关配置均可在 `src/kb/kb_config.py`中找到。可以直接修改为自己的配置，或者修改环境变量（需要和变量名一致，区分大小写，程序启动是会检测虚拟环境并将其存在的注入到配置类中）

## 安装 :package:

## Qdrant 安装与配置 :minidisc:

> [!Tip]
>
> Qdrant是一个专为下一代AI应用设计的向量数据库，它提供了强大的语义搜索和相似性匹配功能，适用于图片、语音、视频搜索以及推荐系统等业务场景。
>
> Qdrant 官方文档：
>
> - [Qdrant Document](https://qdrant.tech/documentation/)
>
> - [Qdrant Docker 启动教程](https://qdrant.tech/documentation/quickstart/)

**Qdrant** 安装可以选择使用**虚拟容器安装**或者直接**二进制安装**，推荐使用**Docker**安装

```shell
sudo docker pull qdrant/qdrant
```

> [!Tip]
>
> 由于国内网路限制，可能存在无法拉取镜像的问题。可以参考[Docker 设置代理](https://neucrack.com/p/286)
>
> 或者使用已经存档的Qdrant镜像文件加载`sudo docker load -i <imagefile>`

启动 **Qdrant** 服务

```shell
sudo docker run -p 6333:6333 \
    -v $(pwd)/qdrant_storage:/qdrant/storage:z \
    qdrant/qdrant
```

> [!Important]
>
> 一定要记得修改相关配置`src/kb/kb_config.py`中的`QdrantConfig`

## Embedding 接口

本项目所使用的embedding接口需要遵循**OpenAI**的接口规范。可以直接使用**OpenAI**提供的接口。如果搭建本地环境，推荐使用*
*Xinference**作为平台构部署Embedding模型。



> [!Important]
>
> 项目所需要的Embedding模型可以在`src/kb/kb_config.py`中的`XinferenceConfig`修改。

## Python 环境安装

### 创建 Conda 虚拟环境（推荐）:star2:

> [!Tip]
>
Conda是一个开源的包管理系统和环境管理系统，它主要用于安装和管理软件包以及创建和维护不同版本的软件环境。Conda可以在Windows、macOS和Linux操作系统上运行，与Python编程语言结合使用。Conda允许用户安装不同版本的库和工具，同时保持它们之间的相互独立，避免版本冲突。
>
> Conda 安装教程： [Conda Installation](https://conda.io/projects/conda/en/latest/user-guide/install/index.html)

1. 开启一个新的虚拟环境并且安装相关依赖

```shell
conda create -n AIOpenPlatform python=3.11 -y
conda activate AIOpenPlatform
python -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --upgrade pip
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 启动项目

```shell
cd src
python -m uvicorn app:app --host 0.0.0.0
```

## 日志审查

启动后控制台默认输出日志级别为***INFO***，如果在控制台看更高级别的日志可以在`src/config.py`文件中的`console_handle()`函数修改
`console_handler.setLevel(logging.DEBUG)`。生产环境不建议如此

生产环境下的日志审计可以查看`src/logs`下的日志文件。全局日志记录为`<date>_G.log`，全局业务异常记录为`<date>_G.log`

> [!Tip]
>
> 由于时间关系没有作以天为单位的日志输出控制，也就是日志只会按照启动时间创建日志文件。生产环境下如果需要作精细化日志，可以考虑使用定期重启的方式或者改写代码



