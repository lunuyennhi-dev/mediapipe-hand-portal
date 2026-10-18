"""
High-Performance Filter Engine: 7 aesthetic, smooth visual filters.
All filters accept and return a BGR uint8 NumPy image of identical dimensions.
"""
import cv2
import numpy as np

class FilterEngine:
    """Optimized computer vision filter engine with 7 distinct visual effects."""

    @staticmethod
    def apply_thermal(image: np.ndarray) -> np.ndarray:
        """Thermal camera simulation using COLORMAP_JET."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        norm_gray = cv2.normalize(gray, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)
        return cv2.applyColorMap(norm_gray, cv2.COLORMAP_JET)

    @staticmethod
    def apply_sketch(image: np.ndarray) -> np.ndarray:
        """Artistic pencil sketch using grayscale invert and dodge blending."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        inv_gray = 255 - gray
        blurred = cv2.GaussianBlur(inv_gray, (21, 21), 0)
        sketch = cv2.divide(gray, 255 - blurred, scale=256)
        return cv2.cvtColor(sketch, cv2.COLOR_GRAY2BGR)

    @staticmethod
    def apply_pixelate(image: np.ndarray, block_size: int = 16) -> np.ndarray:
        """Retro 8-bit arcade pixelation."""
        h, w = image.shape[:2]
        if h < block_size or w < block_size:
            return image
        small_w = max(1, w // block_size)
        small_h = max(1, h // block_size)
        small = cv2.resize(image, (small_w, small_h), interpolation=cv2.INTER_LINEAR)
        return cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)

    @staticmethod
    def apply_night_vision(image: np.ndarray, frame_count: int = 0) -> np.ndarray:
        """Night vision goggles with green phosphor tint, CRT scanlines, and sensor noise."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        zero_channel = np.zeros_like(gray)
        green_enhanced = cv2.normalize(gray, None, alpha=40, beta=255, norm_type=cv2.NORM_MINMAX)
        night_bgr = cv2.merge([zero_channel, green_enhanced, zero_channel])

        # CRT horizontal scanlines
        h, w = image.shape[:2]
        scanlines = np.ones((h, 1), dtype=np.float32)
        scanlines[::3] = 0.70
        night_bgr = (night_bgr.astype(np.float32) * scanlines[:, :, None]).astype(np.uint8)

        # Dynamic subtle noise
        noise = np.random.randint(-10, 10, (h, w), dtype=np.int16)
        g_channel = np.clip(night_bgr[:, :, 1].astype(np.int16) + noise, 0, 255).astype(np.uint8)
        night_bgr[:, :, 1] = g_channel
        return night_bgr

    @staticmethod
    def apply_xray(image: np.ndarray) -> np.ndarray:
        """X-Ray / Negative high-contrast edge enhanced mode."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        inverted = 255 - gray
        edges = cv2.Laplacian(gray, cv2.CV_16S, ksize=3)
        edges = cv2.convertScaleAbs(edges)
        xray_gray = cv2.addWeighted(inverted, 0.8, edges, 0.4, 0)
        
        b = xray_gray
        g = cv2.multiply(xray_gray, 0.9)
        r = cv2.multiply(xray_gray, 0.7)
        return cv2.merge([b, g, r])

    @staticmethod
    def apply_vintage_sepia(image: np.ndarray) -> np.ndarray:
        """Warm vintage film sepia tone with vignette darkening."""
        sepia_matrix = np.array([
            [0.272, 0.534, 0.131],
            [0.349, 0.686, 0.168],
            [0.393, 0.769, 0.189]
        ])
        sepia = cv2.transform(image, sepia_matrix)
        sepia = np.clip(sepia, 0, 255).astype(np.uint8)

        # Smooth vignette
        h, w = image.shape[:2]
        kernel_x = cv2.getGaussianKernel(w, w / 2.2)
        kernel_y = cv2.getGaussianKernel(h, h / 2.2)
        vignette_mask = (kernel_y * kernel_x.T)
        vignette_mask = vignette_mask / vignette_mask.max()
        return (sepia.astype(np.float32) * vignette_mask[:, :, None]).astype(np.uint8)

    @staticmethod
    def apply_matrix(image: np.ndarray, frame_count: int = 0) -> np.ndarray:
        """The Matrix green digital code stream."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        h, w = image.shape[:2]
        levels = 6
        posterized = np.floor_divide(gray, 256 // levels) * (256 // levels)
        
        b = np.zeros_like(posterized)
        g = posterized
        r = np.multiply(posterized, 0.2).astype(np.uint8)
        matrix_base = cv2.merge([b, g, r])

        # Digital green scanline
        grid_step = 14
        offset_y = (frame_count * 3) % grid_step
        matrix_base[offset_y::grid_step, :, 1] = np.clip(matrix_base[offset_y::grid_step, :, 1] + 55, 0, 255)
        return matrix_base

    @classmethod
    def apply(cls, image: np.ndarray, filter_name: str, frame_count: int = 0) -> np.ndarray:
        """Dispatches to the selected filter by name."""
        name = filter_name.upper()
        if name == "THERMAL":
            return cls.apply_thermal(image)
        elif name == "SKETCH":
            return cls.apply_sketch(image)
        elif name == "PIXELATE":
            return cls.apply_pixelate(image)
        elif name == "NIGHT_VISION":
            return cls.apply_night_vision(image, frame_count)
        elif name == "X_RAY":
            return cls.apply_xray(image)
        elif name == "VINTAGE_SEPIA":
            return cls.apply_vintage_sepia(image)
        elif name == "MATRIX":
            return cls.apply_matrix(image, frame_count)
        return image
