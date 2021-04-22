from django.test import TestCase
from ponsol2web import models
from ponsol2web.views import A_LIST
import pandas as pd


# Create your tests here.
class OneTest(TestCase):
    def test_predict_protein_html(self):
        task = models.Task.objects.get(id=83)
        id_group, name_group = task.get_record_group()
        record_group = list(id_group.values()) + list(name_group.values())
        protein_data = []

        def aux(x):
            return pd.Series(x["result"].values, index=x["end"])

        for rs in record_group:
            # 蛋白质信息
            seq_id = rs[0].seq_id
            seq_id_type = rs[0].seq_id_type
            seq = rs[0].seq
            seq_name = rs[0].name
            # 构建 df
            columns = ["st", "index", ] + list(A_LIST)
            df_data = []
            for record in rs:
                aa = record.aa
                st = aa[0]
                indx = aa[1:-1]
                end = aa[-1]
                df_data.append({"st": st, "index": indx, "end": end, "result": record.solubility})
            all_result = pd.DataFrame(df_data).groupby(["st", "index"]).apply(aux)
            all_result = all_result.sort_index(axis="index", level=[1, 2]).unstack()
            all_result = all_result.reset_index().reindex(columns, axis=1)
            protein_data.append(
                {
                    "seq_id": seq_id,
                    "seq_id_type": seq_id_type,
                    "seq": seq,
                    "name": seq_name,
                    "data": {
                        "columns": all_result.columns,
                        "data": all_result.iterrows(),  # 注意是迭代器
                    }
                }
            )
        return protein_data

