import axios from "axios";
import RESTService, { getAxiosEmptyConfig } from "./abstract.ts";
import { IMessagePUTRequestData, IStreamMessageResponse } from "../interfaces/chat";


const BASE_ROUTE = "/api/v1";
const ROUTE = "/chats";


class ChatRESTService extends RESTService {

    public async putChat(name: string, typeCode: string | null): Promise<string | null> {
        try {
            const data = {
                "name": name,
                "typeCode": typeCode
            }
            const url = this.url(ROUTE);
            const resp = await axios.put(url, data, getAxiosEmptyConfig());

            if (resp.status !== 200) {
                console.error(resp.data.message)
                return null;
            }

            return resp.data._id;
        } catch(err) {
            console.error(err)
            return null;
        }
    }

    public async putMessageStream(
        chatID: string,
        requestData: IMessagePUTRequestData,
        setChatResponse: (message: IStreamMessageResponse) => void
    ): Promise<boolean> {
        const url = `${this.url(ROUTE, chatID)}/messages`;
        try {

            // "http://localhost:8000/api/v1/chats/67a71e1201a11db986651334/messages"
            const response = await fetch(url, {
                method: "PUT",
                headers: {
                "Content-Type": "application/json",
                },
                body: JSON.stringify(requestData)
            });

            const reader = response.body?.getReader();
            const decoder = new TextDecoder("utf-8");
        
            let buffer = "";
        
            while (true) {
                const { done, value } = await reader!.read();
                if (done) break;
                
                buffer += decoder.decode(value, { stream: true });
                
                let boundary = buffer.indexOf("\n");
        
                while (boundary !== -1) {
                    const chunk = buffer.slice(0, boundary);
                    buffer = buffer.slice(boundary + 1);
            
                    const chunkJSON = JSON.parse(chunk)
                    setChatResponse(chunkJSON)
                    boundary = buffer.indexOf("\n");

                    console.log(chunkJSON)
                }
            }

            return true;
        } catch(err) {
            console.error(err);
            return false
        }
    }

}

const chatRESTService = new ChatRESTService(BASE_ROUTE)

export default chatRESTService
