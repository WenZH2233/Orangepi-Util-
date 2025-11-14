# OrangePi-Util

## 简介

为家庭打造一个可以控制各种设备的语音助手，并将其用作机顶盒（类似于 Apple TV）。它还可以连接到 AI 和 MCP 以扩展语音助手的功能。此外，还可以将其用作服务器

## 特性
- 语音助手功能--既可以直接使用，也可以搭配 ESP32 语音助手客户端使用
- 红外设备控制
- MCP 支持
- 机顶盒功能
- Minecraft 服务器
- AI 集成
- 本地语音识别

## 安装
请参考各个模块的 README 文档以获取详细的安装步骤和配置说明。

## 目录结构
```
OrangePi-Util/
├── PCB/                  # PCB 设计文件和图片
├── CAD/                  # 模型文件
├── voice_rec/               # 语音识别和助手模块
├──── mcp_assistant/                  # MCP 助手模块
├──── py_xiaozhi/                            # 语音助手客户端
├──── voiceprint-api/                  # 音色识别 API
├──── xiaozhi-esp32-server/      # 语音助手服务端
├──── esp32-client/                  # ESP32 语音助手客户端
├── tv_box/                  # 机顶盒模块
├── server/                  # 服务器模块
```

## 示例图

![客户端电路原理图](PCB/SCH_Schematic_1_1-P1_2025-11-14.png)
![客户端 PCB 设计图](PCB/PCB_IMAGE.png)
![服务端电路原理图](PCB/SCH_Schematic1_1-P1_2025-11-14.png)
![orangepi 外壳](CAD/SnowShot_2025-11-14_18-40-17.png)
## 贡献
欢迎贡献代码！请参考各个模块的贡献指南以了解如何参与开发。

## 许可证
本项目采用 MIT 许可证，详情请参阅 LICENSE 文件。



本README使用 AI 翻译自 (README_cn.md)[README_cn.md]