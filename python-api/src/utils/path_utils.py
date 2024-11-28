from pathlib import Path


def get_project_root():
    """
    获取项目根目录的路径
    """
    # 当前文件所在目录
    current_dir = Path(__file__).resolve().parent
    # 返回项目根目录（假设config目录在src下，src在项目根目录下）
    return current_dir.parent.parent
