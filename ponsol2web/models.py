from django.db import models


# Create your models here.

class Task(models.Model):
    ip = models.GenericIPAddressField()
    mail = models.EmailField(null=True)
    start_time = models.DateTimeField(auto_now=True)
    finish_time = models.DateTimeField(null=True)

    def __str__(self):
        mail = self.mail if self.mail else "no email"
        return f"{mail}-{self.ip}"


class Record(models.Model):
    SOLUBILITY_CHANGE = (
        ("-1", "decrease"),
        ("0", "no-change"),
        ("1", "increase"),
    )
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    name = models.TextField(max_length=200)
    seq = models.TextField(max_length=1000)
    aa = models.TextField(max_length=10)
    solubility = models.TextField(max_length=20, choices=SOLUBILITY_CHANGE)

    def __str__(self):
        return self.name
