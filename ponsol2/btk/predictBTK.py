# 常规类
from collections import defaultdict
from pprint import pprint
import time
import os
import json
# 基本的数据处理库
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
from ponsol2.model import PonSol2

# 定义常量
a_list = ('A', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'V', 'W', 'Y')
OUT_PATH = os.path.join(".", "out", time.strftime("%Y%m%d"))  # 输出路径
if not os.path.exists(OUT_PATH):
    os.makedirs(OUT_PATH)

# 获取序列
btk_path = "./BTK.faste"
with open(btk_path) as f:
    btk = f.read()
btk_seq = "".join(btk.split("\n")[1:])
print("序列长度:", len(btk_seq))

btk_pred = []
ponsol = PonSol2()
for i, a1 in tqdm(enumerate(btk_seq)):
    a_pred = []
    for a2 in a_list:
        if a1 == a2:
            a_pred.append("-")
        else:
            aa = "{}{}{}".format(a1, i + 1, a2)
            # print(aa, ponsol.predict(btk_seq, aa[0]))
            a_pred.append(ponsol.predict(btk_seq, aa)[0])
            # a_pred.append(1)
    btk_pred.append(a_pred)


# 格式化输出
btk_pred_res = pd.DataFrame(btk_pred, columns=a_list, index=list(btk_seq))
btk_pred_res.to_csv(os.path.join(OUT_PATH, "btk predict result.csv"))
btk_pred_res.to_excel(os.path.join(OUT_PATH, "btk predict result.xlsx"))
