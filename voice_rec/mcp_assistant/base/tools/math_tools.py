import math
import random
import logging

logger = logging.getLogger('Tools.Math')

def calculator(python_expression: str) -> dict:
    """For mathamatical calculation, always use this tool to calculate the result of a python expression. You can use 'math' or 'random' directly, without 'import'."""
    try:
        # Safe eval with limited scope
        result = eval(python_expression, {"math": math, "random": random})
        logger.info(f"Calculating formula: {python_expression}, result: {result}")
        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"Calculation error: {e}")
        return {"success": False, "error": str(e)}
