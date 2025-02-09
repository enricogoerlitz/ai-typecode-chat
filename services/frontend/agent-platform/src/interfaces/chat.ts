export interface IChat {
    _id: IOid;
    name: string;
    context: IContext;
    messages: IMessage[];
}

export interface IOid {
    $oid: string;
}

export interface IContext {
    deviceTypeCode: string;
}

export interface IMessage {
    _id: IOid | null;
    conversation: IConversation;
    createTimestamp: ITimestamp | null;
}

export interface IConversation {
    user: IUserOrAssistant;
    assistant: IUserOrAssistant;
}

export interface IUserOrAssistant {
    message: IMessageContent;
}

export interface IMessageContent {
    role: string;
    content: string;
}

export interface ITimestamp {
    $date: string;
}

export interface IMessagePUTRequestData {
    _id?: string | null;
    message: {
        type: "text";
        content: string;
    };
    requestParameters: {
        model: {
            name: string;
        };
        context: {
            deviceTypeCode: string;
        };
        chat: {
            responseType: "USE_DATA_ONLY" | "USE_HYBRID_PRIORITIZE_DATA" | "USE_HYBRID";
            messageHistoryCount: number;
        };
        webSearch: {
            enabled: boolean;
            optimizeWebSearchQuery: boolean;
            optimizeWebSearchResults: boolean;
            deepSearchEnabled: boolean;
            maxResultCount: number;
        };
        vectorSearch: {
            enabled: boolean;
            optimizeVectorSearchQuery: boolean;
            useWebSearchResults: boolean;
            maxResultCount: number;
        };
    };
}
