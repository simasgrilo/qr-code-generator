
import FormData from 'next/form'
import Dropdown from './Dropdown';
import ECLDropdown from './ECLDropdown';


export default function Page(){

    async function createQRCode(formData: FormData) {
        "use server";

        const rawFormData = {
            qrCodeText : formData.get('qrCodeText'),
            version : formData.get('version'),
            errorCorrectionLevel : formData.get("errorCorrectionLevel")

        }
        console.log("bitch", rawFormData);
    }

    return (
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
    )
}