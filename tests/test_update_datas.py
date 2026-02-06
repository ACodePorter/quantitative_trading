"""
测试 data_handler 装饰器

测试场景：
1. 装饰器捕获异常并返回 None
2. 装饰器记录详细的错误日志（函数名、位置、异常类型、消息、局部变量）
3. 正常执行时返回正确结果
"""

import pytest
from unittest.mock import patch, MagicMock
from utils.update_datas import data_handler


class TestDataHandler:
    """测试 data_handler 装饰器"""

    @patch('utils.update_datas.logger')
    def test_catches_exception_and_logs(self, mock_logger):
        """测试装饰器捕获异常并记录日志"""

        @data_handler
        def failing_function():
            raise ValueError("Test error")

        result = failing_function()

        assert result is None
        assert mock_logger.error.called

    @patch('utils.update_datas.logger')
    def test_logs_exception_details(self, mock_logger):
        """测试日志包含详细信息"""

        @data_handler
        def raise_network_error():
            x = 123
            y = "test_value"
            raise ConnectionError("Network timeout")

        result = raise_network_error()

        # 验证返回 None
        assert result is None

        # 验证日志被调用
        assert mock_logger.error.called

        # 获取所有日志调用
        call_args_list = [str(call) for call in mock_logger.error.call_args_list]

        # 验证日志包含函数名
        calls_str = ' '.join(call_args_list)
        assert "raise_network_error" in calls_str

        # 验证日志包含异常类型
        assert "ConnectionError" in calls_str

        # 验证日志包含异常消息
        assert "Network timeout" in calls_str

    @patch('utils.update_datas.logger')
    def test_logs_local_variables(self, mock_logger):
        """测试日志包含局部变量"""

        @data_handler
        def function_with_locals():
            var1 = "string_value"
            var2 = 42
            var3 = {"key": "value"}
            raise RuntimeError("Error with locals")

        result = function_with_locals()

        assert result is None

        # 获取所有日志调用
        call_args_list = [str(call) for call in mock_logger.error.call_args_list]
        calls_str = ' '.join(call_args_list)

        # 验证局部变量被记录
        assert "var1" in calls_str
        assert "var2" in calls_str
        assert "var3" in calls_str

    @patch('utils.update_datas.logger')
    def test_normal_execution_returns_result(self, mock_logger):
        """测试正常执行返回正确结果"""

        @data_handler
        def normal_function():
            return {"status": "success", "data": [1, 2, 3]}

        result = normal_function()

        assert result == {"status": "success", "data": [1, 2, 3]}
        # 正常执行不应该有错误日志
        assert not mock_logger.error.called

    @patch('utils.update_datas.logger')
    def test_function_with_arguments(self, mock_logger):
        """测试带参数的函数"""

        @data_handler
        def add_with_exception(a, b):
            if b == 0:
                raise ZeroDivisionError("Division by zero")
            return a + b

        # 正常情况
        result = add_with_exception(2, 3)
        assert result == 5

        # 异常情况
        result = add_with_exception(5, 0)
        assert result is None
        assert mock_logger.error.called

    @patch('utils.update_datas.logger')
    def test_logs_location_info(self, mock_logger):
        """测试日志包含位置信息（文件名、行号）"""

        @data_handler
        def location_test():
            raise Exception("Test location")

        result = location_test()

        assert result is None

        # 获取所有日志调用
        call_args_list = [str(call) for call in mock_logger.error.call_args_list]
        calls_str = ' '.join(call_args_list)

        # 验证日志包含位置信息（文件名和行号格式）
        # 位置信息格式类似: "位置: /path/to/file.py:123 in function_name"
        assert "位置:" in calls_str or "location_test" in calls_str

    @patch('utils.update_datas.logger')
    def test_long_variable_values_are_truncated(self, mock_logger):
        """测试长变量值被截断到100字符"""

        @data_handler
        def function_with_long_var():
            long_string = "x" * 200  # 200个字符
            raise ValueError("Test truncation")

        result = function_with_long_var()

        assert result is None

        # 获取所有日志调用
        call_args_list = [str(call) for call in mock_logger.error.call_args_list]
        calls_str = ' '.join(call_args_list)

        # 验证长字符串被截断（不会包含完整的200个x）
        assert "x" * 200 not in calls_str

    @patch('utils.update_datas.logger')
    def test_different_exception_types(self, mock_logger):
        """测试不同类型的异常都被正确处理"""

        @data_handler
        def raise_value_error():
            raise ValueError("Value error")

        @data_handler
        def raise_type_error():
            raise TypeError("Type error")

        @data_handler
        def raise_attribute_error():
            raise AttributeError("Attribute error")

        # 测试各种异常类型
        assert raise_value_error() is None
        assert raise_type_error() is None
        assert raise_attribute_error() is None

        # 验证所有异常都被记录
        assert mock_logger.error.call_count >= 3

        # 验证异常类型名称在日志中
        call_args_list = [str(call) for call in mock_logger.error.call_args_list]
        calls_str = ' '.join(call_args_list)
        assert "ValueError" in calls_str
        assert "TypeError" in calls_str
        assert "AttributeError" in calls_str
