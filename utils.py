#!/usr/bin/env python
# coding: utf-8


# 常规类
# 基本的数据处理库
import pandas as pd
import numpy as np
import os

# 导入数据
# matplotlib 设置
pd.options.display.max_rows = 10  # 表格最大行数为10

# 机器学习相关库
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import confusion_matrix, accuracy_score, multilabel_confusion_matrix

skf = StratifiedKFold(n_splits=10, shuffle=True, random_state=0)  # 10 层交叉验证（随机打乱）（训练/测试集数据分布与原数据分布一致）


# 计算指标


def ponsol_metrics(y_true, y_pre, balance=False, k=3):
    """
    计算 ponsol 需要的那几个指标(原来 ponsol 中的代码)
    :param y_true: 标签的正确值
    :param y_pre: 标签的预测值
    :param balance: 是否平衡数据
    :param k: 类的数目
    :return : (accuarcy, gc2, 其他数据) -> (float, float, DateFrame)
    
    注意：id 为 python 关键字，改为 id_
    """
    #     y_true, y_pre = y_test1, p_test1
    label = pd.DataFrame({'true': y_true, 'pre': y_pre})

    # 计算每一类的 TP、FN、FP、TN
    unique_state = label.true.unique()  # 寻找到唯一的标签
    targets = {}  # 保存结果
    ii = io = id_ = oi = oo = od = di = do = dd = 0
    tpi = tni = fpi = fni = tpd = tnd = fpd = fnd = tpo = tno = fpo = fno = 0
    for i, (t, p) in label.iterrows():
        # i, t, p -> 索引，真实值，预测值
        if t == -1 and p == -1:
            dd += 1
        if t == -1 and p == 0:
            do += 1
        if t == -1 and p == 1:
            di += 1
        if t == 0 and p == -1:
            od += 1
        if t == 0 and p == 0:
            oo += 1
        if t == 0 and p == 1:
            oi += 1
        if t == 1 and p == -1:
            id_ += 1
        if t == 1 and p == 0:
            io += 1
        if t == 1 and p == 1:
            ii += 1

    alli = ii + io + id_
    alld = di + do + dd
    allo = oi + oo + od

    # 平衡数据
    if balance:
        ii = ii * allo / alli
        io = io * allo / alli
        id_ = id_ * allo / alli
        di = di * allo / alld
        do = do * allo / alld
        dd = dd * allo / alld

    # 计算指标
    acc = (ii + oo + dd) / (ii + io + id_ + oi + oo + od + di + do + dd)
    N = ii + io + id_ + oi + oo + od + di + do + dd

    ## eii
    eii = (ii + io + id_) * (ii + oi + di) / N
    eio = (ii + io + id_) * (io + oo + do) / N
    eid_ = (ii + io + id_) * (id_ + od + dd) / N

    eoi = (oi + oo + od) * (ii + oi + di) / N
    eoo = (oi + oo + od) * (io + oo + do) / N
    eod = (oi + oo + od) * (id_ + od + dd) / N

    edi = (di + do + dd) * (ii + oi + di) / N
    edo = (di + do + dd) * (io + oo + do) / N
    edd = (di + do + dd) * (id_ + od + dd) / N

    # gc2 (对 0 进行处理)
    gc2 = None
    if 0 not in [eii, eio, eid_, eoi, eoo, eod, edi, edo, edd]:
        gc2 = (((ii - eii) * (ii - eii) / eii) + ((io - eio) * (io - eio) / eio) +
               ((id_ - eid_) * (id_ - eid_) / eid_) + ((oi - eoi) * (oi - eoi) / eoi) +
               ((oo - eoo) * (oo - eoo) / eoo) + ((od - eod) * (od - eod) / eod) +
               ((di - edi) * (di - edi) / edi) + ((do - edo) * (do - edo) / edo) +
               ((dd - edd) * (dd - edd) / edd)) / ((k - 1) * N)

    # sensitivity -> TPR
    seni = ii / (ii + io + id_)
    send = dd / (di + do + dd)
    seno = oo / (oi + oo + od)

    # spciticity -> TNR
    spei = (dd + do + od + oo) / (dd + do + od + oo + di + oi)
    sped = (ii + io + oi + oo) / (ii + io + oi + oo + id_ + od)
    speo = (dd + di + id_ + ii) / (dd + di + id_ + ii + do + io)

    # ppv (对除 0 的处理)
    ppvi = ppvd = ppvo = None
    if ii + oi + di != 0:
        ppvi = ii / (ii + oi + di)
    if id_ + dd + od != 0:
        ppvd = dd / (id_ + dd + od)
    if io + do + oo != 0:
        ppvo = oo / (io + do + oo)

    # npv  (对除 0 的处理)
    npvi = npvd = npvo = None
    if dd + do + od + oo + io + id_ != 0:
        npvi = (dd + do + od + oo) / (dd + do + od + oo + io + id_)
    if ii + io + oi + oo + di + do != 0:
        npvd = (ii + io + oi + oo) / (ii + io + oi + oo + di + do)
    if dd + di + id_ + ii + od + oi != 0:
        npvo = (dd + di + id_ + ii) / (dd + di + id_ + ii + od + oi)

    # tp, tn, fp, fn
    tpi = ii
    tni = oo + od + do + dd
    fpi = oi + di
    fni = io + id_

    tpd = dd
    fnd = di + do
    fpd = id_ + od
    tnd = ii + io + oi + oo

    tpo = oo
    fno = oi + od
    fpo = io + do
    tno = ii + id_ + di + dd

    # 构造成 pandas
    ## 结果1（暂时保留）
    #     indexs1 = [[
    #         'ppv', 'ppv', 'ppv', 'npv', 'npv', 'npv', 'tpr', 'tpr', 'tpr', 'tnr',
    #         'tnr', 'tnr', 'all', 'all'
    #     ], [-1, 0, 1] * 4 + ['accuracy', 'GC2']]
    #     res1 = pd.Series([
    #         ppvd, ppvo, ppvi, npvd, npvo, npvi, send, seno, seni, sped, speo, spei,
    #         acc, gc2
    #     ],
    #                      index=indexs1)
    ## 结果2
    columns = ['tp', 'tn', 'fp', 'fn', 'ppv', 'npv', 'tpr', 'tnr']
    res2 = pd.DataFrame(
        [
            [tpd, tnd, fpd, fnd, ppvd, npvd, send, sped],
            [tpo, tno, fpo, fno, ppvo, npvo, seno, speo],
            [tpi, tni, fpi, fni, ppvi, npvi, seni, spei]
        ],
        columns=columns,
        index=[-1, 0, 1]
    )
    return acc, gc2, res2


