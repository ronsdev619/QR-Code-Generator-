import unittest
import pandas as pd
import os
from qr_analytics import QRLogger


class TestQRLogger(unittest.TestCase):
    """unit tests for QRLogger class"""
    
    def setUp(self):
        """Create test logger before each test"""
        self.test_file = "test_temp.csv"
        self.logger = QRLogger(filename=self.test_file)
    
    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
    
    def test_log_file_created(self):
        """Test that file created"""
        self.assertTrue(os.path.exists(self.test_file))
    
    def test_log_success(self):
        """Test logging a successful"""
        self.logger.log_attempt("Test", success=True)
        
        df = pd.read_csv(self.test_file)
        self.assertEqual(len(df), 1)
        self.assertTrue(df.iloc[0]['success'])
    
    def test_log_failure(self):
        """Test logging a failed"""
        self.logger.log_attempt("Failed", success=False)
        
        df = pd.read_csv(self.test_file)
        self.assertEqual(len(df), 1)
        self.assertFalse(df.iloc[0]['success'])
    
    def test_multiple_logs(self):
        """Test logging multiple attempts"""
        self.logger.log_attempt("Test 1", success=True)
        self.logger.log_attempt("Test 2", success=True)
        self.logger.log_attempt("Test 3", success=False)
        
        df = pd.read_csv(self.test_file)
        self.assertEqual(len(df), 3)
    
    def test_different_ecc_levels(self):
        """Test logging different ECC levels"""
        self.logger.log_attempt("Test", ecc="L", success=True)
        self.logger.log_attempt("Test", ecc="M", success=True)
        
        df = pd.read_csv(self.test_file)
        self.assertIn("L", df['ecc_level'].values)
        self.assertIn("M", df['ecc_level'].values)
    
    def test_get_stats_with_data(self):
        """Test statistics calculation"""
        self.logger.log_attempt("Test 1", success=True)
        self.logger.log_attempt("Test 2", success=True)
        self.logger.log_attempt("Test 3", success=True)
        self.logger.log_attempt("Test 4", success=False)
        
        stats = self.logger.get_stats()
        self.assertEqual(stats['total_attempts'], 4)
        self.assertEqual(stats['successful'], 3)
        self.assertEqual(stats['failed'], 1)
        self.assertEqual(stats['success_rate'], 75.0)
    
    def test_get_stats_empty(self):
        """Test statistics with no data"""
        self.logger.clear_logs()
        stats = self.logger.get_stats()
        self.assertIsNone(stats)
    
    def test_clear_logs(self):
        """Test clearing log data"""
        self.logger.log_attempt("Test", success=True)
    
        self.logger.clear_logs()
        
        df = pd.read_csv(self.test_file)
        self.assertTrue(df.empty)


def run_tests():
    import matplotlib
    matplotlib.use('Agg')
    
    # Run tests
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestQRLogger)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*50)
    print("TEST OUTPUT")
    print("="*50)
    print(f"Tests run: {result.testsRun}")
    print(f"Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failed: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n All tests passed")
    else:
        print("\n Some tests failed")
    
    print("="*50)
    
    return result


if __name__ == "__main__":
    run_tests()