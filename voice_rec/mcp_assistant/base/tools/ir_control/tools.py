"""IR 控制工具函数

这些回调由 MCP 工具管理器注册并被调用。
实现串口与红外学习模块通信，协议兼容 mcps/ir_control/ir_control.py。
"""

from __future__ import annotations

import json
import os
import time
import threading
from typing import Dict, List, Any

try:
	import serial  # type: ignore
except Exception:  # 允许在未安装时加载其它工具
	serial = None  # type: ignore

from .utils import get_logger, get_ir_data_dir

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
	"""寻找仓库中的 IR hex 目录."""
	return get_ir_data_dir()


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


# 全局学习状态
_learning_state = {
	"status": "idle",  # idle, learning, success, error
	"result": None,    # filepath or error message
	"timestamp": 0,
	"name": None
}
_learning_lock = threading.Lock()

def _background_learn_task(target_name: str = None, meta_info: Dict = None):
	global _learning_state
	
	hex_dir = _find_hex_dir()
	os.makedirs(hex_dir, exist_ok=True)

	ser = None
	try:
		ser = _open_serial()
		# 增加超时时间，给用户更多时间操作遥控器
		ser.timeout = 30
		# 设置字节间超时
		ser.inter_byte_timeout = 0.5
		
		logger.info("进入外部学习模式(后台)...")
		ser.write(_build_frame(0x20))

		buffer = bytearray()
		start_time = time.time()
		data = None

		# 循环读取直到超时或获取到有效数据
		while time.time() - start_time < 35:
			chunk = ser.read(1024)
			if chunk:
				buffer.extend(chunk)
				
				# 尝试在 buffer 中寻找有效帧
				i = 0
				while i < len(buffer):
					if buffer[i] == 0x68:
						if i + 2 < len(buffer):
							frame_len = buffer[i+1] + (buffer[i+2] << 8)
							if i + frame_len <= len(buffer):
								frame = buffer[i : i+frame_len]
								if len(frame) > 4:
									afn = frame[4]
									if afn == 0x22:
										data = frame[5:-2]
										break
									elif afn == 0x01:
										pass
								i += frame_len
								continue
					i += 1
				
				if data:
					break
			else:
				if not buffer:
					break
				pass

		if not data:
			debug_hex = buffer.hex(' ') if buffer else '无'
			raise RuntimeError(f"未收到有效的红外学习数据 (AFN=0x22)。收到的数据: {debug_hex}")

		# 保存文件
		if target_name:
			# 如果指定了名称，直接使用该名称
			final_name = target_name
			filename = f"{target_name}.hex"
		else:
			# 否则使用时间戳
			final_name = f"ir_code_{int(time.time())}"
			filename = f"{final_name}.hex"
			
		save_path = os.path.abspath(os.path.join(hex_dir, filename))
		with open(save_path, "w") as f:
			f.write(data.hex(" "))

		# 如果有元数据，更新 meta
		if meta_info or target_name:
			meta = _load_codes_meta(hex_dir)
			if not isinstance(meta, dict):
				meta = {}
			
			entry = meta.get(final_name, {})
			if meta_info:
				entry.update(meta_info)
			
			meta[final_name] = entry
			_save_codes_meta(meta, hex_dir)

		with _learning_lock:
			_learning_state["status"] = "success"
			_learning_state["result"] = save_path
			_learning_state["name"] = final_name
			_learning_state["timestamp"] = time.time()
			
	except Exception as e:
		with _learning_lock:
			_learning_state["status"] = "error"
			_learning_state["result"] = str(e)
			_learning_state["timestamp"] = time.time()
	finally:
		if ser:
			try:
				ser.close()
			except Exception:
				pass


def learn_ir_and_save(args: Dict) -> str:
	"""进入外部学习模式（后台运行）

	参数：
	- name: (可选) 保存的红外码名称（如 tv_power）。如果不填则自动生成。
	- description: (可选) 描述
	- aliases: (可选) 别名
	- category: (可选) 分类
	- device: (可选) 设备名

	立即返回，不等待用户按键。
	"""
	global _learning_state
	
	with _learning_lock:
		if _learning_state["status"] == "learning":
			# 如果已经在学习中，检查是否超时（例如超过40秒）
			if time.time() - _learning_state["timestamp"] < 40:
				return json.dumps({"status": "busy", "message": "正在学习中，请勿重复调用"}, ensure_ascii=False)
		
		_learning_state["status"] = "learning"
		_learning_state["result"] = None
		_learning_state["name"] = None
		_learning_state["timestamp"] = time.time()

	# 提取元数据
	target_name = args.get("name")
	if target_name:
		target_name = target_name.strip()
	
	meta_info = {}
	for key in ["description", "category", "device"]:
		if args.get(key):
			meta_info[key] = args[key].strip()
	
	if args.get("aliases"):
		raw = args["aliases"]
		if isinstance(raw, str):
			meta_info["aliases"] = [s.strip() for s in raw.split(",") if s.strip()]
		elif isinstance(raw, list):
			meta_info["aliases"] = raw

	t = threading.Thread(target=_background_learn_task, args=(target_name, meta_info))
	t.daemon = True
	t.start()

	msg = "已进入后台学习模式。请在30秒内按下遥控器按键。"
	if target_name:
		msg += f" 学习成功后将保存为 '{target_name}'。"
	
	return json.dumps({
		"status": "started", 
		"message": msg
	}, ensure_ascii=False)


def get_learning_result(_: Dict) -> str:
	"""获取最近一次学习的结果"""
	with _learning_lock:
		return json.dumps(_learning_state, ensure_ascii=False)



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


def test_ir_connection(_: Dict) -> str:
    """测试红外模块连接状态"""
    try:
        ser = _open_serial()
        port_name = ser.name
        ser.close()
        return f"串口连接成功: {port_name}"
    except Exception as e:
        return f"串口连接失败: {str(e)}"
