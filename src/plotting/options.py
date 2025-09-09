#!/usr/bin/env python3
# -*- coding: utf-8; fill-column: 80; -*-
#
"""Customizations for matlplotlib figures.
"""


# Default figure dimensions.
FIG_W, FIG_H = (5.0, 3.0)


def get_basic_conf(sz=20):
    return {
        "axes.edgecolor": "#202020",
        "axes.labelsize": sz - 4,
        "axes.linewidth": 1.5,
        "axes.titlesize": sz - 4,
        "axes.spines.right": False,
        "axes.spines.top": False,
        "font.family": "sans-serif",
        # 'font.sans-serif'      : 'Clear Sans',
        "font.size": sz,
        "legend.borderpad": 0.1,
        "legend.columnspacing": 0.5,
        "legend.fontsize": int(0.75 * sz),
        "legend.frameon": True,
        "legend.handlelength": 0.85,
        "legend.handletextpad": 0.2,
        "legend.labelspacing": 0.2,
        "xtick.color": "#404040",
        "xtick.direction": "out",
        "xtick.labelsize": sz - 6,
        "xtick.labelcolor": "#808080",
        "xtick.major.pad": 4,
        "xtick.major.size": 10,
        "xtick.major.width": 1.5,
        "xtick.minor.pad": 2,
        "xtick.minor.size": 6,
        "xtick.minor.width": 1.5,
        "ytick.color": "#404040",
        "ytick.direction": "out",
        "ytick.labelsize": sz - 6,
        "ytick.labelcolor": "#808080",
        "ytick.major.pad": 4,
        "ytick.major.size": 10,
        "ytick.major.width": 1.5,
        "ytick.minor.pad": 2,
        "ytick.minor.size": 6,
        "ytick.minor.width": 1.5,
        # matplotlib uses Type 3 font in PDF outputs by default, which
        # results in small PDFs, but they can not be edited by a PDF editor
        # such as Adobe Acrobat Pro.
        # The following statement, however, forces it to use Type 42 fonts.
        "pdf.fonttype": 42,
    }
