import sys
from pathlib import Path
from qr_encoder import QREncoder
from qr_matrix import QRMatrix
from qr_analytics import QRLogger

logger = QRLogger()


def render_array(grid):
    """Render a QR matrix as text blocks."""
    return '\n'.join(
        ''.join('██' if v == 1 else '  ' for v in row) for row in grid
    )


def generate_qr(text, demo_file=None):
    """
    Generate a QR code from input text.
    """
    # Redirect output if demo file specified
    if demo_file:
        original_stdout = sys.stdout
        sys.stdout = open(demo_file, 'w', encoding='utf-8')
    
    try:
        # Encode the data
        encoder = QREncoder()
        codewords = encoder.process_input(text)
        
        # Build the matrix
        matrix = QRMatrix()
        matrix.build_structure()
        matrix.fill_data(codewords)
        matrix.apply_mask()
        matrix.add_format_info()
        
        # Show result
        print("="*70)
        print("FINAL QR CODE")
        print("="*70)
        print()
        print(matrix.render())
        print()

        #Log generation success
        logger.log_attempt(
            text=text,
            version=1,
            ecc="L",
            mask=0,
            success=True
        )
        
        return matrix.get_array()

    except Exception as e:
        # Log generation failed, then let the caller report it
        logger.log_attempt(
            text=text,
            version=1,
            ecc="L",
            mask=0,
            success=False
        )
        print(f"ERROR: {e}")
        raise
        
    finally:
        if demo_file:
            sys.stdout.close()
            sys.stdout = original_stdout

def view_analytics():
    """display analytics"""
    print("\n" + "="*50)
    print("Analytics Dashboard")
    print("="*50)
    logger.show_analytics()

def view_recent_activity():
    """Show recent QR generation"""
    logger.view_recent_logs(10)



def main():
    """Test with required strings and generate demo files."""
    test_data = [
        ("known", "demo_1.txt"),
        ("We've succeeded!", "demo_2.txt"),
        ("~¡256_-_aA&ñ", "demo_3.txt"),
        ("From α to ɷ...", "demo_4.txt"),
        ("Sugarplum_Fairy_Nightmare", "demo_5.txt")
    ]
    
    print("\n" + "="* 50)
    print("QR CODE GENERATOR - VERSION 1, LEVEL L, MASK 0")
    print("="*50)
    
    for idx, (text, demo) in enumerate(test_data, 1):
        print(f"\n\nTest {idx}: '{text}'")
        
        try:
            # Generate with demo file
            result = generate_qr(text, demo)
            
            # Also display on screen
            print("\n" + render_array(result) + "\n")
            print(f"SUCCESS - Saved to {demo}")
            print(f"Matrix shape: {result.shape}")
            
        except Exception as e:
            print(f"FAILED - {e}")
    
    print("\n" + "="*50)
    print("QR CODES GENERATED")
    print("="*50)
    print("\nRecent Generation Activity:")
    view_recent_activity()

    print("\n" + "="*50)
    print("Analytics dashboard is ready!")
    print("To view charts, uncomment the line below or call:")
    print("  python -c 'from qr_generator import view_analytics; view_analytics()'")
    print("="*50)
    


if __name__ == "__main__":
    main()