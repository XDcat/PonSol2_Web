# -*- coding:utf-8 -*-
'''
__author__ = 'XD'
__mtime__ = 2021/1/23
__project__ = Pon-Sol2
Fix the Problem, Not the Blame.
'''

import model
import logging
import logconfig
from unittest import TestCase

logconfig.setup_logging()
log = logging.getLogger("ponsol.test_model")


class TestModel(TestCase):
    def setUp(self) -> None:
        self.seq = """MSNVRVSNGSPSLERMDARQAEHPKPSACRNLFGPVDHEELTRDLEKHCRDMEEASQRKW
        NFDFQNHKPLEGKYEWQEVEKGSLPEFYYRPPRPPKGACKVPAQESQDVSGSRPAAPLIG
        APANSEDTHLVDPKTDPSDSQTGLAEQCAGIRKRPATDDSSTQNKRANRTEENVSDGSPN
        AGSVEQTPKKPGLRRRQT"""
        self.aa = "S2A"
        self.model = model.PonSol2()

    def test_predict(self):
        pred = self.model.predict(self.seq, self.aa)
        log.debug("pred = %s", pred)
