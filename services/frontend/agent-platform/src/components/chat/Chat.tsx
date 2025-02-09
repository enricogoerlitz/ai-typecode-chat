import React, { useContext, useRef, useState } from "react"
import { ChatContext, IChatContext } from "../../context/chatContext.tsx";
import ReactMarkdown from "react-markdown"
import { RiChatAiFill } from "react-icons/ri";
import { IoIosSettings, IoMdSend } from "react-icons/io";
import { IoClose, IoGlobeOutline, IoDocument, IoExpandSharp } from "react-icons/io5";
import { FaComments } from 'react-icons/fa';
import { FaRobot } from "react-icons/fa6";



import "./Chat.scss"
import { IChat } from "../../interfaces/chat.ts";

const assistantExample = `
# My Markdown Guide

Welcome to my **Markdown** guide!

## Table of Contents
1. [Introduction](#introduction)
2. [Formatting Text](#formatting-text)
3. [Lists](#lists)
4. [Links](#links)
5. [Images](#images)

---

## Introduction
Markdown is a lightweight markup language used to format plain text. It's simple, easy to learn, and widely used in documentation.

## Formatting Text
You can **bold** text by using

You can *italicize* text by using


## Long string
Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.   

Duis autem vel eum iriure dolor in hendrerit in vulputate velit esse molestie consequat, vel illum dolore eu feugiat nulla facilisis at vero eros et accumsan et iusto odio dignissim qui blandit praesent luptatum zzril delenit augue duis dolore te feugait nulla facilisi. Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam erat volutpat.   

Ut wisi enim ad minim veniam, quis nostrud exerci tation ullamcorper suscipit lobortis nisl ut aliquip ex ea commodo consequat. Duis autem vel eum iriure dolor in hendrerit in vulputate velit esse molestie consequat, vel illum dolore eu feugiat nulla facilisis at vero eros et accumsan et iusto odio dignissim qui blandit praesent luptatum zzril delenit augue duis dolore te feugait nulla facilisi.   

Nam liber tempor cum soluta nobis eleifend option congue nihil imperdiet doming id quod mazim placerat facer possim assum. Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam erat volutpat. Ut wisi enim ad minim veniam, quis nostrud exerci tation ullamcorper suscipit lobortis nisl ut aliquip ex ea commodo consequat.   

Duis autem vel eum iriure dolor in hendrerit in vulputate velit esse molestie consequat, vel illum dolore eu feugiat nulla facilisis.   

At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, At accusam aliquyam diam diam dolore dolores duo eirmod eos erat, et nonumy sed tempor et et invidunt justo labore Stet clita ea et gubergren, kasd magna no rebum. sanctus sea sed takimata ut vero voluptua. est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat.   

Consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus.   

Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.   

Duis autem vel eum iriure dolor in hendrerit in vulputate velit esse molestie consequat, vel illum dolore eu feugiat nulla facilisis at vero eros et accumsan et iusto odio dignissim qui blandit praesent luptatum zzril delenit augue duis dolore te feugait nulla facilisi. Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam erat volutpat.   

Ut wisi enim ad minim veniam, quis nostrud exerci tation ullamcorper suscipit lobortis nisl ut aliquip ex ea commodo consequat. Duis autem vel eum iriure dolor in hendrerit in vulputate velit esse molestie consequat, vel illum dolore eu feugiat nulla facilisis at vero eros et accumsan et iusto odio dignissim qui blandit praesent luptatum zzril delenit augue duis dolore te feugait nulla facilisi.   

Nam liber tempor cum soluta nobis eleifend option congue nihil imperdiet doming id quod mazim placerat facer possim assum. Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam erat volutpat. Ut wisi enim ad minim veniam, quis nostrud exerci tation ullamcorper suscipit lobortis nisl ut aliquip ex ea commodo
`;

const chat: IChat = {
    _id: {
        $oid: "id"
    },
    name: "bubable",
    context: {
        deviceTypeCode: "blub"
    },
    messages: [
        {
            _id: {
                $oid: "message_id"
            },
            conversation: {
                user: {
                    message: {
                        role: "user",
                        content: "Welche Desinfektionsmittel sind für die Reinigung des Geräts zugelassen?"
                    }
                },
                assistant: {
                    message: {
                        role: "assistant",
                        content: assistantExample
                    }
                }
            },
            createTimestamp: {
                $date: "2025-01-01"
            }
        }
    ]
}


const Chat: React.FC = () => {
    const { typeCode, showChat, setShowChat } = useContext(ChatContext) as IChatContext;
    const [showChatSettings, setShowChatSettings] = useState(false)
    const [prompt, setPrompt] = useState("")
    const promptInputRef = useRef<HTMLTextAreaElement | null>(null)

    function getPromptLineBreaks() {
        const maxRowCount = 5;
        
        const textarea = promptInputRef.current;
        if (textarea === null || textarea.value === "") return 1;

        const baseHeightRowOne = 28;
        const rowHeight = 19;

        const result = Math.round((textarea.scrollHeight - baseHeightRowOne) / rowHeight) + 1;

        console.log(result, textarea.scrollHeight)
        return result > maxRowCount ? maxRowCount : result
    }

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
                onClick={() => promptInputRef.current?.focus()}
            >
                <div className="chat-window__header">
                    <h4 className="chat-window__header__title"><FaRobot />Chatbot{typeCode ? ` (${typeCode.Typcode})` : ""}</h4>
                    <button className="chat-window__header__close" onClick={() => setShowChat(false)}>
                        <IoClose />
                    </button>
                </div>
                <div className="chat-window__messages">
                    <ul>
                        {chat.messages.map(msg => (
                            <React.Fragment key={msg._id.$oid}>
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
                <div className="chat-window__footer">
                    <textarea
                        id="prompt-input"
                        ref={promptInputRef}
                        autoFocus={true}
                        rows={getPromptLineBreaks()}
                        className="chat-window__footer__input"
                        value={prompt}
                        onChange={(e) => setPrompt(e.target.value)}
                        placeholder="Ask me any question &nbsp;🚀"
                    />
                    <div className="chat-window__footer__utils">
                        <button className="chat-settings-button" onClick={(e) => e.stopPropagation()}>
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
                        <button className="chat-send-button">
                            <IoMdSend />
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
