from django.test import TestCase
from . import models
from .views import A_LIST
import pandas as pd


# Create your tests here.
class OneTest(TestCase):
    def test_predict_protein_html(self):
        task = models.Task.objects.get(id=41)
        id_group, name_group = task.get_record_group()
        record_group = list(id_group.values()) + list(name_group.values())
        protein_data = {}

        def aux(x):
            return pd.Series(x["result"], index=x["end"])

        for rs in record_group:
            # 蛋白质信息
            seq_id = rs[0].seq_id
            seq_id_type = rs[0].seq_id_type
            seq = rs[0].seq
            seq_name = rs[0].name
            # 构建 df
            columns = ["st", "index", "end"] + A_LIST
            df_data = []
            for record in rs:
                aa = record.aa
                st = aa[0]
                indx = aa[1:-1]
                end = aa[-1]
                df_data.append({"st": st, "index": indx, "end": end, "result": record.solubility})
            df = pd.DataFrame(df_data).groupby(["st", "index"]).apply(aux)
            print(df)

        # 创建一个空的 df
        # 遍历列表将数据填充进去
        # 根据 index 来排序
