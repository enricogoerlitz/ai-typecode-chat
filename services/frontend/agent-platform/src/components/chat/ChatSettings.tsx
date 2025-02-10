import React, { useContext } from "react"
import { ChatContext, IChatContext } from "../../context/chatContext.tsx";
import { IoClose } from "react-icons/io5";
import ReactMarkdown from "react-markdown";

import "./Chat.scss"

interface IChatSettings {
    setShow: (show: boolean) => void;
    show: boolean;
}

const ChatSettings: React.FC<IChatSettings> = ({ show, setShow }) => {
    const {
        chatRequest,
        setChatRequest
    } = useContext(ChatContext) as IChatContext;

    const req = chatRequest.requestParameters;

    const reqString = "```json\n" + JSON.stringify(chatRequest, null, 4) + "\n```"

    return (
        <div id="chat-settings" className={show ? "" : "hidden"}>
            <div className="chat-settings__header">
                <h4 className="chat-settings__header__title">Chat Settings</h4>
                <button className="chat-settings__header__close" onClick={() => setShow(false)}>
                    <IoClose />
                </button>
            </div>
            <div className="scroll">
                <div className="chat-settings__sections">
                    <div className="chat-settings__sections__section">
                        <h5 className="chat-settings__sections__section__header">OpenAI Model</h5>
                        <div className="chat-settings__sections__section__content">
                            <span className="label">Model:</span>
                            <input
                                type="text"
                                className="setting text"
                                value={req.model.name}
                                onChange={(e) => {
                                    const updated = {...chatRequest}
                                    updated.requestParameters.model.name = e.target.value;
                                    setChatRequest(updated)
                                }}
                            />
                        </div>
                    </div>
                    <div className="chat-settings__sections__section">
                        <h5 className="chat-settings__sections__section__header">Chat</h5>
                        <div className="chat-settings__sections__section__content">
                            <span className="label">Response type:</span>
                            <select
                                className="setting select"
                                value={req.chat.responseType}
                                onChange={(e) => {
                                    const updated = {...chatRequest}
                                    updated.requestParameters.chat.responseType = e.target.value as any;
                                    setChatRequest(updated)
                                }}
                            >
                                <option>USE_DATA_ONLY</option>
                                <option>USE_HYBRID_PRIORITIZE_DATA</option>
                                <option>USE_HYBRID</option>
                            </select>
                        </div>
                        <div className="chat-settings__sections__section__content">
                            <span className="label">Message history</span>
                            <input
                                type="number"
                                className="setting number"
                                value={req.chat.messageHistoryCount}
                                onChange={(e) => {
                                    const updated = {...chatRequest}
                                    updated.requestParameters.chat.messageHistoryCount = parseInt(e.target.value);
                                    setChatRequest(updated)
                                }}
                            />
                        </div>
                    </div>
                    <div className="chat-settings__sections__section">
                        <h5 className="chat-settings__sections__section__header">Document search</h5>
                        <div className="chat-settings__sections__section__content">
                            <span className="label">Enabled:</span>
                            <label className="switch">
                                <input
                                    type="checkbox"
                                    checked={req.vectorSearch.enabled}
                                    onChange={(e) => {
                                        const updated = {...chatRequest}
                                        updated.requestParameters.vectorSearch.enabled = e.target.checked;
                                        setChatRequest(updated)
                                    }}
                                />
                                <span className="slider"></span>
                            </label>
                        </div>
                        {req.vectorSearch.enabled && (
                            <>
                                <div className="chat-settings__sections__section__content">
                                    <span className="label">optimizeVectorSearchQuery:</span>
                                    <label className="switch">
                                        <input
                                            type="checkbox"
                                            checked={req.vectorSearch.optimizeVectorSearchQuery}
                                            onChange={(e) => {
                                                const updated = {...chatRequest}
                                                updated.requestParameters.vectorSearch.optimizeVectorSearchQuery = e.target.checked;
                                                setChatRequest(updated)
                                            }}
                                        />
                                        <span className="slider"></span>
                                    </label>
                                </div>
                                <div className="chat-settings__sections__section__content">
                                    <span className="label">useWebSearchResults:</span>
                                    <label className="switch">
                                        <input
                                            type="checkbox"
                                            checked={req.vectorSearch.useWebSearchResults}
                                            onChange={(e) => {
                                                const updated = {...chatRequest}
                                                updated.requestParameters.vectorSearch.useWebSearchResults = e.target.checked;
                                                setChatRequest(updated)
                                            }}
                                        />
                                        <span className="slider"></span>
                                    </label>
                                </div>
                                <div className="chat-settings__sections__section__content">
                                    <span className="label">maxResultCount:</span>
                                    <input
                                        type="number"
                                        className="setting number"
                                        value={req.vectorSearch.maxResultCount}
                                        onChange={(e) => {
                                            const updated = {...chatRequest}
                                            updated.requestParameters.vectorSearch.maxResultCount = parseInt(e.target.value);
                                            setChatRequest(updated)
                                        }}
                                    />
                                </div>
                            </>
                        )}
                        
                    </div>
                    <div className="chat-settings__sections__section">
                        <h5 className="chat-settings__sections__section__header">Web search</h5>
                        <div className="chat-settings__sections__section__content">
                            <span className="label">Enabled:</span>
                            <label className="switch">
                                <input
                                    type="checkbox"
                                    checked={req.webSearch.enabled}
                                    onChange={(e) => {
                                        const updated = {...chatRequest}
                                        updated.requestParameters.webSearch.enabled = e.target.checked;
                                        setChatRequest(updated)
                                    }}
                                />
                                <span className="slider"></span>
                            </label>
                        </div>

                        {req.webSearch.enabled && (
                            <>
                                <div className="chat-settings__sections__section__content">
                                    <span className="label">optimizeWebSearchQuery:</span>
                                    <label className="switch">
                                        <input
                                            type="checkbox"
                                            checked={req.webSearch.optimizeWebSearchQuery}
                                            onChange={(e) => {
                                                const updated = {...chatRequest}
                                                updated.requestParameters.webSearch.optimizeWebSearchQuery = e.target.checked;
                                                setChatRequest(updated)
                                            }}
                                        />
                                        <span className="slider"></span>
                                    </label>
                                </div>
                                <div className="chat-settings__sections__section__content">
                                    <span className="label">optimizeWebSearchResults:</span>
                                    <label className="switch">
                                        <input
                                            type="checkbox"
                                            checked={req.webSearch.optimizeWebSearchResults}
                                            onChange={(e) => {
                                                const updated = {...chatRequest}
                                                updated.requestParameters.webSearch.optimizeWebSearchResults = e.target.checked;
                                                setChatRequest(updated)
                                            }}
                                        />
                                        <span className="slider"></span>
                                    </label>
                                </div>
                                <div className="chat-settings__sections__section__content">
                                    <span className="label">deepSearchEnabled:</span>
                                    <label className="switch">
                                        <input
                                            type="checkbox"
                                            checked={req.webSearch.deepSearchEnabled}
                                            onChange={(e) => {
                                                const updated = {...chatRequest}
                                                updated.requestParameters.webSearch.deepSearchEnabled = e.target.checked;
                                                setChatRequest(updated)
                                            }}
                                        />
                                        <span className="slider"></span>
                                    </label>
                                </div>
                                <div className="chat-settings__sections__section__content">
                                    <span className="label">maxResultCount:</span>
                                    <input
                                        type="number"
                                        className="setting number"
                                        value={req.webSearch.maxResultCount}
                                        onChange={(e) => {
                                            const updated = {...chatRequest}
                                            updated.requestParameters.webSearch.maxResultCount = parseInt(e.target.value);
                                            setChatRequest(updated)
                                        }}
                                    />
                                </div>
                            </>
                        )}
                    </div>
                    <div className="chat-settings__sections__section">
                        <h5 className="chat-settings__sections__section__header">Request</h5>
                        <div className="chat-settings__sections__request-section">
                            <ReactMarkdown>{reqString}</ReactMarkdown>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default ChatSettings;
