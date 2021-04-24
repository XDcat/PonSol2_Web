import pandas as pd
from django.db import models
from collections import defaultdict
A_LIST = ('A', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'V', 'W', 'Y')

# Create your models here.

class Task(models.Model):
    INPUT_TYPE = (
        ("id", "ID"),
        ("seq", "Sequence"),
        ("protein", "Protein")
    )
    ip = models.GenericIPAddressField()
    mail = models.EmailField(null=True)
    start_time = models.DateTimeField(auto_now=True)
    finish_time = models.DateTimeField(null=True)
    status = models.TextField(null=True)  # 是否正确预测
    input_type = models.TextField(max_length=10, choices=INPUT_TYPE, null=True)
    error_msg = models.TextField(max_length=1000, null=True)  # 错误信息

    def __str__(self):
        mail = self.mail if self.mail else "no email"
        return f"{mail}-{self.ip}"

    def get_record_group(self):
        """
        如果record有id，则根据id分组；否则根据名称分组。
        """
        records = self.record_set.all()
        id_group = defaultdict(list)
        name_group = defaultdict(list)
        for records in records:
            if records.seq_id_type == "seq" or records.seq_id_type is None:
                name_group[records.name].append(records)
            else:
                id_group[records.seq_id].append(records)
        return id_group, name_group

    def get_protein_information(self):
        id_group, name_group = self.get_record_group()
        record_group = list(id_group.values()) + list(name_group.values())
        protein_data = []

        def aux(x):
            return pd.Series(x["result"].values, index=x["end"])

        for rs in record_group:
            # 蛋白质信息
            seq_id = rs[0].seq_id
            seq_id_type = rs[0].get_seq_id_type_display()
            seq = rs[0].seq
            seq_name = rs[0].name
            # 构建 df
            columns = ["index", "st"] + list(A_LIST)
            df_data = []
            for record in rs:
                aa = record.aa
                st = aa[0]
                indx = aa[1:-1]
                end = aa[-1]
                df_data.append({"st": st, "index": indx, "end": end, "result": record.solubility})
            all_result = pd.DataFrame(df_data).groupby(["st", "index"]).apply(aux)
            all_result = all_result.sort_index(axis="index", level=[1, 2]).unstack()
            all_result = all_result.reset_index().reindex(columns, axis=1).fillna("-")
            # 排序
            all_result["index"] = all_result["index"].astype(int)
            all_result = all_result.sort_values("index")
            all_result = all_result.rename(columns={"st": "origin", "index": "#"})
            protein_data.append(
                {
                    "seq_id": seq_id,
                    "seq_id_type": seq_id_type,
                    "seq": seq,
                    "name": seq_name,
                    "record_id": rs[0].id,
                    "data": {
                        "columns": all_result.columns,
                        "data": all_result.iterrows(),  # 注意是迭代器
                    }
                }
            )
        return protein_data


class Record(models.Model):
    SOLUBILITY_CHANGE = (
        ("-1", "decrease"),
        ("0", "no-change"),
        ("1", "increase"),
    )
    SEQ_ID_TYPE = (
        ("uniprot id", "UniProtKB/Swiss-Prot ID"),
        ("gi", "Entrez Gene ID"),
        ("ensembl id", "Ensembl ID"),
        ("seq", "Only Sequence")
    )
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    name = models.TextField(max_length=200)
    seq = models.TextField(max_length=1000)
    seq_id = models.TextField(max_length=100, null=True)
    seq_id_type = models.TextField(max_length=20, null=True, choices=SEQ_ID_TYPE)
    aa = models.TextField(max_length=10)
    solubility = models.TextField(max_length=20, choices=SOLUBILITY_CHANGE, null=True)
    status = models.TextField(max_length=20, null=True, default="running")
    error_msg = models.TextField(max_length=1000, null=True)  # 错误信息

    def __str__(self):
        return f"{self.name}\t{self.status}\t{self.solubility}"
