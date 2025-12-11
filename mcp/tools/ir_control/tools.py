"""IR 控制工具函数

这些回调由 MCP 工具管理器注册并被调用。
实现串口与红外学习模块通信，协议兼容 mcps/ir_control/ir_control.py。
"""

from __future__ import annotations

import json
import os
import time
from typing import Dict, List, Any

try:
	import serial  # type: ignore
except Exception:  # 允许在未安装时加载其它工具
	serial = None  # type: ignore

from src.utils.logging_config import get_logger

logger = get_logger(__name__)


# 默认串口参数（可通过环境变量覆盖）
DEFAULT_SERIAL_PORT = os.environ.get("IR_SERIAL_PORT", "/dev/ttyS1")
DEFAULT_BAUD_RATE = int(os.environ.get("IR_BAUD", "115200"))


def _calculate_checksum(address: int, afn: int, data: bytes) -> int:
	payload = [address, afn] + list(data)
	return sum(payload) % 256


def _build_frame(afn: int, data: bytes = b"") -> bytes:
	frame_header = b"\x68"
	frame_tail = b"\x16"
	module_address = 0xFF  # 广播地址

	length = 7 + len(data)  # 1头 +2长 +1址 +1功能 +N数据 +1校验 +1尾
	len_low = length & 0xFF
	len_high = (length >> 8) & 0xFF

	checksum = _calculate_checksum(module_address, afn, data)

	command = bytearray()
	command.extend(frame_header)
	command.append(len_low)
	command.append(len_high)
	command.append(module_address)
	command.append(afn)
	command.extend(data)
	command.append(checksum)
	command.extend(frame_tail)
	return bytes(command)


def _find_hex_dir() -> str:
	"""寻找仓库中的 IR hex 目录.

	由于运行目录通常是 voice_rec/py-xiaozhi，直接定位 mcps/ir_control/hex。
	从当前文件向上逐级查找，直到发现目标目录为止。
	"""
	cur = os.path.abspath(os.path.dirname(__file__))
	for _ in range(8):
		candidate = os.path.join(cur, "mcps", "ir_control", "hex")
		if os.path.isdir(candidate):
			return candidate
		# 兼容当前位于 src/mcp/tools/ir_control 的情况
		candidate2 = os.path.join(cur, "..", "..", "..", "..", "..", "..", "mcps", "ir_control", "hex")
		candidate2 = os.path.abspath(candidate2)
		if os.path.isdir(candidate2):
			return candidate2
		cur = os.path.abspath(os.path.join(cur, os.pardir))

	# 回退到相对路径（在 voice_rec/py-xiaozhi 下运行常用）
	fallback = os.path.abspath(os.path.join(os.getcwd(), "..", "mcps", "ir_control", "hex"))
	return fallback


def _open_serial() -> "serial.Serial":
	if serial is None:
		raise RuntimeError("pyserial 未安装，请先在 py-xiaozhi/requirements.txt 中安装 'pyserial'")
	try:
		ser = serial.Serial(DEFAULT_SERIAL_PORT, DEFAULT_BAUD_RATE, timeout=2)
		return ser
	except Exception as e:
		raise RuntimeError(f"无法打开串口 {DEFAULT_SERIAL_PORT}: {e}")


def _meta_file_path(hex_dir: str | None = None) -> str:
	if not hex_dir:
		hex_dir = _find_hex_dir()
	return os.path.join(hex_dir, "codes_meta.json")


def _load_codes_meta(hex_dir: str | None = None) -> Dict[str, Any]:
	try:
		meta_path = _meta_file_path(hex_dir)
		if os.path.isfile(meta_path):
			with open(meta_path, "r", encoding="utf-8") as f:
				return json.load(f)
	except Exception as e:
		logger.warning(f"读取 codes_meta.json 失败: {e}")
	return {}