def ponsol_metrics_new(y_true, y_pred, labels=[-1, 0, 1], verbose=0, balance=False):
    """
    ! 使用了新的方法，但是无法做到 balance
    计算 ponsol 需要的那几个指标(原来 ponsol 中的代码)
    :param y_true: 标签的正确值
    :param y_pre: 标签的预测值
    :param labels: 标签
    :param verbose: 控制是否输出日志
    :return : (accuarcy, gc2, 其他数据) -> (float, float, DateFrame)
    注意：id 为 python 关键字，改为 id_
    """
    N = len(y_true)
    K = len(labels)
    mcms = multilabel_confusion_matrix(y_true, y_pred, labels=labels)
    res = pd.DataFrame([i.ravel() for i in mcms], columns="tn fp fn tp".split(), index=labels)
    res = res.loc[:, "tp  tn  fp  fn".split()]
    # PPV NPV TPR TNR
    res["ppv"] = res.tp / (res.tp + res.fp)
    res["npv"] = res.tn / (res.tn + res.fn)
    res["sensitivity"] = res.tp / (res.tp + res.fn)
    res["specificity"] = res.tn / (res.tn + res.fp)
    if verbose > 4:
        print("MCM = ")
        print(res)

    # gcc
    # zij, xi, yi
    zij = confusion_matrix(y_true, y_pred, labels=labels).astype(np.float)
    #     if balance:
    #         zij = zij * zij.sum(axis=1)[0] / np.tile(zij.sum(axis=1), (K, 1)).T

    xi = np.sum(zij, axis=1)  # 原始值为 i 的数目
    yi = np.sum(zij, axis=0)  # 预测值为 j 的数目
    # xij, yij
    xij = xi.reshape(xi.shape[0], 1)
    xij = np.repeat(xij, xi.shape[0]).reshape((-1, xi.shape[0]))
    yij = np.array([yi for _ in range(yi.shape[0])])
    # zij
    eij = xij * yij / N
    gcc = np.sum((zij - eij) ** 2 / eij) / (N * (K - 1))
    acc = accuracy_score(y_true, y_pred)
    if verbose > 4:
        print("zij = \n%s" % zij)
        print("xi = \n%s" % xi)
        print("yi = \n%s" % yi)
        print("xij = \n%s" % xij)
        print("yij = \n%s" % yij)
        print("xij * yij = \n%s" % (xij * yij))
        print("eij = \n%s" % eij)
        print("gcc = %s" % gcc)
    if verbose > 0:
        print("acc:", acc)
        print("gcc:", gcc)
        print("res:")
        print(res)
    return acc, gcc, res


## 测试数据


# y_true = [-1, -1, -1, 0, 0, 0, 1, 1, 1, 0]
# y_pred = [-1, 0, 1, -1, 0, 1, 0, 0, 1, 0]
# y_true = [-1, 1, 1, -1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, -1, 0, -1, 0, -1, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 0, -1, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 0, -1, -1, -1, -1, -1, -1, 1, -1, 0, -1, 0, 0, -1, 0, 0, -1, -1, -1, -1, -1, -1, -1, 0, 0, 0, 0, 0, -1, -1, 0, -1, -1, -1, 0, 0, -1, 0, 0, 0, 0, -1, -1, 0, -1, 0, 0, 0, 0, -1, -1, 0, 1, 1, 0, 0, 0, -1, 0, 1, 0, -1, 0, -1, -1, -1, -1, 0, -1, -1, -1, -1, 0, 0, 0, -1, 0, -1, 0, 1, -1, -1, 0, 1, 0, -1, -1, -1, -1, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 0, -1, -1, -1, -1, -1, -1, -1, 0, -1, 0, 0, 0, -1, -1, 0, 0, 0, 0, -1, -1, 0, 0, -1, -1, -1, -1, -1, -1, 0, -1, -1, -1, -1, -1, -1, -1, -1, 0, 0, -1, -1, -1, -1, -1, 1, -1, 0, 0, -1, 0, 0, 0, -1, -1, -1, -1, 1, -1, 1, -1, -1, -1, 0, 1, 0, -1, 1, -1, -1, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 0, -1, -1, -1, 0, 1, -1, -1, 0, -1, -1, -1, -1, -1, -1, -1, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 0, -1, 0, 1, -1, -1, 0, -1, 0, 1, 1, -1, -1, 0, -1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, -1, 0, -1, -1, 0, 0, 0, 1, 1, 0, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 0, 0, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 0, 0, 0, 0, -1, 0, 0, 1, 0, -1, 0, 0, 1, 0, 1, 1, 0, -1, 1, 0, -1, 1, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 0, -1, -1, -1, -1, 0, -1, -1, -1, 0, 0, -1, 1, 0, 0, -1, 1, 0, 0, 0, -1, 1, 1, -1, 0, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 0, -1, -1, -1, -1, -1, -1, -1, -1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 1, 1, -1, -1, -1, -1, 0, -1, -1, -1, 1, -1, -1, -1, -1, 0, 1, 0, 0, 1, -1, 0, 0, 0, 0, -1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, -1, 1, 0, 0, 1, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0, 0, 1, 0, 0, 0, 1, -1, -1, 0, -1, 0, -1, -1, -1, 0, -1, -1, -1, 0, -1, -1, -1, -1, -1, -1, 0, -1, -1, -1, -1, -1, -1, 0, -1, -1, 1, -1, -1, -1, 0, 0, 0, 0, 0, 0, -1, -1, -1, 0, -1, -1, -1, -1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 1]
# y_pred = [-1, 0, -1, 0, 0, 0, 0, 0, 0, -1, 0, 1, 0, -1, 0, 1, 0, 0, 0, 1, 0, 0, -1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, -1, -1, -1, -1, 0, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 0, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 0, 0, -1, -1, -1, 0, -1, 0, -1, -1, 0, 0, -1, -1, -1, -1, -1, -1, -1, -1, 0, 0, -1, 0, 0, -1, -1, -1, -1, -1, -1, 0, -1, 0, 0, 0, -1, -1, -1, 0, -1, -1, 0, -1, -1, -1, -1, 0, -1, 0, -1, 0, 1, -1, -1, -1, -1, 0, 0, 0, 0, -1, 0, 0, 0, -1, 0, -1, 0, 0, 0, -1, 0, -1, 0, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 0, 0, -1, 0, -1, 0, 0, 0, 0, -1, 0, -1, -1, -1, -1, 0, 0, 0, 0, -1, -1, -1, 0, -1, -1, -1, -1, -1, -1, 0, -1, -1, -1, -1, -1, -1, -1, -1, 0, 0, 0, -1, -1, -1, -1, -1, -1, 0, -1, -1, 0, 0, 0, -1, -1, -1, -1, 1, -1, -1, -1, -1, -1, 0, 0, 0, -1, 0, -1, -1, 1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 0, -1, -1, -1, 0, 0, -1, -1, -1, -1, -1, -1, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 0, 0, -1, -1, 0, -1, -1, -1, 0, -1, -1, 0, -1, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, -1, 0, 0, 0, -1, 0, -1, -1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0, 1, 1, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 0, -1, -1, 0, 0, 1, -1, -1, -1, 0, 0, 0, -1, 0, 0, 0, -1, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, -1, 0, -1, -1, -1, -1, 0, -1, -1, -1, 0, -1, -1, -1, 0, 0, -1, -1, -1, 0, 1, -1, 0, 0, -1, -1, -1, 1, -1, 0, -1, 0, 1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 0, 0, 0, -1, -1, -1, -1, -1, -1, 0, -1, -1, -1, 0, -1, -1, -1, -1, 0, 0, -1, -1, 0, -1, 0, -1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, -1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, -1, 0, -1, 0, 1, 0, -1, -1, 1, -1, 1, -1, -1, -1, 0, -1, -1, -1, 0, -1, -1, -1, -1, -1, 0, 0, -1, -1, 0, 0, 0, -1, -1, 0, 0, 0, -1, 0, 0, 0, -1, 0, -1, -1, -1, -1, 0, -1, 0, -1, 0, 0, 0, -1, 0, 0, -1, -1, 1, -1, 1, 1, -1, -1, -1, -1, -1, 0, -1, 0, -1, 1, 0, 0, 0, 0, 0, 0]
# print(ponsol_metrics_new(y_true, y_pred))
# print(ponsol_metrics_new(y_true, y_pred, balance=True))
# print(ponsol_metrics(y_true, y_pred))
# print(ponsol_metrics(y_true, y_pred, True))

