from enum import Enum


class VoucherType(str, Enum):
    INTERIOR_CLEAN = "interior_clean"
    EXTERIOR_CLEAN = "exterior_clean"
    SEAT_CLEAN = "seat_clean"
    FULL_CLEAN = "full_clean"
    FULL_CLEAN_WITH_SEAT_CLEAN = "full_clean_with_seat_clean"
