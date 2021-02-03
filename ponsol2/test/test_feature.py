# -*- coding:utf-8 -*-
'''
__author__ = 'XD'
__mtime__ = 2021/1/22
__project__ = Pon-Sol2
Fix the Problem, Not the Blame.
'''

# 本地
from unittest import TestCase
import logging
# 第三方
import pandas as pd
import numpy as np

# 自定义
import feature_extraction as fe
import logconfig
import model


class FeatureTest(TestCase):
    def setUp(self) -> None:
        logconfig.setup_logging()
        self.log = logging.getLogger("ponsol.test.feature_extraction")
        self.seq = """MSNVRVSNGSPSLERMDARQAEHPKPSACRNLFGPVDHEELTRDLEKHCRDMEEASQRKW
NFDFQNHKPLEGKYEWQEVEKGSLPEFYYRPPRPPKGACKVPAQESQDVSGSRPAAPLIG
APANSEDTHLVDPKTDPSDSQTGLAEQCAGIRKRPATDDSSTQNKRANRTEENVSDGSPN
AGSVEQTPKKPGLRRRQT"""
        self.aa = "S2A"

    def test_feature_extraction(self):
        features = {}
        features.update(fe.get_length(self.seq, self.aa))
        features.update(fe.get_aaindex(self.seq, self.aa))
        features.update(fe.get_neighborhood_features(self.seq, self.aa))
        df_features = pd.DataFrame([features])
        self.log.debug("df_features = \n%s", df_features)
        self.log.debug("df_features[0] = \n%s", df_features.iloc[0])

    def test_get_all_features(self):
        features = fe.get_all_features(self.seq, self.aa)
        self.log.debug("all features = \n%s", features)

    def test_feature_selected(self):
        features = fe.get_all_features(self.seq, self.aa)
        ponsol = model.PonSol2()
        self.log.debug("feature1 = %s", ponsol.model.fs1)
        self.log.debug("feature2 = %s", ponsol.model.fs2)
        # self.log.debug("fs1 = %s", features.loc[:, ponsol.model.fs1.values], )
        # self.log.debug("fs2 = %s", features.loc[:, ponsol.model.fs2.values], )
        self.log.debug("check features: %s", ponsol.check_X(features))

    def test_predict_single_aa(self):
        features = fe.get_all_features(self.seq, self.aa)
        ponsol = model.PonSol2()
        p = ponsol.predict(features)
        self.log.debug("p = %s", p)
