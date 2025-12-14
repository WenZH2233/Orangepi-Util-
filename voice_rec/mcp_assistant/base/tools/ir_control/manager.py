"""红外控制工具管理器

负责将红外学习/发送能力以 MCP 工具的方式对外暴露。
"""

from typing import Any, Dict

from .utils import get_logger

from .tools import (
	list_ir_codes,
	send_ir_by_name,
	learn_ir_and_save,
	get_ir_code_info,
	set_ir_code_info,
	test_ir_connection,
	get_learning_result,
)

logger = get_logger(__name__)


class IRControlManager:
	"""IR 控制工具管理器"""

	def __init__(self):
		self._inited = False

	def init_tools(self, add_tool, PropertyList, Property, PropertyType):
		"""注册 IR 相关 MCP 工具

		参数与其它工具管理器一致，便于统一注册：
		- add_tool: 用于注册工具的方法
		- PropertyList/Property/PropertyType: 构建工具入参规范
		"""
		# 列出可用的红外码
		add_tool(
			(
				"self.ir.list_codes",
				"列出可用的红外编码文件（存放于 mcps/ir_control/hex 目录）。返回 JSON 数组，包含 name 与 path。",
				PropertyList(),
				list_ir_codes,
			)
		)

		# 通过名称发送（名称对应 hex 文件名，支持 tv_power、tv_ok 等）
		props_send_named = PropertyList([Property("name", PropertyType.STRING)])
		add_tool(
			(
				"self.ir.send_named",
				"发送已保存的红外编码。name 为文件名（不含 .hex），例如 'tv_power'。",
				props_send_named,
				send_ir_by_name,
			)
		)



		# 获取单个红外码信息
		props_get_info = PropertyList([Property("name", PropertyType.STRING)])
		add_tool(
			(
				"self.ir.get_ir_code_info",
				"获取指定红外码的元数据（描述、别名、分类、设备等）。",
				props_get_info,
				get_ir_code_info,
			)
		)

		# 更新/设置红外码信息（别名可用逗号分隔或JSON数组字符串）
		props_set_info = PropertyList(
			[
				Property("name", PropertyType.STRING),
				Property("description", PropertyType.STRING, default_value=""),
				Property("aliases", PropertyType.STRING, default_value=""),
				Property("category", PropertyType.STRING, default_value=""),
				Property("device", PropertyType.STRING, default_value=""),
			]
		)
		add_tool(
			(
				"self.ir.set_ir_code_info",
				"设置/更新红外码的元数据（描述、别名、分类、设备）。别名支持逗号分隔或JSON字符串数组。",
				props_set_info,
				set_ir_code_info,
			)
		)

		# 学习外部红外并保存
		props_learn = PropertyList(
			[
				Property("name", PropertyType.STRING, default_value=""),
				Property("description", PropertyType.STRING, default_value=""),
				Property("aliases", PropertyType.STRING, default_value=""),
				Property("category", PropertyType.STRING, default_value=""),
				Property("device", PropertyType.STRING, default_value=""),
			]
		)
		add_tool(
			(
				"self.ir.learn_external",
				"进入后台学习模式。调用后立即返回，请在30秒内按下遥控器按键。可指定 name 直接保存为该名称。",
				props_learn,
				learn_ir_and_save,
			)
		)

		# 获取学习结果
		add_tool(
			(
				"self.ir.get_learning_result",
				"获取最近一次红外学习的结果（状态、文件路径或错误信息）。",
				PropertyList(),
				get_learning_result,
			)
		)

		# 测试连接
		add_tool(
			(
				"self.ir.test_connection",
				"测试红外模块串口连接状态。",
				PropertyList(),
				test_ir_connection,
			)
		)

		self._inited = True
		logger.info("[IRControl] IR MCP 工具注册完成")

	def is_initialized(self) -> bool:
		return self._inited

	def get_status(self) -> Dict[str, Any]:
		return {"initialized": self._inited}


_ir_ctrl_mgr = None


def get_ir_control_manager() -> IRControlManager:
	global _ir_ctrl_mgr
	if _ir_ctrl_mgr is None:
		_ir_ctrl_mgr = IRControlManager()
	return _ir_ctrl_mgr

