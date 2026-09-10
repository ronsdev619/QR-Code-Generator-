"""
Accessible QR Code Customisation Enhancement
Inclusive display customisation while maintaining scan reliability
"""

import numpy as np
import matplotlib.colors as mcolors
from typing import Dict, Tuple, Optional, List
import warnings

class QRColorAnalyzer:
    """Analyze color combinations for accessibility and scan reliability"""
    
    # Color deficiency safe palettes
    COLOR_PALETTES = {
        'default': {'dark': '#000000', 'light': '#FFFFFF'},
        'high_contrast': {'dark': '#000000', 'light': '#FFFF00'},
        'deuteranopia': {'dark': '#003366', 'light': '#FFCC00'},  # Blue/Yellow
        'protanopia': {'dark': '#660033', 'light': '#00CCFF'},    # Red/Blue
        'tritanopia': {'dark': '#006600', 'light': '#FF66CC'},    # Green/Pink
        'grayscale': {'dark': '#000000', 'light': '#808080'},
        'inverted': {'dark': '#FFFFFF', 'light': '#000000'},
    }
    
    @staticmethod
    def check_contrast_ratio(color1: str, color2: str) -> float:
        """
        Calculate WCAG contrast ratio (minimum 4.5:1 for normal text)
        Returns ratio (higher = better contrast)
        """
        def hex_to_rgb(hex_color):
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) / 255 for i in (0, 2, 4))
        
        def luminance(rgb):
            # Convert to relative luminance
            rc = []
            for c in rgb:
                c = c / 255.0 if c > 1 else c
                if c <= 0.03928:
                    rc.append(c / 12.92)
                else:
                    rc.append(((c + 0.055) / 1.055) ** 2.4)
            return 0.2126 * rc[0] + 0.7152 * rc[1] + 0.0722 * rc[2]
        
        rgb1 = hex_to_rgb(color1)
        rgb2 = hex_to_rgb(color2)
        
        l1 = luminance(rgb1)
        l2 = luminance(rgb2)
        
        if l1 > l2:
            return (l1 + 0.05) / (l2 + 0.05)
        else:
            return (l2 + 0.05) / (l1 + 0.05)
    
    @staticmethod
    def is_colorblind_safe(color1: str, color2: str) -> Tuple[bool, str]:
        """
        Check if color combination is safe for common color vision deficiencies
        Returns: (is_safe, message)
        """
        # Convert to RGB
        rgb1 = mcolors.hex2color(color1)
        rgb2 = mcolors.hex2color(color2)
        
        # Check if color brightness
        brightness1 = 0.299 * rgb1[0] + 0.587 * rgb1[1] + 0.114 * rgb1[2]
        brightness2 = 0.299 * rgb2[0] + 0.587 * rgb2[1] + 0.114 * rgb2[2]
        
        brightness_diff = abs(brightness1 - brightness2)
        
        if brightness_diff > 0.5:
            return True, "Good brightness contrast for color vision deficiencies"
        elif brightness_diff > 0.3:
            return True, "Moderate brightness contrast"
        else:
            return False, "Low brightness contrast - may be hard to distinguish for color blind users"


class QRShapeCustomizer:
    """Customize module shapes while maintaining scan reliability"""
    
    SHAPE_TYPES = {
        'square': 'Standard square modules (best for scanning)',
        'circle': 'Rounded circular modules (good aesthetics)',
        'rounded': 'Squares with rounded corners (balanced)',
        'diamond': 'Diamond shapes (for decorative use)',
        'dot': 'Small circular dots (minimalist)',
    }
    
    @staticmethod
    def apply_shape_filter(matrix: np.ndarray, shape_type: str = 'square', 
                          radius: float = 0.3) -> np.ndarray:
        """
        Apply shape customization to QR matrix
        Returns modified matrix with shape effects
        """
        if shape_type == 'square':
            return matrix  # No change
        
        # Create shaped version
        shaped = np.zeros_like(matrix, dtype=float)
        rows, cols = matrix.shape
        
        for r in range(rows):
            for c in range(cols):
                if matrix[r, c] == 1:  # Dark module
                    if shape_type == 'circle':
                        # Simple circle approximation
                        shaped[r, c] = 1.0
                    elif shape_type == 'rounded':
                        # Rounded square
                        shaped[r, c] = 1.0
                    elif shape_type == 'diamond':
                        # Diamond shape
                        shaped[r, c] = 1.0 if (abs(r - rows/2) + abs(c - cols/2)) < 10 else 0.5
                    elif shape_type == 'dot':
                        # Small dot
                        shaped[r, c] = 1.0 if (r % 2 == 0 and c % 2 == 0) else 0
        
        return shaped


