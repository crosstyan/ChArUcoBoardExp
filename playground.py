# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.17.0
#   kernelspec:
#     language: python
#     name: python3
# ---


# %%
import awkward as ak
from pathlib import Path
import numpy as np
from IPython.display import display
from typing import TypedDict
from jaxtyping import Int, Num

NDArray = np.ndarray


# %%
class MarkerFace(TypedDict):
    """
    for diamond ArUco markers, N is 4
    """

    name: str
    """
    a label for the face
    """
    ids: Int[NDArray, "N"]
    """
    ArUco marker ids
    """
    corners: Num[NDArray, "N 4 3"]
    """
    Corner coordinates in 3D of rectangle,
    relative to the world origin
    """


# %%
# OBJECT_POINTS_PARQUET = Path("output") / "object_points.parquet"
OBJECT_POINTS_PARQUET = Path("output") / "standard_box_markers.parquet"
ops = ak.from_parquet(OBJECT_POINTS_PARQUET)
display(ops)

# %%
