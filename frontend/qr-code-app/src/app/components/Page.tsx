"use client";

import FormData from 'next/form'
import Dropdown from './Dropdown';
import ECLDropdown from './ECLDropdown';
import QRCode from './QRCode';
import { useState } from 'react';


export default function Page(){


    const[qrCodeInput, setQRCodeInput] = useState<{
        data: string,
        version: string,
        errorCorrectionLevel: string
    } | null>(null);

    function createQRCode(formData: FormData) {
        const rawFormData = {
            data : formData.get('qrCodeText') as string,
            version: document.getElementById("versionDropdown")?.textContent as string,
            errorCorrectionLevel : document.getElementById("eclDropdown")?.textContent as string
        }
        setQRCodeInput(rawFormData);
    }

    return (
        <div>
            <FormData action={createQRCode} className="max-w-xl mx-auto p-6 space-y-6">
                <div className="grid grid-cols-3 gap-4 items-center">
                    <label htmlFor='qrCodeText' className='text-right'>QR Code data</label>
                    <input placeholder="My QR code text..." 
                        type='text'
                        className="col-span-2 border px-3 py-2 rounded w-full input-highlight"
                        name='qrCodeText'
                        id='qrCodeText'></input>
                    <label htmlFor='version' className='text-right'>Version</label>
                    <div className='col-span-2'>
                        <Dropdown></Dropdown>
                    </div>
                    <label htmlFor='version' className='text-right'> Error Correction Level</label>
                    <div className='col-span-2'>
                        <ECLDropdown></ECLDropdown>
                    </div>
                    <div className="col-span-3 flex justify-center">
                        <button type='submit' 
                            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded">Create QR Code</button>
                    </div>
                </div>
            </FormData>
            <QRCode qrCodeData={qrCodeInput ?? undefined}></QRCode>
        </div>
    )
}