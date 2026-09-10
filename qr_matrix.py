import numpy as np


# Mask pattern condition for each of the eight standard patterns.
# A module is flipped where the condition is True (ISO/IEC 18004 Table 10).
MASK_FORMULAS = [
    lambda r, c: (r + c) % 2 == 0,
    lambda r, c: r % 2 == 0,
    lambda r, c: c % 3 == 0,
    lambda r, c: (r + c) % 3 == 0,
    lambda r, c: (r // 2 + c // 3) % 2 == 0,
    lambda r, c: (r * c) % 2 + (r * c) % 3 == 0,
    lambda r, c: ((r * c) % 2 + (r * c) % 3) % 2 == 0,
    lambda r, c: ((r + c) % 2 + (r * c) % 3) % 2 == 0,
]

# Pre-computed BCH(15,5) format strings for ECC level L, masks 0-7.
FORMAT_STRINGS_L = [
    '111011111000100',
    '111001011110011',
    '111110110101010',
    '111100010011101',
    '110011000101111',
    '110001100011000',
    '110110001000001',
    '110100101110110',
]


class QRMatrix:
    """2D QR code matrix structure."""
    
    def __init__(self):
        self.size = 21  # Version 1
        self.grid = np.zeros((self.size, self.size), dtype=int)
        self.mask_map = np.zeros((self.size, self.size), dtype=bool)
        self.unmasked_grid = None
        self.mask = 0
        
    def build_structure(self):
        """Add all fixed patterns to the matrix."""
        print("-" * 50)
        print("4. Building matrix structure")

        self._add_finders()
        self._add_separators()
        self._add_timing()
        self._add_dark()
        self._mark_format_zones()
        
        print("Pattern placement done")
    
    def _add_finders(self):
        """Add three 7x7 finder patterns in corners."""
        # 7x7 finder pattern
        pattern = np.array([
            [1,1,1,1,1,1,1],
            [1,0,0,0,0,0,1],
            [1,0,1,1,1,0,1],
            [1,0,1,1,1,0,1],
            [1,0,1,1,1,0,1],
            [1,0,0,0,0,0,1],
            [1,1,1,1,1,1,1]
        ])
        
        # place in three corners
        positions = [(0, 0), (0, 14), (14, 0)]
        for r, c in positions:
            self.grid[r:r+7, c:c+7] = pattern
            self.mask_map[r:r+7, c:c+7] = True
        
        print("Finder patterns")
    
    def _add_separators(self):
        """Add white separator borders around finders."""
        # top-left
        self.grid[7, :8] = 0
        self.grid[:8, 7] = 0
        self.mask_map[7, :8] = True
        self.mask_map[:8, 7] = True
        
        # Top-right
        self.grid[7, 13:] = 0
        self.grid[:8, 13] = 0
        self.mask_map[7, 13:] = True
        self.mask_map[:8, 13] = True
        
        # Bottom-left
        self.grid[13, :8] = 0
        self.grid[13:, 7] = 0
        self.mask_map[13, :8] = True
        self.mask_map[13:, 7] = True
        
        print("Separators")
    
    def _add_timing(self):
        """Add alternating timing patterns."""
        for pos in range(8, 13):
            val = (pos + 1) % 2
            self.grid[6, pos] = val
            self.grid[pos, 6] = val
            self.mask_map[6, pos] = True
            self.mask_map[pos, 6] = True
        
        print("Timing patterns")
    
    def _add_dark(self):
        """Add the mandatory dark module at (13, 8)."""
        self.grid[13, 8] = 1
        self.mask_map[13, 8] = True
        print("Dark module")
    
    def _mark_format_zones(self):
        """Mark format information zones as protected."""
        # Around top-left
        for i in range(9):
            self.mask_map[8, i] = True
            self.mask_map[i, 8] = True
        
        # Top-right and bottom-left
        self.mask_map[8, 13:] = True
        self.mask_map[13:, 8] = True
        
        print("Format zones reserved")
    
    def fill_data(self, codewords):

        print("-" * 50)
        print("5. Filling data modules")
        
        # Convert to bit string
        all_bits = ''.join(f'{b:08b}' for b in codewords)
        bit_idx = 0
        
        # placement from right to left
        column = self.size - 1
        moving_up = True
        
        while column >= 0:
            # Skip timing column
            if column == 6:
                column -= 1
                continue
            
            # Process two-column strip
            start_row = self.size - 1 if moving_up else 0
            step = -1 if moving_up else 1
            
            for row_offset in range(self.size):
                current_row = start_row + (row_offset * step)
                
                # Right column
                if not self.mask_map[current_row, column] and bit_idx < len(all_bits):
                    self.grid[current_row, column] = int(all_bits[bit_idx])
                    bit_idx += 1
                
                # Left column
                if not self.mask_map[current_row, column-1] and bit_idx < len(all_bits):
                    self.grid[current_row, column-1] = int(all_bits[bit_idx])
                    bit_idx += 1
            
            # Next pair
            column -= 2
            moving_up = not moving_up
        
        print(f"Data placed: {bit_idx} bits")
    
    def apply_mask(self, pattern=0):
        """
        Apply mask pattern to data modules.

        Args:
            pattern: Mask pattern number 0-7 (default 0)
        """
        if not 0 <= pattern <= 7:
            raise ValueError(f"Mask pattern must be 0-7, got {pattern}")

        print("-" * 50)
        print("6. Applying mask")

        # Remember which pattern was used so the format info matches
        self.mask = pattern
        condition = MASK_FORMULAS[pattern]

        # Before Masking
        self.unmasked_grid = self.grid.copy()

        print("Grid (before masking):")
        print(np.array2string(self.unmasked_grid,
                            formatter={'int': lambda x: str(int(x))},
                            separator=' '))
        # Generate before masking
        mask_pattern = np.zeros((self.size, self.size), dtype=int)
        for r in range(self.size):
            for c in range(self.size):
                if condition(r, c):
                    mask_pattern[r, c] = 1
        
        print(f"Mask pattern {pattern}:")
        print(np.array2string(mask_pattern,
                            formatter = {'int': lambda x: str(int(x))},
                            separator=' '))
        
        # Masking
        count = 0
        for r in range(self.size):
            for c in range(self.size):
                if not self.mask_map[r, c]:
                    if condition(r, c):
                        self.grid[r, c] ^= 1
                        count += 1
        print(f"Modules masked: {count}")

    def add_format_info(self):
        """format information string to the matrix."""
        print("-" * 50)
        print("7. Configuration")
        
        # ECC Level L + the mask pattern that was actually applied
        format_str = FORMAT_STRINGS_L[self.mask]
        print(f"version: 1, ECC level: L, Mask: {self.mask}")
        
        # top-left area positions
        tl_pos = [
            (8,0), (8,1), (8,2), (8,3), (8,4), (8,5),
            (8,7), (8,8), (7,8), (5,8), (4,8), (3,8),
            (2,8), (1,8), (0,8)
        ]
        
        for idx, (r, c) in enumerate(tl_pos):
            self.grid[r, c] = int(format_str[idx])
        
        # replicate to other locations (bottom-left & top-right).
        # format_str[0] is the MSB (bit 14), which sits at (20,8) and runs
        # upward, then continues left-to-right from (8,13) to (8,20).
        other_pos = [
            (20,8), (19,8), (18,8), (17,8), (16,8), (15,8), (14,8),
            (8,13), (8,14), (8,15), (8,16), (8,17), (8,18), (8,19), (8,20)
        ]
        
        for idx, (r, c) in enumerate(other_pos):
            self.grid[r, c] = int(format_str[idx])

        print("Final grid (with masking):")
        print(" " + np.array2string(self.grid,
                                    formatter={'int': lambda x: str(int(x))},
                                    separator=' '))

    def render(self):
        """
        create QR code as text.
        """
        lines = []
        for row in self.grid:
            lines.append(''.join('██' if v == 1 else '  ' for v in row))
        return '\n'.join(lines)
    
    def get_array(self):
        """
        get the matrix as numpy array.
        """
        return self.grid.copy()