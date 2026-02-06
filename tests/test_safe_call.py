"""
测试 safe_call() 超时保护函数

测试场景：
1. 正常调用返回正确结果
2. 超时返回 None
3. 异常捕获返回 None
4. 日志记录正确
"""

import time
from unittest.mock import patch, MagicMock
import pytest
from func_timeout import FunctionTimedOut

from utils.update_datas import safe_call


class TestSafeCall:
    """测试 safe_call() 函数"""

    def test_normal_call_returns_result(self):
        """测试正常调用返回正确结果"""
        def normal_func():
            return "success"

        result = safe_call(normal_func, timeout_seconds=5)
        assert result == "success"

    def test_normal_call_with_args(self):
        """测试带参数的正常调用"""
        def add(a, b):
            return a + b

        result = safe_call(add, 2, 3, timeout_seconds=5)
        assert result == 5

    def test_normal_call_with_kwargs(self):
        """测试带关键字参数的正常调用"""
        def greet(name, greeting="Hello"):
            return f"{greeting}, {name}!"

        result = safe_call(greet, name="World", greeting="Hi", timeout_seconds=5)
        assert result == "Hi, World!"

    def test_timeout_returns_none(self):
        """测试超时返回 None"""
        def slow_func():
            time.sleep(15)  # 超过 10 秒超时
            return "should not reach here"

        result = safe_call(slow_func, timeout_seconds=2)
        assert result is None

    def test_exception_returns_none(self):
        """测试异常捕获返回 None"""
        def raise_error():
            raise ValueError("Test error")

        result = safe_call(raise_error, timeout_seconds=5)
        assert result is None

    @patch('utils.update_datas.logger')
    def test_timeout_logs_warning(self, mock_logger):
        """测试超时记录警告日志"""
        def slow_func():
            time.sleep(15)
            return "should not reach here"

        result = safe_call(slow_func, timeout_seconds=2)

        assert result is None
        mock_logger.warning.assert_called_once()
        args = mock_logger.warning.call_args[0]
        assert "【超时】" in args[0]
        assert "slow_func" in args[0]

    @patch('utils.update_datas.logger')
    def test_exception_logs_error(self, mock_logger):
        """测试异常记录错误日志"""
        def raise_error():
            raise ValueError("Test error message")

        result = safe_call(raise_error, timeout_seconds=5)

        assert result is None
        mock_logger.error.assert_called_once()
        args = mock_logger.error.call_args[0]
        assert "【失败】" in args[0]
        assert "raise_error" in args[0]

    def test_default_timeout_10_seconds(self):
        """测试默认超时时间为 10 秒"""
        def normal_func():
            return "quick"

        # 不指定 timeout_seconds，应使用默认值 10
        result = safe_call(normal_func)
        assert result == "quick"


class TestSafeCallIntegration:
    """集成测试：测试 safe_call 与实际网络场景"""

    def test_slow_function_timeout(self):
        """模拟慢函数超时场景"""
        def slow_api():
            time.sleep(15)

        result = safe_call(slow_api, timeout_seconds=2)
        assert result is None

    def test_quick_function_success(self):
        """模拟快速函数成功场景"""
        def quick_api():
            return {"data": "success"}

        result = safe_call(quick_api, timeout_seconds=5)
        assert result == {"data": "success"}

    def test_function_exception(self):
        """模拟函数异常场景"""
        def failing_api():
            raise ConnectionError("Network error")

        result = safe_call(failing_api, timeout_seconds=5)
        assert result is None

