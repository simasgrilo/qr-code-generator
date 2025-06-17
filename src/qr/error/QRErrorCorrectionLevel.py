import enum


class QRErrorCorrectionLevel(enum.Enum):
    """
    Enum representing the QR Code error correction levels.
    """
    L = "L"  # Low (7% of codewords can be restored)
    M = "M"  # Medium (15% of codewords can be restored)
    Q = "Q"  # Quartile (25% of codewords can be restored)
    H = "H"  # High (30% of codewords can be restored)

    def __str__(self):
        return self.value