import "./App.css"
import React, { useState } from "react";
import ReactMarkdown from "react-markdown"
import { FaComments } from 'react-icons/fa';



const App = () => {
  const [chatQuestion, setChatQuestion] = useState("");
  const [chatResponse, setChatResponse] = useState("");

  const askChat = async () => {
    setChatResponse(""); // Reset previous responses
      const response = await fetch('http://localhost:8000/api/v1/chats/67a71e1201a11db986651334/messages', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          //"_id": "67a762a364ebc22659684ba7", // to update a message
          "message": {
            "type": "text",
            "content": chatQuestion
          },
          "requestParameters": {
            "model": {
              "name": "gpt-4o"
            },
                "context": {
                    "deviceTypeCode": "WFHD0001"
                },
            "chat": {
                    "responseType": "USE_HYBRID", // USE_DATA_ONLY, USE_HYBRID_PRIORITIZE_DATA, USE_HYBRID
              "messageHistoryCount": 5
            },
            "webSearch": {
              "enabled": false,
              "optimizeWebSearchQuery": true,
                    "optimizeWebSearchResults": true,
              "deepSearchEnabled": true,
              "maxResultCount": 5
            },
            "vectorSearch": {
                    "enabled": false,
              "optimizeVectorSearchQuery": true,
              "useWebSearchResults": true,
              "maxResultCount": 5
            }
          }
        }),
      })
      const reader = response.body?.getReader();
      const decoder = new TextDecoder('utf-8');

      let buffer = '';

      while (true) {
        const { done, value } = await reader!.read();
        if (done) break;
        
        buffer += decoder.decode(value, { stream: true });
        
        let boundary = buffer.indexOf('\n');

        while (boundary !== -1) {
          const chunk = buffer.slice(0, boundary);
          buffer = buffer.slice(boundary + 1);

          const chunkJSON = JSON.parse(chunk)
          setChatResponse(chunkJSON.message)

          // if (chunk.startsWith('data: ')) {
          //   const message = chunk.slice(6);
          //   setChatResponse((prev) => [...prev, message]);
          // }

          boundary = buffer.indexOf('\n');
      }
    }
  };

  return (
    <div className="App">
      <input type="text" onChange={(e) => setChatQuestion(e.target.value)} />
      <p>{chatQuestion}</p>
      <button onClick={askChat}>Submit</button>
      <div className="chat">
        <h1>Chat Response:</h1>
        <div>
          <FaComments />
        </div>
        <ReactMarkdown>{chatResponse}</ReactMarkdown>
      </div>
    </div>
  );
};

export default App;
