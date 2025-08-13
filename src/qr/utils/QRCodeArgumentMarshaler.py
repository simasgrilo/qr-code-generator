"""Utility Module to validate and process each of the arguments passed in the CLI"""

from typing import List


class QRCodeArgumentMarshaler:
    """Utility class to validate, process and marshal the arguments 
       to create a QR Code object
    """

    @staticmethod
    def process_args(cmd_input: List[str]):
        """Method to validate the arguments
           provided to the CLI tool
           they need to follow the following syntax:
           python main.py "HELLO WORLD" "c:\\my_files\\qr_code.png" L 4:
           
           1) "HELLO WORLD" is the message to be encoded 
           2) "c:\\my_files\\qr_code.png" is the directory where the QR code will be stored
           3) L is the error correction level
           4) 4 is the QR code version. This can be ommited, and the system
              will determine the minimum QR code version to encode the information

        Args:
            cmd_input (List[str]): arguments list
        """
        if len(cmd_input) != 3 and len(cmd_input) != 4:
            raise ValueError(("Invalid number of parameters. "
                              "Please check documentation for more details"))
        args = [cmd_input[0], cmd_input[1]]
        error_correction_level = cmd_input[2]
        args.append(error_correction_level)
        if error_correction_level not in ['L','Q','M','H']:
            raise ValueError("Invalid error correction level indicator. Values are L, Q, M or H")
        version = int(cmd_input[3])
        args.append(version)
        if not 1 <= version <= 40:
            raise ValueError("Invalid version. only values from 1 to 40 are accepted")
        return args
