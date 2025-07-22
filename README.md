# QR Code Generator

## A Python-based app to generate QR code generation as specified in ISO 18004:2015

This application implements from scratch all the features of generating QR codes. Although all major languages already have an embedded framework to allow genreation of QR codes in one of the 40+ formats, the objective of this implementation is to understand back and forth the ideas behing this product.

QR Codes were invented by Denso Wave, a japanese company, to label car parts back in 1994. Consisting in a two-dimensional barcode-like structure, it allows encoding of data in many formats, like alphanumeric, numeric, bytes and Kanji (using Shift-JIS encoding) and nowadaws are used pretty much everywhere.

The emphasis of this application is to implement the following products:

- A QR code generation framework according with ISO 18004:2015
- A webapp to allow users to generate QR codes as necessary
- A FastAPI set of RESTful APIs to be the backbone of the webapp aforementioned

Therefore, the release will be split into three parts, starting with the QR code above.

I am currently halfway the first step, currently implementing the image generation algorithm.

## Stack used

- Python 3.11.5
- FastAPI 0.116.1