# print(ponsol_metrics_new(y_true, y_pred)[2].values == ponsol_metrics(y_true, y_pred)[2].values)
# labels = [-1, 0, 1]
# t = confusion_matrix(y_true, y_pred, labels=labels).astype(np.float)
# print(t.sum(axis=1).reshape(3, ))
# print(np.tile(t.sum(axis=1), (3, 1)).T)
# print(t * t.sum(axis=1)[0] / np.tile(t.sum(axis=1), (3, 1)).T)


# 格式化 metics 的输出数据


def format_metrics(metrics, name=None):
    """
    格式化 metrics
    :param metrics: (accuracy, gc2, other)
    :param name: string
    :reutrn : 形如
             tag     
        fn   -1          28.500000
             0           19.500000
             1           26.600000
        fp   -1          32.000000
             0            9.900000
                           ...    
        tpr  -1           0.546416
             0            0.204500
             1            0.583755
        all  accuracy     0.506627
             gc2          0.061903
        Length: 26, dtype: float64
    """
    acc, gc2, other = metrics
    other = other.sort_index().unstack()
    other = other.append(pd.Series([acc, gc2], index=[['all', 'all'], ['accuracy', 'gc2']]))
    other.name = name
    return other


# 10cv util class


class CVUtil:
    def __init__(self, rfc, name, cv_method, n_cv=10, feature_select=None):
        """
        :param rfc: 训练模型
        :param name: 名称 string
        :param cv_method: 划分cv的方法
        :param n_cv: cv数目
        :param feature_select: 特征选择模型
        """
        self.rfc = rfc
        self.name = name
        self.cv_method = cv_method
        self.n_cv = n_cv
        self.feature_select = feature_select

    def set_data(self, X_train, y_train, g_train):
        """定义数据数据"""
        self.X_train = np.array(X_train)
        self.y_train = np.array(y_train)
        self.g_train = np.array(g_train)

        print("原数据特征数目：", self.X_train.shape[1])
        if self.feature_select:
            self.X_train = self.feature_select.transform(self.X_train)

        print("实际数据特征数目：", self.X_train.shape[1])
        return self

    def fit(self):
        # n cv 的结果
        self.normal, self.balance = self._cv()
        return self

    def get_res(self, kind):
        """
        对结果进行格式化
        :param kind: 1-normal, 2-balance, 3-all
        """
        # nomal
        acc, gc2, metr = self.normal
        acc = np.mean(acc)
        gc2 = np.mean(gc2)
        metr = metr.groupby('tag').mean()
        res = metr.unstack()
        res1 = res.append(pd.Series([acc, gc2], index=[['all', 'all'], ['accuracy', 'gc2']]))
        # res1 = res1.map(lambda x: round(x, 3))
        res1.name = self.name

        # balance
        acc, gc2, metr = self.balance
        acc = np.mean(acc)
        gc2 = np.mean(gc2)
        metr = metr.groupby('tag').mean()
        res = metr.unstack()
        res2 = res.append(pd.Series([acc, gc2], index=[['all', 'all'], ['accuracy', 'gc2']]))
        # res2 = res2.map(lambda x: round(x, 3))
        res2.name = self.name

        # 整合版
        res3 = []
        for i in range(len(res2)):
            if '%.3f' % res1.iloc[i] == '%.3f' % res2.iloc[i]:
                res3.append('%.3f' % res1.iloc[i])
            else:
                res3.append('%.3f/%.3f' % (res1.iloc[i], res2.iloc[i]))
        res3 = pd.Series(res3, index=res2.index)
        res3.name = self.name
        # 判断返回值
        if kind == 1:
            return res1
        elif kind == 2:
            return res2
        elif kind == 3:
            return res3
        else:
            raise RuntimeError("kind in [1, 2, 3]")

    def _cv(self):
        """
        通过 n 重交叉验证，获得评判的指标
        :param rfc: 训练的方法
        :param name: 对于训练方法的命名
        :param is_save: 是否保存结果
        :param out_path: 结果保存的路径
        :return (res_acc, res_gc2, res_metr) -> (float, float, DateFrame)
        """
        print('%s: 进行交叉验证' % self.name)
        print("特征数目：", self.X_train.shape[1])

        # 查看数据中不同类型的比例
        print("train数据分布")
        print(pd.value_counts(self.y_train))

        _value_counts = pd.Series(self.y_train).value_counts().reindex([-1, 0, 1])
        print('原有数据数目：{} : {} : {}'.format(*_value_counts), )
        # 保存结果的列表
        ## normal
        cv_accuracy = []  # 正确率
        cv_gc2 = []  # gc2
        cv_metrics = []  # 其他指标
        ## balance
        cv_accuracy_balance = []  # 正确率
        cv_gc2_balance = []  # gc2
        cv_metrics_balance = []  # 其他指标
        for (index, (train_index, test_index)) in enumerate(
                self.cv_method.split(self.X_train, self.y_train, groups=self.g_train)):
            print('------cv %s------' % (index + 1))
            cv_X_train, cv_X_test = self.X_train[train_index], self.X_train[test_index]
            cv_y_train, cv_y_test = self.y_train[train_index], self.y_train[test_index]
            # 输出比例
            _value_counts = pd.Series(cv_y_train).value_counts().reindex([-1, 0, 1])
            print('cv test ：{} : {} : {}'.format(*_value_counts))

            _value_counts = pd.Series(cv_y_test).value_counts().reindex([-1, 0, 1])
            print('cv test ：{} : {} : {}'.format(*_value_counts))
            _rfc = self.rfc.fit(cv_X_train, cv_y_train)
            p_test = _rfc.predict(cv_X_test)
            # 评估指标
            ## normal
            acc, gc2, metr = ponsol_metrics(cv_y_test, p_test)
            cv_accuracy.append(acc)
            cv_gc2.append(gc2)
            metr['tag'] = metr.index
            metr['cv'] = 'cv%s' % (index + 1)
            cv_metrics.append(metr)
            ## balance
            acc, gc2, metr = ponsol_metrics(cv_y_test, p_test, balance=True)
            cv_accuracy_balance.append(acc)
            cv_gc2_balance.append(gc2)
            metr['tag'] = metr.index
            metr['cv'] = 'cv%s' % (index + 1)
            cv_metrics_balance.append(metr)

        # 结果
        ## normal
        res_metr = pd.concat(cv_metrics)
        res_metr.name = self.name
        res_acc = cv_accuracy
        res_gc2 = cv_gc2
        ## balance
        res_metr_balance = pd.concat(cv_metrics_balance)
        res_metr_balance.name = self.name
        res_acc_balance = cv_accuracy_balance
        res_gc2_balance = cv_gc2_balance
        return [[res_acc, res_gc2, res_metr], [res_acc_balance, res_gc2_balance, res_metr_balance]]


