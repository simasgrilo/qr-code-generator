""" Main entry point for the QR code generator through a Command-line Interface"""

import sys
from src.qr.utils.QRCodeArgumentMarshaler import QRCodeArgumentMarshaler

def main():
    """ Main method to trigger the QR Code generation
        This is a temporary entry point, as this will
        soon be replaced by a FastAPI API instantiation
        and a CLI tool is no longer to be supported
    
        usage:
        - python main.py "HELLO WORLD" "c:\\my_files\\qr_code.png" L 4
        - python main.py "HELLO WORLD "c:\\my_files\\qr_code.png"
        the second option will determine automatically the minimum QR code version
        and error correction code that fits the message to be encoded
    """
    args = sys.argv[1::]
    QRCodeArgumentMarshaler.generate_qr_code(args)

if __name__ == '__main__':
    main()