def _save_codes_meta(meta: Dict[str, Any], hex_dir: str | None = None) -> None:
	try:
		hex_dir = hex_dir or _find_hex_dir()
		os.makedirs(hex_dir, exist_ok=True)
		meta_path = _meta_file_path(hex_dir)
		with open(meta_path, "w", encoding="utf-8") as f:
			json.dump(meta, f, ensure_ascii=False, indent=2)
	except Exception as e:
		raise RuntimeError(f"保存 codes_meta.json 失败: {e}")


def list_ir_codes(_: Dict) -> str:
	"""列出可用的 IR hex 文件

	返回 JSON 字符串：[{"name": "tv_power", "path": "/abs/path"}, ...]
	"""
	hex_dir = _find_hex_dir()
	if not os.path.isdir(hex_dir):
		return json.dumps({"error": f"目录不存在: {hex_dir}", "items": []}, ensure_ascii=False)

	meta = _load_codes_meta(hex_dir)
	items: List[Dict[str, Any]] = []
	for fn in os.listdir(hex_dir):
		if not fn.endswith(".hex"):
			continue
		name = fn[:-4]
		path = os.path.abspath(os.path.join(hex_dir, fn))
		info = meta.get(name, {}) if isinstance(meta, dict) else {}
		# 兼容别名字段名：aliases/labels
		aliases = info.get("aliases") or info.get("labels") or []
		# 兼容字符串型 aliases（逗号分隔）
		if isinstance(aliases, str):
			aliases = [s.strip() for s in aliases.split(",") if s.strip()]
		items.append(
			{
				"name": name,
				"path": path,
				"description": info.get("description", ""),
				"aliases": aliases,
				"category": info.get("category", ""),
				"device": info.get("device", ""),
			}
		)

	return json.dumps({"dir": hex_dir, "items": items}, ensure_ascii=False)


def _parse_hex_string(hex_str: str) -> bytes:
	try:
		return bytes.fromhex(hex_str.replace("\n", " ").replace("\t", " ").replace("  ", " ").strip())
	except Exception:
		raise ValueError("无效的十六进制数据")


def _send_external_data(data: bytes) -> str:
	ser = _open_serial()
	try:
		cmd = _build_frame(0x22, data=data)
		ser.write(cmd)
		resp = ser.read(8)
		if resp:
			return f"发送成功，设备回复: {resp.hex(' ')}"
		return "发送成功（无回复）"
	finally:
		try:
			ser.close()
		except Exception:
			pass


def send_ir_by_name(args: Dict) -> str:
	name: str = args.get("name", "").strip()
	if not name:
		raise ValueError("缺少参数 name")

	hex_dir = _find_hex_dir()
	file_path = os.path.join(hex_dir, f"{name}.hex")
	if not os.path.isfile(file_path):
		raise FileNotFoundError(f"未找到红外文件: {file_path}")

	with open(file_path, "r") as f:
		data_hex = f.read()
	data = _parse_hex_string(data_hex)
	return _send_external_data(data)


def send_ir_by_hex(args: Dict) -> str:
	hex_str: str = args.get("hex", "").strip()
	if not hex_str:
		raise ValueError("缺少参数 hex")
	data = _parse_hex_string(hex_str)
	return _send_external_data(data)