## 测试数据


# name = 'RandomForeast_10cv_3class'
# rfc = RandomForestClassifier(n_estimators=25)  # 使用随机森林
# cv = [CVUtil(rfc, name) for i in range(3)]

# CVUtil.jion(cv)


# blind test util test


class BlindTestUtil:
    """盲测工具类
    直接测试test1和test2的效果
    """

    def __init__(self, rfc, name='', feature_select=None):
        """
        rfc: 模型
        name： 名称
        feature_select： 特征选择的模型
        """
        self.rfc = rfc
        self.name = name

        self.feature_select = feature_select

    def set_data(self, X_train, y_train, X_test1, y_test1, X_test2, y_test2):
        """定义数据"""
        self.X_train = np.array(X_train)
        self.y_train = np.array(y_train)
        self.X_test1 = np.array(X_test1)
        self.y_test1 = np.array(y_test1)
        self.X_test2 = np.array(X_test2)
        self.y_test2 = np.array(y_test2)

        print("原数据特征数目：", self.X_train.shape[1])
        if self.feature_select:
            self.X_train = self.feature_select.transform(self.X_train)
            self.X_test1 = self.feature_select.transform(self.X_test1)
            self.X_test2 = self.feature_select.transform(self.X_test2)
        print("实际特征数目：", self.X_train.shape[1])
        return self

    def fit(self):
        # 结果
        self.test1, self.test1_balance, self.test2, self.test2_balance = self._test(
        )
        return self

    def get_res(self, kind):
        """
        对结果进行格式化
        :param kind: 1-test1, 2-test2, 3-all
        """
        # test1
        acc, gc2, metr = self.test1
        res = metr.unstack()
        res1 = res.append(
            pd.Series([acc, gc2], index=[['all', 'all'], ['accuracy', 'gc2']]))
        res1.name = self.name + '_test1'
        acc, gc2, metr = self.test1_balance
        res = metr.unstack()
        res1_balance = res.append(
            pd.Series([acc, gc2], index=[['all', 'all'], ['accuracy', 'gc2']]))
        res1_balance.name = self.name + '_test1_balance'
        res1_all = pd.concat([res1, res1_balance], axis=1)

        # test2
        acc, gc2, metr = self.test2
        res = metr.unstack()
        res2 = res.append(
            pd.Series([acc, gc2], index=[['all', 'all'], ['accuracy', 'gc2']]))
        res2.name = self.name + '_test2'
        acc, gc2, metr = self.test2_balance
        res = metr.unstack()
        res2_balance = res.append(
            pd.Series([acc, gc2], index=[['all', 'all'], ['accuracy', 'gc2']]))
        res2_balance.name = self.name + '_test2_balance'
        res2_all = pd.concat([res2, res2_balance], axis=1)

        # 整合版
        ## test1
        res3_1 = []
        for i in range(len(res1)):
            if '%.3f' % res1.iloc[i] == '%.3f' % res2.iloc[i]:
                res3_1.append('%.3f' % res1.iloc[i])
            else:
                res3_1.append('%.3f/%.3f' %
                              (res1.iloc[i], res1_balance.iloc[i]))
        res3_1 = pd.Series(res3_1, index=res1.index)
        res3_1.name = self.name + '_test1'
        ## test2
        res3_2 = []
        for i in range(len(res2)):
            if res2.iloc[i] == res2_balance.iloc[i]:
                res3_2.append('%.3f' % res2.iloc[i])
            else:
                res3_2.append('%.3f/%.3f' %
                              (res2.iloc[i], res2_balance.iloc[i]))
        res3_2 = pd.Series(res3_2, index=res2.index)
        res3_2.name = self.name + '_test2'
        res3_all = pd.concat([res3_1, res3_2], axis=1)

        # 判断返回值
        if kind == 1:
            return res1_all
        elif kind == 2:
            return res2_all
        elif kind == 3:
            return res3_all
        else:
            raise RuntimeError("kind in [1, 2, 3]")

    def _test(self):
        print("特征数目：", self.X_train.shape[1])
        print("train数据分布")
        print(pd.value_counts(self.y_train))
        print("test1数据分布")
        print(pd.value_counts(self.y_test1))
        print("test2数据分布")
        print(pd.value_counts(self.y_test2))
        _rfc = self.rfc.fit(self.X_train, self.y_train)
        p_test1 = _rfc.predict(self.X_test1)
        p_test2 = _rfc.predict(self.X_test2)
        # test1
        res1 = ponsol_metrics(self.y_test1, p_test1)
        res1[2].name = self.name + '_test1'
        # test1 balance
        res1_balance = ponsol_metrics(self.y_test1, p_test1, balance=True)
        res1_balance[2].name = self.name + '_test1_balance'
        # test2
        res2 = ponsol_metrics(self.y_test2, p_test2)
        res2[2].name = self.name + '_test2'
        # test2 balca
        res2_balance = ponsol_metrics(self.y_test2, p_test2, balance=True)
        res2_balance[2].name = self.name + '_test2_balance'
        return res1, res1_balance, res2, res2_balance


## 测试数据


# name = 'RandomForeast_3class'
# rfc = RandomForestClassifier(n_estimators=25)  # 使用随机森林
# cv = [CVUtil(rfc, name) for i in range(3)]
# cv = [BlindTestUtil(rfc, name) for i in range(3)]
# BlindTestUtil.jion(cv)


# Pon-Sol layer estimator


