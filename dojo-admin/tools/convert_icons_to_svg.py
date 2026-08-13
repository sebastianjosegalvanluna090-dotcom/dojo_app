"""Convert QPainter-based icon drawers to SVG files.

Intercepts QPainter draw calls and translates them to SVG elements.
Each icon key in ICON_DRAWERS produces a standalone .svg file.
"""
from __future__ import annotations

import math
import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------

VB = 24.0  # viewBox size (matches icon_library.py)


class _PathBuf:
    """Accumulates QPainterPath operations as SVG path-data strings."""

    def __init__(self) -> None:
        self._parts: list[str] = []
        self._has_move = False

    def moveTo(self, x: float, y: float) -> None:
        self._parts.append(f"M{_f(x)},{_f(y)}")
        self._has_move = True

    def lineTo(self, x: float, y: float) -> None:
        self._parts.append(f"L{_f(x)},{_f(y)}")

    def quadTo(self, cx: float, cy: float, x: float, y: float) -> None:
        self._parts.append(f"Q{_f(cx)},{_f(cy)} {_f(x)},{_f(y)}")

    def cubicTo(self, c1x: float, c1y: float, c2x: float, c2y: float,
                x: float, y: float) -> None:
        self._parts.append(f"C{_f(c1x)},{_f(c1y)} {_f(c2x)},{_f(c2y)} {_f(x)},{_f(y)}")

    def closeSubpath(self) -> None:
        self._parts.append("Z")
        self._has_move = False

    def arcTo(self, x: float, y: float, w: float, h: float,
              start: float, sweep: float) -> None:
        """Approximate arc with cubic beziers (accurate enough for icons)."""
        if w <= 0 or h <= 0:
            return
        cx, cy = x + w / 2, y + h / 2
        rx, ry = w / 2, h / 2
        start_rad = math.radians(start)
        sweep_rad = math.radians(sweep)
        steps = max(3, int(abs(sweep_rad) / (math.pi / 4)) + 1)
        dt = sweep_rad / steps
        for i in range(steps):
            a1 = start_rad + i * dt
            a2 = a1 + dt
            x1 = cx + rx * math.cos(a1)
            y1 = cy + ry * math.sin(a1)
            x2 = cx + rx * math.cos(a2)
            y2 = cy + ry * math.sin(a2)
            delta = 4 * math.tan(dt / 4) / 3
            c1x = x1 - delta * rx * math.sin(a1)
            c1y = y1 + delta * ry * math.cos(a1)
            c2x = x2 + delta * rx * math.sin(a2)
            c2y = y2 - delta * ry * math.cos(a2)
            if i == 0 and not self._has_move:
                self.moveTo(x1, y1)
            self.cubicTo(c1x, c1y, c2x, c2y, x2, y2)

    def data(self) -> str:
        return " ".join(self._parts)

    def is_empty(self) -> bool:
        return not self._parts


def _f(v: float) -> str:
    """Format float: drop trailing zeros, max 2 decimals."""
    s = f"{v:.2f}"
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return s


# ---------------------------------------------------------------------------
# QPainter2SVG — intercepts draw calls → SVG elements
# ---------------------------------------------------------------------------

