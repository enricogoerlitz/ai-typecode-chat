import React, { createContext, useState, useEffect } from 'react';
import { IReactNodeChildren } from '../interfaces/component.ts';
import { IDeviceType } from '../interfaces/imt.ts';
import deviceTypeData from "../assets/deviceTypesData.json";

export interface IChatContext {
    typeCode: IDeviceType | null;
    setTypeCodeID: (typeCodeID: string | null) => void;

    showChat: boolean;
    setShowChat: (show: boolean) => void;
}

export const ChatContext = createContext<IChatContext | undefined>(undefined);

export const ChatProvider: React.FC<IReactNodeChildren> = ({ children }) => {
    const [showChat, setShowChat] = useState(false);
    const [typeCode, setTypeCode] = useState<IDeviceType | null>(null);
    const [typeCodeID, setTypeCodeID] = useState<string | null>(null);

    useEffect(() => {

        const fetchDeviceType = () => {
            const filteredData: IDeviceType = (deviceTypeData as Array<any>).find(item => item.Typcode === typeCodeID);
            setTypeCode(filteredData);
        }

        if (typeCodeID !== undefined) {
            fetchDeviceType()
        }

    }, [typeCodeID, setTypeCodeID]);


    return (
        <ChatContext.Provider value={{ 
            showChat, setShowChat,
            typeCode, setTypeCodeID
         }}>
            {children}
        </ChatContext.Provider>
    );
}