def learn_ir_and_save(_: Dict) -> str:
	"""进入外部学习模式，成功后保存到 hex 目录

	设备交互流程：
	- 发送 AFN=0x20 进入学习
	- 可能先收到状态帧 AFN=0x01, 然后再收到 AFN=0x22 的数据帧
	- 将数据部分保存为 .hex 文件
	"""
	hex_dir = _find_hex_dir()
	os.makedirs(hex_dir, exist_ok=True)

	ser = _open_serial()
	try:
		logger.info("进入外部学习模式...")
		ser.write(_build_frame(0x20))

		# 等待第一段数据
		resp = ser.read(500)
		if resp and len(resp) >= 7 and resp[0] == 0x68 and resp[4] == 0x22:
			data = resp[5:-2]
		elif resp and len(resp) >= 8 and resp[0] == 0x68 and resp[4] == 0x01:
			# 继续等待真正数据帧
			resp2 = ser.read(800)
			if resp2 and len(resp2) >= 7 and resp2[0] == 0x68 and resp2[4] == 0x22:
				data = resp2[5:-2]
			else:
				raise RuntimeError("未收到学习成功的数据帧")
		else:
			raise RuntimeError(f"未收到有效响应: {resp.hex(' ') if resp else '无'}")

		if not data:
			raise RuntimeError("学习数据为空")

		filename = f"ir_code_{int(time.time())}.hex"
		save_path = os.path.abspath(os.path.join(hex_dir, filename))
		with open(save_path, "w") as f:
			f.write(data.hex(" "))

		return json.dumps({"saved": save_path, "bytes": len(data)}, ensure_ascii=False)
	finally:
		try:
			ser.close()
		except Exception:
			pass


def get_ir_code_info(args: Dict) -> str:
	"""获取单个红外码的元数据信息

	参数：
	- name: 代码名称（去掉 .hex）
	返回：{ name, path, description, aliases, category, device }
	"""
	name: str = (args.get("name") or "").strip()
	if not name:
		raise ValueError("缺少参数 name")
	hex_dir = _find_hex_dir()
	file_path = os.path.join(hex_dir, f"{name}.hex")
	if not os.path.isfile(file_path):
		raise FileNotFoundError(f"未找到红外文件: {file_path}")
	meta = _load_codes_meta(hex_dir)
	info = meta.get(name, {}) if isinstance(meta, dict) else {}
	aliases = info.get("aliases") or info.get("labels") or []
	if isinstance(aliases, str):
		aliases = [s.strip() for s in aliases.split(",") if s.strip()]
	return json.dumps(
		{
			"name": name,
			"path": os.path.abspath(file_path),
			"description": info.get("description", ""),
			"aliases": aliases,
			"category": info.get("category", ""),
			"device": info.get("device", ""),
		},
		ensure_ascii=False,
	)


def set_ir_code_info(args: Dict) -> str:
	"""设置/更新红外码的元数据信息

	参数：
	- name: 必填
	- description: 可选
	- aliases: 可选（字符串，逗号分隔），也可传 JSON 字符串数组（将尝试解析）
	- category/device: 可选
	写入 mcps/ir_control/hex/codes_meta.json
	返回更新后的对象。
	"""
	name: str = (args.get("name") or "").strip()
	if not name:
		raise ValueError("缺少参数 name")

	hex_dir = _find_hex_dir()
	file_path = os.path.join(hex_dir, f"{name}.hex")
	if not os.path.isfile(file_path):
		raise FileNotFoundError(f"未找到红外文件: {file_path}")

	meta = _load_codes_meta(hex_dir)
	if not isinstance(meta, dict):
		meta = {}

	entry = meta.get(name, {}) if isinstance(meta.get(name), dict) else {}

	# description
	if "description" in args and isinstance(args["description"], str):
		entry["description"] = args["description"].strip()

	# aliases: 逗号分隔或 JSON 字符串
	if "aliases" in args and isinstance(args["aliases"], str):
		raw = args["aliases"].strip()
		aliases_list: List[str] = []
		if raw:
			try:
				parsed = json.loads(raw)
				if isinstance(parsed, list):
					aliases_list = [str(x).strip() for x in parsed if str(x).strip()]
				else:
					aliases_list = [s.strip() for s in raw.split(",") if s.strip()]
			except Exception:
				aliases_list = [s.strip() for s in raw.split(",") if s.strip()]
		entry["aliases"] = aliases_list

	# category/device
	for key in ("category", "device"):
		if key in args and isinstance(args[key], str):
			entry[key] = args[key].strip()

	meta[name] = entry
	_save_codes_meta(meta, hex_dir)

	return json.dumps(
		{
			"name": name,
			"path": os.path.abspath(file_path),
			**entry,
		},
		ensure_ascii=False,
	)

