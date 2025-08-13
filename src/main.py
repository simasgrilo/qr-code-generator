import sys
from src.qr.QRCodeImage import QRCodeImage
from src.qr.QRCodeEncoder import QRCodeEncoder
from src.qr.QRCodeInputAnalyzer import QRCodeInputAnalyzer
from src.qr.error.QRErrorCorrectionLevel import QRErrorCorrectionLevel
from src.qr.QRCodeFormatInfo import QRCodeFormatInfoEncoder
from src.qr.QRCode import QRCode
from src.qr.utils.QRCodeArgumentMarshaler import QRCodeArgumentMarshaler

def main():
    """ Main method to trigger the QR Code generation
        This is a temporary entry point, as this will
        soon be replaced by a FastAPI API instantiation
        and a CLI tool is no longer to be supported
    
        usage:
        python main.py "HELLO WORLD" "c:\\my_files\\qr_code.png" L 4 or
        python main.py "HELLO WORLD "c:\\my_files\\qr_code.png" - to be supported soon
    """ 
    args = sys.argv[1::]
    marshaled_args = QRCodeArgumentMarshaler.process_args(args)
    if len(marshaled_args) != 4:
        raise ValueError("Invalid arguments provided to the CLI. Please check documentation")
    if len(marshaled_args) == 4:
        data = marshaled_args[0]
        path = marshaled_args[1]
        error_correctioh_level = QRErrorCorrectionLevel(marshaled_args[2])
        version = marshaled_args[3]
        qr_encoder = QRCodeEncoder(version, error_correctioh_level, QRCodeInputAnalyzer())
        qr_format_encoder = QRCodeFormatInfoEncoder(getattr(qr_encoder, 'error_correction_level'))
        qr_code_gen = QRCodeImage(version, qr_encoder, qr_format_encoder, 1)
        qr = QRCode(path, qr_code_gen)
        qr.create_qr_code(data)

main()