class PonsolLayerEstimator:
    def __init__(self, estimator, feature_selected=None, special_kind=-1, kwargs=None):
        """
        :param estimator: 模型算法，只是类
        :param feature_selected: 选择出的特征列表，为特征的名称，提供两个
        :param special_kind: 区分第一层的类型
        :kwargs: 给模型的参数
        """
        self.Estimator = estimator
        self.feature_selected = feature_selected
        self.kwargs = kwargs
        self.special_kind = special_kind
        print("初始化完毕，模型：%s，模型参数：%s，特征：%s，第一层区分的类别：%s" % (
            self.Estimator, self.kwargs, self.feature_selected, self.special_kind,
        ))

    def fit(self, X, y):
        # X 是 DF，y 是 list 
        print("====== 开始训练模型")
        print("输入数据")
        y = np.array(y)
        print("X 数目:", X.shape)
        print("y 分布情况:", solubility_distribute(y))
        print("y=", y)

        print("是否进行使用指定特征：", self.feature_selected)
        if self.feature_selected is not None:
            self.fs1 = self.feature_selected[0]
            self.fs2 = self.feature_selected[1]
        else:
            self.fs1 = X.columns.values
            self.fs2 = X.columns.values
        print("第一层使用 %s 个特征: %s" % (len(self.fs1), self.fs1))
        print("第二层使用 %s 个特征: %s" % (len(self.fs2), self.fs2))

        # 数据 X y
        index_layer_1 = (y == self.special_kind)
        index_layer_2 = (y != self.special_kind)
        X1 = X.loc[:, self.fs1]
        y1 = np.array(y)
        y1[index_layer_2] = self.special_kind + 1
        X2 = X.loc[index_layer_2, self.fs2]
        y2 = y[index_layer_2]

        # 第一层
        print("开始训练第一层模型")
        print("X 数目:", X1.shape)
        print("y 分布情况:", solubility_distribute(y1))
        print("y=", y1)
        estimator1 = self.Estimator(**self.kwargs)
        self.estimator1 = estimator1.fit(X1, y1)

        # 第二层
        print("开始训练第二层模型")
        print("X 数目:", X2.shape)
        print("y 分布情况:", solubility_distribute(y2))
        print("y=", y2)
        estimator2 = self.Estimator(**self.kwargs)
        self.estimator2 = estimator2.fit(X2, y2)
        return self

    def predict(self, X):
        print("====== 开始预测")
        print("输入数据数目:", X.shape)
        print("第一层使用 %s 个特征: %s" % (len(self.fs1), self.fs1))
        print("第二层使用 %s 个特征: %s" % (len(self.fs2), self.fs2))

        print("开始第一层预测")
        X1 = X.loc[:, self.fs1]
        print("输入X数目:", X1.shape)
        p_layer1 = self.estimator1.predict(X1)
        p_layer1 = np.array(p_layer1)
        print("第一层预测结果分布:", solubility_distribute(p_layer1))
        index_layer1_is_special = p_layer1 == self.special_kind
        index_layer1_not_special = p_layer1 != self.special_kind

        # 保存最终的结果
        p_all = np.full(X.shape[0], None)
        p_all[index_layer1_is_special] = p_layer1[index_layer1_is_special]

        print("开始第二层预测")
        X2 = X.loc[index_layer1_not_special, self.fs2]
        print("输入X数目:", X2.shape)
        if X2.shape[0] > 0:
            p_layer2 = self.estimator2.predict(X2)
            print("第二层预测结果分布:", solubility_distribute(p_layer2))

            print("合并两次预测结果")
            p_all[index_layer1_not_special] = p_layer2
        else:
            print("X2 无数据")
        print("最终预测结果分布:", solubility_distribute(p_all))
        return p_all


## 测试


# cv_kind = 1
# train_set_kind = 1
# 获取数据
# X_test1, y_test1, X_test2, y_test2 = BalanceDate.get_test_values()  # 两组测试数据  
# X_train, y_train, g_train = BalanceDate.get_train_values(train_set_kind)  
# cvs = BalanceDate.split_cv(kind=cv_kind, train_set_kind=train_set_kind)
# cvs_method = BalanceDate.split_cv(kind=cv_kind, train_set_kind=train_set_kind, return_kind=2)

# print("test1 分布情况")
# solubility_distribute(y_test1, 0, 1)
# print("test2 分布情况")
# solubility_distribute(y_test2, 0, 1)
# print("train 分布情况")
# solubility_distribute(y_train, 0, 1)

# print("# 训练模型")
# Estimator = lgb.LGBMClassifier
# kwargs = {"random_state":0, }
# layer_estimator = PonsolLayerEstimator(Estimator, kwargs=kwargs, special_kind=-1)
# layer_estimator.fit(X_train, y_train)

# print("# 盲测")
# p_test1 = layer_estimator.predict(X_test1)
# print()
# p_test2 = layer_estimator.predict(X_test2)

# print("test1 预测结果")
# print(accuracy_score(np.array(y_test1), p_test1))
# print(sum(np.array(y_test1) == p_test1)/ len(p_test1))

# print("test2 预测结果")
# print(accuracy_score(np.array(y_test2), p_test2))
# print(sum(np.array(y_test2) == p_test2)/ len(p_test2))

# print("# *使用原模型直接盲测的结果")
# model3 = lgb.LGBMClassifier(random_state=0).fit(X_train, y_train)
# p_test1_d = model3.predict(X_test1)
# p_test2_d = model3.predict(X_test2)


# print("test1 预测结果")
# print(accuracy_score(np.array(y_test1), p_test1))
# print(sum(np.array(y_test1) == p_test1_d)/ len(p_test1))

# print("test2 预测结果")
# print(accuracy_score(np.array(y_test2), p_test2))
# print(sum(np.array(y_test2) == p_test2_d)/ len(p_test2))


# 10cv util class for layer 2