class QRAccessibilityChecker:
    """Check customization options for accessibility issues"""
    
    @staticmethod
    def validate_customization(colors: Dict[str, str], shape: str, 
                              size_factor: float) -> Tuple[bool, List[str]]:
        """
        Validate customization options for accessibility
        Returns: (is_valid, warnings_list)
        """
        warnings = []
        
        # Check contrast ratio
        analyzer = QRColorAnalyzer()
        contrast = analyzer.check_contrast_ratio(colors['dark'], colors['light'])
        
        if contrast < 3.0:
            warnings.append(f"CRITICAL: Very low contrast ratio ({contrast:.1f}:1). QR may not scan.")
            return False, warnings
        elif contrast < 4.5:
            warnings.append(f"WARNING: Low contrast ratio ({contrast:.1f}:1). May be hard to scan in poor conditions.")
        
        # Check color blindness safety
        is_safe, message = analyzer.is_colorblind_safe(colors['dark'], colors['light'])
        if not is_safe:
            warnings.append(f"WARNING: {message}")
        
        # Check size
        if size_factor < 0.5:
            warnings.append("WARNING: Small QR size may be hard to scan with older devices")
        elif size_factor > 3.0:
            warnings.append("WARNING: Very large QR may not fit on some screens")
        
        # Check shape
        if shape not in ['square', 'circle', 'rounded']:
            warnings.append(f"NOTE: '{shape}' shape may reduce scan reliability")
        
        return len(warnings) == 0 or all('NOTE' in w for w in warnings), warnings


class QRCustomizer:
    """Main class for accessible QR customization"""
    
    PRESET_CONFIGS = {
        'standard': {
            'description': 'Standard black/white (best scanning)',
            'colors': {'dark': '#000000', 'light': '#FFFFFF'},
            'shape': 'square',
            'size': 1.0,
            'frame': False
        },
        'high_visibility': {
            'description': 'High contrast for low vision',
            'colors': {'dark': '#000000', 'light': '#FFFF00'},
            'shape': 'square',
            'size': 1.2,
            'frame': True
        },
        'colorblind_friendly': {
            'description': 'Optimized for color vision deficiencies',
            'colors': {'dark': '#003366', 'light': '#FFCC00'},
            'shape': 'circle',
            'size': 1.0,
            'frame': False
        },
        'dark_mode': {
            'description': 'Inverted for dark backgrounds',
            'colors': {'dark': '#FFFFFF', 'light': '#000000'},
            'shape': 'rounded',
            'size': 1.0,
            'frame': True
        },
        'minimalist': {
            'description': 'Simple, clean appearance',
            'colors': {'dark': '#333333', 'light': '#F5F5F5'},
            'shape': 'dot',
            'size': 0.8,
            'frame': False
        }
    }
    
    def __init__(self):
        self.color_analyzer = QRColorAnalyzer()
        self.shape_customizer = QRShapeCustomizer()
        self.access_checker = QRAccessibilityChecker()
        
        # Current settings
        self.settings = self.PRESET_CONFIGS['standard'].copy()
        self.warnings = []
    
    def apply_preset(self, preset_name: str) -> Dict:
        """
        Apply a preset configuration
        Returns: Settings dictionary
        """
        if preset_name not in self.PRESET_CONFIGS:
            raise ValueError(f"Unknown preset: {preset_name}. Available: {list(self.PRESET_CONFIGS.keys())}")
        
        self.settings = self.PRESET_CONFIGS[preset_name].copy()
        
        # Validate the preset
        is_valid, warnings = self.access_checker.validate_customization(
            self.settings['colors'],
            self.settings['shape'],
            self.settings['size']
        )
        
        self.warnings = warnings
        
        print(f"Applied preset: {preset_name}")
        print(f"Description: {self.settings['description']}")
        
        if warnings:
            print("\nAccessibility notes:")
            for warning in warnings:
                print(f"  • {warning}")
        
        return self.settings
    
    def customize(self, colors: Optional[Dict[str, str]] = None,
                  shape: Optional[str] = None,
                  size: Optional[float] = None,
                  add_frame: Optional[bool] = None,
                  add_logo: bool = False) -> Dict:
        """
        Apply custom customization options
        Returns: Updated settings dictionary
        """
        # Update settings with the given values
        if colors:
            self.settings['colors'] = colors
        
        if shape:
            if shape not in self.shape_customizer.SHAPE_TYPES:
                raise ValueError(f"Invalid shape. Choose from: {list(self.shape_customizer.SHAPE_TYPES.keys())}")
            self.settings['shape'] = shape
        
        if size:
            self.settings['size'] = max(0.1, min(5.0, size))  # Clamp between 0.1 and 5.0
        
        if add_frame is not None:
            self.settings['frame'] = add_frame
        
        self.settings['logo'] = add_logo
        
        # Validate the customisation
        is_valid, warnings = self.access_checker.validate_customization(
            self.settings['colors'],
            self.settings['shape'],
            self.settings['size']
        )
        
        self.warnings = warnings
        
        # Generate user message
        self._generate_user_message(is_valid)
        
        return self.settings
    
    def _generate_user_message(self, is_valid: bool):
        """Generate user-friendly message about current settings"""
        print("\n" + "="*60)
        print("QR CUSTOMIZATION SETTINGS")
        print("="*60)
        
        # Show current settings
        colors = self.settings['colors']
        print(f"Colors: Dark={colors['dark']}, Light={colors['light']}")
        print(f"Contrast ratio: {self.color_analyzer.check_contrast_ratio(colors['dark'], colors['light']):.1f}:1")
        
        shape_desc = self.shape_customizer.SHAPE_TYPES.get(self.settings['shape'], 'Unknown')
        print(f"Shape: {self.settings['shape']} ({shape_desc})")
        print(f"Size: {self.settings['size']:.1f}x {'(enlarged)' if self.settings['size'] > 1 else '(reduced)' if self.settings['size'] < 1 else ''}")
        print(f"Frame: {'Yes' if self.settings.get('frame', False) else 'No'}")
        print(f"Logo: {'Yes' if self.settings.get('logo', False) else 'No'}")
        
        # Show warnings
        if self.warnings:
            print("\n⚠️  ACCESSIBILITY NOTICES:")
            for warning in self.warnings:
                if 'CRITICAL' in warning:
                    print(f"  🔴 {warning}")
                elif 'WARNING' in warning:
                    print(f"  🟡 {warning}")
                else:
                    print(f"  ℹ️  {warning}")
            
            if not is_valid:
                print("\n❌ Some settings may prevent scanning. Consider adjusting.")
            else:
                print("\n✅ Customization applied with notes above.")
        else:
            print("\n✅ All settings are scan-safe!")
        
        # Give specific advice
        contrast = self.color_analyzer.check_contrast_ratio(colors['dark'], colors['light'])
        if contrast < 4.5:
            print(f"\n💡 TIP: Increase contrast (current: {contrast:.1f}:1, recommended: >4.5:1)")
        
        if self.settings['shape'] != 'square':
            print("💡 TIP: Non-square shapes may reduce scan reliability on older devices")
        
        if self.settings['size'] < 0.7:
            print("💡 TIP: Very small QR codes may be hard to scan")
    
    def get_settings_description(self) -> str:
        """Get text description of current settings for display to user"""
        colors = self.settings['colors']
        contrast = self.color_analyzer.check_contrast_ratio(colors['dark'], colors['light'])
        
        description = [
            f"Current QR customization:",
            f"• Colors: Dark={colors['dark']}, Light={colors['light']}",
            f"• Contrast ratio: {contrast:.1f}:1 ({'Good' if contrast >= 4.5 else 'Low'})",
            f"• Module shape: {self.settings['shape']}",
            f"• Size multiplier: {self.settings['size']:.1f}x",
            f"• Frame: {'Enabled' if self.settings.get('frame', False) else 'Disabled'}",
        ]
        
        if self.warnings:
            description.append("\nAccessibility notes:")
            for warning in self.warnings[:3]:  # Show first 3 warnings
                description.append(f"• {warning}")
        
        return "\n".join(description)
    
    def apply_to_matrix(self, matrix: np.ndarray) -> np.ndarray:
        """
        Apply current customization to a QR matrix
        Returns: Customized matrix (for display purposes)
        """
        # Apply shape customization
        shaped = self.shape_customizer.apply_shape_filter(matrix, self.settings['shape'])
        
        # Note: Actual color application happens in rendering (matplotlib)
        # This returns a matrix that can be colored during display
        
        return shaped


