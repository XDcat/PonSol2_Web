from django.db import models
from collections import defaultdict


# Create your models here.

class Task(models.Model):
    INPUT_TYPE = (
        ("id", "ID"),
        ("seq", "Sequence")
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
