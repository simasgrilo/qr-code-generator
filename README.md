# QR Code Generator

## A Python-based app to generate QR codes as specified in [ISO 18004:2024](https://www.iso.org/standard/83389.html)

This application implements from scratch most of the the features of generating QR codes (excepting Structured append - see Section 8 of the ISO ). Although all major languages already have an embedded framework to allow genreation of QR codes in one of the 40+ formats, the objective of this implementation is to understand back and forth the ideas behing this product, which envolve error correction algorithms based on BCH codes and Galois Field, encoding and parsing of information and how we can deal with information being encoded into a 2D dimension structure.

QR Codes were invented by Denso Wave, a japanese company, to label car parts back in 1994. Consisting in a two-dimensional barcode-like structure, it allows encoding of data in many formats, like alphanumeric, numeric, bytes and Kanji (using Shift-JIS encoding) and nowadaws are used pretty much everywhere. ALl rights reserved to the respective owners.

The emphasis of this application is to implement the following products:

- [x] A QR code generation framework according with ISO 18004:2024
- [] A webapp to allow users to generate QR codes as necessary
- [] A FastAPI set of RESTful APIs to be the backbone of the webapp aforementioned

Currently, the application can be used in CLI as a standard Python app with the following arguments:

```Python
  # to create a QR code encoding the string HELLO WORLD in the directory, with error correction level L, version 4:
  python main_cli.py <data_to_be_encoded> <directory> <errorCorrectionLevel> <version> 

  # to only focus on the data being encoded and where the QR code image is to be saved:
  # this procedure will calculate the minimum QR code capacity that fits the data
  python main_cli.py <data_to_be_encoded> <directory> 

```

where:

```
<errorCorrectionLevel> is either L, H, M or Q
<version> is either an integer from 1 to 40 (current version supports only up to version 7)
```

Therefore, if the app is executed with `main_cli.py https://www.google.com/ qr_code.png`, it will generate the QR Code below:

<img src="assets/qr_code_sample_auto.png" width=100 heigh=100>

While executing it with `main_cli.py https://www.google.com/ qr_code.png L 4` yields the following QR code:

<img src="assets/qr_code_sample_4_L.png" width=100 heigh=100>

## Stack used

- Python 3.11.5
- FastAPI 0.116.1