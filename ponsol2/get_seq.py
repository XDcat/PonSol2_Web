import re
import traceback

import mygene
import requests

from . import logconfig
import logging

logconfig.setup_logging()
log = logging.getLogger("ponsol.get_seq")

a_list = ('A', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'V', 'W', 'Y')


def get_seq_by_id(ids, type):
    log.debug("id=%s, type=%s", ids, type)
    log.debug(f"ids={ids}, type={type}")
    if type == "gi":
        return get_seq_from_gi(ids)
    elif type == "ensembl id":
        return get_seq_from_ensembl(ids)
    elif type == "uniprot id":
        return get_seq_from_uniprot(ids)
    else:
        return None


def get_seq_from_ensembl(ensembl_id):
    """
    将 ensembl id 转化为 uniprot id, 然后通过 uniprot id 获取序列
    :param ensembl_id:
    :return:
    """
    mg = mygene.MyGeneInfo()
    xli = [ensembl_id, ]
    out = mg.querymany(xli, scopes="ensembl.gene", fields="uniprot", species="human")
    if (len(out) > 0) and ("uniprot" in out[0]) and ("Swiss-Prot" in out[0]["uniprot"]):
        out_swiss_prot = out[0]["uniprot"]["Swiss-Prot"]
        if isinstance(out_swiss_prot, str):
            return get_seq_from_uniprot(out_swiss_prot)
        elif isinstance(out_swiss_prot, list) and len(out_swiss_prot) > 0:
            return get_seq_from_uniprot(out_swiss_prot[0])
        else:
            raise RuntimeError("Can't translate ensembl id into uniprot id. ensembl id = {}".format(ensembl_id))
    else:
        raise RuntimeError("Can't translate ensembl id into uniprot id. ensembl id = {}".format(ensembl_id))


def get_seq_from_uniprot(uniprot_id):
    url = "https://www.uniprot.org/uniprot/{}.fasta".format(uniprot_id.upper())
    try:
        response = requests.get(url)
        faste = response.text
        name, seq = parse_faste(faste)
    except Exception as e:
        raise RuntimeError("Can't get seq by uniprot id. Please check id./n" + traceback.format_exc())
    return name, seq


def get_seq_from_gi(gi):
    """
    通过 genebank 获取序列
    :param gb_id: genebank id
    :return:
    """
    url = "https://www.ncbi.nlm.nih.gov/sviewer/viewer.fcgi?id={}&db=protein&report=fasta&retmode=text&withmarkup=on&tool=portal&log$=seqview&maxdownloadsize=1000000".format(
        gi.upper())
    try:
        response = requests.get(url)
        faste = response.text
        name, seq = parse_faste(faste)
    except Exception as e:
        raise RuntimeError("Can't get seq by gi. Please check id./n" + traceback.format_exc())
    return name, seq


def parse_faste(faste):
    lines = faste.strip().split("\n")
    name = lines[0]
    seq = "".join(lines[1:]).replace(" ", "").upper()
    # 检查序列和名称
    name_re = re.match(">.*", name)
    seq_re = True
    for i in seq:
        if i not in a_list:
            seq_re = False
            break
    if name_re and seq_re:
        return name, seq
    else:
        raise RuntimeError("Name or sequence of faste has error.\nname={}\nseq={}".format(name, seq))


if __name__ == '__main__':
    # print(get_seq_from_ensembl("ENSG00000214562"))
    print(get_seq_from_gi("213133708"))
