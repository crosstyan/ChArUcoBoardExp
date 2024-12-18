from dataclasses import dataclass

# Order of detection result
# 0,   1,     2,    3
# TL,  TR,    BR,   BL
# RED, GREEN, BLUE, YELLOW


@dataclass
class DiamondBoardParameter:
    marker_leghth: float
    """
    the ArUco marker length in meter
    """
    chess_length: float
    """
    the length of the chess board in meter
    """
    border_length: float = 0.01
    """
    border_length in m, default is 1cm
    """

    @property
    def marker_border_length(self):
        assert self.chess_length > self.marker_leghth
        return (self.chess_length - self.marker_leghth) / 2

    @property
    def total_side_length(self):
        assert self.chess_length > self.marker_leghth
        return self.marker_border_length * 2 + self.chess_length * 3


# 9mm + 127mm + 127mm (97mm marker) + 127mm + 10mm
# i.e. marker boarder = 127mm - 97mm = 30mm (15mm each side)
Point2D = tuple[float, float]
Quad2D = tuple[Point2D, Point2D, Point2D, Point2D]


@dataclass
class ArUcoMarker:
    id: int
    corners: Quad2D


# let's let TL be the origin
def generate_diamond_corners(
    ids: tuple[int, int, int, int], params: DiamondBoardParameter
):
    """
    A diamond chess board, which could be count as a kind of ChArUco board

    C | 0 | C
    ---------
    1 | C | 2
    ---------
    C | 3 | C

    where C is the chess box, and 0, 1, 2, 3 are the markers (whose ids are passed in order)

    Args:
        ids: a tuple of 4 ids of the markers
        params: DiamondBoardParameter
    """

    def tl_to_square(tl_x: float, tl_y: float, side_length: float) -> Quad2D:
        return (
            (tl_x, tl_y),
            (tl_x + side_length, tl_y),
            (tl_x + side_length, tl_y + side_length),
            (tl_x, tl_y + side_length),
        )

    tl_0_x = params.border_length + params.chess_length + params.marker_border_length
    tl_0_y = params.border_length + params.marker_border_length

    tl_1_x = params.border_length + params.marker_border_length
    tl_1_y = params.border_length + params.chess_length + params.marker_border_length

    tl_2_x = (
        params.border_length + params.chess_length * 2 + params.marker_border_length
    )
    tl_2_y = tl_1_y

    tl_3_x = params.border_length + params.chess_length + params.marker_border_length
    tl_3_y = (
        params.border_length + params.chess_length * 2 + params.marker_border_length
    )
    return (
        ArUcoMarker(ids[0], tl_to_square(tl_0_x, tl_0_y, params.marker_leghth)),
        ArUcoMarker(ids[1], tl_to_square(tl_1_x, tl_1_y, params.marker_leghth)),
        ArUcoMarker(ids[2], tl_to_square(tl_2_x, tl_2_y, params.marker_leghth)),
        ArUcoMarker(ids[3], tl_to_square(tl_3_x, tl_3_y, params.marker_leghth)),
    )
