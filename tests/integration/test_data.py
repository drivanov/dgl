import gzip
import io
import os
import tarfile
import tempfile
import unittest

import backend as F

import dgl
import dgl.data as data
import numpy as np
import pandas as pd
import pytest
import yaml
from dgl import DGLError


@unittest.skipIf(
    F._default_context_str == "gpu",
    reason="Datasets don't need to be tested on GPU.",
)
@unittest.skipIf(dgl.backend.backend_name == "mxnet", reason="Skip MXNet")
def test_reddit():
    # RedditDataset
    g = data.RedditDataset()[0]
    assert g.num_nodes() == 232965
    assert g.num_edges() == 114615892
    dst = F.asnumpy(g.edges()[1])
    assert np.array_equal(dst, np.sort(dst))

    transform = dgl.AddSelfLoop(allow_duplicate=True)
    g2 = data.RedditDataset(transform=transform)[0]
    assert g2.num_edges() - g.num_edges() == g.num_nodes()


@unittest.skipIf(
    F._default_context_str == "gpu",
    reason="Datasets don't need to be tested on GPU.",
)
@unittest.skipIf(dgl.backend.backend_name == "mxnet", reason="Skip MXNet")
def test_fakenews():
    transform = dgl.AddSelfLoop(allow_duplicate=True)

    ds = data.FakeNewsDataset("politifact", "bert")
    assert len(ds) == 314
    g = ds[0][0]
    g2 = data.FakeNewsDataset("politifact", "bert", transform=transform)[0][0]
    assert g2.num_edges() - g.num_edges() == g.num_nodes()

    ds = data.FakeNewsDataset("gossipcop", "profile")
    assert len(ds) == 5464
    g = ds[0][0]
    g2 = data.FakeNewsDataset("gossipcop", "profile", transform=transform)[0][0]
    assert g2.num_edges() - g.num_edges() == g.num_nodes()


@unittest.skipIf(
    F._default_context_str == "gpu",
    reason="Datasets don't need to be tested on GPU.",
)
@unittest.skipIf(dgl.backend.backend_name == "mxnet", reason="Skip MXNet")
def test_as_graphpred():
    ds = data.GINDataset(name="MUTAG", self_loop=True)
    new_ds = data.AsGraphPredDataset(ds, [0.8, 0.1, 0.1], verbose=True)
    assert len(new_ds) == 188
    assert new_ds.num_tasks == 1
    assert new_ds.num_classes == 2

    ds = data.FakeNewsDataset("politifact", "profile")
    new_ds = data.AsGraphPredDataset(ds, verbose=True)
    assert len(new_ds) == 314
    assert new_ds.num_tasks == 1
    assert new_ds.num_classes == 2

    ds = data.QM7bDataset()
    new_ds = data.AsGraphPredDataset(ds, [0.8, 0.1, 0.1], verbose=True)
    assert len(new_ds) == 7211
    assert new_ds.num_tasks == 14
    assert new_ds.num_classes is None

    ds = data.QM9Dataset(label_keys=["mu", "gap"])
    new_ds = data.AsGraphPredDataset(ds, [0.8, 0.1, 0.1], verbose=True)
    assert len(new_ds) == 130831
    assert new_ds.num_tasks == 2
    assert new_ds.num_classes is None

    ds = data.QM9EdgeDataset(label_keys=["mu", "alpha"])
    new_ds = data.AsGraphPredDataset(ds, [0.8, 0.1, 0.1], verbose=True)
    assert len(new_ds) == 130831
    assert new_ds.num_tasks == 2
    assert new_ds.num_classes is None

    ds = data.TUDataset("DD")
    new_ds = data.AsGraphPredDataset(ds, [0.8, 0.1, 0.1], verbose=True)
    assert len(new_ds) == 1178
    assert new_ds.num_tasks == 1
    assert new_ds.num_classes == 2

    ds = data.LegacyTUDataset("DD")
    new_ds = data.AsGraphPredDataset(ds, [0.8, 0.1, 0.1], verbose=True)
    assert len(new_ds) == 1178
    assert new_ds.num_tasks == 1
    assert new_ds.num_classes == 2

    ds = data.BA2MotifDataset()
    new_ds = data.AsGraphPredDataset(ds, [0.8, 0.1, 0.1], verbose=True)
    assert len(new_ds) == 1000
    assert new_ds.num_tasks == 1
    assert new_ds.num_classes == 2
