import numpy as np
from reedsolo import RSCodec
from qr_matrix import QRMatrix, MASK_FORMULAS


def unmask_data(grid, mask_map, pattern=0):
    """
    Reverse the mask pattern applied to the data modules.
    """
    condition = MASK_FORMULAS[pattern]
    unmasked = grid.copy()
    for r in range(21):
        for c in range(21):
            if not mask_map[r, c]:
                if condition(r, c):
                    unmasked[r, c] ^= 1
    return unmasked


def extract_data_bits(grid, mask_map):
    """
    Extract data bits using QR zig-zag traversal (Version 1).
    """
    bits = []
    col = 20
    upward = True

    while col >= 0:
        if col == 6:
            col -= 1
            continue

        rows = range(20, -1, -1) if upward else range(21)

        for r in rows:
            for c in [col, col - 1]:
                if not mask_map[r, c]:
                    bits.append(grid[r, c])

        upward = not upward
        col -= 2

    return bits


def bits_to_codewords(bits):
    """
    Convert bit stream into 8-bit codewords.
    """
    codewords = []
    for i in range(0, len(bits), 8):
        byte = bits[i:i + 8]
        if len(byte) == 8:
            codewords.append(int("".join(map(str, byte)), 2))
    return codewords


def decode_codewords(codewords):
    """
    Apply Reed–Solomon error correction (Version 1-L → 7 ECC bytes).
    """
    rs = RSCodec(7)
    decoded, _, _ = rs.decode(bytes(codewords))
    return list(decoded)


def decode_byte_mode(data_bytes):
    """
    Decode QR byte-mode payload into text.

    The stream is 4 mode bits + an 8-bit character count + the payload, so
    every payload byte straddles two codewords and has to be reassembled
    from the low nibble of one and the high nibble of the next.
    """
    mode = data_bytes[0] >> 4
    if mode != 0b0100:
        raise ValueError(f"Expected byte mode (0100), got {mode:04b}")

    length = ((data_bytes[0] & 0x0F) << 4) | (data_bytes[1] >> 4)
    if length + 2 > len(data_bytes):
        raise ValueError(
            f"Declared length {length} exceeds the {len(data_bytes) - 2} "
            f"payload bytes available"
        )

    payload = bytes(
        ((data_bytes[i + 1] & 0x0F) << 4) | (data_bytes[i + 2] >> 4)
        for i in range(length)
    )
    return payload.decode("latin-1")


def decode_qr_matrix(matrix_array):
    """
    Fully decode a QR code matrix into its original text.
    """
    matrix = QRMatrix()
    matrix.grid = matrix_array.copy()
    matrix.build_structure()  # rebuilds mask_map

    unmasked = unmask_data(matrix.grid, matrix.mask_map)
    bits = extract_data_bits(unmasked, matrix.mask_map)
    codewords = bits_to_codewords(bits)
    decoded_bytes = decode_codewords(codewords)

    return decode_byte_mode(decoded_bytes)
