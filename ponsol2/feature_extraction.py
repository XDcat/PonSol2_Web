from collections import defaultdict

import pandas as pd
import os

import logging
from . import config, logconfig

logconfig.setup_logging()
log = logging.getLogger("ponsol.extract_feature")
# constant
a_list = ('A', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'V', 'W', 'Y')
aa_list = [i + j for i in a_list for j in a_list]
log.debug("aaindex path: %s", os.path.abspath(config.aa_index_path))
aaindex = pd.read_csv(config.aa_index_path, sep="\t", header=None, names=['name'] + aa_list, index_col='name')
aaindex = aaindex.T


def check_aa(seq, aa):
    seq = "".join(seq.split())
    aaf = aa[0]  # from
    aai = int(aa[1:-1])  # index
    aat = aa[-1]  # to
    log.info("seq = %s, aa = %s", seq, aa)
    if aaf not in a_list:
        raise RuntimeError("aa error, origin of aa is invalid.")
    if aat not in a_list:
        raise RuntimeError("aa error, nutation of aa is invalid.")
    if aai < 1 or aai > len(seq):
        raise RuntimeError("aa error, index of aa is invalid.")
    if seq[aai - 1] != aaf:
        raise RuntimeError("aa error, seq[index -1] = {}, but origin of aa = {}".format(seq[aai - 1], aaf))

    return seq, aaf, aat, aai


def get_aaindex(seq, aa):
    seq, aaf, aat, aai = check_aa(seq, aa)
    res = aaindex.loc["{}{}".format(aaf, aat), :]
    return res.to_dict()


def get_length(seq, aa):
    seq, aaf, aat, aai = check_aa(seq, aa)
    res = {"len.1": len(seq)}
    return res


def get_neighborhood_features(seq, aa):
    seq, aaf, aat, aai = check_aa(seq, aa)

    def find_win(seq, aai):
        # 确定边界
        index = aai - 1
        front = 0 if index - 11 < 0 else index - 11
        after = len(seq) if index + 12 > len(seq) - 1 else index + 12
        return seq[front: after]

    def get_count_a(win):
        """ count number of aa in windows"""
        a_dict = defaultdict(int)
        for i in win:
            a_dict[i] += 1  # 递增
        return {'AA20D.' + i: a_dict[i] for i in a_list}

    win = find_win(seq, aai)
    count_a = get_count_a(win)
    nei_feature = count_a
    # 1.NonPolarAA:Number of nonpolar neighborhood residues
    nei_feature['NonPolarAA'] = nei_feature['AA20D.' + a_list[0]] + nei_feature['AA20D.' + a_list[4]] + nei_feature[
        'AA20D.' + a_list[5]] + nei_feature['AA20D.' + a_list[7]] + nei_feature['AA20D.' + a_list[9]] + nei_feature[
                                    'AA20D.' + a_list[10]] + nei_feature['AA20D.' + a_list[12]] + nei_feature[
                                    'AA20D.' + a_list[17]] + nei_feature['AA20D.' + a_list[18]] + nei_feature[
                                    'AA20D.' + a_list[19]]
    # 2.PolarAA:Number of polar neighborhood residues
    nei_feature['PolarAA'] = nei_feature['AA20D.' + a_list[1]] + nei_feature['AA20D.' + a_list[11]] + nei_feature[
        'AA20D.' + a_list[13]] + nei_feature['AA20D.' + a_list[15]] + nei_feature['AA20D.' + a_list[16]]
    # 3.ChargedAA:Number of charged neighborhood residues
    nei_feature['ChargedAA'] = nei_feature['AA20D.' + a_list[2]] + nei_feature['AA20D.' + a_list[3]] + nei_feature[
        'AA20D.' + a_list[6]] + nei_feature['AA20D.' + a_list[8]] + nei_feature['AA20D.' + a_list[14]]
    # 4.PosAA:Number of Positive charged neighborhood residues
    nei_feature['PosAA'] = nei_feature['AA20D.' + a_list[2]] + nei_feature['AA20D.' + a_list[3]]
    # 5.NegAA:Number of Negative charged neighborhood residues
    nei_feature['NegAA'] = nei_feature['AA20D.' + a_list[6]] + nei_feature['AA20D.' + a_list[8]] + nei_feature[
        'AA20D.' + a_list[14]]
    return nei_feature


def get_feature_selected(seq, aa):
    pass


def get_all_features(seq, aa):
    features = {}
    features.update(get_length(seq, aa))
    features.update(get_aaindex(seq, aa))
    features.update(get_neighborhood_features(seq, aa))
    df_features = pd.DataFrame([features])
    return df_features
