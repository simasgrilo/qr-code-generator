"use client";
import { useState, useEffect } from "react";
import Image from "next/image";


export interface QRCodeStruct {
    qrCodeData? : {
        data: string;
        version: string;
        errorCorrectionLevel: string;
    };
}

export default function QRCode( { qrCodeData } : QRCodeStruct) {

    const [ qrCode, setQRCode ] = useState<string | null>(null);
    const [ loading, setLoading ] = useState<boolean>(true)

    async function fetchQRCode( data : {
            data : string,
            version : string,
            errorCorrectionLevel: string
    }) {
        try {
            const qrCodeResponse = await fetch("http://localHost:8000/qr", {
                method: 'POST',
                headers: {
                    'Content-Type': "application/json"
                },
                body: JSON.stringify(data)
            });
            if (!qrCodeResponse.ok) {
                throw new Error(`Failed to fetch QR Code: status code ${qrCodeResponse.status}, message: ${qrCodeResponse.statusText}`);
            }
            const qrCodeBlob = await qrCodeResponse.blob();
            const qrCodeUrl = URL.createObjectURL(qrCodeBlob);
            setQRCode(qrCodeUrl);
        }
        catch (err) {
            alert(err);
            return;
        }
        finally {
            setLoading(false);
        }
    }
    
    function downloadHandler() {
        const downloadLink = document.createElement("a");
        downloadLink.href = qrCode;
        downloadLink.download = 'qr-code.png';
        document.body.appendChild(downloadLink);
        downloadLink.click();
        document.body.removeChild(downloadLink);
    }


    useEffect(() => {
        if (qrCodeData) {
            fetchQRCode(qrCodeData);
        }
    }, [qrCodeData]);

    return (
        <div className='mt-6 text-center'>
            {loading && <p>Your QR Code will appear here...</p>}
            {qrCode && 
            <div className="col-span-3 justify-stretch">
                <Image 
                    src={qrCode}
                    alt="QR Code"
                    className="mx-auto border rounded"
                    width='150'
                    height='150'>
                </Image> 
                <button type='submit' onClick={downloadHandler}
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded">
                    Download
                </button>
            </div>
            }
        </div>
    );
}