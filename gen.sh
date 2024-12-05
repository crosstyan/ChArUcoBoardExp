SQUARE_MM=115
MARKER_MM=90
MARKER_SEP_MM=$(echo "scale=4; $SQUARE_MM - $MARKER_MM" | bc)

if [ $MARKER_SEP_MM -lt 0 ]; then
    echo "Marker size must be smaller than square size"
    exit 1
fi

SQUARE_SIZE=$(echo "scale=4; $SQUARE_MM / 1000" | bc)
MARKER_SIZE=$(echo "scale=4; $MARKER_MM / 1000" | bc)
MARKER_SEP=$(echo "scale=4; $MARKER_SEP_MM / 1000" | bc)

PAGE_PADDING_MM=10
PAGE_PADDING=$(echo "scale=4; $PAGE_PADDING_MM / 1000" | bc)

# A0
PAGE_WIDTH_MM=1189
PAGE_HEIGHT_MM=841

BOARD_WIDTH_IN_SQUARE=$(echo "scale=0; ($PAGE_WIDTH_MM - $PAGE_PADDING_MM) / $SQUARE_MM" | bc)
BOARD_HEIGHT_IN_SQUARE=$(echo "scale=0; ($PAGE_HEIGHT_MM - $PAGE_PADDING_MM) / $SQUARE_MM" | bc)
START_MARKER_ID=10

OUTPUT_FILENAME="charuco_${PAGE_WIDTH_MM}x${PAGE_HEIGHT_MM}_${BOARD_WIDTH_IN_SQUARE}x${BOARD_HEIGHT_IN_SQUARE}_s${SQUARE_MM}_m${MARKER_MM}.pdf"

# DICT_4X4_1000
# DICT_5X5_1000
# DICT_6X6_1000
# DICT_7X7_1000
# DICT_ARUCO_ORIGINAL
# DICT_APRILTAG_16h5
# DICT_APRILTAG_25h9
# DICT_APRILTAG_36h10
# DICT_APRILTAG_36h11

python MarkerPrinter.py --charuco \
    --file $OUTPUT_FILENAME \
    --dictionary DICT_4X4_1000 \
    --page_border_x $PAGE_PADDING \
    --page_border_y $PAGE_PADDING \
    --square_length $SQUARE_SIZE \
    --marker_length $MARKER_SIZE \
    --marker_separation $MARKER_SEP \
    --charuco_size_x $BOARD_WIDTH_IN_SQUARE \
    --charuco_size_y $BOARD_HEIGHT_IN_SQUARE \
    --first_marker $START_MARKER_ID 
