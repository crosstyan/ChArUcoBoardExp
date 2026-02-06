#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = [
#   "numpy",
#   "opencv-python",
#   "trimesh",
#   "awkward",
#   "orjson",
#   "click",
# ]
# ///

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

import awkward as ak
import click
import cv2
import numpy as np
import orjson
import trimesh
from cv2 import aruco
from numpy.typing import NDArray


@dataclass
class Marker:
    id: int
    center: NDArray[np.float64]
    corners: NDArray[np.float64]


def normalize_point(
    point: NDArray[Any], width: int, height: int
) -> NDArray[np.float64]:
    return cast(
        NDArray[np.float64], point / np.array([width, height], dtype=np.float64)
    )


def flip_y(point: NDArray[Any], y_max: float = 1.0) -> NDArray[np.float64]:
    return np.array([point[0], y_max - point[1]], dtype=np.float64)


def detect_markers_as_uv(
    input_image: Path,
    dictionary: int,
) -> list[Marker]:
    frame = cv2.imread(str(input_image))
    if frame is None:
        raise FileNotFoundError(f"Failed to read image: {input_image}")

    detector = aruco.ArucoDetector(
        dictionary=aruco.getPredefinedDictionary(dictionary),
        detectorParams=aruco.DetectorParameters(),
    )
    grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    markers, ids, _ = detector.detectMarkers(grey)
    if ids is None:
        return []

    markers = np.reshape(markers, (-1, 4, 2))
    ids = np.reshape(ids, (-1, 1))
    image_width = frame.shape[1]
    image_height = frame.shape[0]

    output_markers: list[Marker] = []
    for m, marker_id in zip(markers, ids):
        center = np.mean(m, axis=0)
        output_markers.append(
            Marker(
                id=int(marker_id[0]),
                center=flip_y(normalize_point(center, image_width, image_height)),
                corners=np.array(
                    [
                        flip_y(normalize_point(corner, image_width, image_height))
                        for corner in m
                    ],
                    dtype=np.float64,
                ),
            )
        )

    return output_markers


def interpolate_uvs_to_3d(
    uv_points: NDArray[np.float64],
    vertices: NDArray[np.float64],
    uvs: NDArray[np.float64],
    faces: NDArray[np.int64],
    epsilon: float = 1e-6,
) -> NDArray[np.float64]:
    results = np.full((uv_points.shape[0], 3), np.nan, dtype=np.float64)
    for point_index, uv_point in enumerate(uv_points):
        for face in faces:
            uv_tri = uvs[face]
            v_tri = vertices[face]
            matrix = np.array(
                [
                    [uv_tri[0, 0] - uv_tri[2, 0], uv_tri[1, 0] - uv_tri[2, 0]],
                    [uv_tri[0, 1] - uv_tri[2, 1], uv_tri[1, 1] - uv_tri[2, 1]],
                ],
                dtype=np.float64,
            )
            rhs = uv_point - uv_tri[2]
            try:
                w0, w1 = np.linalg.solve(matrix, rhs)
            except np.linalg.LinAlgError:
                continue
            w2 = 1.0 - w0 - w1
            if min(w0, w1, w2) >= -epsilon:
                results[point_index] = w0 * v_tri[0] + w1 * v_tri[1] + w2 * v_tri[2]
                break
    return results


def interpolate_uvs_to_3d_trimesh(
    uv_points: NDArray[np.float64],
    mesh: trimesh.Trimesh,
    epsilon: float = 1e-6,
) -> NDArray[np.float64]:
    if mesh.visual is None:
        raise ValueError("Mesh has no visual")
    uv_data = cast(Any, mesh.visual).uv
    if uv_data is None:
        raise ValueError("Mesh has no UV")
    return interpolate_uvs_to_3d(
        uv_points=uv_points,
        vertices=cast(NDArray[np.float64], mesh.vertices),
        uvs=cast(NDArray[np.float64], uv_data),
        faces=cast(NDArray[np.int64], mesh.faces),
        epsilon=epsilon,
    )


def scale_mesh_for_box_size_mm(
    mesh: trimesh.Trimesh,
    box_size_mm: float,
    unit_box_side: float = 2.0,
) -> trimesh.Trimesh:
    if box_size_mm <= 0:
        raise ValueError("box_size_mm must be positive")
    if unit_box_side <= 0:
        raise ValueError("unit_box_side must be positive")

    scale = (box_size_mm / 1000.0) / unit_box_side
    scaled = mesh.copy()
    scaled.vertices = cast(NDArray[np.float64], scaled.vertices * scale)
    return scaled


def marker_to_3d_coords(marker: Marker, mesh: trimesh.Trimesh) -> NDArray[np.float64]:
    return interpolate_uvs_to_3d_trimesh(marker.corners, mesh)


def parse_dictionary(value: str) -> int:
    if not hasattr(aruco, value):
        raise ValueError(f"Unknown aruco dictionary name: {value}")
    return int(getattr(aruco, value))


@click.command(
    help="Convert draw_uv marker detections into 3D object points with real-world box sizing"
)
@click.option(
    "--input-image",
    type=click.Path(path_type=Path),
    default=Path("merged_uv_layout.png"),
    show_default=True,
)
@click.option(
    "--mesh",
    type=click.Path(path_type=Path),
    default=Path("sample/standard_box.glb"),
    show_default=True,
)
@click.option(
    "--dictionary", type=str, default="DICT_APRILTAG_36H11", show_default=True
)
@click.option("--box-size-mm", type=float, default=600.0, show_default=True)
@click.option("--unit-box-side", type=float, default=2.0, show_default=True)
@click.option(
    "--output-json",
    type=click.Path(path_type=Path),
    default=Path("output/aruco_2d_uv_coords_normalized.json"),
    show_default=True,
)
@click.option(
    "--output-parquet",
    type=click.Path(path_type=Path),
    default=Path("output/standard_box_markers.parquet"),
    show_default=True,
)
def main(
    input_image: Path,
    mesh: Path,
    dictionary: str,
    box_size_mm: float,
    unit_box_side: float,
    output_json: Path,
    output_parquet: Path,
) -> None:
    dictionary_value = parse_dictionary(dictionary)
    output_markers = detect_markers_as_uv(input_image, dictionary_value)

    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_bytes(
        orjson.dumps(output_markers, option=orjson.OPT_SERIALIZE_NUMPY)
    )

    loaded = trimesh.load_mesh(mesh)
    if isinstance(loaded, trimesh.Scene):
        if not loaded.geometry:
            raise ValueError("Scene has no geometry")
        mesh = list(loaded.geometry.values())[0]
    else:
        mesh = loaded
    if not isinstance(mesh, trimesh.Trimesh):
        raise TypeError("Expected Trimesh or Scene with Trimesh geometry")

    mesh = scale_mesh_for_box_size_mm(mesh, box_size_mm, unit_box_side)
    id_to_3d_coords = {
        marker.id: marker_to_3d_coords(marker, mesh) for marker in output_markers
    }

    face_to_ids = {
        "bottom": [21],
        "back": [22],
        "top": [23],
        "front": [24],
        "right": [26],
        "left": [25],
    }
    rows: list[dict[str, Any]] = []
    for name, marker_ids in face_to_ids.items():
        corners = np.array([id_to_3d_coords[marker_id] for marker_id in marker_ids])
        rows.append(
            {
                "name": name,
                "ids": np.array(marker_ids),
                "corners": corners,
            }
        )

    output_parquet.parent.mkdir(parents=True, exist_ok=True)
    ak.to_parquet(rows, str(output_parquet))


if __name__ == "__main__":
    main()
