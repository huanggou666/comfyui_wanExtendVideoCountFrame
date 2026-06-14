"""
wanExtendVideoCountFrame - ComfyUI 自定义节点
功能：将长视频帧数按每轮最大帧数拆分，根据当前轮次输出对应帧数
"""

import math


class wanExtendVideoCountFrame:
    """
    视频帧数分轮计算节点

    逻辑说明：
    - 每轮工作流最多处理 max_frames_per_round 帧（默认 81，可自由修改）
    - 除最后一轮外，其余每轮固定输出 max_frames_per_round
    - 最后一轮输出剩余帧数
    - 节点会同时输出：当前轮帧数、总轮数、当前轮起始帧、当前轮结束帧
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "total_frames": (
                    "INT",
                    {
                        "default": 163,
                        "min": 1,
                        "max": 100000,
                        "step": 1,
                        "display": "number",
                        "tooltip": "视频总帧数",
                    },
                ),
                "max_frames_per_round": (
                    "INT",
                    {
                        "default": 81,
                        "min": 1,
                        "max": 10000,
                        "step": 1,
                        "display": "number",
                        "tooltip": "每轮工作流最大帧数（默认 81）",
                    },
                ),
                "current_round": (
                    "INT",
                    {
                        "default": 1,
                        "min": 1,
                        "max": 10000,
                        "step": 1,
                        "display": "number",
                        "tooltip": "当前是第几轮（从 1 开始）",
                    },
                ),
            }
        }

    # 输出类型定义
    RETURN_TYPES = ("INT", "INT", "INT", "INT", "STRING")
    RETURN_NAMES = (
        "current_round_frames",   # 当前轮应处理的帧数
        "total_rounds",           # 总共需要多少轮
        "start_frame",            # 当前轮起始帧（1-based）
        "end_frame",              # 当前轮结束帧（1-based，含）
        "info",                   # 汇总信息字符串，方便调试
    )

    FUNCTION = "calculate"
    CATEGORY = "Video/Frame Utils"
    OUTPUT_NODE = False

    def calculate(self, total_frames: int, max_frames_per_round: int, current_round: int):
        max_fr = max(1, max_frames_per_round)  # 防止除以零

        # 1. 计算总轮数
        total_rounds = math.ceil(total_frames / max_fr)

        # 2. 校正 current_round 范围（防止用户输入超出范围）
        current_round_clamped = max(1, min(current_round, total_rounds))

        # 3. 计算当前轮帧数
        if current_round_clamped < total_rounds:
            # 非最后一轮：固定 81 帧
            current_round_frames = max_fr
        else:
            # 最后一轮：剩余帧数
            current_round_frames = total_frames - (total_rounds - 1) * max_fr

        # 4. 计算起始帧 / 结束帧（1-based 索引，第一帧为 1）
        start_frame = (current_round_clamped - 1) * max_fr + 1
        end_frame = start_frame + current_round_frames - 1

        # 5. 构建信息字符串
        info = (
            f"总帧数: {total_frames} | "
            f"每轮上限: {max_fr} | "
            f"总轮数: {total_rounds} | "
            f"当前轮: {current_round_clamped}/{total_rounds} | "
            f"本轮帧数: {current_round_frames} | "
            f"帧范围: [{start_frame}, {end_frame}]"
        )

        # 若输入 current_round 超出范围，附加警告
        if current_round != current_round_clamped:
            info += f" ⚠️ 输入轮次 {current_round} 超出范围，已自动限制为 {current_round_clamped}"

        print(f"[wanExtendVideoCountFrame] {info}")

        return (
            current_round_frames,
            total_rounds,
            start_frame,
            end_frame,
            info,
        )


# ─────────────────────────────────────────────
#  ComfyUI 注册入口
# ─────────────────────────────────────────────

NODE_CLASS_MAPPINGS = {
    "wanExtendVideoCountFrame": wanExtendVideoCountFrame,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "wanExtendVideoCountFrame": "Wan Extend Video Count Frame",
}
