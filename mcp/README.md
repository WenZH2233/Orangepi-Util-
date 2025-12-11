# MCP（Model Context Protocol）说明

py-xiaozhi 内置了一个轻量的 MCP 服务器实现（`src/mcp/mcp_server.py`），用于通过「工具」对外暴露本地能力（系统、相机、截图、音乐、日历、温湿度、红外等）。

本说明涵盖：
- 传输与握手
- 工具发现与调用
- 返回结果与错误语义（含本项目的约定）
- 如何新增/注册一个工具
- 示例：红外（IR）控制工具

---

## 传输与握手
- 传输：通过 WebSocket 与上层服务通信（参见 `src/protocols/websocket_protocol.py`）。
- 连接建立后，客户端会发送 `hello`，服务器返回 `hello` 确认。
- MCP 消息以 JSON-RPC 2.0 格式承载，主要方法：
  - `initialize`
  - `tools/list`
  - `tools/call`

> 本仓库的 MCP 部分遵循网站规范（2024-11-05 版），但实现做了实用化精简。

---

## 工具发现（tools/list）
请求示例：
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/list",
  "params": {}
}
```
响应示例（截断）：
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "tools": [
      {
        "name": "self.ir.send_named",
        "description": "发送已保存的红外编码",
        "inputSchema": {
          "type": "object",
          "properties": {
            "name": { "type": "string" }
          },
          "required": ["name"]
        }
      }
    ]
  }
}
```

分页：如果工具很多，`tools/list` 会使用 `nextCursor` 进行分页。

---

## 工具调用（tools/call）
请求示例：
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "self.ir.send_named",
    "arguments": { "name": "tv_power" }
  }
}
```

响应（成功）：
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "content": [ { "type": "text", "text": "发送成功（无回复）" } ],
    "isError": false
  }
}
```

响应（失败）：
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "content": [ { "type": "text", "text": "无法打开串口 /dev/ttyS1: Permission denied" } ],
    "isError": true
  }
}
```

> 重要：本项目做了约定——即使出错也通过 `result` 返回（`isError=true`，并在 `content[0].text` 放置明确的错误原因），尽量不使用 JSON-RPC 的 `error` 字段，避免上游丢失提示文案。

---

## 如何新增/注册一个工具
1. 定义回调（同步或异步函数），签名接收 `Dict[str, Any]` 参数，返回 `bool|int|str` 或自定义文本。
2. 在某个工具管理器中进行注册，或直接通过 `McpServer.add_tool` 注册。

示例（最小化直接注册）：
```python
from src.mcp.mcp_server import McpServer, McpTool, PropertyList, Property, PropertyType

async def hello(args):
    name = args.get("name", "world")
    return f"Hello, {name}!"

srv = McpServer.get_instance()
srv.add_tool(McpTool(
    name="self.demo.hello",
    description="示例工具：打招呼",
    properties=PropertyList([Property("name", PropertyType.STRING, default_value="world")]),
    callback=hello
))
```

集中注册（推荐）：
- 每类工具提供一个 manager，在 `init_tools(add_tool, PropertyList, Property, PropertyType)` 里集中注册。
- 在 `McpServer.add_common_tools()` 中统一加载各 manager（如系统/相机/红外等），避免散落注册。

---

## 示例：红外（IR）工具
- 代码：`src/mcp/tools/ir_control/`
- 对外工具：
  - `self.ir.list_codes`（列目录）
  - `self.ir.send_named`（按名称发送）
  - `self.ir.send_hex`（十六进制字符串发送）
  - `self.ir.learn_external`（学习并保存）
- 文档：`src/mcp/tools/ir_control/README.md`
- 依赖：`pyserial`（已在 `requirements.txt`）
- 串口：默认 `/dev/ttyS1`（可通过环境变量 `IR_SERIAL_PORT`、`IR_BAUD` 覆盖）

---

## 常见问题（FAQ）
- Q：为什么 result 里会有 isError=true？
  - A：为了让上游始终拿到明确的错误文本，统一错误载荷，避免丢信息。
- Q：如何查看当前已注册的工具？
  - A：发送 `tools/list`。在代码侧，`McpServer.get_instance().tools` 也可直接查看。
- Q：如何保证大工具列表不超出体积？
  - A：`tools/list` 内置按 payload 大小分页，使用 `nextCursor`。

---

## 参考
- `src/mcp/mcp_server.py`
- `src/mcp/tools/*`
- `src/protocols/websocket_protocol.py`
