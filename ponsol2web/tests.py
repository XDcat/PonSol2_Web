from django.test import TestCase
from django.urls import reverse

from ponsol2web import models
from ponsol2web.views import A_LIST
import pandas as pd
import pdfkit


# Create your tests here.
class OneTest(TestCase):
    def test_generate_pdf(self):
        url = "http://127.0.0.1:8000/task/44?type=email"
        url = "http://127.0.0.1:8000/task/13?type=email"
        # url = reverse("ponsol2:task-detail", args=(19,))
        # pdf = pdfkit.from_url(url, r"C:\Users\17844\Desktop\protein_1.pdf")
        pdf = pdfkit.from_url(url, False)
        print(pdf)

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
