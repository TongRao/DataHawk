import sys
import pandas as pd


def load_df():
    """
    用于加载目标文件，需要在terminal中指定目标文件，可以直接拖拽，比如：
    python doorKeeper.py jerry/Desktop/test.csv
    """
    if len(sys.argv) == 1:
        print("没有识别到目标文件，请执行[python doorKeeper.py target_file_path]")
    else:
        if ".csv" in sys.argv[1]:
            df = pd.read_csv(sys.argv[1])
            return df
        elif ".xlsx" in sys.argv[1]:
            df = pd.read_excel(sys.argv[1])
            return df
        else:
            print("文件类型暂不支持")


if __name__ == "__main__":
    df = load_df()
