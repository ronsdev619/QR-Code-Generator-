from reedsolo import RSCodec


class QREncoder:
    """converts text input to QR codewords"""
    
    def __init__(self):
        self.version = 1
        self.data_capacity = 19  # bytes for Version 1, Level L
        self.ecc_capacity = 7    # ECC bytes
        
    def process_input(self, text):
        """
        Convert input text to final codewords with ECC.
        Args:
            text: String to encode (ISO-8859-1)
        Returns:
            bytes: Complete codeword sequence (data + ECC)
        """
        print(f"Processing: '{text}'")
        
        # build the bit stream
        bits = self._build_bit_stream(text)
        
        # convert to bytes
        data_bytes = self._bits_to_bytes(bits)
        
        # add Reed-Solomon ECC
        final_codewords = self._add_ecc(data_bytes)
        
        return final_codewords
    
    def _build_bit_stream(self, text):
        print("-" * 50)
        print("1. bit stream")

        # Mode: Byte = 0100
        # Character count (8 bits for Version 1)

        mode = '0100'
        byte_array = text.encode('iso-8859-1')

        # Mode indicator (4 bits) + character count (8 bits) leave
        # data_capacity - 2 bytes for the payload itself.
        max_bytes = self.data_capacity - 2
        if len(byte_array) > max_bytes:
            raise ValueError(
                f"Input is {len(byte_array)} bytes; version {self.version} "
                f"level L holds at most {max_bytes} in byte mode."
            )

        count = format(len(byte_array), '08b')

        print(f"Mode indicator (Byte): {mode}")
        # Character count (8 bits for Version 1)
        print(f"Character count: {len(byte_array)} -> {count}")
        
        # Data bits
        data = ''.join(format(b, '08b') for b in byte_array)

        print(f"Data encoding: {len(byte_array)} bytes -> {len(data)} bits")

        for i, byte in enumerate(byte_array):
            char_repr = chr(byte) if 32 <= byte < 127 else '?'
            print(f"  Byte {i+1}: {char_repr} = 0x{byte:02X} = {format(byte, '08b')}")
        
        # Combine
        stream = mode + count + data

        # Terminator
        capacity_bits = self.data_capacity * 8
        term_len = max(0, min(4, capacity_bits - len(stream)))
        stream += '0' * term_len

        # Byte boundary padding
        remainder = len(stream) % 8
        if remainder:
            pad = 8 - remainder
            stream += '0' * pad
        
        # Padding bytes pattern
        padding_pattern = ['11101100', '00010001']
        idx = 0
        while len(stream) < capacity_bits:
            stream += padding_pattern[idx % 2]
            idx += 1
        return stream
    
    def _bits_to_bytes(self, bit_string):
        
        """convert bit string to byte array."""
        print("-" * 50)
        print("2. Converting to byte array")
        
        bytes_list = []
        for i in range(0, len(bit_string), 8):
            byte_val = int(bit_string[i:i+8], 2)
            bytes_list.append(byte_val)
        
        print(f"Data codewords ({len(bytes_list)} bytes):")
        print(f"Dec: {bytes_list}")
        
        return bytes(bytes_list)
    
    def _add_ecc(self, data):
        """Reed-Solomon error correction."""
        print("-" * 50)
        print("3. ECC")
        
        rs_encoder = RSCodec(self.ecc_capacity)
        full_data = rs_encoder.encode(data)
        
        ecc_bytes = full_data[self.data_capacity:]
        print(f"ECC codewords ({len(ecc_bytes)} bytes): {list(ecc_bytes)}")
        print(f"Total codewords: {len(full_data)} codewords")
        
        return full_data