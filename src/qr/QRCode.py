""" Module that contains the QRCode generation"""

from PIL import Image
from src.qr.QRCodeImage import QRCodeImage

class QRCode:
    """Class to model the QR code generation. 
        This is essentially the entry point
        of the QR code generation by delegating
        each algorithmic part of the underlying
        data structure, and finally creating the image
    """

    def __init__(self, path: str, qr_code_image_gen: QRCodeImage):
        self.path = path
        self.generator = qr_code_image_gen

    def create_qr_code(self, data: str):
        """Main method to generate the QR code symbol

        Args:
            data (str): String representation of the data to be encoded

        Raises:
            OSError: Raised if the output file cannot be opened
        """
        data_bitmap = self.generator.create_qr_code(data)
        qr_symbol_size = len(data_bitmap)
        # module_size = getattr(self.generator, "_module_size")
        try:
            qr_image = Image.new('1',
                                 (qr_symbol_size, qr_symbol_size)
                                 )
            for row in range(qr_symbol_size):
                for col in range(qr_symbol_size):
                    #pixel = (255, 255, 255) if data_bitmap[row][col] == 0 else (0, 0, 0)
                    qr_image.putpixel((row,col), 1 - data_bitmap[row][col])
            qr_image.save(self.path)
        except OSError as exc:
            raise OSError((f'Error upon saving file {self.path}. \
                 Probably the file cannot be saved (perhaps a protected directory?)')) from exc
