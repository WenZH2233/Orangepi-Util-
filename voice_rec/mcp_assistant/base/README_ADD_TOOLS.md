# 如何添加新的 MCP 工具

本文档详细说明如何在 `mcp_assistant/base` 框架下添加新的 MCP (Model Context Protocol) 工具。

## 目录结构

当前工具位于 `voice_rec/mcp_assistant/base/tools/` 目录下。

```text
voice_rec/mcp_assistant/base/
├── all_tools.py          # MCP 服务器入口，负责注册所有工具
├── tools/                # 工具实现目录
│   ├── math_tools.py     # 简单工具示例
│   ├── ir_control/       # 复杂工具包示例
│   ├── ir_control_tools.py # 复杂工具的包装器
│   └── ...
```

## 添加工具的步骤

### 方式一：添加简单工具 (单文件)

如果你的工具逻辑比较简单，可以直接创建一个新的 Python 文件。

1.  **创建工具文件**
    在 `tools/` 目录下创建文件，例如 `tools/my_tools.py`。

    ```python
    # tools/my_tools.py
    
    def hello_world(name: str) -> str:
        """
        这是一个示例工具，用于向用户打招呼。
        
        Args:
            name: 用户的名字
        """
        return f"Hello, {name}!"
    ```
    *注意：函数的文档字符串 (Docstring) 非常重要，它会被用作工具的描述，帮助 AI 理解何时以及如何使用该工具。*

2.  **注册工具**
    打开 `voice_rec/mcp_assistant/base/all_tools.py`。

    *   **导入你的函数**：
        ```python
        # ... 现有的导入 ...
        from tools.my_tools import hello_world
        ```

    *   **注册到 MCP 服务器**：
        ```python
        # ... 现有的注册 ...
        mcp.tool()(hello_world)
        ```
    
    *   **更新启动日志 (可选但推荐)**：
        在 `if __name__ == "__main__":` 块中，将你的工具名添加到 `tool_names` 列表中，以便在启动时看到它被加载。

### 方式二：添加复杂工具 (目录结构)

如果你的工具包含多个文件、依赖或复杂的业务逻辑，建议使用目录结构。

1.  **创建工具目录**
    在 `tools/` 下创建一个新目录，例如 `tools/smart_home/`。
    在该目录下实现你的核心逻辑（例如 `manager.py`, `device.py` 等）。

2.  **创建包装器 (Wrapper)**
    为了保持 `all_tools.py` 的整洁，建议在 `tools/` 根目录下创建一个包装器文件，例如 `tools/smart_home_tools.py`。这个文件负责将底层逻辑封装成简单的异步或同步函数，供 MCP 调用。

    ```python
    # tools/smart_home_tools.py
    
    from .smart_home.manager import SmartHomeManager
    
    # 实例化管理器 (如果是单例模式)
    manager = SmartHomeManager()
    
    async def turn_on_light(room: str) -> str:
        """
        打开指定房间的灯。
        """
        return await manager.control_light(room, True)
    ```

3.  **注册工具**
    同样在 `voice_rec/mcp_assistant/base/all_tools.py` 中注册。

    ```python
    from tools.smart_home_tools import turn_on_light
    
    # ...
    mcp.tool()(turn_on_light)
    ```

## 最佳实践

1.  **类型提示 (Type Hints)**：务必为参数和返回值添加类型提示（如 `str`, `int`, `dict`）。FastMCP 会利用这些信息生成工具的 Schema。
2.  **文档字符串 (Docstrings)**：清晰描述工具的功能、参数含义。这是 AI "看到" 的说明书。
3.  **错误处理**：在工具内部捕获预期的异常，并返回易读的错误信息字符串或 JSON，而不是让程序崩溃。
4.  **异步支持**：如果工具涉及 I/O 操作（网络请求、文件读写），建议定义为 `async def`。

## 测试新工具

1.  **重启 MCP 服务**
    修改代码后，需要重启 MCP 服务才能生效。
    ```bash
    sudo systemctl restart xz-mcp.service
    ```
    或者如果你是在命令行手动运行的：
    ```bash
    python mcp_pipe.py
    ```

2.  **验证加载**
    查看日志，确认你的工具出现在 "Loaded tools" 列表中。
    ```bash
    journalctl -u xz-mcp.service -f
    ```

3.  **交互测试**
    启动客户端 CLI 进行测试：
    ```bash
    python ./main.py --mode cli
    ```
    直接用自然语言要求 AI 使用新工具，例如："使用 hello_world 工具向 Alice 打招呼"。
