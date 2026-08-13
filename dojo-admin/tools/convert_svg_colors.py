"""Replace hardcoded colors in SVG icons with currentColor.

Scans all SVGs in assets/icons/outline/ and replaces:
  - #fff / #ffffff in stroke/fill -> currentColor
  - rgba(...) in fill/stroke -> currentColor with opacity
  - #000000 in stroke -> currentColor
"""
from pathlib import Path
import re

SVG_DIR = Path(__file__).resolve().parent.parent / "assets" / "icons" / "outline"

# Patterns to replace
REPLACEMENTS = [
    # White hex colors (stroke="#fff" or fill="#ffffff")
    (r'(?:stroke|fill)="#fff(?:fff)?"', lambda m: m.group(0).replace("#fff", "currentColor").replace("#ffffff", "currentColor")),
    # Black hex colors
    (r'(?:stroke|fill)="#000000"', lambda m: m.group(0).replace("#000000", "currentColor")),
    # rgba fills (fill="rgba(255,255,255,0.12)") -> currentColor + opacity attribute
    (r'fill="rgba\((\d+),(\d+),(\d+),([\d.]+)\)"', None),  # handled separately
]

def convert_svg_colors(content: str) -> str:
    # Replace #fff and #ffffff
    content = re.sub(r'#ffffff', 'currentColor', content, flags=re.IGNORECASE)
    content = re.sub(r'#fff(?!f)', 'currentColor', content, flags=re.IGNORECASE)
    
    # Replace #000000
    content = re.sub(r'#000000', 'currentColor', content)
    
    # Replace rgba(r,g,b,a) fills -> currentColor + fill-opacity
    def rgba_to_current(m):
        attr = m.group(1)  # "fill" or "stroke"
        alpha = m.group(2)
        return '{}="currentColor" {}-opacity="{}"'.format(attr, attr, alpha)
    
    content = re.sub(r'(fill|stroke)="rgba\(\d+,\d+,\d+,([\d.]+)\)"', rgba_to_current, content)
    
    return content


count = 0
for svg_file in sorted(SVG_DIR.glob("*.svg")):
    original = svg_file.read_text(encoding="utf-8")
    converted = convert_svg_colors(original)
    if converted != original:
        svg_file.write_text(converted, encoding="utf-8")
        count += 1

print("{}/82 SVGs converted to currentColor".format(count))