# Example usage and testing
def test_customization():
    """Test the customization system"""
    print("Testing QR Customization Enhancement")
    print("="*50)
    
    customizer = QRCustomizer()
    
    # Test preset configurations
    print("\n1. Testing preset configurations:")
    presets_to_test = ['standard', 'high_visibility', 'colorblind_friendly', 'dark_mode']
    
    for preset in presets_to_test:
        print(f"\n--- Applying '{preset}' preset ---")
        settings = customizer.apply_preset(preset)
        print(f"Settings: {settings}")
    
    # Test custom customisation
    print("\n\n2. Testing custom customization:")
    
    # Good customisation
    print("\n--- Good customization (safe) ---")
    customizer.customize(
        colors={'dark': '#000000', 'light': '#FFFFFF'},
        shape='rounded',
        size=1.0
    )
    
    # Problematic customisation (low contrast)
    print("\n--- Problematic customization (low contrast) ---")
    customizer.customize(
        colors={'dark': '#666666', 'light': '#888888'},  # Very similar
        shape='diamond',
        size=0.5
    )
    
    # Colorblind-friendly customisation
    print("\n--- Colorblind-friendly customization ---")
    customizer.customize(
        colors={'dark': '#003366', 'light': '#FF9900'},  # Blue/Orange
        shape='circle',
        size=1.2,
        add_frame=True
    )
    
    print("\n" + "="*50)
    print("Customization testing complete!")


if __name__ == "__main__":
    test_customization()