class CVUtilLayer2:
    def __init__(self, Estimator, cvs_method, name="", n_cv=10, kwargs=None):
        """
        :param Estimator: 训练的模型
        :param cvs_method:  cv 方法
        :param name:  名称
        :param n_cv:  cv 数目
        
        """
        self.Estimator = Estimator
        self.kwargs = kwargs
        self.cvs_method = cvs_method
        self.name = name
        self.n_cv = n_cv

    def set_data(self, X_train, y_train, g_train, special_layer_kind, features_for_layer_1=None,
                 features_for_layer_2=None):
        """定义数据"""
        self.X_train = X_train
        self.y_train = y_train
        self.g_train = g_train
        self.special_layer_kind = special_layer_kind
        self.features_for_layer_1 = features_for_layer_1
        self.features_for_layer_2 = features_for_layer_2
        return self

    def fit(self):
        # n cv 的结果
        self.normal, self.balance = self._cv(
            self.special_layer_kind,
            self.X_train,
            self.y_train,
            self.cvs_method,
            self.features_for_layer_1,
            self.features_for_layer_2
        )
        return self

    def get_res(self, kind):
        """
        对结果进行格式化
        :param kind: 1-normal, 2-balance, 3-all
        """
        # nomal
        acc, gc2, metr = self.normal
        acc = np.mean(acc)
        gc2 = np.mean(gc2)
        metr = metr.groupby('tag').mean()
        res = metr.unstack()
        res1 = res.append(pd.Series([acc, gc2], index=[['all', 'all'], ['accuracy', 'gc2']]))
        # res1 = res1.map(lambda x: round(x, 3))
        res1.name = self.name

        # balance
        acc, gc2, metr = self.balance
        acc = np.mean(acc)
        gc2 = np.mean(gc2)
        metr = metr.groupby('tag').mean()
        res = metr.unstack()
        res2 = res.append(pd.Series([acc, gc2], index=[['all', 'all'], ['accuracy', 'gc2']]))
        # res2 = res2.map(lambda x: round(x, 3))
        res2.name = self.name

        # 整合版
        res3 = []
        for i in range(len(res2)):
            if '%.3f' % res1.iloc[i] == '%.3f' % res2.iloc[i]:
                res3.append('%.3f' % res1.iloc[i])
            else:
                res3.append('%.3f/%.3f' % (res1.iloc[i], res2.iloc[i]))
        res3 = pd.Series(res3, index=res2.index)
        res3.name = self.name
        # 判断返回值
        if kind == 1:
            return res1
        elif kind == 2:
            return res2
        elif kind == 3:
            return res3
        else:
            raise RuntimeError("kind in [1, 2, 3]")

    def _cv(self, special_layer_kind,
            X_train,
            y_train,
            cvs_method,
            features_for_layer_1=None,
            features_for_layer_2=None,
            **args):
        """
        @param special_layer_kind: 区分第一层的大类
        @param X_train: 训练集 X
        @param y_train: 训练集 y 
        @param cvs_method: cv 的方法

        @param features_for_layer_1: 第一层使用到的特征
        @param features_for_layer_2: 第二层使用到的特征
        Note: 
            1. 属性为属性名称的列表，不是索引的列表
            2. @param args: 用于存放多余参数
        """
        # TODO: 是否平衡数据
        # 对于属性的处理
        if (features_for_layer_1 is None):
            features_for_layer_1 = X_train.columns.values
        if (features_for_layer_2 is None):
            features_for_layer_2 = X_train.columns.values
        layer_name = {
            0: special_layer_kind,
            1: [i for i in [-1, 0, 1] if i != special_layer_kind]
        }

        # 保存结果的列表
        ## normal
        cv_accuracy = []  # 正确率
        cv_gc2 = []  # gc2
        cv_metrics = []  # 其他指标
        ## balance
        cv_accuracy_balance = []  # 正确率
        cv_gc2_balance = []  # gc2
        cv_metrics_balance = []

        print("》》》》》》开始10cv")
        print("第一层: {0}和非{0}".format(layer_name[0]))
        print("第二层: {}和{}".format(*layer_name[1]))
        for (index, (train_index,
                     test_index)) in enumerate(cvs_method.split(X_train, y_train)):
            print('------cv %s------' % (index + 1))
            cv_X_train, cv_X_validate = X_train.iloc[train_index, :], X_train.iloc[
                                                                      test_index, :]
            cv_y_train, cv_y_validate = y_train.iloc[train_index], y_train.iloc[
                test_index]
            # 训练
            # print("# 训练模型")
            Estimator = self.Estimator
            if self.kwargs is None:
                kwargs = {"random_state": 0, }
            else:
                kwargs = self.kwargs
            layer_estimator = PonsolLayerEstimator(Estimator, kwargs=kwargs, special_kind=special_layer_kind,
                                                   feature_selected=[features_for_layer_1, features_for_layer_2])
            layer_estimator.fit(cv_X_train, cv_y_train)
            cv_y_pred = layer_estimator.predict(cv_X_validate)
            cv_y_true = cv_y_validate

            # 评估指标
            ## normal
            acc, gc2, metr = ponsol_metrics(cv_y_true, cv_y_pred)
            cv_accuracy.append(acc)
            cv_gc2.append(gc2)
            metr['tag'] = metr.index
            metr['cv'] = 'cv%s' % (index + 1)
            cv_metrics.append(metr)
            ## balance
            acc, gc2, metr = ponsol_metrics(cv_y_true, cv_y_pred, True)
            cv_accuracy_balance.append(acc)
            cv_gc2_balance.append(gc2)
            metr['tag'] = metr.index
            metr['cv'] = 'cv%s' % (index + 1)
            cv_metrics_balance.append(metr)

        print("accuracy")
        print(" ".join(["{:.3f}".format(i) for i in cv_accuracy]))
        print("mean:", np.mean(cv_accuracy))
        print()
        print("gc2")
        print(" ".join(["{:.3f}".format(i) for i in cv_gc2]))
        print("mean:", np.mean(cv_gc2))

        # 结果
        ## normal
        res_metr = pd.concat(cv_metrics)
        res_metr.name = self.name
        res_acc = cv_accuracy
        res_gc2 = cv_gc2
        ## balance
        res_metr_balance = pd.concat(cv_metrics_balance)
        res_metr_balance.name = self.name
        res_acc_balance = cv_accuracy_balance
        res_gc2_balance = cv_gc2_balance
        return [[res_acc, res_gc2, res_metr], [res_acc_balance, res_gc2_balance, res_metr_balance]]


## 测试


# kind = -1
# _cvUtil = CVUtilLayer2(lgb.LGBMClassifier, cvs_method,).set_data(X_train, y_train, g_train, kind,).fit()


# blind test util test for layer 2


