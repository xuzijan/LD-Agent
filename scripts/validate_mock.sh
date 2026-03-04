#!/usr/bin/env bash
# LD-Agent Mock 验证：完全离线跑通 QuickEval 流程
# 使用: conda activate ld-agent && bash scripts/validate_mock.sh
set -e
cd "$(dirname "$0")/.."

MOCK_PORT=19998
API_BASE="http://127.0.0.1:${MOCK_PORT}/v1"

echo "=== 1. 启动 Mock OpenAI 服务 (端口 ${MOCK_PORT}) ==="
PYTHON="${CONDA_PREFIX}/bin/python"
[ -z "$CONDA_PREFIX" ] && PYTHON="python"
$PYTHON scripts/mock_openai_server.py &
MOCK_PID=$!
sleep 2

echo "=== 2. 运行 QuickEval (Mock API) ==="
python scripts/run_mock_eval.py \
    --dataset quickeval \
    --data_path dataset/MSC \
    --data_name test.json \
    --id_set id_set.json \
    --client chatgpt \
    --model gpt-3.5-turbo-1106 \
    --api_key dummy \
    --api_base_url "${API_BASE}" \
    --test_num 1

echo "=== 3. 停止 Mock 服务 ==="
kill $MOCK_PID 2>/dev/null || true

echo "=== Mock 验证完成 ==="
