import pandas as pd
import matplotlib.pyplot as plt
import uuid
from datetime import datetime
import os


class QRLogger:
    """Handles data logging and analytics for QR code generation"""
    
    def __init__(self, filename="qr_app_log.csv"):
        """Initialize the logger"""
        self.filename = filename
        self._init_log_file()
    
    def _init_log_file(self):
        """Initialize the CSV file with headers if it doesn't exist."""
        if not os.path.exists(self.filename):
            df = pd.DataFrame(columns=[
                "timestamp", 
                "unique_id", 
                "text_content", 
                "text_length",
                "version", 
                "ecc_level", 
                "mask_pattern", 
                "success"
            ])
            df.to_csv(self.filename, index=False)
            print(f"[Logger] Created new log file: {self.filename}")
    
    def log_attempt(self, text, version=1, ecc="L", mask=0, success=True):
        """
        Log a QR code generation attempt
        
        Records timestamp, unique ID, input parameters, and success status
        to persistent CSV storage using pandas.
        
        Args:
            text: The user input text to encode
            version: QR code version (1)
            ecc: error correction level - L, M, Q, or H (L)
            mask: mask pattern applied 0-7 (0)
            success: Whether generation succeeded (True)
        
        Returns:
            str: Unique 8-character ID assigned to this attempt
        """
        # unique identifier
        unique_id = str(uuid.uuid4())[:8]
        
        # log entry
        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "unique_id": unique_id,
            "text_content": text[:50],
            "text_length": len(text),
            "version": version,
            "ecc_level": ecc,
            "mask_pattern": mask,
            "success": success
        }
        
        df = pd.DataFrame([entry])
        df.to_csv(self.filename, mode='a', header=False, index=False)
        
        print(f"[Logger] recorded transaction ID: {unique_id}")
        return unique_id
    
    def get_stats(self):
        """Calculate statistics from logged data"""
        if not os.path.exists(self.filename):
            return None
        
        try:
            df = pd.read_csv(self.filename)
            if df.empty:
                return None
            
            total = len(df)
            successful = df['success'].sum()
            
            stats = {
                'total_attempts': total,
                'successful': successful,
                'failed': total - successful,
                'success_rate': (successful / total * 100) if total > 0 else 0,
                'most_common_ecc': df['ecc_level'].mode()[0] if not df['ecc_level'].mode().empty else 'N/A',
                'avg_text_length': df['text_length'].mean()
            }
            return stats
        except Exception as e:
            print(f"[Logger] Error calculating stats: {e}")
            return None
    
    def show_analytics(self):
        """
        generate and display analytics visualizations
        creates three charts:
        1.Text length distribution histogram
        2.ECC level frequency bar chart
        3.Success and failure pie
        """
        if not os.path.exists(self.filename):
            print("[Logger] No log data available.")
            return
        
        try:
            df = pd.read_csv(self.filename)
            
            if df.empty:
                print("[Logger] Log file is empty")
                return
            
            # display statistics summary
            stats = self.get_stats()
            if stats:
                print("\n" + "="*50)
                print("QR GENERATION ANALYTICS")
                print("="*50)
                print(f"Total Attempts:    {stats['total_attempts']}")
                print(f"Successful:        {stats['successful']}")
                print(f"Failed:            {stats['failed']}")
                print(f"Success Rate:      {stats['success_rate']:.1f}%")
                print(f"Most Common ECC:   {stats['most_common_ecc']}")
                print(f"Avg Text Length:   {stats['avg_text_length']:.1f} chars")
                print("="*50 + "\n")
            
            # Setup  plot 
            fig = plt.figure(figsize=(15, 5))
            fig.suptitle('QR CODE GENERATION ANALYTICS', 
                        fontsize=16, fontweight='bold')
                        
            # CHART 1: text length distribution (Histogram)
            ax2 = plt.subplot(1, 3, 2)
            ax2.hist(df['text_length'], bins=10, color='#66b366', 
                    alpha=0.7, edgecolor='black')
            ax2.set_title('Input Text Length Distribution', fontweight='bold')
            ax2.set_xlabel('Character Count')
            ax2.set_ylabel('Frequency')
            ax2.grid(axis='y', alpha=0.3)

            # CHART 2: ECC Level frequency (bar chart)
            ax3 = plt.subplot(1, 3, 3)
            ecc_counts = df['ecc_level'].value_counts().sort_index()
            colors_ecc = ['#2ecc71', '#3498db', '#f39c12', '#e74c3c']
            bars = ax3.bar(ecc_counts.index, ecc_counts.values, 
                        color=colors_ecc[:len(ecc_counts)])
            ax3.set_title('Error Correction Level Usage', fontweight='bold')
            ax3.set_xlabel('ECC Level')
            ax3.set_ylabel('Frequency')
            ax3.grid(axis='y', alpha=0.3)

            # CHART 3: (Pie Chart)
            ax1 = plt.subplot(1, 3, 1)
            status_counts = df['success'].value_counts()
            colors = ["#1362b1", "#da2a2a"]
            labels = ['Success', 'Failed']
            ax1.pie(status_counts, labels=labels, autopct='%1.1f%%', 
                colors=colors, startangle=90, shadow=True)
            ax1.set_title('Generation Success Rate', fontweight='bold')
            
            #value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax3.text(bar.get_x() + bar.get_width()/2., height,
                        f'{int(height)}',
                        ha='center', va='bottom', fontweight='bold')
            
            plt.tight_layout()
            print("[Logger] Displaying analytics dashboard...")
            plt.show()
            
        except Exception as e:
            print(f"[Logger] Error generating analytics: {e}")
    
    def view_recent_logs(self, n=10):
        """Display recent logs"""
        if not os.path.exists(self.filename):
            print("[Logger] No log file found.")
            return
        
        try:
            df = pd.read_csv(self.filename)
            if df.empty:
                print("[Logger] No log entries")
                return
            
            print(f"\n{'='*80}")
            print(f"Recent log entries (Last {min(n, len(df))})")
            print('='*80)
            
            # Show last n entries with selected columns
            recent = df.tail(n)[['timestamp', 'unique_id', 'text_content', 'ecc_level', 'success']]
            print(recent.to_string(index=False))
            print('='*80 + '\n')
            
        except Exception as e:
            print(f"[Logger] Error logs: {e}")
    
    def clear_logs(self):
        """
        Clear all logged data
        
        Removes existing log file and creates a fresh one.
        """
        if os.path.exists(self.filename):
            os.remove(self.filename)
            print(f"[Logger] Cleared log file: {self.filename}")
        self._init_log_file()


# Standalone testing
if __name__ == "__main__":
    print("QR Logger")
    print("="*50 + "\n")
    
    # logger
    logger = QRLogger("test_qr_log.csv")
    
    # QR generation attempts
    print("Simulating QR generation attempts\n")
    
    test_data = [
        ("Hello World", 1, "L", 0, True),
        ("Test QR", 1, "L", 0, True),
        ("Short", 1, "M", 2, True),
        ("This is a longer test string", 1, "L", 0, True),
        ("Failed attempt", 1, "Q", 4, False),
        ("Another success", 1, "L", 0, True),
        ("QR", 1, "H", 7, True),
        ("Testing 123", 1, "M", 3, True),
        ("Error case", 1, "L", 0, False),
        ("Final test", 1, "L", 0, True),
    ]
    
    for text, ver, ecc, mask, success in test_data:
        logger.log_attempt(text, ver, ecc, mask, success)
    
    print("\n" + "="*50)
    
    # View recent logs
    logger.view_recent_logs(5)
    
    # Show analytics
    logger.show_analytics()
    
    print("\nTest complete, Check 'test_qr_log.csv' for logged data.")