class BlindTestUtilLayer2:
    def __init__(self, Estimator, name="", kwargs=None):
        """
        :param Estimator: 模型
        :param name: 名称
        """
        self.Estimator = Estimator
        self.kwargs = kwargs
        self.name = name

    def set_data(self,
                 X_train,
                 y_train,
                 X_test1,
                 y_test1,
                 X_test2,
                 y_test2,
                 special_layer_kind,
                 features_for_layer_1=None,
                 features_for_layer_2=None):
        self.X_train = X_train
        self.y_train = y_train
        self.X_test1 = X_test1
        self.y_test1 = y_test1
        self.X_test2 = X_test2
        self.y_test2 = y_test2
        self.special_layer_kind = special_layer_kind
        self.features_for_layer_1 = features_for_layer_1
        self.features_for_layer_2 = features_for_layer_2
        return self

    def fit(self):
        self.test1, self.test1_balance, self.test2, self.test2_balance = self._test(
            self.special_layer_kind, self.X_train, self.y_train,
            self.X_test1, self.y_test1, self.X_test2, self.y_test2,
            self.features_for_layer_1,
            self.features_for_layer_2)
        return self

    def get_res(self, kind):
        """
        对结果进行格式化
        :param kind: 1-test1, 2-test2, 3-all
        """
        # test1
        acc, gc2, metr = self.test1
        res = metr.unstack()
        res1 = res.append(
            pd.Series([acc, gc2], index=[['all', 'all'], ['accuracy', 'gc2']]))
        res1.name = self.name + '_test1'
        acc, gc2, metr = self.test1_balance
        res = metr.unstack()
        res1_balance = res.append(
            pd.Series([acc, gc2], index=[['all', 'all'], ['accuracy', 'gc2']]))
        res1_balance.name = self.name + '_test1_balance'
        res1_all = pd.concat([res1, res1_balance], axis=1)

        # test2
        acc, gc2, metr = self.test2
        res = metr.unstack()
        res2 = res.append(
            pd.Series([acc, gc2], index=[['all', 'all'], ['accuracy', 'gc2']]))
        res2.name = self.name + '_test2'
        acc, gc2, metr = self.test2_balance
        res = metr.unstack()
        res2_balance = res.append(
            pd.Series([acc, gc2], index=[['all', 'all'], ['accuracy', 'gc2']]))
        res2_balance.name = self.name + '_test2_balance'
        res2_all = pd.concat([res2, res2_balance], axis=1)

        # 整合版
        ## test1
        res3_1 = []
        for i in range(len(res1)):
            if '%.3f' % res1.iloc[i] == '%.3f' % res2.iloc[i]:
                res3_1.append('%.3f' % res1.iloc[i])
            else:
                res3_1.append('%.3f/%.3f' %
                              (res1.iloc[i], res1_balance.iloc[i]))
        res3_1 = pd.Series(res3_1, index=res1.index)
        res3_1.name = self.name + '_test1'
        ## test2
        res3_2 = []
        for i in range(len(res2)):
            if res2.iloc[i] == res2_balance.iloc[i]:
                res3_2.append('%.3f' % res2.iloc[i])
            else:
                res3_2.append('%.3f/%.3f' %
                              (res2.iloc[i], res2_balance.iloc[i]))
        res3_2 = pd.Series(res3_2, index=res2.index)
        res3_2.name = self.name + '_test2'
        res3_all = pd.concat([res3_1, res3_2], axis=1)

        # 判断返回值
        if kind == 1:
            return res1_all
        elif kind == 2:
            return res2_all
        elif kind == 3:
            return res3_all
        else:
            raise RuntimeError("kind in [1, 2, 3]")

    def _test(self,
              special_layer_kind,
              X_train,
              y_train,
              X_test1,
              y_test1,
              X_test2,
              y_test2,
              features_for_layer_1=None,
              features_for_layer_2=None,
              **args):
        """
        @param special_layer_kind: 区分第一层的大类
        @param X_train: 训练集 X
        @param y_train: 训练集 y 
        @param X_test1: 测试集1 X
        @param y_test1: 测试集2 y 
        @param X_test2: 测试集1 X
        @param y_test2: 测试集2 y 

        @param features_for_layer_1: 第一层使用到的特征
        @param features_for_layer_2: 第二层使用到的特征
        note: 属性为属性名称的列表，不是索引的列表
        """
        # TODO: 是否平衡数据
        # 对于属性的处理
        if (features_for_layer_1 is None):
            features_for_layer_1 = X_train.columns
        if (features_for_layer_2 is None):
            features_for_layer_2 = X_train.columns

        layer_name = {
            0: special_layer_kind,
            1: [i for i in [-1, 0, 1] if i != special_layer_kind]
        }
        res = []

        print("》》》》》》开始 blind test")
        print("第一层: {0}和非{0}".format(layer_name[0]))
        print("第二层: {}和非{}".format(*layer_name[1]))
        y_train_blind, y_test1_blind, y_test2_blind = y_train, y_test1, y_test2

        # 训练
        if self.kwargs is None:
            kwargs = {"random_state": 0, }
        else:
            kwargs = self.kwargs
        Estimator = self.Estimator
        layer_estimator = PonsolLayerEstimator(Estimator, kwargs=kwargs, special_kind=special_layer_kind,
                                               feature_selected=[features_for_layer_1, features_for_layer_2])
        layer_estimator.fit(X_train, y_train)

        # test1
        y_true_test1 = y_test1
        y_pred_test1 = layer_estimator.predict(X_test1)

        # 普通
        res1 = ponsol_metrics(y_true_test1,
                              y_pred_test1)
        res1[2].name = self.name + '_test1'
        # test1 balance
        res1_balance = ponsol_metrics(y_true_test1,
                                      y_pred_test1, True)
        res1_balance[2].name = self.name + '_test1_balance'
        # 输出
        acc, gc2, metr = ponsol_metrics(y_true_test1,
                                        y_pred_test1)

        print("训练结果：")
        print("test1 acc: {}, gc2: {}".format(acc, gc2))
        res.append((acc, gc2, metr))

        # test2
        y_true_test2 = y_test2
        y_pred_test2 = layer_estimator.predict(X_test2)

        # 普通
        res2 = ponsol_metrics(y_true_test2,
                              y_pred_test2)
        res2[2].name = self.name + '_test2'
        # test1 balance
        res2_balance = ponsol_metrics(y_true_test2,
                                      y_pred_test2, True)
        res2_balance[2].name = self.name + '_test2_balance'

        # 输出
        acc, gc2, metr = ponsol_metrics(y_true_test2,
                                        y_pred_test2, )
        print("训练结果：")
        print("test2 acc: {}, gc2: {}".format(acc, gc2))
        return res1, res1_balance, res2, res2_balance


## 测试


# kind = -1
# _blindUtil = BlindTestUtilLayer2(lgb.LGBMClassifier,).set_data(X_train, y_train, X_test1, y_test1, X_test2, y_test2, kind,).fit()


# 导出结果