class QPainter2SVG:
    """Drop-in replacement for QPainter that builds an SVG document."""

    class _PainterState:
        def __init__(self) -> None:
            self.pen_color = "#000000"
            self.pen_width = 1.0
            self.pen_style = "solid"
            self.pen_cap = "round"
            self.pen_join = "round"
            self.brush_color: str | None = None
            self.brush_style = "none"
            self.clip_path: _PathBuf | None = None

    class _ProxyPen:
        def __init__(self, svg: "QPainter2SVG") -> None:
            self._svg = svg

        def widthF(self) -> float:
            return self._svg._state.pen_width

        def color(self) -> Any:
            class _C:
                def __init__(self, hex_str: str) -> None:
                    self._hex = hex_str
                def name(self) -> str:
                    return self._hex
                def isValid(self) -> bool:
                    return True
            return _C(self._svg._state.pen_color)

    class _ProxyBrush:
        def __init__(self, svg: "QPainter2SVG") -> None:
            self._svg = svg

        def color(self) -> Any:
            class _C:
                def __init__(self, hex_str: str | None) -> None:
                    self._hex = hex_str or "#000000"
                def name(self) -> str:
                    return self._hex
                def isValid(self) -> bool:
                    return self._hex is not None
            return _C(self._svg._state.brush_color)

        def style(self) -> int:
            return self._svg._brush_style_enum()

    class _ProxyViewport:
        def __init__(self, svg: "QPainter2SVG") -> None:
            self._svg = svg
        def width(self) -> float:
            return VB
        def height(self) -> float:
            return VB

    class _ProxyPainterPath:
        """Proxy for QPainterPath that records operations."""

        def __init__(self, svg: "QPainter2SVG") -> None:
            self._buf = _PathBuf()
            self._svg = svg

        def moveTo(self, *args: Any) -> None:
            if len(args) == 1:
                pt = args[0]
                x = pt.x() if hasattr(pt, "x") else float(pt)
                y = pt.y() if hasattr(pt, "y") else 0
            else:
                x, y = float(args[0]), float(args[1])
            self._buf.moveTo(x, y)

        def lineTo(self, *args: Any) -> None:
            if len(args) == 1:
                pt = args[0]
                x = pt.x() if hasattr(pt, "x") else float(pt)
                y = pt.y() if hasattr(pt, "y") else 0
            else:
                x, y = float(args[0]), float(args[1])
            self._buf.lineTo(x, y)

        def quadTo(self, *args: Any) -> None:
            if len(args) == 2:
                ctrl, end = args
                cx = ctrl.x() if hasattr(ctrl, "x") else float(ctrl)
                cy = ctrl.y() if hasattr(ctrl, "y") else 0
                ex = end.x() if hasattr(end, "x") else float(end)
                ey = end.y() if hasattr(end, "y") else 0
            else:
                cx, cy, ex, ey = (float(a) for a in args)
            self._buf.quadTo(cx, cy, ex, ey)

        def cubicTo(self, *args: Any) -> None:
            if len(args) == 3:
                c1, c2, end = args
                c1x = c1.x() if hasattr(c1, "x") else float(c1)
                c1y = c1.y() if hasattr(c1, "y") else 0
                c2x = c2.x() if hasattr(c2, "x") else float(c2)
                c2y = c2.y() if hasattr(c2, "y") else 0
                ex = end.x() if hasattr(end, "x") else float(end)
                ey = end.y() if hasattr(end, "y") else 0
            else:
                c1x, c1y, c2x, c2y, ex, ey = (float(a) for a in args)
            self._buf.cubicTo(c1x, c1y, c2x, c2y, ex, ey)

        def closeSubpath(self) -> None:
            self._buf.closeSubpath()

        def addRoundedRect(self, rect: Any, rx: float, ry: float) -> None:
            if hasattr(rect, "x"):
                x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()
            else:
                x, y, w, h = float(rect[0]), float(rect[1]), float(rect[2]), float(rect[3])
            self._buf.moveTo(x + rx, y)
            self._buf.lineTo(x + w - rx, y)
            self._buf.quadTo(x + w, y, x + w, y + ry)
            self._buf.lineTo(x + w, y + h - ry)
            self._buf.quadTo(x + w, y + h, x + w - rx, y + h)
            self._buf.lineTo(x + rx, y + h)
            self._buf.quadTo(x, y + h, x, y + h - ry)
            self._buf.lineTo(x, y + ry)
            self._buf.quadTo(x, y, x + rx, y)
            self._buf.closeSubpath()

        def addEllipse(self, *args: Any) -> None:
            if len(args) == 1:
                rect = args[0]
                if hasattr(rect, "x"):
                    cx = rect.x() + rect.width() / 2
                    cy = rect.y() + rect.height() / 2
                    rx = rect.width() / 2
                    ry = rect.height() / 2
                else:
                    return
            elif len(args) == 3:
                center, rx, ry = args
                cx = center.x() if hasattr(center, "x") else float(center)
                cy = center.y() if hasattr(center, "y") else 0
                rx, ry = float(rx), float(ry)
            elif len(args) == 4:
                cx, cy, rx, ry = (float(a) for a in args)
            else:
                return
            # Approximate ellipse with 4 cubic bezier arcs
            k = 0.5522847498
            kx, ky = rx * k, ry * k
            self._buf.moveTo(cx + rx, cy)
            self._buf.cubicTo(cx + rx, cy + ky, cx + kx, cy + ry, cx, cy + ry)
            self._buf.cubicTo(cx - kx, cy + ry, cx - rx, cy + ky, cx - rx, cy)
            self._buf.cubicTo(cx - rx, cy - ky, cx - kx, cy - ry, cx, cy - ry)
            self._buf.cubicTo(cx + kx, cy - ry, cx + rx, cy - ky, cx + rx, cy)
            self._buf.closeSubpath()

        def arcTo(self, *args: Any) -> None:
            if len(args) == 3:
                rect, start, sweep = args
                if hasattr(rect, "x"):
                    x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()
                else:
                    return
                self._buf.arcTo(x, y, w, h, float(start), float(sweep))
            elif len(args) == 6:
                x, y, w, h, start, sweep = args
                self._buf.arcTo(float(x), float(y), float(w), float(h),
                                float(start), float(sweep))

        def addRect(self, *args: Any) -> None:
            if len(args) == 1:
                rect = args[0]
                if hasattr(rect, "x"):
                    x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()
                else:
                    return
            elif len(args) == 4:
                x, y, w, h = (float(a) for a in args)
            else:
                return
            self._buf.moveTo(x, y)
            self._buf.lineTo(x + w, y)
            self._buf.lineTo(x + w, y + h)
            self._buf.lineTo(x, y + h)
            self._buf.closeSubpath()

    # -- Brush style enum values (match Qt constants) --
    _BRUSH_NO = 0
    _BRUSH_SOLID = 1

    _PEN_SOLID = 1
    _PEN_DASH = 2
    _PEN_DOT = 3
    _PEN_DASHDOT = 4
    _PEN_DASHDOTDOT = 5
    _PEN_NOPEN = 0

    def __init__(self) -> None:
        self._state = self._PainterState()
        self._elements: list[str] = []
        self._clip_counter = 0

    # -- State setting methods --

    def setPen(self, pen: Any) -> None:
        from PyQt6.QtCore import Qt as _Qt
        # Handle pen style enums (Qt.PenStyle.NoPen etc.)
        if hasattr(pen, "value"):
            # It's an enum — check if it's PenStyle.NoPen
            try:
                if pen == _Qt.PenStyle.NoPen:
                    self._state.pen_style = "none"
                    return
            except TypeError:
                pass
        if isinstance(pen, int):
            if pen == int(_Qt.PenStyle.NoPen):
                self._state.pen_style = "none"
                return
        # Pen object
        if hasattr(pen, "color"):
            c = pen.color()
            self._state.pen_color = c.name() if hasattr(c, "name") else str(c)
        if hasattr(pen, "widthF"):
            w = pen.widthF()
            self._state.pen_width = w if w > 0 else 0
        if hasattr(pen, "style"):
            s = pen.style()
            if s == _Qt.PenStyle.NoPen:
                self._state.pen_style = "none"
            elif s == _Qt.PenStyle.SolidLine:
                self._state.pen_style = "solid"
            elif s == _Qt.PenStyle.DashLine:
                self._state.pen_style = "dash"
            elif s == _Qt.PenStyle.DotLine:
                self._state.pen_style = "dot"
            else:
                self._state.pen_style = "solid"
        if hasattr(pen, "capStyle"):
            cs = pen.capStyle()
            if cs == _Qt.PenCapStyle.RoundCap:
                self._state.pen_cap = "round"
            elif cs == _Qt.PenCapStyle.FlatCap:
                self._state.pen_cap = "butt"
            else:
                self._state.pen_cap = "square"
        if hasattr(pen, "joinStyle"):
            js = pen.joinStyle()
            if js == _Qt.PenJoinStyle.RoundJoin:
                self._state.pen_join = "round"
            elif js == _Qt.PenJoinStyle.BevelJoin:
                self._state.pen_join = "bevel"
            else:
                self._state.pen_join = "miter"

    def setBrush(self, brush: Any) -> None:
        from PyQt6.QtCore import Qt as _Qt
        if isinstance(brush, int):
            if brush == int(_Qt.BrushStyle.NoBrush):
                self._state.brush_style = "none"
                self._state.brush_color = None
            elif brush == int(_Qt.BrushStyle.SolidPattern):
                self._state.brush_style = "solid"
            return
        if hasattr(brush, "style"):
            s = brush.style()
            if s == _Qt.BrushStyle.NoBrush:
                self._state.brush_style = "none"
                self._state.brush_color = None
            else:
                self._state.brush_style = "solid"
                if hasattr(brush, "color"):
                    c = brush.color()
                    hex_name = c.name() if hasattr(c, "name") else str(c)
                    alpha = c.alpha() if hasattr(c, "alpha") else 255
                    if alpha < 255:
                        r, g, b = int(hex_name[1:3], 16), int(hex_name[3:5], 16), int(hex_name[5:7], 16)
                        self._state.brush_color = f"rgba({r},{g},{b},{alpha/255:.2f})"
                    else:
                        self._state.brush_color = hex_name
        elif hasattr(brush, "color"):
            c = brush.color()
            self._state.brush_color = c.name() if hasattr(c, "name") else str(c)
            self._state.brush_style = "solid"

    def setClipRect(self, *args: Any) -> None:
        pass  # skip clipping for icon export

    def setClipPath(self, *args: Any) -> None:
        pass

    def setClipping(self, enabled: bool) -> None:
        pass

    def pen(self) -> Any:
        return self._ProxyPen(self)

    def brush(self) -> Any:
        return self._ProxyBrush(self)

    def viewport(self) -> Any:
        return self._ProxyViewport(self)

    def isActive(self) -> bool:
        return True

    def setRenderHint(self, hint: Any, enabled: bool = True) -> None:
        pass

    def save(self) -> None:
        pass

    def restore(self) -> None:
        pass

    def translate(self, *args: Any) -> None:
        pass  # We work in the icon's local 24×24 coord system

    def scale(self, sx: float, sy: float) -> None:
        pass

    def rotate(self, angle: float) -> None:
        pass

    def end(self) -> bool:
        return True

    def begin(self, *args: Any) -> bool:
        return True

    # -- Helper --

    def _brush_style_enum(self) -> int:
        if self._state.brush_style == "none":
            return self._BRUSH_NO
        return self._BRUSH_SOLID

    def _svg_attrs(self) -> dict[str, str]:
        """Return SVG attributes dict for current pen/brush state."""
        attrs: dict[str, str] = {}
        # Stroke
        if self._state.pen_style == "none":
            attrs["stroke"] = "none"
        else:
            attrs["stroke"] = self._state.pen_color
            if self._state.pen_width != 1.0:
                attrs["stroke-width"] = _f(self._state.pen_width)
            if self._state.pen_cap != "round":
                attrs["stroke-linecap"] = self._state.pen_cap
            if self._state.pen_join != "round":
                attrs["stroke-linejoin"] = self._state.pen_join
            if self._state.pen_style == "dash":
                attrs["stroke-dasharray"] = "6 3"
            elif self._state.pen_style == "dot":
                attrs["stroke-dasharray"] = "1 3"
        # Fill
        if self._state.brush_style == "none" or self._state.brush_color is None:
            attrs["fill"] = "none"
        else:
            attrs["fill"] = self._state.brush_color
        return attrs

    # -- Drawing methods --

    def _add_element(self, tag: str, extra: dict[str, str] | None = None) -> None:
        attrs = self._svg_attrs()
        if extra:
            attrs.update(extra)
        attr_str = " ".join(f'{k}="{v}"' for k, v in attrs.items())
        self._elements.append(f"<{tag} {attr_str}/>")

    def drawPath(self, path: Any) -> None:
        buf = getattr(path, "_buf", None)
        if buf is None or buf.is_empty():
            return
        self._add_element("path", {"d": buf.data()})

    def drawLine(self, *args: Any) -> None:
        if len(args) == 2:
            p1, p2 = args
            x1 = p1.x() if hasattr(p1, "x") else float(p1)
            y1 = p1.y() if hasattr(p1, "y") else 0
            x2 = p2.x() if hasattr(p2, "x") else float(p2)
            y2 = p2.y() if hasattr(p2, "y") else 0
        else:
            x1, y1, x2, y2 = (float(a) for a in args)
        self._add_element("line", {
            "x1": _f(x1), "y1": _f(y1),
            "x2": _f(x2), "y2": _f(y2),
        })

    def drawEllipse(self, *args: Any) -> None:
        if len(args) == 1:
            rect = args[0]
            if hasattr(rect, "x"):
                cx = rect.x() + rect.width() / 2
                cy = rect.y() + rect.height() / 2
                rx = rect.width() / 2
                ry = rect.height() / 2
            else:
                return
        elif len(args) == 2:
            center, radius = args
            cx = center.x() if hasattr(center, "x") else float(center)
            cy = center.y() if hasattr(center, "y") else 0
            if hasattr(radius, "x"):
                rx = radius.x()
                ry = radius.y()
            else:
                rx = ry = float(radius)
        elif len(args) == 3:
            center, rx, ry = args
            cx = center.x() if hasattr(center, "x") else float(center)
            cy = center.y() if hasattr(center, "y") else 0
            rx, ry = float(rx), float(ry)
        elif len(args) == 4:
            cx, cy, rx, ry = (float(a) for a in args)
        else:
            return
        self._add_element("ellipse", {
            "cx": _f(cx), "cy": _f(cy),
            "rx": _f(abs(rx)), "ry": _f(abs(ry)),
        })

    def drawRoundedRect(self, *args: Any) -> None:
        if len(args) == 3:
            rect, rx, ry = args
            if hasattr(rect, "x"):
                x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()
            else:
                return
            rx, ry = float(rx), float(ry)
        elif len(args) == 5:
            x, y, w, h, r = (float(a) for a in args)
            rx = ry = r
        else:
            return
        buf = _PathBuf()
        buf.moveTo(x + rx, y)
        buf.lineTo(x + w - rx, y)
        buf.quadTo(x + w, y, x + w, y + ry)
        buf.lineTo(x + w, y + h - ry)
        buf.quadTo(x + w, y + h, x + w - rx, y + h)
        buf.lineTo(x + rx, y + h)
        buf.quadTo(x, y + h, x, y + h - ry)
        buf.lineTo(x, y + ry)
        buf.quadTo(x, y, x + rx, y)
        buf.closeSubpath()
        self._add_element("path", {"d": buf.data()})

    def drawRect(self, *args: Any) -> None:
        if len(args) == 1:
            rect = args[0]
            if hasattr(rect, "x"):
                x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()
            else:
                return
        elif len(args) == 4:
            x, y, w, h = (float(a) for a in args)
        else:
            return
        self._add_element("rect", {
            "x": _f(x), "y": _f(y),
            "width": _f(w), "height": _f(h),
        })

    def fill(self, rect: Any, color: Any) -> None:
        if hasattr(rect, "x"):
            x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()
        else:
            return
        if hasattr(color, "name"):
            c = color.name()
        else:
            c = str(color)
        self._add_element("rect", {
            "x": _f(x), "y": _f(y),
            "width": _f(w), "height": _f(h),
            "stroke": "none",
            "fill": c,
        })

    def QPainterPath(self) -> Any:  # noqa: N802
        return self._ProxyPainterPath(self)

    # -- SVG generation --

    def to_svg(self, icon_key: str) -> str:
        """Return a complete SVG string for this icon."""
        elements = "\n  ".join(self._elements)
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     viewBox="0 0 {VB:.0f} {VB:.0f}"
     width="{VB:.0f}" height="{VB:.0f}"
     fill="none">
  {elements}
