import React, { createContext, useState, useEffect } from 'react';
import { IReactNodeChildren } from '../interfaces/component.ts';
import { IDeviceType } from '../interfaces/imt.ts';
import deviceTypeData from "../assets/deviceTypesData.json";
import { IChat, IMessage, IMessagePUTRequestData } from '../interfaces/chat.ts';
import chatRESTService from '../services/chatService.ts';


const getDefaultChatRequest = (): IMessagePUTRequestData => {
    return {
        "_id": null,
        "message": {
            "type": "text",
            "content": ""
        },
        "requestParameters": {
            "model": {
                "name": "gpt-4o"
            },
            "context": {
                "deviceTypeCode": ""
            },
            "chat": {
                "responseType": "USE_HYBRID", // USE_DATA_ONLY, USE_HYBRID_PRIORITIZE_DATA, USE_HYBRID
                "messageHistoryCount": 5
            },
            "webSearch": {
                "enabled": false,
                "optimizeWebSearchQuery": true,
                "optimizeWebSearchResults": true,
                "deepSearchEnabled": false,
                "maxResultCount": 5
            },
            "vectorSearch": {
                "enabled": false,
                "optimizeVectorSearchQuery": true,
                "useWebSearchResults": true,
                "maxResultCount": 5
            }
        }
    }
}

const getNewMessage = (userMessage: string): IMessage => {
    return {
        _id: null,
        conversation: {
            user: {
                message: {
                    role: "user",
                    content: userMessage
                }
            },
            assistant: {
                message: {
                    role: "assistant",
                    content: ""
                }
            }
        },
        createTimestamp: null
    }
}

const getEmptyChat = (
    id: string,
    name: string,
    deviceTypeCode: string | null
): IChat => {
    return {
        _id: {
            $oid: id
        },
        name: name,
        context: {
            deviceTypeCode: deviceTypeCode || ""
        },
        messages: []
    }
}

export interface IChatContext {
    isChatLoading: boolean;
    chat: IChat | null;
    chatRequest: IMessagePUTRequestData;
    setMessage: (message: string) => void;
    setChatRequest: (chatRequest: IMessagePUTRequestData) => void;
    sendMessage: () => Promise<void>;

    typeCode: IDeviceType | null;
    setTypeCodeID: (typeCodeID: string | null) => void;

    showChat: boolean;
    setShowChat: (show: boolean) => void;
}

export const ChatContext = createContext<IChatContext | undefined>(undefined);

export const ChatProvider: React.FC<IReactNodeChildren> = ({ children }) => {
    const [isChatLoading, setIsChatLoading] = useState(false);
    const [showChat, setShowChat] = useState(false);
    const [typeCode, setTypeCode] = useState<IDeviceType | null>(null);
    const [typeCodeID, setTypeCodeID] = useState<string | null>(null);
    let [chat, setChat] = useState<IChat | null>(null);
    const [chatRequest, setChatRequest] = useState<IMessagePUTRequestData>(getDefaultChatRequest());

    useEffect(() => {

        const fetchDeviceType = () => {
            const filteredData: IDeviceType = (deviceTypeData as Array<any>).find(item => item.Typcode === typeCodeID);
            setTypeCode(filteredData);
        }

        if (typeCodeID !== undefined) {
            fetchDeviceType()
        }

    }, [typeCodeID, setTypeCodeID]);

    const _setChatResponseStream = (message: string): void => {
        const updatedChat = {...chat} as IChat;

        const messageIndex = updatedChat.messages!.length - 1;

        updatedChat.messages![messageIndex].conversation.assistant.message.content = message

        setChat(updatedChat);
    }

    const setMessage = (message: string): void => {
        const updatedRequest = {...chatRequest};

        updatedRequest.message.content = message;

        setChatRequest(updatedRequest);
    }

    const sendMessage = async (): Promise<void> => {
        setIsChatLoading(true)
        try {
            if (chat === null) {
                // create new chat
                const chatName = "untitled";
                const chatID = await chatRESTService.putChat(chatName, typeCodeID);
                if (chatID === null) return;
                chat = getEmptyChat(chatID, chatName, typeCodeID);
            }
    
            const message = getNewMessage(chatRequest.message.content);
            chat.messages.push(message);
            setChat({...chat});
            await chatRESTService.putMessageStream(chat!._id.$oid, chatRequest, _setChatResponseStream);
            setMessage("");
        } finally {
            setIsChatLoading(false);
        }
    };

    const changeTypeCodeID = (id: string | null) => {
        setTypeCodeID(id);
        setChat(null);
    }


    return (
        <ChatContext.Provider value={{ 
            isChatLoading,
            setMessage,
            showChat, setShowChat,
            typeCode,
            setTypeCodeID: changeTypeCodeID,
            chat, sendMessage,
            chatRequest, setChatRequest
         }}>
            {children}
        </ChatContext.Provider>
    );
}