import pandas as pd
import numpy as np
import os


def aux(x, s):
    """
    统计s中x的数目
    :param x: 查询的值
    :param s: serise
    """
    res = s == str(x)
    res = sum(res)
    return res


def generate_output(s, path):
    """将结果保存为文件"""
    with open(path, "w") as f:
        for i, v in enumerate(s):
            f.write(f":{i+1}\t{v}\n")


if __name__ == '__main__':
    result_path = "./out/20210215/btk predict result.csv"
    btk = pd.read_csv(result_path, index_col=0)
    de_count = btk.apply(lambda x: aux(-1, x), axis=1)
    no_count = btk.apply(lambda x: aux(0, x), axis=1)
    in_count = btk.apply(lambda x: aux(1, x), axis=1)

    # output
    dir_path = "./out/20210215"
    generate_output(de_count, os.path.join(dir_path, "btk decrease.txt"))
    generate_output(no_count, os.path.join(dir_path, "btk no effect.txt"))
    generate_output(in_count, os.path.join(dir_path, "btk increase.txt"))

    # check value
    print(btk)
    print(de_count)
    print("sum(-1) =", de_count.sum())
    print("sum(0) =", no_count.sum())
    print("sum(1) =", in_count.sum())
    all_count = de_count + no_count + in_count
    print(all_count)
    print((all_count == 19).any())
