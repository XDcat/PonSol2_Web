# -*- coding:utf-8 -*-
'''
__author__ = 'XD'
__mtime__ = 2021/1/22
__project__ = Pon-Sol2
Fix the Problem, Not the Blame.
'''
import joblib
import pandas as pd
from . import feature_extraction, config

A_LIST = ('A', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'V', 'W', 'Y')
class PonSol2:
    def __init__(self):
        """
        model
        self.Estimator: 使用的训练器模型
        self.kwargs: 模型参数
        self.feature_selected: 使用到的特征的列表，具体还是看 fs1 和 fs2
        self.special_kind: 划分第一层的特殊类
        self.fs1: 第一层使用的特征
        self.fs2: 第二层使用的特征

        """
        self.model_path = config.model_path
        self.model = joblib.load(self.model_path)
        self.fs1 = self.model.fs1
        self.fs2 = self.model.fs2

    def check_X(self, X):
        # 检查类型
        if not isinstance(X, pd.DataFrame):
            raise RuntimeError("The input is not the object of pandas.DataFrame")
        # 检查特征
        all_features = set(self.fs1.to_list() + self.fs2.to_list())
        input_data_features = set(X.columns.to_list())
        reduce_features = all_features - input_data_features
        if len(reduce_features) > 0:
            raise RuntimeError("缺少特征:%s" % reduce_features)
        return True

    def predict(self, seq, aa):
        """
        预测
        :param seq: 氨基酸序列，不包含名称
        :param aa: 变异，索引从1开始，e.g. A1B
        :return: 预测结果
        """
        all_features = feature_extraction.get_all_features(seq, aa)
        if aa[0] == aa[-1]:
            return 0
        pred = self._predict(all_features)
        return pred


    def _predict(self, X):
        # 检查 X
        self.check_X(X)
        pred = self.model.predict(X)
        return pred