</svg>
'''


# ---------------------------------------------------------------------------
# Converter
# ---------------------------------------------------------------------------

def convert_all_icons(output_dir: Path) -> dict[str, Path]:
    """Run every drawer function through QPainter2SVG and write SVG files.

    Monkey-patches QPainterPath in the icon_library module so drawer
    functions produce _PathBuf-backed paths we can serialise to SVG.
    """
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    import views.icon_library as _il
    from PyQt6.QtGui import QColor

    # Save originals
    _orig_qp = _il.QPainterPath

    output_dir.mkdir(parents=True, exist_ok=True)
    result: dict[str, Path] = {}

    for key, drawer_fn in _il.ICON_DRAWERS.items():
        svg = QPainter2SVG()
        # Patch QPainterPath so drawers build our _PathBuf-backed proxy
        _il.QPainterPath = svg.QPainterPath
        try:
            drawer_fn(svg, QColor("#FFFFFF"))
        except Exception as exc:
            print("  SKIP {}: {}".format(key, exc))
            continue
        finally:
            _il.QPainterPath = _orig_qp

        svg_str = svg.to_svg(key)
        filename = f"{key}.svg"
        filepath = output_dir / filename
        filepath.write_text(svg_str, encoding="utf-8")
        result[key] = filepath

    return result


def _convert_single(key: str) -> str:
    """Convert a single icon and return its SVG string (for testing)."""
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    import views.icon_library as _il
    from PyQt6.QtGui import QColor

    drawer_fn = _il.ICON_DRAWERS.get(key)
    if drawer_fn is None:
        raise ValueError("Unknown icon key: {!r}".format(key))

    svg = QPainter2SVG()
    _orig_qp = _il.QPainterPath
    _il.QPainterPath = svg.QPainterPath
    try:
        drawer_fn(svg, QColor("#FFFFFF"))
    finally:
        _il.QPainterPath = _orig_qp
    return svg.to_svg(key)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent.parent
    output = project_root / "assets" / "icons" / "outline"

    print("Converting icons -> " + str(output))
    mapping = convert_all_icons(output)
    print("Generated {} SVG files.".format(len(mapping)))
    for key, path in sorted(mapping.items()):
        size = path.stat().st_size
        print("  {}.svg ({} bytes)".format(key, size))