def _result_output(res_cv, res_blind, names, path, filename):
    """
    @param: res_cv:  cv 结果
    @param: res_blind:  盲测结果
    @param: names:  每种类型的名称
    @param: path:  保存路径
    @param: filename:  文件名称
    """
    # 总览
    _res_all = []
    _res_all.append([
        *[res_cv[i].get_res(1)[("all", "accuracy")] for i in range(len(names))],  # acc
        *[res_cv[i].get_res(1)[("all", "gc2")] for i in range(len(names))],  # gc2
    ])
    _res_all.append([
        *[res_blind[i].get_res(1).iloc[:, 0][("all", "accuracy")] for i in range(len(names))],
        *[res_blind[i].get_res(1).iloc[:, 0][("all", "gc2")] for i in range(len(names))]
    ])
    _res_all.append([
        *[res_blind[i].get_res(2).iloc[:, 0][("all", "accuracy")] for i in range(len(names))],
        *[res_blind[i].get_res(2).iloc[:, 0][("all", "gc2")] for i in range(len(names))]
    ])
    dp_overall = pd.DataFrame(_res_all, columns=pd.MultiIndex.from_product([["acc", "gc2"], names]),
                              index=["10cv", "test1", "test2"])

    # acc
    dp_acc_detail = pd.concat(
        [
            pd.DataFrame([
                *res_cv[i].normal[0],  # 10cv
                res_blind[i].get_res(1).iloc[:, 0][("all", "accuracy")],  # test1
                res_blind[i].get_res(2).iloc[:, 0][("all", "accuracy")],  # test2
            ]) for i in range(len(names))
        ],
        axis=1, )
    dp_acc_detail.index = [*["cv{}".format(i) for i in range(1, 11)], "test1", "test2"]
    dp_acc_detail.columns = names

    # gc2
    dp_gc2_detail = pd.concat(
        [
            pd.DataFrame([
                *res_cv[i].normal[1],  # 10cv
                res_blind[i].get_res(1).iloc[:, 0][("all", "gc2")],  # test1
                res_blind[i].get_res(2).iloc[:, 0][("all", "gc2")],  # test2
            ]) for i in range(len(names))
        ],
        axis=1, )
    dp_gc2_detail.index = [*["cv{}".format(i) for i in range(1, 11)], "test1", "test2"]
    dp_gc2_detail.columns = names

    # 其他
    dp_metr_detail = pd.concat([pd.concat(
        [
            res_cv[i].get_res(1).unstack().unstack().unstack().loc[
                [-1, 0, 1], "tp	tn	fp	fn	ppv	npv	tpr	tnr".split()],
            res_blind[i].get_res(1).iloc[:, 0].unstack().unstack().unstack().loc[
                [-1, 0, 1], "tp	tn	fp	fn	ppv	npv	tpr	tnr".split()],
            res_blind[i].get_res(2).iloc[:, 0].unstack().unstack().unstack().loc[
                [-1, 0, 1], "tp	tn	fp	fn	ppv	npv	tpr	tnr".split()]
        ],
        keys=["10cv", "test1", "test2"]
    ) for i in range(len(names))], keys=names)

    # 保存结果
    _path = os.path.join(path, "{}_res.xlsx".format(filename))
    print("输出路径为:", _path)
    with pd.ExcelWriter(_path) as writer:
        dp_overall.to_excel(writer, sheet_name="overall", float_format="%.3f")
        dp_acc_detail.to_excel(writer, sheet_name="acc_detail", float_format="%.3f")
        dp_gc2_detail.to_excel(writer, sheet_name="acc_gc2", float_format="%.3f")
        dp_metr_detail.to_excel(writer, sheet_name="metr_detail", float_format="%.3f")
    return dp_overall, dp_acc_detail, dp_gc2_detail, dp_metr_detail


def _result_balance_output(res_cv, res_blind, names, path, filename):
    """
    @param: res_cv:  cv 结果
    @param: res_blind:  盲测结果
    @param: names:  每种类型的名称
    @param: path:  保存路径
    @param: filename:  文件名称
    """
    # 总览
    _res_all = []
    _res_all.append([
        *[res_cv[i].get_res(2)[("all", "accuracy")] for i in range(len(names))],  # acc
        *[res_cv[i].get_res(2)[("all", "gc2")] for i in range(len(names))],  # gc2
    ])
    _res_all.append([
        *[res_blind[i].get_res(1).iloc[:, 1][("all", "accuracy")] for i in range(len(names))],
        *[res_blind[i].get_res(1).iloc[:, 1][("all", "gc2")] for i in range(len(names))]
    ])
    _res_all.append([
        *[res_blind[i].get_res(2).iloc[:, 1][("all", "accuracy")] for i in range(len(names))],
        *[res_blind[i].get_res(2).iloc[:, 1][("all", "gc2")] for i in range(len(names))]
    ])
    dp_overall_balance = pd.DataFrame(_res_all, columns=pd.MultiIndex.from_product([["acc", "gc2"], names]),
                                      index=["10cv", "test1", "test2"])

    # acc
    dp_acc_detail_balance = pd.concat(
        [
            pd.DataFrame([
                *res_cv[i].balance[0],  # 10cv
                res_blind[i].get_res(1).iloc[:, 1][("all", "accuracy")],  # test1
                res_blind[i].get_res(2).iloc[:, 1][("all", "accuracy")],  # test2
            ]) for i in range(len(names))
        ],
        axis=1, )
    dp_acc_detail_balance.index = [*["cv{}".format(i) for i in range(1, 11)], "test1", "test2"]
    dp_acc_detail_balance.columns = names

    # gc2
    dp_gc2_detail_balance = pd.concat(
        [
            pd.DataFrame([
                *res_cv[i].balance[1],  # 10cv
                res_blind[i].get_res(1).iloc[:, 1][("all", "gc2")],  # test1
                res_blind[i].get_res(2).iloc[:, 1][("all", "gc2")],  # test2
            ]) for i in range(len(names))
        ],
        axis=1, )
    dp_gc2_detail_balance.index = [*["cv{}".format(i) for i in range(1, 11)], "test1", "test2"]
    dp_gc2_detail_balance.columns = names

    # 其他
    dp_metr_detail_balance = pd.concat([pd.concat(
        [
            res_cv[i].get_res(2).unstack().unstack().unstack().loc[
                [-1, 0, 1], "tp	tn	fp	fn	ppv	npv	tpr	tnr".split()],
            res_blind[i].get_res(1).iloc[:, 1].unstack().unstack().unstack().loc[
                [-1, 0, 1], "tp	tn	fp	fn	ppv	npv	tpr	tnr".split()],
            res_blind[i].get_res(2).iloc[:, 1].unstack().unstack().unstack().loc[
                [-1, 0, 1], "tp	tn	fp	fn	ppv	npv	tpr	tnr".split()]
        ],
        keys=["10cv", "test1", "test2"]
    ) for i in range(len(names))], keys=names)

    _path = os.path.join(path, "{}_res_balanced.xlsx".format(filename))
    print("输出路径为:", _path)
    with pd.ExcelWriter(_path) as writer:
        dp_overall_balance.to_excel(writer, sheet_name="overall", float_format="%.3f")
        dp_acc_detail_balance.to_excel(writer, sheet_name="acc_detail", float_format="%.3f")
        dp_gc2_detail_balance.to_excel(writer, sheet_name="acc_gc2", float_format="%.3f")
        dp_metr_detail_balance.to_excel(writer, sheet_name="metr_detail", float_format="%.3f")
    return dp_overall_balance, dp_acc_detail_balance, dp_gc2_detail_balance, dp_metr_detail_balance


def result_output(res_cv, res_blind, names, path, filename, is_res_balance=False):
    """
    @param: res_cv:  cv 结果  utils.CVUtil对象
    @param: res_blind:  盲测结果  utils.BlindTestUtil对象
    @param: names:  每种类型的名称
    @param: path:  保存路径
    @param: filename:  文件名称
    @param: is_res_balance: 结果是否需要平衡
    """
    if is_res_balance:
        return _result_balance_output(res_cv, res_blind, names, path, filename)
    else:
        return _result_output(res_cv, res_blind, names, path, filename)


# 展示特征选择的结果


# 展示数据比例


def solubility_distribute(y, i=0, verb=0):
    _vc = pd.value_counts(y)
    _index = _vc.index.sort_values()
    _vc = _vc[_index]
    _str = ": ".join(map(str, _index)) + " = " + ": ".join(map(str, _vc.values)) + "= " + ": ".join(
        map(lambda x: "%.2f" % x, (_vc / _vc.iloc[i]).values))
    if (verb > 0):
        print(_str)
    return _str
