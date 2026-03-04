#!/usr/bin/env python3
"""
Mock 验证脚本：使用假 API 跑通 QuickEval 流程
需先启动 mock server: python scripts/mock_openai_server.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 运行 main（nlgeval/metric 已提供 mock 实现）
import runpy
runpy.run_path(os.path.join(os.path.dirname(os.path.dirname(__file__)), "main.py"), run_name="__main__")
