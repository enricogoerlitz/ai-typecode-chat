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
    _id: IOid;
    conversation: IConversation;
    createTimestamp: ITimestamp;
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
