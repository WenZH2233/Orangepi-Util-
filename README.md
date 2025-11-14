# OrangePi-Util

## Introduction

Create a voice assistant for the home that can control various devices, and use it as a set-top box (similar to Apple TV). It can also connect to AI and MCP to expand the voice assistant's functionality. Additionally, use it as a server.

## Features
- Voice assistant functionality—can be used directly or paired with the ESP32 voice assistant client
- Infrared device control
- MCP support
- Set-top box functionality
- Minecraft server
- AI integration
- Local speech recognition

## Installation
Please refer to the README documentation of each module for detailed installation steps and configuration instructions.

## Directory Structure
```
OrangePi-Util/
├── PCB/                  # PCB design files and images
├── CAD/                  # Model files
├── voice_rec/               # Voice recognition and assistant module
├──── mcp_assistant/                  # MCP assistant module
├──── py_xiaozhi/                            # Voice assistant client
├──── voiceprint-api/                  # Voiceprint recognition API
├──── xiaozhi-esp32-server/      # Voice assistant server
├──── esp32-client/                  # ESP32 voice assistant client
├── tv_box/                  # Set-top box module
├── server/                  # Server module
```

## Examples

![Client Circuit Schematic](PCB/SCH_Schematic_1_1-P1_2025-11-14.png)
![Client PCB Design](PCB/PCB_IMAGE.png)
![Server Circuit Schematic](PCB/SCH_Schematic1_1-P1_2025-11-14.png)
![OrangePi Case](CAD/SnowShot_2025-11-14_18-40-17.png)

## Contribution
Contributions are welcome! Please refer to the contribution guidelines of each module to learn how to participate in development.

## License
This project is licensed under the MIT License. For details, please refer to the LICENSE file.


This README was translated using AI from [README_cn.md](README_cn.md)