# IR（红外）控制 MCP 工具

本目录为 py-xiaozhi 的红外控制工具集成点，封装了 `mcps/ir_control/ir_control.py` 的能力，并通过 MCP 暴露以下工具：

- `self.ir.list_codes`：列出可用的红外编码（位于 `mcps/ir_control/hex`）。
- `self.ir.get_ir_code_info`：获取单个编码的元数据（描述、别名、分类、设备等）。
- `self.ir.send_named`：按名称发送（名称为 hex 文件名，不含后缀）。
- `self.ir.send_hex`：直接发送十六进制字符串（字节间可有空格）。
- `self.ir.learn_external`：进入学习模式，保存为 `.hex` 文件。
- `self.ir.set_ir_code_info`：设置/更新红外码的元数据（描述、别名、分类、设备）。

## 依赖与权限

- Python 依赖：`pyserial`（已在 `requirements.txt` 中添加）。
- 串口权限：确保当前用户可读写串口（常见为 `/dev/ttyS1`）。可使用 `mcps/ir_control/setup_serial_permissions.sh` 一键配置。

## 串口参数

可通过环境变量覆盖默认值：

- `IR_SERIAL_PORT`（默认 `/dev/ttyS1`）
- `IR_BAUD`（默认 `115200`）

## HEX 目录与元数据

工具会自动查找本仓库的 `mcps/ir_control/hex` 目录。新增的学习结果也会保存到此目录下。

### 给 HEX 文件添加“别名/说明”等元数据

在 `mcps/ir_control/hex` 目录下新增 `codes_meta.json`，用于为每个 hex 文件（不带后缀的名称）添加说明、别名、分类、设备等信息：

```json
{
  "tv_ok": {
    "description": "确认/播放暂停键（部分设备 ‘OK’ 同时具备播放/暂停功能）",
    "aliases": ["确认", "OK", "播放/暂停", "确定"],
    "category": "tv",
    "device": "电视/机顶盒"
  }
}
```

你也可以通过 MCP 工具直接更新：`self.ir.set_ir_code_info`（见下）。

## 作为 MCP 工具使用

MCP 服务启动后，可以通过 `tools/list` 查看工具定义，通过 `tools/call` 调用：

- 列表工具（示例）：
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/list",
  "params": {}
}
```

- 发送已保存的 IR（示例 `tv_power`）：
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {"name": "self.ir.send_named", "arguments": {"name": "tv_power"}}
}
```

- 发送十六进制串：
```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "method": "tools/call",
  "params": {"name": "self.ir.send_hex", "arguments": {"hex": "b7 04 b4 04 ..."}}
}
```

- 学习保存为 hex：
```json
{
  "jsonrpc": "2.0",
  "id": 5,
  "method": "tools/call",
  "params": {"name": "self.ir.learn_external", "arguments": {}}
}
```

- 查看单个编码的说明/别名：
```json
{
  "jsonrpc": "2.0",
  "id": 6,
  "method": "tools/call",
  "params": {"name": "self.ir.get_ir_code_info", "arguments": {"name": "tv_ok"}}
}
```

- 设置/更新说明与别名：
```json
{
  "jsonrpc": "2.0",
  "id": 7,
  "method": "tools/call",
  "params": {
    "name": "self.ir.set_ir_code_info",
    "arguments": {
      "name": "tv_ok",
      "description": "确认/播放暂停键",
      "aliases": "确认,OK,播放/暂停,确定",
      "category": "tv",
      "device": "电视/机顶盒"
    }
  }
}
```

> 注意：`aliases` 支持逗号分隔字符串，或 JSON 字符串数组（如 "[\"确认\", \"OK\"]"）。

## 故障排查

- 无法打开串口：检查 `IR_SERIAL_PORT` 是否正确、用户是否在 `dialout` 组、设备文件权限是否正确。
- 发送成功但无响应：部分设备不会回包；可通过外设实际动作或串口抓包确认。
- 学习模式无数据：确认 10 秒内按下遥控器，必要时减少环境红外干扰距离。
