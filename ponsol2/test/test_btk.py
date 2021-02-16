import pandas as pd
import numpy as np

path = r"D:\Box\Pycharm_Project\Ponsol Web\ponsol2\btk\out\20210215\btk predict result.csv"
if __name__ == '__main__':
    df = pd.read_csv(path, index_col=0)
    # print(df)
    values = df.values.reshape(1, -1)[0]
    print(pd.value_counts(values))
