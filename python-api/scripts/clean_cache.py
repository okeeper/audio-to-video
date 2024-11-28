import os
import shutil

def clean_cache(directory):
    """
    清理指定目录下的所有Python缓存文件
    """
    for root, dirs, files in os.walk(directory):
        # 删除 __pycache__ 目录
        if '__pycache__' in dirs:
            pycache_path = os.path.join(root, '__pycache__')
            print(f"删除目录: {pycache_path}")
            shutil.rmtree(pycache_path)
            
        # 删除 .pyc 文件
        for file in files:
            if file.endswith('.pyc'):
                pyc_path = os.path.join(root, file)
                print(f"删除文件: {pyc_path}")
                os.remove(pyc_path)

if __name__ == '__main__':
    # 获取项目根目录
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    clean_cache(project_root)
    print("缓存清理完成！") 