"""
Unit tests for QR code generation system.
5 total tests
"""

import unittest
import numpy as np
from qr_encoder import QREncoder
from qr_matrix import QRMatrix
from qr_generator import generate_qr
import sys
import io


class SuppressOutput:
    """Context manager to suppress all output."""
    def __enter__(self):
        self._original_stdout = sys.stdout
        self._original_stderr = sys.stderr
        sys.stdout = io.StringIO()
        sys.stderr = io.StringIO()
        return self
    
    def __exit__(self, *args):
        sys.stdout = self._original_stdout
        sys.stderr = self._original_stderr


class TestQRSystem(unittest.TestCase):
    
    
    # Test 1
    def test_encoder_produces_26_codewords(self):
        """
        TEST 1: Verify encoder produces exactly 26 codewords (19 data + 7 ECC).
        Critical for Version 1, Level L compliance.
        """
        with SuppressOutput():
            encoder = QREncoder()
            result = encoder.process_input("known")
        
        # Check length
        self.assertEqual(len(result), 26, 
                        f"Expected 26 codewords, got {len(result)}")
        
        # reedsolo returns bytearray, not bytes - both are acceptable
        self.assertIn(type(result).__name__, ['bytes', 'bytearray'],
                     f"Expected bytes or bytearray, got {type(result)}")
    
    # Test 2
    def test_matrix_is_21x21_with_correct_structure(self):
        """
        TEST 2: Verify QR matrix has correct size and structure.
        Version 1 QR codes must be exactly 21×21 modules.
        """
        with SuppressOutput():
            matrix = QRMatrix()
            matrix.build_structure()
        
        # Check matrix size
        self.assertEqual(matrix.grid.shape, (21, 21))
        self.assertEqual(matrix.size, 21)
        
        # Verify finder patterns in corners
        self.assertEqual(matrix.grid[0, 0], 1)    # Top-left
        self.assertEqual(matrix.grid[0, 14], 1)   # Top-right  
        self.assertEqual(matrix.grid[14, 0], 1)   # Bottom-left
        
        # Verify dark module at (13, 8)
        self.assertEqual(matrix.grid[13, 8], 1)
    
    # Test 3
    def test_complete_qr_generation_produces_valid_output(self):
        """
        TEST 3: Integration test - complete QR generation returns valid array.
        Tests entire pipeline: encoding → matrix → masking → output.
        """
        with SuppressOutput():
            result = generate_qr("known")
        
        # Check output type and size
        self.assertIsInstance(result, np.ndarray)
        self.assertEqual(result.shape, (21, 21))
        
        # Check it contains both 0s and 1s (not blank)
        self.assertTrue(np.any(result == 0))
        self.assertTrue(np.any(result == 1))
        
        # Check only binary values (0 or 1)
        unique_values = np.unique(result)
        self.assertTrue(np.all(np.isin(unique_values, [0, 1])))
    
    # Test 4
    def test_different_inputs_produce_different_outputs(self):
        """
        TEST 4: Verify different inputs produce different QR codes.
        Ensures system actually encodes the input data.
        """
        with SuppressOutput():
            qr1 = generate_qr("test1")
            qr2 = generate_qr("test2")
            qr3 = generate_qr("test1")
        
        # Different inputs should produce different QR codes
        self.assertFalse(np.array_equal(qr1, qr2),
                        "Different inputs should produce different QR codes")
        
        # Same input should be deterministic (produce identical output)
        self.assertTrue(np.array_equal(qr1, qr3),
                       "Same input should produce identical QR codes")
    
    # Test 5
    def test_system_handles_various_inputs(self):
        """
        TEST 5: Verify system handles special characters and edge cases.
        Tests ISO-8859-1 encoding and different input lengths.
        """
        with SuppressOutput():
            # Test special characters (ISO-8859-1)
            special_result = generate_qr("café")
            self.assertEqual(special_result.shape, (21, 21))
            
            # Test empty string
            encoder = QREncoder()
            empty_result = encoder.process_input("")
            self.assertEqual(len(empty_result), 26)
            
            # Test maximum capacity (17 characters)
            max_result = generate_qr("A" * 17)
            self.assertEqual(max_result.shape, (21, 21))
            
            # Test single character
            single_result = generate_qr("A")
            self.assertEqual(single_result.shape, (21, 21))


if __name__ == "__main__":
    # Run tests 
    print("="*70)
    print("Running QR Code System Tests")
    print("="*70)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestQRSystem)
    
    # Run with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✓ ALL TESTS PASSED!")
    else:
        print("\n✗ SOME TESTS FAILED")
    
    print("="*70)