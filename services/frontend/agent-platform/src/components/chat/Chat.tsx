import React, { useCallback, useContext, useEffect, useRef, useState } from "react"
import { ChatContext, IChatContext } from "../../context/chatContext.tsx";
import ReactMarkdown from "react-markdown"
import { RiChatAiFill } from "react-icons/ri";
import { IoIosSettings, IoMdSend } from "react-icons/io";
import { IoClose, IoGlobeOutline, IoDocument } from "react-icons/io5";
import { FaRobot } from "react-icons/fa6";
import { FaSpinner } from "react-icons/fa";



import "./Chat.scss"

const Chat: React.FC = () => {
    const {
        isChatLoading,
        typeCode,
        showChat,
        chat,
        chatRequest,
        setMessage,
        setShowChat,
        sendMessage
    } = useContext(ChatContext) as IChatContext;
    const [showChatSettings, setShowChatSettings] = useState(false)
    const promptInputRef = useRef<HTMLTextAreaElement | null>(null)
    const messagesContainerRef = useRef<HTMLDivElement | null>(null);


    const scrollMessagesContainer = useCallback(() => {
        if (!messagesContainerRef.current || !chat) {
            return;
        }
        const scrollTop = messagesContainerRef.current.scrollTop;
        const scrollHeight = messagesContainerRef.current.scrollHeight;
        const differenz = scrollHeight - scrollTop;

        let lastMessageIndex = chat.messages.length - 1;
        if (lastMessageIndex < 0) return;

        const isAssistantMessageEmpty = chat.messages[lastMessageIndex].conversation.assistant.message.content === "";
        if (!isAssistantMessageEmpty && differenz > 750) return;

        messagesContainerRef.current.scrollTo({
            top: messagesContainerRef.current.scrollHeight,
            behavior: "smooth"
        });

        return;
    }, [messagesContainerRef, chat]);


    useEffect(() => {
        scrollMessagesContainer()
    }, [chat, chatRequest, scrollMessagesContainer]); 

    function getPromptLineBreaks() {
        const maxRowCount = 5;
        
        const textarea = promptInputRef.current;
        if (textarea === null || textarea.value === "") return 1;

        const baseHeightRowOne = 28;
        const rowHeight = 19;

        const result = Math.round((textarea.scrollHeight - baseHeightRowOne) / rowHeight) + 1;

        return result > maxRowCount ? maxRowCount : result
    }

    const handleSubmitMessage = () => {
        sendMessage()
    }

    const handleKeyDownSubmitMessage = (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
        if (event.key !== "Enter" || event.shiftKey) return;
        event.preventDefault();
        handleSubmitMessage();
    };

    return (
        <>
            <button id="chat-button" onClick={() => {
                if (!showChat) {
                    promptInputRef.current?.focus()
                }
                setShowChat(!showChat);
            }}>
                <RiChatAiFill />
            </button>
            <div
                id="chat-window"
                className={showChat ? "" : "hidden"}
            >
                <div className="chat-window__header">
                    <h4 className="chat-window__header__title"><FaRobot />Chatbot{typeCode ? ` (${typeCode.Typcode})` : ""}</h4>
                    <button className="chat-window__header__close" onClick={() => setShowChat(false)}>
                        <IoClose />
                    </button>
                </div>
                <div className="chat-window__messages" ref={messagesContainerRef}>
                    <ul>
                        {chat?.messages.map((msg, msgIdx) => (
                            <React.Fragment key={msgIdx}>
                                <li className="chat-window__messages__message user">
                                    <p className="chat-window__messages__message__content user">
                                        {msg.conversation.user.message.content}
                                    </p>
                                </li>
                                <li className="chat-window__messages__message assistant">
                                    <ReactMarkdown className="chat-window__messages__message__content assistant">
                                        {msg.conversation.assistant.message.content}
                                    </ReactMarkdown>
                                </li>
                            </React.Fragment>
                        ))}
                    </ul>
                </div>
                <div
                    className="chat-window__footer"
                    onClick={() => promptInputRef.current?.focus()}
                >
                    <textarea
                        id="prompt-input"
                        ref={promptInputRef}
                        autoFocus={true}
                        rows={getPromptLineBreaks()}
                        className="chat-window__footer__input"
                        value={chatRequest.message.content}
                        onChange={(e) => setMessage(e.target.value)}
                        onKeyDown={handleKeyDownSubmitMessage}
                        placeholder="Ask me any question &nbsp;🚀"
                    />
                    <div className="chat-window__footer__utils">
                        <button className="chat-settings-button" onClick={(e) => {
                            setShowChatSettings(true);
                            e.stopPropagation();
                        }}>
                            <IoIosSettings />
                        </button>
                        <button className="active">
                            <IoGlobeOutline />
                            Suche
                        </button>
                        <button>
                            <IoDocument />
                            Dok. durchsuchen
                        </button>
                        <button className="chat-send-button" onClick={handleSubmitMessage}>
                            {isChatLoading ? <FaSpinner className="spinner" /> : <IoMdSend />}
                            
                        </button>
                    </div>
                </div>
            </div>
            <div id="chat-settings" className={showChatSettings ? "" : "hidden"}>
                Settings
                {/* hier auch Kontext rein! */}
            </div>
        </>
    )
}

export default Chat;
