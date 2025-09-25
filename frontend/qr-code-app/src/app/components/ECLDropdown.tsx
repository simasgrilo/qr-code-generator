'use client';
import { useState } from "react";
import { FaCaretDown } from "react-icons/fa";

export default function Dropdown() {
    
    const [ isOpen, setIsOpen ] = useState(false);
    const [ selectedECL, setSelectedVersion ] = useState('Select Error Correction Level');

    const eclList = ['L','H','Q','M'];

    const toggleDown = () => {
        setIsOpen(!isOpen);
    }

    const handleSelect = (version: string) => {
        setSelectedVersion(version);
        setIsOpen(false);
    }

    return (
        <div className="flex justify-center ">
            <div className="relative inline-block text-left">
                <button id="eclDropdown" type="button" className="inline-flex justify-center w-full rounded-md 
                                                 border border-gray-300 shadow-sm px-4 py-2 bg-white text-sm font-medium text-black hover:bg-gray-50"
                                      onClick={toggleDown}>
                {selectedECL}
                <FaCaretDown className="ml-2"/>
                </button>
            {isOpen && (
                <div className="origin-top-right absolute right-0 mt-2 w-56
                                rounded-md shadow-lg bg-white ring-1 ring-black
                                ring-opacity-5 focus:outline-none z-50">
                    <div className="py-1">
                        {eclList.map((ecl, index) => (
                            <a key={index} href="#" className="block px-4 py-2 text-sm text-black hover:bg-gray-100"
                               onClick={() => {handleSelect(ecl)}}>
                                {ecl}
                            </a>
                        ))}
                    </div>
                </div>
            )}
            </div>
        </div>
    )

}
